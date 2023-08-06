# Copyright (C) 2001-2008 by the Free Software Foundation, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

"""Master sub-process watcher."""

from __future__ import with_statement

__metaclass__ = type
__all__ = [
    'Loop',
    'get_lock_data',
    ]


import os
import sys
import errno
import signal
import socket
import logging

from datetime import timedelta
from locknix import lockfile
from munepy import Enum

from mailman import Defaults
from mailman import loginit
from mailman.configuration import config
from mailman.i18n import _
from mailman.options import Options


DOT = '.'
LOCK_LIFETIME = Defaults.days(1) + Defaults.hours(6)



class ScriptOptions(Options):
    """Options for the master watcher."""

    usage = _("""\
Master sub-process watcher.

Start and watch the configured queue runners and ensure that they stay alive
and kicking.  Each are fork and exec'd in turn, with the master waiting on
their process ids.  When it detects a child queue runner has exited, it may
restart it.

The queue runners respond to SIGINT, SIGTERM, SIGUSR1 and SIGHUP.  SIGINT,
SIGTERM and SIGUSR1 all cause the qrunners to exit cleanly.  The master will
restart qrunners that have exited due to a SIGUSR1 or some kind of other exit
condition (say because of an exception).  SIGHUP causes the master and the
qrunners to close their log files, and reopen then upon the next printed
message.

The master also responds to SIGINT, SIGTERM, SIGUSR1 and SIGHUP, which it
simply passes on to the qrunners.  Note that the master will close and reopen
its own log files on receipt of a SIGHUP.  The master also leaves its own
process id in the file `data/master-qrunner.pid` but you normally don't need
to use this pid directly.

Usage: %prog [options]""")

    def add_options(self):
        self.parser.add_option(
            '-n', '--no-restart',
            dest='restartable', default=True, action='store_false',
            help=_("""\
Don't restart the qrunners when they exit because of an error or a SIGUSR1.
Use this only for debugging."""))
        self.parser.add_option(
            '-f', '--force',
            default=False, action='store_true',
            help=_("""\
If the master watcher finds an existing master lock, it will normally exit
with an error message.  With this option,the master will perform an extra
level of checking.  If a process matching the host/pid described in the lock
file is running, the master will still exit, requiring you to manually clean
up the lock.  But if no matching process is found, the master will remove the
apparently stale lock and make another attempt to claim the master lock."""))
        self.parser.add_option(
            '-r', '--runner',
            dest='runners', action='append', default=[],
            help=_("""\
Override the default set of queue runners that the master watch will invoke
instead of the default set.  Multiple -r options may be given.  The values for
-r are passed straight through to bin/qrunner."""))

    def sanity_check(self):
        if len(self.arguments) > 0:
            self.parser.error(_('Too many arguments'))



def get_lock_data():
    """Get information from the master lock file.

    :return: A 3-tuple of the hostname, integer process id, and file name of
        the lock file.
    """
    with open(config.LOCK_FILE) as fp:
        filename = os.path.split(fp.read().strip())[1]
    parts = filename.split('.')
    hostname = DOT.join(parts[1:-2])
    pid = int(parts[-2])
    return hostname, int(pid), filename


class WatcherState(Enum):
    # Another master watcher is running.
    conflict = 1
    # No conflicting process exists.
    stale_lock = 2
    # Hostname from lock file doesn't match.
    host_mismatch = 3


def master_state():
    """Get the state of the master watcher.

    :return: WatcherState describing the state of the lock file.
    """

    # 1 if proc exists on host (but is it qrunner? ;)
    # 0 if host matches but no proc
    # hostname if hostname doesn't match
    hostname, pid, tempfile = get_lock_data()
    if hostname <> socket.gethostname():
        return WatcherState.host_mismatch
    # Find out if the process exists by calling kill with a signal 0.
    try:
        os.kill(pid, 0)
        return WatcherState.conflict
    except OSError, e:
        if e.errno == errno.ESRCH:
            # No matching process id.
            return WatcherState.stale_lock
        # Some other error occurred.
        raise


def acquire_lock_1(force):
    """Try to acquire the master queue runner lock.

    :param force: Flag that controls whether to force acquisition of the lock.
    :return: The master queue runner lock.
    :raises: `TimeOutError` if the lock could not be acquired.
    """
    lock = lockfile.Lock(config.LOCK_FILE, LOCK_LIFETIME)
    try:
        lock.lock(timedelta(seconds=0.1))
        return lock
    except lockfile.TimeOutError:
        if not force:
            raise
        # Force removal of lock first.
        lock.disown()
        hostname, pid, tempfile = get_lock_data()
        os.unlink(config.LOCK_FILE)
        os.unlink(os.path.join(config.LOCK_DIR, tempfile))
        return acquire_lock_1(force=False)


def acquire_lock(force):
    """Acquire the master queue runner lock.

    :return: The master queue runner lock or None if the lock couldn't be
        acquired.  In that case, an error messages is also printed to standard
        error.
    """
    try:
        lock = acquire_lock_1(force)
        return lock
    except lockfile.TimeOutError:
        status = master_state()
        if status == WatcherState.conflict:
            # Hostname matches and process exists.
            message = _("""\
The master qrunner lock could not be acquired because it appears
as though another master qrunner is already running.
""")
        elif status == WatcherState.stale_lock:
            # Hostname matches but the process does not exist.
            message = _("""\
The master qrunner lock could not be acquired.  It appears as though there is
a stale master qrunner lock.  Try re-running mailmanctl with the -s flag.
""")
        else:
            assert status == WatcherState.host_mismatch, (
                'Invalid enum value: %s' % status)
            # Hostname doesn't even match.
            hostname, pid, tempfile = get_lock_data()
            message = _("""\
The master qrunner lock could not be acquired, because it appears as if some
process on some other host may have acquired it.  We can't test for stale
locks across host boundaries, so you'll have to clean this up manually.

Lock file: $config.LOCK_FILE
Lock host: $hostname

Exiting.""")
        config.options.parser.error(message)



class Loop:
    """Main control loop class."""

    def __init__(self, lock=None, restartable=None, config_file=None):
        self._lock = lock
        self._restartable = restartable
        self._config_file = config_file
        self._kids = {}

    def install_signal_handlers(self):
        """Install various signals handlers for control from mailmanctl."""
        log = logging.getLogger('mailman.qrunner')
        # Set up our signal handlers.  Also set up a SIGALRM handler to
        # refresh the lock once per day.  The lock lifetime is 1 day + 6 hours
        # so this should be plenty.
        def sigalrm_handler(signum, frame):
            self._lock.refresh()
            signal.alarm(int(Defaults.days(1)))
        signal.signal(signal.SIGALRM, sigalrm_handler)
        signal.alarm(int(Defaults.days(1)))
        # SIGHUP tells the qrunners to close and reopen their log files.
        def sighup_handler(signum, frame):
            loginit.reopen()
            for pid in self._kids:
                os.kill(pid, signal.SIGHUP)
            log.info('Master watcher caught SIGHUP.  Re-opening log files.')
        signal.signal(signal.SIGHUP, sighup_handler)
        # SIGUSR1 is used by 'mailman restart'.
        def sigusr1_handler(signum, frame):
            for pid in self._kids:
                os.kill(pid, signal.SIGUSR1)
            log.info('Master watcher caught SIGUSR1.  Exiting.')
        signal.signal(signal.SIGUSR1, sigusr1_handler)
        # SIGTERM is what init will kill this process with when changing run
        # levels.  It's also the signal 'mailmanctl stop' uses.
        def sigterm_handler(signum, frame):
            for pid in self._kids:
                os.kill(pid, signal.SIGTERM)
            log.info('Master watcher caught SIGTERM.  Exiting.')
        signal.signal(signal.SIGTERM, sigterm_handler)
        # SIGINT is what control-C gives.
        def sigint_handler(signum, frame):
            for pid in self._kids:
                os.kill(pid, signal.SIGINT)
            log.info('Master watcher caught SIGINT.  Restarting.')
        signal.signal(signal.SIGINT, sigint_handler)

    def _start_runner(self, spec):
        """Start a queue runner.

        All arguments are passed to the qrunner process.

        :param spec: A queue runner spec, in a format acceptable to
            bin/qrunner's --runner argument, e.g. name:slice:count
        :return: The process id of the child queue runner.
        """
        pid = os.fork()
        if pid:
            # Parent.
            return pid
        # Child.
        #
        # Craft the command line arguments for the exec() call.
        rswitch = '--runner=' + spec
        # Wherever mailmanctl lives, so too must live the qrunner script.
        exe = os.path.join(config.BIN_DIR, 'qrunner')
        # config.PYTHON, which is the absolute path to the Python interpreter,
        # must be given as argv[0] due to Python's library search algorithm.
        args = [sys.executable, sys.executable, exe, rswitch, '-s']
        if self._config_file is not None:
            args.extend(['-C', self._config_file])
        log = logging.getLogger('mailman.qrunner')
        log.debug('starting: %s', args)
        os.execl(*args)
        # We should never get here.
        raise RuntimeError('os.execl() failed')

    def start_qrunners(self, qrunners=None):
        """Start all the configured qrunners.

        :param qrunners: If given, a sequence of queue runner names to start.
            If not given, this sequence is taken from the configuration file.
        """
        if not qrunners:
            spec_parts = config.qrunners.items()
        else:
            spec_parts = []
            for qrname in qrunners:
                if '.' in qrname:
                    spec_parts.append((qrname, 1))
                else:
                    spec_parts.append((config.qrunner_shortcuts[qrname], 1))
        for qrname, count in spec_parts:
            for slice_number in range(count):
                # qrunner name, slice #, # of slices, restart count
                info = (qrname, slice_number, count, 0)
                spec = '%s:%d:%d' % (qrname, slice_number, count)
                pid = self._start_runner(spec)
                log = logging.getLogger('mailman.qrunner')
                log.debug('[%d] %s', pid, spec)
                self._kids[pid] = info

    def loop(self):
        """Main loop.

        Wait until all the qrunners have exited, restarting them if necessary
        and configured to do so.
        """
        log = logging.getLogger('mailman.qrunner')
        while True:
            try:
                pid, status = os.wait()
            except OSError, error:
                # No children?  We're done.
                if error.errno == errno.ECHILD:
                    break
                # If the system call got interrupted, just restart it.
                elif error.errno == errno.EINTR:
                    continue
                else:
                    raise
            # Find out why the subprocess exited by getting the signal
            # received or exit status.
            if os.WIFSIGNALED(status):
                why = os.WTERMSIG(status)
            elif os.WIFEXITED(status):
                why = os.WEXITSTATUS(status)
            else:
                why = None
            # We'll restart the subprocess if it exited with a SIGUSR1 or
            # because of a failure (i.e. no exit signal), and the no-restart
            # command line switch was not given.  This lets us better handle
            # runaway restarts (e.g.  if the subprocess had a syntax error!)
            qrname, slice_number, count, restarts = self._kids.pop(pid)
            restart = False
            if why == signal.SIGUSR1 and self._restartable:
                restart = True
            # Have we hit the maximum number of restarts?
            restarts += 1
            if restarts > config.MAX_RESTARTS:
                restart = False
            # Are we permanently non-restartable?
            log.debug("""\
Master detected subprocess exit
(pid: %d, why: %s, class: %s, slice: %d/%d) %s""",
                     pid, why, qrname, slice_number + 1, count,
                     ('[restarting]' if restart else ''))
            # See if we've reached the maximum number of allowable restarts
            if restarts > config.MAX_RESTARTS:
                log.info("""\
qrunner %s reached maximum restart limit of %d, not restarting.""",
                         qrname, config.MAX_RESTARTS)
            # Now perhaps restart the process unless it exited with a
            # SIGTERM or we aren't restarting.
            if restart:
                spec = '%s:%d:%d' % (qrname, slice_number, count)
                newpid = self._start_runner(spec)
                self._kids[newpid] = (qrname, slice_number, count, restarts)

    def cleanup(self):
        """Ensure that all children have exited."""
        log = logging.getLogger('mailman.qrunner')
        # Send SIGTERMs to all the child processes and wait for them all to
        # exit.
        for pid in self._kids:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, error:
                if error.errno == errno.ESRCH:
                    # The child has already exited.
                    log.info('ESRCH on pid: %d', pid)
        # Wait for all the children to go away.
        while self._kids:
            try:
                pid, status = os.wait()
                del self._kids[pid]
            except OSError, e:
                if e.errno == errno.ECHILD:
                    break
                elif e.errno == errno.EINTR:
                    continue
                raise



def main():
    """Main process."""

    options = ScriptOptions()
    options.initialize()

    # Acquire the master lock, exiting if we can't acquire it.  We'll let the
    # caller handle any clean up or lock breaking.  No with statement here
    # because Lock's constructor doesn't support a timeout.
    lock = acquire_lock(options.options.force)
    try:
        with open(config.PIDFILE, 'w') as fp:
            print >> fp, os.getpid()
        loop = Loop(lock, options.options.restartable, options.options.config)
        loop.install_signal_handlers()
        try:
            loop.start_qrunners(options.options.runners)
            loop.loop()
        finally:
            loop.cleanup()
            os.remove(config.PIDFILE)
    finally:
        lock.unlock()



if __name__ == '__main__':
    main()
