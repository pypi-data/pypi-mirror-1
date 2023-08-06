# -*- coding: utf-8 -*-

# daemon/pidlockfile.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2008–2009 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Lockfile behaviour implemented via Unix PID files.
    """

import os
import errno
import time

from lockfile import (
    LockBase,
    AlreadyLocked, LockFailed,
    NotLocked, NotMyLock,
    )


class PIDLockFile(LockBase):
    """ Lockfile implemented as a Unix PID file.

        The lock file is a normal file named by the attribute `path`.
        A lock's PID file contains a single line of text, containing
        the process ID (PID) of the process that acquired the lock.

        """

    def read_pid(self):
        """ Get the PID from the lock file.
            """
        result = read_pid_from_pidfile(self.path)
        return result

    def is_locked(self):
        """ Test if the lock is currently held.

            The lock is held if the PID file for this lock exists.

            """
        result = pidfile_exists(self.path)
        return result

    def i_am_locking(self):
        """ Test if the lock is held by the current process.

            Returns ``True`` if the current process ID matches the
            number stored in the PID file.

            """
        result = False
        current_pid = os.getpid()
        pidfile_pid = self.read_pid()
        if current_pid == pidfile_pid:
            result = True
        return result

    poll_interval = 0.1

    def acquire(self, timeout=None):
        """ Acquire the lock.

            Creates the PID file for this lock, then returns None.

            If the lock is already held, behaviour depends on the
            `timeout` parameter:

            * `timeout` is ``None``: poll every 0.1 seconds, waiting
              for the lock indefinitely.

            * `timeout` > 0: poll every 0.1 seconds, waiting for the
              lock. After `timeout` seconds elapse without acquiring
              the lock, raise an `AlreadyLocked` error.

            * `timeout` <= 0: immediately raise an `AlreadyLocked`
              error.

            """
        if timeout is not None:
            request_timestamp = time.time()
            timeout_timestamp = request_timestamp + timeout
        while pidfile_exists(self.path):
            if timeout is not None:
                if time.time() > timeout_timestamp:
                    error = AlreadyLocked()
                    raise error
            time.sleep(self.poll_interval)
        try:
            write_pid_to_pidfile(self.path)
        except OSError:
            error = LockFailed()
            raise error

    def release(self):
        """ Release the lock.

            Removes the PID file to release the lock, or raises an
            error if the current process does not hold the lock.

            """
        if not self.is_locked():
            error = NotLocked()
            raise error
        if not self.i_am_locking():
            error = NotMyLock()
            raise error
        remove_existing_pidfile(self.path)

    def break_lock(self):
        """ Break an existing lock.

            Removes the PID file if it already exists, otherwise does
            nothing.

            """
        remove_existing_pidfile(self.path)


def pidfile_exists(pidfile_path):
    """ Return True if the named PID file exists on the filesystem.
        """
    result = os.path.exists(pidfile_path)
    return result


def read_pid_from_pidfile(pidfile_path):
    """ Read the PID recorded in the named PID file.

        Read and return the numeric PID recorded as text in the named
        PID file. If the PID file cannot be read, or if the content is
        not a valid PID, return ``None``.

        """
    pid = None
    try:
        pidfile = open(pidfile_path, 'r')
    except IOError:
        pass
    else:
        line = pidfile.read().strip()
        try:
            pid = int(line)
        except ValueError:
            pass
        pidfile.close()

    return pid


def write_pid_to_pidfile(pidfile_path):
    """ Write the PID in the named PID file.

        Get the numeric process ID (“PID”) of the current process
        and write it to the named file as a line of text.

        """
    pidfile = open(pidfile_path, 'w')

    pid = os.getpid()
    line = "%(pid)d\n" % vars()
    pidfile.write(line)


def remove_existing_pidfile(pidfile_path):
    """ Remove the named PID file if it exists.

        Remove the named PID file. Ignore the condition if the file
        does not exist, since that only means we are already in the
        desired state.

        """
    try:
        os.remove(pidfile_path)
    except OSError, exc:
        if exc.errno == errno.ENOENT:
            pass
        else:
            raise
