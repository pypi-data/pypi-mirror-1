# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import shelve
import shutil
import anydbm
import datetime
import os
import select
import threading

class BaseMultiHashDriver(object):
    """
    Base multihash driver class. Multihash driver is like dictionary of
    dictionaries, it stores multiple dictionaries (hashes) accessible by key
    string. Each hash is read only, to modify use save() method passing new
    dictionary or sequence of (key, value) to it.
    """

    def load(self, key):
        """
        Loads hash associated with key. If no hash found raises KeyError.

        @param key: key string
        @return: read only dictionary like object
        """
        raise KeyError(key)

    def get_mtime(self, key):
        """
        Returns hash modification time (last save time). Raises KeyError if no
        hash found.

        @param key: key string
        @return: datetime.datetime object of last modification

        """
        raise KeyError(key)

    def save(self, key, value, blocking = True):
        """
        Creates new hash or overrides existing. New hash initialized by value
        that is dictionary or sequence of (key, value).

        If any concurrent thread/process already updates hash and blocking is
        True, then call to this method sleeps until other thread/process finish
        hash updating. If blocking is False and concurrent write access was
        detected, returns False.

        @param key: key string
        @param value: dictionary or sequence of (key, value) to initialize new hash
        @keyword blocking: use blocking or unblocking call
        @return: True if hash was saved, otherwise False
        """
        raise KeyError(key)

class MultiHashInFilesMixin:
    """
    Mixin class for multihash drivers that use files to store hash objects.
    """
    def __init__(self, filename, max_lock_time = None, no_excl = False):
        """
        @param filename: file name to use for hash files (string or callable)
        @param max_lock_time: maximum lock time in seconds or as
                              datetime.timedelta object
        @param no_excl: disable usage of O_EXCL flag when locking
        """
        self.filename = filename
        if max_lock_time is None:
            max_lock_time = datetime.timedelta(seconds = 600)
        elif type(max_lock_time) in (int, long, float):
            max_lock_time = datetime.timedelta(seconds = max_lock_time)
        self.max_lock_time = max_lock_time
        self.no_excl = no_excl

    def get_filename(self, key):
        filename = self.filename
        if callable(filename):
            filename = filename(key)
        elif 'XXX' in filename:
            filename = filename.replace('XXX', key)
        else:
            filename += key
        return filename

    def get_new_filename(self, real_filename):
        return real_filename + '.new'

    def get_lock_filename(self, real_filename):
        return real_filename + '.lock'

    def save_with_locking(self, key, value, blocking, do_save):
        real_filename = self.get_filename(key)
        lock_filename = self.get_lock_filename(real_filename)
        new_filename = self.get_new_filename(real_filename)
        error = None
        loop_cnt = 0

        while True:
            loop_cnt += 1
            if self.no_excl:
                # if usage of O_EXCL flag is disabled
                try:
                    fd = os.open(lock_filename, os.O_RDONLY)
                except OSError:
                    fd = os.open(lock_filename, os.O_CREAT)
                    break
            else:
                # locking using O_EXCL flag
                try:
                    fd = os.open(lock_filename, os.O_CREAT | os.O_EXCL)
                except OSError, e:
                    error = e
                else:
                    break
                try:
                    fd = os.open(lock_filename, os.O_RDONLY)
                except OSError:
                    if loop_cnt >= 3:
                        raise error
                    continue
            try:
                # check lock time
                lock_time = datetime.datetime.fromtimestamp(os.fstat(fd).st_ctime)
                if lock_time + self.max_lock_time <= datetime.datetime.now():
                    os.unlink(lock_filename)
                    continue
                if not blocking:
                    return False
                # wait until lock file was removed
                select.select((), (), (fd,), 5)
            finally:
                os.close(fd)
        try:
            # save data to newly created file, then just move it to the real
            # file, so that other precesses/threads can read old data while new
            # data is not completely written
            do_save(new_filename, value)
            shutil.move(new_filename, real_filename)
        finally:
            os.close(fd)
            os.unlink(lock_filename)
        return True

class MemMultiHashDriver(BaseMultiHashDriver):
    """
    Memory multihash driver.

    >>> drv = MemMultiHashDriver()
    >>> drv.save('foo', dict(bar = 3))
    True
    >>> drv.load('foo')['bar']
    3
    """
    def __init__(self):
        self.db = {}
        self.db_mtime = {}
        self.db_lock = threading.Lock()

    def load(self, key):
        return self.db[key]

    def get_mtime(self, key):
        return self.db_mtime[key]

    def save(self, key, value, blocking = True):
        result = self.db_lock.acquire(blocking)
        if not result:
            return False
        try:
            if isinstance(value, dict):
                value = value.copy()
            else:
                value = dict(value)
            self.db[key] = value
            self.db_mtime[key] = datetime.datetime.now()
        finally:
            self.db_lock.release()
        return True

class ShelveMultiHashDriver(BaseMultiHashDriver, MultiHashInFilesMixin):
    """
    Multihash driver that use shelve module to store hashes.

    >>> import os
    >>> import os.path
    >>> filename = 'shelve_multihash_test_XXX.db'
    >>> os.path.exists(filename.replace('XXX', 'foo'))
    False
    >>> drv = ShelveMultiHashDriver(filename)
    >>> drv.save('foo', dict(bar = 3))
    True
    >>> os.path.exists(filename.replace('XXX', 'foo'))
    True
    >>> drv.load('foo')['bar']
    3
    >>> def test_generator():
    ...   for i in range(100):
    ...     if i == 5:
    ...       x = drv.save('foo', dict(bar = 3), blocking = False)
    ...       assert x == False
    ...     yield ('bar%d' % i, i)
    >>> drv.save('foo', test_generator())
    True
    >>> drv.load('foo')['bar55']
    55
    >>> os.unlink(filename.replace('XXX', 'foo'))
    """
    def __init__(self, filename, max_lock_time = None, no_excl = False,
            db_module = None):
        """
        @param filename: file name to use for hash files (string or callable)
        @keyword max_lock_time: maximum lock time in seconds or as
                                datetime.timedelta object
        @keyword no_excl: disable usage of O_EXCL flag when locking
        @keyword db_module: DBM module to use
        """
        MultiHashInFilesMixin.__init__(self, filename, max_lock_time, no_excl)
        if isinstance(db_module, basestring):
            db_module = __import__(db_module)
        self.db_module = db_module

    def load(self, key):
        try:
            return shelve.open(self.get_filename(key), 'r')
        except anydbm.error:
            raise KeyError(key)

    def get_mtime(self, key):
        try:
            return datetime.datetime.fromtimestamp(os.stat(
                self.get_filename(key)).st_mtime)
        except OSError:
            raise KeyError(key)

    def save(self, key, value, blocking = True):
        def do_save(new_filename, value):
            if isinstance(value, dict):
                value = value.items()
            if self.db_module:
                # if appropriate db module is specified, use it to create empty
                # database
                db = self.db_module.open(new_filename, 'n')
                db.sync()
                db = shelve.open(new_filename, 'w')
            else:
                db = shelve.open(new_filename, 'n')
            for k, v in value:
                db[k] = v
            db.sync()
        return self.save_with_locking(key, value, blocking, do_save)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
