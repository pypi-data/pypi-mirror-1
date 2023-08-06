"""
Phases of a pipelined study exhibiting different processing models.

Copyright (C) 2009  Alexander Lamaison <awl03@doc.ic.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import time
import threading
import multiprocessing

class Phase(object):
    """
    Phase of a study that operates on a single input.

    A phase is a particular stage of a data-munging study which takes data and
    transforms it into results which may be processed further by any later
    phases in a chain.

    The type of phase implemented by this class executes a given callable
    worker once on any data passed to run().  The worker will transform the
    data as desired and return the results which are then returned from run().

    Subclasses of this class *may* override:
        munge()  - change the way in which the work is performed on the data
                   by, for example, running the worker separately on each datum
                   in a set of data.
    """

    def __init__(self, name, worker, stream=sys.stdout, progress=None,
                 shared_state=None):
        self.name = name or "<unnamed phase>"
        self.worker = worker
        self.stream = stream
        self.progress = progress
        self.shared_state = shared_state

        if hasattr(self.worker, "init_per_process_state"):
            self.init_per_process_state = self.worker.init_per_process_state
        else:
            self.init_per_process_state = None

    def run(self, data=None):
        """
        Run a phase of the study.

        Return any value from munge(), so that it can be passed to the next
        phase (if any) in the chain of phases.
        """

        start_time = time.time()
        results = self.munge(data)
        end_time = time.time()

        print >> self.stream, "**%s took %.2f seconds**" % (self.name,
                                                            (end_time - start_time))
        return results

    def munge(self, data):
        """
        Transform input data into results.

        The results returned from this method may be passed to another phase
        for further processing.

        This method can be overridden to provide alternative run strategies.
        """

        _init_process(self.shared_state, self.init_per_process_state)
        if self.progress:
            self.progress.set_total_work_units(1)

        if data:
            return self._do_work(data)
        else:
            return self._do_work()

    def _do_work(self, *args):
        """
        Perform the work unit calling the progress monitor before and after.
        """

        if self.progress:
            self.progress.starting_work_unit(*args)

        result = self.worker(*args)

        if self.progress:
            self.progress.finished_work_unit()
        return result

class SequentialPhase(Phase):
    """
    Phase of a study that operates on a sequence of items in order.

    The type of phase implemented by this class executes the given callable
    worker on each item in a *sequence* of data passed to run().  This is
    done *one item at a time* in the order of the original sequence.

    The worker will transform each datum as desired and return the result.  The
    results are collated and returned from run() as a sequence in the same
    order as the original input unless filter_none is True. In this case
    any result found to be None is omitted from the sequence which allows
    the worker to filter out any arbitrary datum from the study simply by
    setting its result to None.

    Subclasses of this class *may* override:
        munge_sequence()  - change the way in which the work is performed on
                            the sequence by, for example, running the worker
                            on the data items in parallel.
    """

    def __init__(self, name, worker, filter_none=False, **kwargs):

        Phase.__init__(self, name, worker, **kwargs)
        self.filter_none = filter_none

    def munge(self, sequence):
        """
        Run the worker over the items in the data set sequentially and,
        optionally, filter 'None' values out of the sequence of results.

        This method may not be overridden by subclasses as it performs work
        essential to the essence of a sequential phase such as preparing
        the progress monitor.
        """

        # only force generators to become lists if progress updates are needed
        if self.progress:
            sequence = list(sequence)
            self.progress.set_total_work_units(len(sequence))

        if self.filter_none:
            return [r for r in self.munge_sequence(sequence) if r is not None]
        else:
            return list(self.munge_sequence(sequence))

    def munge_sequence(self, sequence):
        """
        Run the worker over the items in the data set sequentially.
        """

        _init_process(self.shared_state, self.init_per_process_state)

        return (self._do_work(datum) for datum in sequence)

class QueueSentinel(object):
    pass

class MultiprocessPhase(SequentialPhase):
    """
    Phase of a study whose work on a sequence is divided out amongst
    several processes.

    The type of phase implemented by this class executes the given callable
    worker on each item in a *sequence* of data passed to run().  This is
    done *in parallel* up to the number of processes specified in the
    constructor.

    The worker will transform each datum as desired and return the result.  The
    results are collated and returned from run() as a sequence in the same
    order as the original input unless filter_none is True. In this case
    any result found to be None is omitted from the sequence which allows
    the worker to filter out any arbitrary datum from the study simply by
    setting its result to None.

    **WARNING:**
    As the multiprocessing makes copies of the worker, it cannot store any
    state of its own: i.e. if it is a functor, the __call__ method must be pure
    (not modify any attributes of 'self').  This makes it hard to maintain
    state, such as a progress count, between workers.  The correct way to do
    this is to pass the state externally to the MultiprocessPhase constructor
    as the shared_state parameter.  This state will be saved in the module-
    global phase.SHARED_STATE attribute.  The worker can update this state.

    If the worker is a functor as has a shared_state attribute initialised to
    None, the shared state will be saved back to this attribute of the original
    worker instance at the end of the run
    """

    def __init__(self, name, worker, process_count=multiprocessing.cpu_count(),
                 **kwargs):
        """
        Initialise phase with additional parameters required to initialise
        each process.
        """

        SequentialPhase.__init__(self, name, worker, **kwargs)

        self.process_count = process_count

        self._setup_queues()

    def __del__(self):
        self._terminate_queues()

    def munge_sequence(self, sequence):
        """
        Divide the sequence set amongst the worker processes and return the results
        once all have completed.
        """

        pool = multiprocessing.Pool(processes=self.process_count,
                                    initializer=_init_process,
                                    initargs=(self.shared_state,
                                              self.init_per_process_state,
                                              self._start_queue, self._finish_queue))

        results = pool.map(_do_work, ((self.worker, datum) for datum in sequence))

        # Only save shared state back to the worker if it is a functor and it
        # was __init__ed with a 'shared_state' attribute (should be None)
        if hasattr(self.worker, "shared_state"):
            assert self.worker.shared_state is None
            self.worker.shared_state = self.shared_state

        return results

    def _setup_queues(self):
        """
        Create queues for workers to report progress and threads to manage them.
        """
        if self.progress:
            self._start_queue = multiprocessing.Queue()
            self._finish_queue = multiprocessing.Queue()
            self._start_handler = threading.Thread(
                name='Progress start report thread',
                target=self._handle_starts,
                args=(self._start_queue,))
            self._start_handler.daemon = True
            self._start_handler.start()

            self._finish_handler = threading.Thread(
                name='Progress finish report thread',
                target=self._handle_finishes,
                args=(self._finish_queue,))
            self._finish_handler.daemon = True
            self._finish_handler.start()
        else:
            self._start_queue = None
            self._finish_queue = None

    def _terminate_queues(self):
        """
        Terminate progress queues by passing a sentinel.
        """
        if self._start_queue:
            self._start_queue.put(self.sentinel)
            self._finish_queue.put(self.sentinel)

    sentinel = QueueSentinel()

    def _handle_starts(self, start_queue):
        for unit in iter(start_queue.get, self.sentinel):
            self.progress.starting_work_unit(unit)

    def _handle_finishes(self, finish_queue):
        for unit in iter(finish_queue.get, self.sentinel):
            self.progress.finished_work_unit()

def _do_work((worker, datum)):
    """
    Perform the work unit calling the progress monitor before and after.
    """

    if START_QUEUE:
        START_QUEUE.put(datum)

    result = worker(datum)

    if FINISH_QUEUE:
        FINISH_QUEUE.put(datum)

    return result

def _init_process(shared_state, init_per_process_state,
                  start_queue=None, finish_queue=None):
    """
    Process setup.

    This is called *once per process* to set up any process-specific state.
    Currently, this just stores a per-process global reference to the shared
    state passed to the phase in the constructor.
    """

    globals()['SHARED_STATE'] = shared_state
    if callable(init_per_process_state):
        init_per_process_state()

    globals()['START_QUEUE'] = start_queue
    globals()['FINISH_QUEUE'] = finish_queue

