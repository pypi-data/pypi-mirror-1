Supported options
=================

The recipe supports the following options:

backup-script-name
    Name of the backup script. Default: `backup`

restore-script-name
    Name of the restore script. Default: `restore`

format
    Formated name of the archive.
    Default to %(name)s-%(year)s-%(month)s-%(day)s-%(hour)s-%(minute)s
    where name is the section name

exclude-folders
    Names of folder to avoid backing up. Relative to buildout root.

include-folders
    If set, back up those folders only. Relative to buildout root.

fs-location
    If given, indicates the path of the file system storage.
    The recipe will carefully copy it when doing a backup,
    by using a transaction-level read of the file.
    This means that you can launch a backup without stopping
    the Zope server.

target-folder
    Folder where the archives are stored. **Mandatory**

log-file
    File where all calls are recorded. **Mandatory**

archive-before-restore
    If not set to 0, do a complete backup before a restore

prompt-before-restore
    If not set to 0, prompt before a restore
    
base-path
    If set, backup this path instead base on instance path

Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> import os
    >>> root =  os.path.split(sample_buildout)[0]
    >>> if root == '':
    ...     root = '.'

Let's copy a real Data.fs in our buildout::

    >>> import shutil
    >>> data_fs = os.path.join(test_dir, 'Data.fs')
    >>> shutil.copyfile(data_fs, join(sample_buildout, 'Data.fs'))

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = backup
    ... index = http://pypi.python.org/simple
    ...
    ... [backup]
    ... recipe = iw.recipe.backup
    ...
    ... format = %(format)s
    ... target-folder = %(root)s
    ... log-file = %(root)s/backup.log
    ... fs-location = ${buildout:directory}/Data.fs
    ... """ % {'root': root, 'format':'%(name)s-%(year)s-%(month)s-%(day)s'})

Let's run the buildout::

    >>> null = system(buildout)

Let's see what we got in the backup script::

    >>> print open(join(sample_buildout, 'bin', 'backup')).read()
    #!...
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      ...
      ]
    <BLANKLINE>
    import iw.recipe.backup.archive
    <BLANKLINE>
    if __name__ == '__main__':
        iw.recipe.backup.archive.archive_buildout(('/sample-buildout', '%(name)s-%(year)s-%(month)s-%(day)s', '..._TEST_', '/backup.log', [], [], '/sample-buildout/Data.fs', {'name': 'backup'}))
    <BLANKLINE>

Ok, let's call it to backup the current buildout::

    >>> print system(join(sample_buildout, 'bin', 'backup'))
    Starting the backup...
    Archived in /backup-XXXX-XX-XX.tar.gz
    ...
    <BLANKLINE>

We should have a log file generated as well::

    >>> print open(join(root, 'backup.log')).read()
    20... Starting the backup...
    20... INFO Archived in /backup-XXXX-XX-XX.tar.gz

We also have a restore feature::

    >>> print system(join(sample_buildout, 'bin', 'restore'))
    Usage: ...restore archive_name
    <BLANKLINE>

Let's set the user input::

    >>> from iw.recipe.backup.testing import set_input
    >>> set_input('Y')

Oh right, the restore script takes the name of the archive::

    >>> import glob
    >>> arc = glob.glob('%s/*.tar.gz' % root)[0]
    >>> print system(join(sample_buildout, 'bin', 'restore %s' % arc))
    Are you sure you want to restore ? Every data will be lost ! (y/N)  Y
    Archiving current folder before restoring
    Starting the backup...
    Archived in /before-restore-XXXX-XX-XX-XX-XX.tar.gz
    Starting the restore...
    Archive restored in /sample-buildout
    ...
    <BLANKLINE>

And a restore *always* makes an archive on the current folder before
it is applied, to make sure nothing is never lost.

There's also something quite important: make sure the archive and
log files are not located in the buildout !::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = backup
    ... index = http://pypi.python.org/simple
    ...
    ... [backup]
    ... recipe = iw.recipe.backup
    ...
    ... target-folder = %(root)s
    ... log-file = %(root)s/backup.log
    ... """ % {'root': sample_buildout})

    >>> print system(buildout)
    Uninstalling backup.
    Installing backup.
    While:
      Installing backup.
    <BLANKLINE>
    An internal error occured due to a bug in either zc.buildout or in a
    recipe being used:
    ...
    ValueError: Cannot backup within the buildout ! Check your values
    <BLANKLINE>

A bit of cleaning::

    >>> import glob
    >>> arc = glob.glob('%s/*.tar.gz' % root)
    >>> for f in arc:
    ...     os.remove(f)

We can also exclude some folders from being archived::

    >>> os.mkdir(join(sample_buildout, 'not'))
    >>> open(join(sample_buildout, 'not', 'f'), 'w').write('me file')

    >>> os.mkdir(join(sample_buildout, 'neh'))

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = backup
    ... index = http://pypi.python.org/simple
    ...
    ... [backup]
    ... recipe = iw.recipe.backup
    ...
    ... target-folder = %(root)s
    ... log-file = %(root)s/backup.log
    ... fs-location = ${buildout:directory}/Data.fs
    ... exclude-folders =
    ...     %(sample_buildout)s/not
    ...     %(sample_buildout)s/neh
    ... """ % {'root': root, 'sample_buildout': sample_buildout})

Running the buildout again::

    >>> print system(buildout+' -D')
    Installing backup.
    Generated script '...backup'.
    Generated script '...restore'.
    <BLANKLINE>

Let's backup::

    >>> print system(join(sample_buildout, 'bin', 'backup'))
    Starting the backup...
    Archived in /backup-XXXX-XX-XX-XX-XX.tar.gz
    ...
    <BLANKLINE>

Let's remove the folder and the Data.fs::

    >>> import shutil
    >>> shutil.rmtree(join(sample_buildout, 'not'))
    >>> os.rmdir(join(sample_buildout, 'neh'))
    >>> os.remove(join(sample_buildout, 'Data.fs'))

Let's restore::

    >>> arc = glob.glob('%s/*.tar.gz' % root)[0]
    >>> print system(join(sample_buildout, 'bin', 'restore %s' % arc))
    Are you sure you want to restore ? Every data will be lost ! (y/N)  Y
    ...
    <BLANKLINE>

And make sure the `not` folder is not back !

    >>> os.path.exists(join(sample_buildout, 'not'))
    False
    >>> os.path.exists(join(sample_buildout, 'neh'))
    False

And the `Data.fs` is back, so we're OK::

    >>> os.path.exists(join(sample_buildout, 'Data.fs'))
    True

==============

We can also restrict archive on some folders ::

    >>> os.mkdir(join(sample_buildout, 'not'))
    >>> open(join(sample_buildout, 'not', 'f'), 'w').write('me file')

    >>> os.mkdir(join(sample_buildout, 'neh'))
    >>> open(join(sample_buildout, 'neh', 'f'), 'w').write('me file')
    
    >>> os.mkdir(join(sample_buildout, 'neh/not'))
    >>> open(join(sample_buildout, 'neh/not', 'f'), 'w').write('me file')

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = backup
    ... index = http://pypi.python.org/simple
    ...
    ... [backup]
    ... recipe = iw.recipe.backup
    ...
    ... target-folder = %(root)s
    ... log-file = %(root)s/backup.log
    ... fs-location = ${buildout:directory}/Data.fs
    ... exclude-folders =
    ...     %(sample_buildout)s/not
    ...     %(sample_buildout)s/neh/not
    ... include-folders =
    ...     %(sample_buildout)s/neh
    ... prompt-before-restore = 0
    ... archive-before-restore = 0
    ... """ % {'root': root, 'sample_buildout': sample_buildout})

Running the buildout again::

    >>> print system(buildout+' -D')
    Uninstalling backup.
    Installing backup.
    Generated script '...backup'.
    Generated script '...restore'.
    <BLANKLINE>

Let's see what we got in the backup script::

    >>> print open(join(sample_buildout, 'bin', 'backup')).read()
    #!...
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      ...
      ]
    <BLANKLINE>
    import iw.recipe.backup.archive
    <BLANKLINE>
    if __name__ == '__main__':
        iw.recipe.backup.archive.archive_buildout(('/sample-buildout', '...', '..._TEST_', '/backup.log', ['/sample-buildout/not', '/sample-buildout/neh/not'], ['/sample-buildout/neh'], '/sample-buildout/Data.fs', {'name': 'backup'}))
    <BLANKLINE>

    
Let's backup::

    >>> print system(join(sample_buildout, 'bin', 'backup'))
    Starting the backup...
    Archived in /backup-XXXX-XX-XX-XX-XX.tar.gz
    <BLANKLINE>

Let's remove the folder and the Data.fs::
    
    >>> import shutil
    >>> shutil.rmtree(join(sample_buildout, 'not'))
    >>> shutil.rmtree(join(sample_buildout, 'neh'))
    >>> os.remove(join(sample_buildout, 'Data.fs'))
    
Let's restore::

    >>> arc = glob.glob('%s/*.tar.gz' % root)[0]
    >>> rest = os.popen(join(sample_buildout, 'bin', 'restore %s' % arc))
	
And make sure the `not` folder and 'neh/not' are not back and neh is back !
    >>> os.path.exists(join(sample_buildout, 'not'))
    False
    >>> os.path.exists(join(sample_buildout, 'neh/not'))
    False
    >>> os.path.exists(join(sample_buildout, 'neh'))
    True
