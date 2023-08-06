import os
import sys
import logging

from tempfile import mkdtemp
from tarfile import TarFile
from tarfile import ExtractError
from datetime import datetime
join = os.path.join

from iw.recipe.backup.testing import get_input
from iw.recipe.backup.filestorage import backup_fs

if sys.version_info[0:2] < (2, 5):
    # this come from python 2.5
    def extractall(self, path=".", members=None):
        """Extract all members from the archive to the current working
        directory and set owner, modification time and permissions on
        directories afterwards. `path' specifies a different directory
        to extract to. `members' is optional and must be a subset of the
        list returned by getmembers().
        """
        directories = []
        if members is None:
            members = self
        for tarinfo in members:
            if tarinfo.isdir():
                # Extract directory with a safe mode, so that
                # all files below can be extracted as well.
                try:
                    os.makedirs(os.path.join(path, tarinfo.name), 0700)
                except EnvironmentError:
                    pass
                directories.append(tarinfo)
            else:
                self.extract(tarinfo, path)

        # Revers sort directories.
        directories.sort(lambda a, b: cmp(a.name, b.name))
        directories.reverse()

        # Set correct owner, mtime and filemode on directories.
        for tarinfo in directories:
            path = os.path.join(path, tarinfo.name)
            try:
                self.chown(tarinfo, path)
                self.utime(tarinfo, path)
                self.chmod(tarinfo, path)
            except ExtractError, e:
                if self.errorlevel > 1:
                    raise
                else:
                    self._dbg(1, "tarfile: %s" % e)
    TarFile.extractall = extractall

def archive_folder(location, archive, target_folder, exclude_folders, include_folders,
                   fs_location):
    """Generates an archive given a folder."""
    if fs_location is not None:
        fs_location = os.path.realpath(fs_location)
    # we want a relative storage
    old_dir = os.getcwd()
    os.chdir(location)
    exclude_folders = [os.path.realpath(path) for path in exclude_folders]
    include_folders = [os.path.realpath(path) for path in include_folders]
    tar = TarFile.open(join(target_folder, archive), 'w:gz')
    tmp = None
    try:
        
        for root, dirs, filenames in os.walk('.'):
            stop = False
            real_path = os.path.realpath(root)
            for exclude in exclude_folders:
                if real_path.startswith(exclude):
                    stop = True
                    break
            if include_folders:
                not_included = True
                for include in include_folders:
                    if real_path.startswith(include):
                        not_included = False
                if not_included:
                    stop = True
            if stop:
                continue
            # archiving empty dirs as well
            for dir_ in dirs:
                fullpath = os.path.join(root, dir_)
                if os.path.realpath(fullpath) in exclude_folders:
                    continue
                if os.listdir(fullpath) == []:
                    arcname = fullpath.replace(location, '.')
                    tar.add(fullpath, arcname, False)
            for filename in filenames:
                path = join(root, filename)
                arcname = path.replace(location, '.')
                # backing up fs with a clean transaction-level
                if os.path.realpath(path) == fs_location:
                    tmp = os.path.join(mkdtemp(), 'Data.fs')
                    backup_fs(fs_location, tmp)
                    tar.add(tmp, arcname, False)
                else:
                    tar.add(path, arcname, False)
    finally:
        tar.close()
        os.chdir(old_dir)

    if tmp is not None:
        os.remove(tmp)

def restore_folder(archive, target_folder):
    """Restores an archive"""
    tar = TarFile.open(archive, 'r')
    tar.extractall(target_folder)

def _log(msg, logfile=None):
    """Logs the actions"""
    print msg
    if logfile is None:
        return
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(levelname)s %(message)s',
                filename=logfile,
                filemode='a')
    logging.info(msg)

def archive_buildout(args):
    """Archive a buildout."""
    (location, format, target_folder, log_file,
     exclude_folders, include_folders, fs_location, options) = args
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    _log('Starting the backup...', log_file)
    now = datetime.now()
    options['year'] = str(now.year)
    options['month'] = '%02i' % now.month
    options['day'] = '%02i' % now.day
    options['hour'] = '%02i' % now.hour
    options['minute'] = '%02i' % now.minute
    archive_name = '%s.tar.gz' % (format % options,)
    archive_folder(location, archive_name, target_folder, exclude_folders,
                   include_folders, fs_location)
    _log('Archived in %s' % join(target_folder, archive_name), log_file)

def _get_input(msg):
    debug = get_input(msg)
    if debug is not None:
        res = debug
    else:
        res = raw_input(msg)
    return res.lower().strip() == 'y'

def restore_buildout(args):
    """De-archive buildout"""
    target_folder, archives_folder, log_file, \
    fs_location, archive_before_backup, prompt_before_restore = args
    if len(sys.argv) != 2:
        _log('Usage: %s archive_name' % sys.argv[0])
        sys.exit(0)
    if prompt_before_restore:
        res = _get_input(('Are you sure you want to restore ? '
                          'Every data will be lost ! (y/N) '))
        if not res:
            sys.exit(1)

    if archive_before_backup:
        # create an archive of the existing folder
        _log('Archiving current folder before restoring')
        args = [target_folder,
                '%(name)s-%(year)s-%(month)s-%(day)s-%(hour)s-%(minute)s',
                archives_folder, log_file, [], [], fs_location,
                {'name':'before-restore'}]
        archive_buildout(args)

    _log('Starting the restore...', log_file)
    restore_folder(sys.argv[1], target_folder)
    _log('Archive restored in %s' % target_folder, log_file)

