#!/usr/bin/env python

"""
    Restart python scripts when their source files change.

    Very basic and universal restarter for python scripts, that analyses
    their dependencies and restarts the entire script if anything changes.
"""

__autor__ = "Djings"
__email__ = "rogkor@gmail.com"

import os
import sys

import time
from datetime import timedelta, datetime

# File system watching via watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Coordinate the restarts of the child scrip via subprocess
import subprocess as sp
import threading

class RestartHandler(FileSystemEventHandler):
    """ Event Handler for watchdog API.

        Uppon any file event, check whether one of
        the child scripts dependencies are involved
        and trigger restart accordingly.
    """
    def on_any_event(self, event):
        f = os.path.abspath(event.src_path)
        if f in self.dependencies:
            self.restart_lock.acquire()
            self.restart = True
            self.restart_lock.notifyAll()
            self.restart_lock.release()

def get_dependencies(scriptfilename):
    """ Returns a set of all file dependencies for the given script name 
        
        Only used imports count as actual dependencies.
    """

    def read_depends(f):
        "Generator for the dependencies read from the given file object."
        for line in f:
            if len(line.strip()) == 0:
                continue
            try:
                yield eval(line)
            except Exception:
                pass

    def flatten_depends(depends):
        """Yield the list of dependency pairs to a single list of (root, relfn)
        pairs, in the order that they appear. The list is guaranteed to be unique
        (we remove duplicates)."""
        seen = set([(None, None)])
        for dep in depends:
            for pair in dep:
                if pair in seen:
                    continue
                seen.add(pair)
                yield pair

    def flatten(val):
        result = []
        depends = read_depends(val.split('\n'))
        for droot, drel in flatten_depends(depends):
            result.append(os.path.join(droot, drel))
        return result

    # Call the snakefood binary.
    # FIXME: Call this as python module directly
    dependencies = sp.check_output(["sfood", "-fq", script])
    dependencies = flatten(dependencies)
    return set(dependencies)


if __name__ == "__main__":
    scr = sys.argv[1]
    script = os.path.abspath(scr)

    restart_lock = threading.Condition()
    observer = Observer()
    event_handler = RestartHandler()
    event_handler.restart_lock = restart_lock
    event_handler.restart = True
    process = None
    observer.start()

    try:
        while True:
            restart_lock.acquire()
            if event_handler.restart:
                event_handler.restart = False
    
                observer.unschedule_all()
                
                dependencies = get_dependencies(script)
                watchdirs = set(map(os.path.dirname, dependencies))

                event_handler.dependencies = dependencies
                for d in watchdirs:
                    observer.schedule(event_handler, d, recursive=False)
                
                # Do we have a running process that needs to be stopped?
                if not process is None:
                    ret = process.poll()
                    # If process is still running. Send ctrl+c
                    if ret is None:
                        process.send_signal(sp.signal.SIGINT)
                        start = datetime.now()
                        # Poll process and wait for it to shut down
                        # after 2 second timeout. Kill it hard.
                        while process.poll() is None and \
                                datetime.now() - start < timedelta(seconds=2):
                            time.sleep(0.1)

                    ret = process.poll()
                    # Process is still running
                    # Send in SIGTERM to clean up
                    if ret is None:
                        process.send_signal(sp.signal.SIGTERM)
                        process.wait()

                    process = None

                process = sp.Popen(("python", script))
            else:
                restart_lock.wait(0.1)
            restart_lock.release()
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
