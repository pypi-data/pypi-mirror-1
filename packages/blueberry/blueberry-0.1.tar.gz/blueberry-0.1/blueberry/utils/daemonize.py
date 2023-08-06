import os
import sys

# taken from django.utils.daemonize
def become_daemon():
    try:
        if os.fork() > 0:
            sys.exit(0) # kill off parent
    except OSError, e:
        sys.stderr.write('fork #1 failed: (%d) %s\n' % (e.errno, e.strerror))
        sys.exit(1)

    os.setsid()
    os.chdir('.')
    os.umask(022)

    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, e:
        sys.stderr.write('fork #2 failed: (%d) %s\n' % (e.errno, e.strerror))
        os._exit(1)

    si = open('/dev/null', 'r')
    so = open('/dev/null', 'a+', 0)
    se = open('/dev/null', 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # set custom file descriptors so they get proper buffering
    sys.stdout, sys.stderr = so, se
