# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import uuid

from tank.platform.qt import QtCore
from threading import Lock, Condition, Thread


# Simple class to allow Worker to notify any observers of
# completed or failure events. We cannot emit signals
# directly from the Worker since it does not inherit
# from QObject, now that we're using Python native threads
# instead of QtCore.QThread
class WorkerNotifier(QtCore.QObject):
    work_completed = QtCore.Signal(str, object)
    work_failure = QtCore.Signal(str, str)


class Worker(Thread):
    """
    Background worker class
    """

    # Indicates that this worker class has been fixed to stop
    # gc of QThread from resulting in a crash.  This happens
    # when the mutex object had been gc'd but the thread is
    # still trying to access it - the fix is to wait for the
    # thread to terminate before returning from 'stop()'
    _SGTK_IMPLEMENTS_QTHREAD_CRASH_FIX_ = True

    def __init__(self, app, parent=None):
        """
        Construction
        """
        super().__init__()

        self._execute_tasks = True
        self._app = app

        self._queue_mutex = Lock()

        self._queue = []
        self._receivers = {}

        self._wait_condition = Condition(self._queue_mutex)

        self._notifier = WorkerNotifier()

    @property
    def notifier(self):
        return self._notifier

    def stop(self, wait_for_completion=True):
        """
        Stops the worker, run this before shutdown
        """
        with self._queue_mutex:
            self._execute_tasks = False
            self._wait_condition.notifyAll()

        if wait_for_completion:
            self.join()

        self._notifier.deleteLater()

    def clear(self):
        """
        Empties the queue
        """
        with self._queue_mutex:
            self._queue = []

    def queue_work(self, worker_fn, params, asap=False):
        """
        Queues up some work.
        Returns a unique identifier to identify this item
        """
        uid = uuid.uuid4().hex

        work = {"id": uid, "fn": worker_fn, "params": params}
        with self._queue_mutex:
            if asap:
                # first in the queue
                self._queue.insert(0, work)
            else:
                self._queue.append(work)

            self._wait_condition.notifyAll()

        return uid

    ############################################################################################
    #

    def run(self):

        while self._execute_tasks:

            # get the next item to process:
            item_to_process = None
            with self._queue_mutex:
                if len(self._queue) == 0:
                    # wait for some more work - this unlocks the mutex
                    # until the wait condition is signalled where it
                    # will then attempt to obtain a lock before returning
                    self._wait_condition.wait()

                    if len(self._queue) == 0:
                        # still nothing in the queue!
                        continue

                item_to_process = self._queue.pop(0)

            if not self._execute_tasks:
                break

            # ok, have something to do so lets do it:
            data = None
            try:
                # process the item:
                data = item_to_process["fn"](item_to_process["params"])
            except Exception as e:
                if self._execute_tasks:
                    self.notifier.work_failure.emit(
                        item_to_process["id"], "An error occured: %s" % e
                    )
            else:
                if self._execute_tasks:
                    self.notifier.work_completed.emit(item_to_process["id"], data)
