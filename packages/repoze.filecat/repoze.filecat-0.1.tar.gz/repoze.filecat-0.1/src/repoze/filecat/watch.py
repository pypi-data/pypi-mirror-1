import os
import time
import logging
from stat import *
import threading
import mimetypes

import transaction

from ore.xapian.interfaces import IOperationFactory

from resource import FileSystemResource

warn = logging.getLogger("repoze.filecat.watch").warn
info = logging.getLogger("repoze.filecat.watch").info



def collect(d, dirname, fnames):
    for f in fnames:
        fname = os.path.join(dirname, f)
        stat_data = os.stat(fname)

        if S_ISDIR(stat_data[ST_MODE]):
            continue

        # XXX: currently we only care about images
        mimetype = mimetypes.guess_type(f)[0]
        if not mimetype:
            continue

        if mimetype and not mimetype.startswith("image"):
            continue

        d[fname] = stat_data[ST_MTIME]


class DirectoryChangeObserver(object):
    """ directory observer

    This class implements a threaded directory change observer.  Changes are
    reported by calling a user-supplied callback.  The callback gets called
    with the event and the file name.  The event is one of "added", "removed",
    "changed".
    """

    observer_running = False
    observer_thread = None

    CHECK_PERIOD = 10

    def __init__(self, path, callback):
        info("DirectoryChangeObserver: init with path=%s" % path)
        self.path = path
        self.before = self.get_files(path)
        self.callback = callback

    def get_files(self, path):
        d = dict()
        os.path.walk(path, collect, d)
        return d

    def check(self, path):
        after = self.get_files(path)
        self.added = [f for f in after if not f in self.before]
        self.removed = [f for f in self.before if not f in after]
        self.changed = [f for f in after if f in self.before and self.before[f] != after[f]]
        self.before = after

    def ticker(self):
        i=0
        while self.observer_running:
            time.sleep(self.CHECK_PERIOD)
            yield i
            i = i+1

    def _do_cb(self, event, path):
        try:
            self.callback(event, path[len(self.path)+1:])
        except Exeption, e:
            error("Exception calling callback %s for event '%s' on file '%s'" % (
                self.callback, event, path))

    def __call__(self):
        info("DirectoryChangeObserver: start")
        for tick in self.ticker():
            self.check(self.path)
            for f in self.added:
                self._do_cb("added", f)

            for f in self.removed:
                self._do_cb("removed", f)

            for f in self.changed:
                self._do_cb("changed", f)

    def __repr__(self):
        return "<DirectoryChangeObserver for path=%s>" % self.path

    @classmethod
    def start(klass, path, callback):
        if klass.observer_running:
            raise RuntimeError("Observer already running")

        klass.observer_running = True
        observer = klass(path, callback)
        klass.observer_thread = threading.Thread(target=observer)
        klass.observer_thread.setDaemon(True)
        klass.observer_thread.start()
        return observer

    @classmethod
    def stop(klass):
        if not klass.observer_running:
            return

        klass.observer_running = False
        klass.observer_thread.join()


def op_callback(event, path):
    """ callback called for file change events

    This will be called in the context of the directory observer thread.
    """
    info("Event '%s' for file '%s'"% (event, path))
    resource = FileSystemResource(path)

    if event == "added":
        IOperationFactory(resource).add()
    elif event == "removed":
        IOperationFactory(resource).remove()
    elif event == "changed":
        IOperationFactory(resource).modify()
    else:
        warn("Unknown event '%s' for file '%s'"% (event, path))
        return
    transaction.commit()


def start(path, period):
    DirectoryChangeObserver.CHECK_PERIOD = 3
    return DirectoryChangeObserver.start(path, op_callback)


if __name__ == "__main__":
    import sys
    print "Start"
    print "*"*70
    def callback(evt, f):
        print evt, f
    DirectoryChangeObserver.CHECK_PERIOD = 3
    observer = DirectoryChangeObserver.start(sys.argv[1], callback)
    print observer
    time.sleep(300)
    DirectoryChangeObserver.stop()
