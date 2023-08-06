# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

import os
import sys
import subprocess
from optparse import OptionParser

from blueberry.wsgiserver import CherryPyWSGIServer

import blueberry

_blueberry_reloader_key = 'RELOADER_SHOULD_RUN'

def start(app, reloader=False, ssl_certificate=None, ssl_private_key=None):
    if reloader:
        if os.environ.get(_blueberry_reloader_key):
            from blueberry import reloader
            print 'Running reloading file monitor'
            reloader.install()
        else:
            return restart_with_reloader()

    host = blueberry.config['server']['host']
    port = int(blueberry.config['server']['port'])
    name = blueberry.config['server']['name']

    server = CherryPyWSGIServer(
        (host, port),
        app,
        server_name=name)

    server.ssl_certificate = ssl_certificate
    server.ssl_private_key = ssl_private_key

    try:
        print 'Serving on %s:%s' % (host, port)
        server.start()
    except KeyboardInterrupt:
        server.stop()

def restart_with_reloader():
    restart_with_monitor(reloader=True)

def restart_with_monitor(reloader=False):
    if reloader:
        print 'Starting subprocess with file monitor'

    while 1:
        args = [sys.executable] + sys.argv
        environ = os.environ.copy()
        if reloader:
            environ[_blueberry_reloader_key] = 'true'

        proc = None
        try:
            try:
                _turn_sigterm_into_systemexit()
                proc = subprocess.Popen(args, env=environ)
                exit_code = proc.wait()
                proc = None
            except KeyboardInterrupt:
                print '^C caught in monitor process'
                raise
        finally:
            if (proc is not None
                and hasattr(os, 'kill')):
                import signal
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                except (OSError, IOError):
                    pass

        if reloader:
            if exit_code != 3:
                return exit_code

        print '-'*20, 'Restarting', '-'*20

def _turn_sigterm_into_systemexit():
    try:
        import signal
    except ImportError:
        return
    def handle_term(signo, frame):
        raise SystemExit
    signal.signal(signal.SIGTERM, handle_term)
