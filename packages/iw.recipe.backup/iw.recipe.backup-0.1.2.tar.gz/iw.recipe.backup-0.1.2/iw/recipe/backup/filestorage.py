# inspired from repozo.py
import os
from stat import ST_SIZE
import warnings

READCHUNK = 16 * 1024

try:
    from ZODB.FileStorage import FileStorage
    _no_transaction = False
except ImportError:
    # will not support transaction read
    _no_transaction = True

def _fsync(afile):
    afile.flush()
    fileobject = getattr(afile, 'fileobj', afile)
    os.fsync(fileobject.fileno())

def _read_file(func, fp, n=None):
    """Read file bytes"""
    bytesread = 0L
    while n is None or n > 0:
        if n is None:
            todo = READCHUNK
        else:
            todo = min(READCHUNK, n)
        data = fp.read(todo)
        if not data:
            break
        func(data)
        nread = len(data)
        bytesread += nread
        if n is not None:
            n -= nread
    return bytesread

def _last_transaction_pos(data_fs):
    """returns the last valid transaction position"""
    if _no_transaction:
        warnings.warn('The storage might contain broken transactions') 
        return os.stat(data_fs)[ST_SIZE]
    fs = FileStorage(filename, read_only=True)
    try:
        return fs.getSize()
    finally:
        fs.close()

def backup_fs(source, target):
    """Perform a binary backup, by taking care of getting the
    last valid transaction record"""
    pos = _last_transaction_pos(source)
    data_fs = open(source, 'rb')
    data_fs.seek(0)
    tempname = os.path.join(os.path.dirname(target), 'tmp.tmp')    
    target_file = open(tempname, 'wb')
    ndone = _read_file(target_file.write, data_fs, pos)
    data_fs.close()
    _fsync(target_file)
    target_file.close()
    os.rename(tempname, target)

