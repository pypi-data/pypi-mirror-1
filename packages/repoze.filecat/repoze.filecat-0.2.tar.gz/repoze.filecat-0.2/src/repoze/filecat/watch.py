import os
import stat
import time
import logging
import threading
import mimetypes

import transaction

from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import ObjectRemovedEvent
from zope.event import notify

from repoze.filecat.resource import FileSystemResource

logger = logging.getLogger("repoze.filecat.watch")

def collect(d, dirname, fnames):
    for f in fnames:
        fname = os.path.join(dirname, f)
        try:
            stat_data = os.stat(fname)
        except OSError:
            continue

        if stat.S_ISDIR(stat_data[stat.ST_MODE]):
            continue

        mimetype = mimetypes.guess_type(f)[0]
        if not mimetype:
            continue

        d[fname] = stat_data[stat.ST_MTIME]

class DirectoryChangeObserver(object):
    """Directory observer.

    This class implements a threaded directory change observer.
    Changes are reported by calling a user-supplied callback. The
    callback gets called with the event and the file name. The event
    is one of 'added', 'removed', 'changed'.
    """

    observer_running = False
    observer_thread = None

    CHECK_PERIOD = 10

    def __init__(self, path, callback):
        logger.info("DirectoryChangeObserver: init with path=%s" % path)
        self.path = path
        self.files = self.get_files(path)
        self.callback = callback

        self.added = set()
        self.removed = set()
        self.changed = set()

    def clear(self):
        self.files.clear()
        
    def get_files(self, path):
        d = dict()
        os.path.walk(path, collect, d)
        return d

    def update(self, path):
        files = self.get_files(path)

        self.removed.clear()
        for f in self.files:
            if f not in files:
                self.removed.add(f)

        for f in self.removed:
            del self.files[f]

        self.added.clear()
        for f, timestamp in files.items():
            if f not in self.files:
                self.added.add(f)
                self.files[f] = timestamp                

        self.changed.clear()
        for f, timestamp in files.items():
            if f not in self.removed and self.files.get(f) != timestamp:
                self.changed.add(f)
                self.files[f] = timestamp
                
    def ticker(self):
        i = 0
        while self.observer_running:
            time.sleep(self.CHECK_PERIOD)
            yield i
            i = i + 1

    def _do_cb(self, event, path):
        try:
            self.callback(event, path[len(self.path)+1:])
        except Exception, e:
            logging.error("Error calling callback %s for event '%s' on file '%s'" % (
                self.callback, event, path))
            raise
        
    def __call__(self):
        logger.info("DirectoryChangeObserver started.")
        for tick in self.ticker():
            self.update(self.path)
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
    
    logger.debug("Queueing event '%s' for file '%s'"% (event, path))
    resource = FileSystemResource(path)

    if event == "added":
        notify(ObjectCreatedEvent(resource))
    elif event == "removed":
        notify(ObjectRemovedEvent(resource))
    elif event == "changed":
        notify(ObjectModifiedEvent(resource))
    else:
        raise RuntimeError("Unknown event '%s' for file '%s'"% (event, path))

    transaction.commit()

def start(path, period):
    DirectoryChangeObserver.CHECK_PERIOD = 3
    return DirectoryChangeObserver.start(path, op_callback)
