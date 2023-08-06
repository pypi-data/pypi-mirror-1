# blueberry - Yet another Python web framework.
#
#       http://code.google.com/p/blueberrypy
#
# Copyright 2009 David Reynolds
#
# Use and distribution licensed under the BSD license. See
# the LICENSE file for full text.

import os, sys, time, threading
import traceback

def install(poll_interval=1):
    monitor = Monitor(poll_interval)
    t = threading.Thread(target=monitor.periodic_reload)
    t.setDaemon(True)
    t.start()

class Monitor(object):
    instances = []
    global_extra_files = []
    global_file_callbacks = []

    def __init__(self, poll_interval):
        self.mtimes = {}
        self.keep_running = True
        self.poll_interval = poll_interval
        self.extra_files = list(self.global_extra_files)
        self.instances.append(self)
        self.file_callbacks = list(self.global_file_callbacks)

    def periodic_reload(self):
        while True:
            if not self.check_reload():
                os._exit(3)
                break
            time.sleep(self.poll_interval)

    def check_reload(self):
        filenames = list(self.extra_files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                print >> sys.stderr, "Error calling reloader callback %r:" % file_callback
                traceback.print_exc()
        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError):
                continue

            if filename is not None:
                filenames.append(filename)

        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue

            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)

            if not self.mtimes.has_key(filename):
                self.mtimes[filename] = mtime
            elif self.mtimes[filename] < mtime:
                print >> sys.stderr, "%s changed; reloading..." % filename
                return False
        return True
