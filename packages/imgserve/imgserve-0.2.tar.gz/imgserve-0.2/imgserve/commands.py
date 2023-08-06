"""
Implements the imgserve command line tool's commands, which are run by
the args module dynamically.  Each command has it's actual user
displayed command line documentation as the __doc__ string.
"""

import os
import signal
import sys
import time
import imgserve
from imgserve.manager import ImgManager
from imgserve import args, utils


if os.getuid():
    # Non root user
    DIR = os.path.join(os.path.expanduser('~'), '.imgserve')
    PID_FILEPATH = os.path.join(DIR, 'imgserve.pid')
    LOG_DIR = os.path.join(DIR, 'log')
else:
    # Root user
    PID_FILEPATH = '/var/run/imgserve.pid'
    LOG_DIR = '/var/log/imgserve'


def start_command(pid=PID_FILEPATH, logdir=LOG_DIR, FORCE=False, chroot=False,
                  chdir=".", boot="config.boot", uid=False, gid=False,
                  umask=False, host="0.0.0.0", port=8602):
    """
    Runs an imgserve server out of the current directory:

        imgserve start -host 127.0.0.1 -port 8602
    """
    utils.start_server(pid, logdir, FORCE, chroot, chdir, uid, gid, umask,
                       ImgManager, host, port)


def stop_command(pid=PID_FILEPATH, KILL=False):
    """
    Stops a running imgserve server.  Give -KILL True to have it
    stopped violently.  The PID file is removed after the signal is
    sent.

        imgserve stop
    """

    if not os.path.exists(pid):
        print "PID file %s doesn't exist, maybe imgserve isn't running?" % pid
        sys.exit(1)
        return # for unit tests mocking sys.exit

    pid_f = pid
    pid = open(pid_f).readline()

    print "Attempting to stop imgserve at pid %d" % int(pid)

    try:
        if KILL:
            os.kill(int(pid), signal.SIGTERM)
        else:
            os.kill(int(pid), signal.SIGHUP)

        os.unlink(pid_f)
    except OSError, exc:
        print "ERROR stopping imgserve on PID %d: %s" % (int(pid), exc)


def restart_command(**options):
    """
    Simply attempts a stop and then a start command.  All options for
    both apply to restart.  See stop and start for options available.

        imgserve restart
    """
    stop_command(**options)
    time.sleep(2)
    start_command(**options)


def status_command(pid=PID_FILEPATH):
    """
    Prints out status information about imgserve useful for finding
    out if it's running and where.

        imgserve status
    """
    if os.path.exists(pid):
        pid = open(pid).readline()
        print "imgserve running with PID %d" % int(pid)
    else:
        print "imgserve not running."


def help_command(**options):
    """
    Prints out help for the commands.

        imgserve help

    You can get help for one command with:

        imgserve help -for cmd
    """
    if "for" in options:
        help_text = args.help_for_command(imgserve.commands, options['for'])
        if help_text:
            print help_text
        else:
            args.invalid_command_message(imgserve.commands, exit_on_error=True)
    else:
        print "imgserve help:\n"
        print "\n".join(args.available_help(imgserve.commands))


def version_command():
    """
    Prints the version of imgserve.
    """

    from imgserve import version

    print "Imgserve-Version: ", version.VERSION['version']
    print ""
    print "Imgserve is Copyright (C) Wu Zhe <wu@madk.org> 2009.  Licensed GPLv3."
    print ""
    print "Have fun."
