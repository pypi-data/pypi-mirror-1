# -*- coding: utf-8 -*-
"""Recipe backup"""
import sys
import os

from zc.buildout import easy_install 
from zc.recipe.egg import Egg

realpath = os.path.realpath

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.egg = Egg(buildout, options['recipe'], options)
        self.buildout, self.options, self.name = buildout, options, name
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
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
        archive_name = options.get('archive-root-name', 'archive')
        exclude_folders = options.get('exclude-folders', '')
        exclude_folders = [folder.strip() 
                           for folder in exclude_folders.split('\n')
                           if folder.strip() != '']
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
                                                 fs_location))

        res2 = easy_install.scripts([(restore_name, module_name, 
                                     'restore_buildout')],
                                      ws, executable, 
                                      options['bin-directory'],
                                      arguments=(location, target_folder,
                                                 logfile, fs_location))

        # will remove all returned files upon reinstall.
        return tuple(res+res2)

    # it is perfectly safe here to rewrite the scripts
    update = install

