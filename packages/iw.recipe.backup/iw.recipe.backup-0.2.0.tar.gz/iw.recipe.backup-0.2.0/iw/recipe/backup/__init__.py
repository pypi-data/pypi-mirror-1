# -*- coding: utf-8 -*-
"""Recipe backup"""
import sys
import os
import warnings

from zc.buildout import easy_install
from zc.recipe.egg import Egg

realpath = os.path.realpath

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.egg = Egg(buildout, options['recipe'], options)
        self.buildout, self.options, self.name = buildout, options, name
        options['location'] = options.get('location', os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            ))
        options['buildout-directory'] = buildout['buildout']['directory']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['scripts'] = '' # suppress script generation.

    def install(self):
        """Installer"""
        options = self.options
        requirements, ws = self.egg.working_set()
        backup_name = options.get('backup-script-name', 'backup')
        restore_name = options.get('restore-script-name', 'restore')
        module_name = 'iw.recipe.backup.archive'
        executable = options.get('executable', sys.executable)
        location = realpath(options['buildout-directory'])
        # backward compat
        archive_name = options.get('archive-root-name', None)
        if not archive_name:
            archive_name = options.get('format',
                    '%(name)s-%(year)s-%(month)s-%(day)s-%(hour)s-%(minute)s')
        else:
            message = 'archive-root-name option is deprecated.'
            message += ' Please use format instead'
            warnings.warn(message, DeprecationWarning)
            archive_name += '-%(year)s-%(month)s-%(day)s-%(hour)s-%(minute)s'

        exclude_folders = options.get('exclude-folders', '')
        exclude_folders = [folder.strip()
                           for folder in exclude_folders.split('\n')
                           if folder.strip() != '']
        include_folders = options.get('include-folders', '')
        include_folders = [folder.strip()
                           for folder in include_folders.split('\n')
                           if folder.strip() != '']
        archive_before_restore = options.get('archive-before-restore', '1')
        archive_before_restore = bool(int(archive_before_restore))
        prompt_before_restore = options.get('prompt-before-restore', '1')
        prompt_before_restore = bool(int(prompt_before_restore))

        fs_location = options.get('fs-location', None)

        # mandatory options
        target_folder = realpath(options['target-folder'])
        logfile = realpath(options['log-file'])

        if (target_folder.startswith(location) or
            logfile.startswith(location)):
            raise ValueError(('Cannot backup within the buildout !'
                              ' Check your values'))

        res = easy_install.scripts([(backup_name, module_name,
                                     'archive_buildout')],
                                    ws, executable,
                                    options['bin-directory'],
                                    arguments = (location, archive_name,
                                                 target_folder, logfile,
                                                 exclude_folders,
                                                 include_folders,
                                                 fs_location,
                                                 dict(name=self.name)))

        res2 = easy_install.scripts([(restore_name, module_name,
                                     'restore_buildout')],
                                      ws, executable,
                                      options['bin-directory'],
                                      arguments=(location, target_folder,
                                                 logfile, fs_location,
                                                 archive_before_restore,
                                                 prompt_before_restore))

        # will remove all returned files upon reinstall.
        return tuple(res+res2)

    # it is perfectly safe here to rewrite the scripts
    update = install

