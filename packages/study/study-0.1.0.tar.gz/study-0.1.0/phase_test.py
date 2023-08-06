#!/usr/bin/env python
"""
Unit tests for study.phases module.

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

import multiprocessing
from nose.tools import assert_raises

from study import phase

#
# Basic tests
#

class RootWorker:
    """
    Worker functor that starts of the chain of studies like a Big Bang.

    Such a type of worker takes no data when called and uses its own internal
    'knowledge' to spark all the subsequent processing.
    """

    def __init__(self):
        self.data = 42

    def __call__(self):
        return self.data

def test_root_worker():
    """
    Test a root worker in a phase that is run without data.
    """

    worker = RootWorker()
    test_phase = phase.Phase("RootTestPhaseName", worker)
    output = test_phase.run()

    assert output == 42
    assert test_phase.name == "RootTestPhaseName"

class SimpleWorker:
    """
    Very basic worker functor that stores the data it is called with and
    returns it unaltered.
    """

    def __init__(self):
        self.call_count = 0
        self.data = None

    def __call__(self, data_set):
        """
        Store data for later checking.
        """
        self.call_count += 1
        self.data = data_set
        return data_set

class ModifyingWorker:
    """
    Worker functor that stores the data it is called with but returns the data
    reversed.

    Because __call__() tries to reversed() the data set it only makes sense
    to use this worker with a sequence.
    """

    def __init__(self):
        self.call_count = 0
        self.data = None

    def __call__(self, data_set):
        """
        Store data for later checking and return the data in reverse.
        """
        self.call_count += 1
        self.data = data_set
        return list(reversed(data_set))

def _test_phase(test_data):
    """
    Does Phase.run() invoke the worker once?
    """

    worker = SimpleWorker()
    test_phase = phase.Phase("SimpleTestPhaseName", worker)
    output = test_phase.run(test_data)

    assert worker.call_count == 1
    assert worker.data == test_data
    assert output == test_data
    assert test_phase.name == "SimpleTestPhaseName"

def test_phase_single():
    """
    Does Phase.run() invoke the worker once with non-sequence data?
    """

    test_data = 1024
    _test_phase(test_data)

def test_phase_sequence():
    """
    Does Phase.run() invoke the worker once for a whole sequence of data?
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]
    _test_phase(test_data)

def test_phase_modifying_sequence():
    """
    Is data transformation by the worker reflected in the output of the Phase?
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]

    worker = ModifyingWorker()
    test_phase = phase.Phase(None, worker)
    output = test_phase.run(test_data)

    assert worker.call_count == 1
    assert worker.data == test_data
    assert output == list(reversed(test_data))
    assert test_phase.name == "<unnamed phase>"

#
# Sequential processing tests
#

class SequentialWorker:
    """
    Worker functor that stores each item of data it is called with and which
    call it occurred at.  When called it calls * 2 on each datum and return it.
    """

    def __init__(self):
        self.call_count = 0
        self.data = {}

    def __call__(self, datum):
        """
        Store data for later checking.
        """
        self.call_count += 1
        self.data[self.call_count] = datum
        return datum * 2

def test_sequential_phase():
    """
    Does SequentialPhase.run() invoke worker once for each item in sequence?
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]

    worker = SequentialWorker()
    test_phase = phase.SequentialPhase("SequentialTestPhaseName", worker)
    output = test_phase.run(test_data)

    assert worker.call_count == len(test_data)
    for call, datum in worker.data.iteritems():
        assert datum == test_data[call - 1]
    assert output == [x * 2 for x in test_data]
    assert test_phase.name == "SequentialTestPhaseName"

#
# Multiprocessing tests
#

def multiprocess_worker(datum):
    """
    Worker function that calls * 2 on each datum and returns it.
    """
    return datum * 2

class StatelessWorker:
    """
    Worker functor that just calls * 2 on each datum and returns it.
    """

    def __init__(self):
        pass

    def __call__(self, datum):
        """
        Do stateless operation.
        """
        return datum * 2

def test_multiprocess_phase_with_stateless_function():
    """
    Does MultiprocessPhase.run() invoke worker function on each item?

    Uses a *stateless* worker function.
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]

    test_phase = phase.MultiprocessPhase("MultiprocessTestPhaseName",
                                         multiprocess_worker)
    output = test_phase.run(test_data)

    assert output == [x * 2 for x in test_data]
    assert test_phase.name == "MultiprocessTestPhaseName"

def test_multiprocess_phase_with_stateless_functor():
    """
    Does MultiprocessPhase.run() invoke worker functor on each item?

    Uses a *stateless* worker functor.
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]

    worker = StatelessWorker()
    test_phase = phase.MultiprocessPhase("MultiprocessTestPhaseName", worker)
    output = test_phase.run(test_data)

    assert output == [x * 2 for x in test_data]
    assert test_phase.name == "MultiprocessTestPhaseName"

def multiprocess_stateful_worker(datum):
    """
    Worker function that relies on shared state. It applied * 2 to each
    datum and returns it as well as keeping track on how many data have been
    processed in a shared value.
    """
    phase.SHARED_STATE.acquire()
    phase.SHARED_STATE.value += 1
    phase.SHARED_STATE.release()
    return datum * 2

class StatefulWorker:
    """
    Worker functor that relies on shared state. It applied * 2 to each
    datum and returns it as well as keeping track on how many data have been
    processed in a shared value.
    """

    def __init__(self):
        self.shared_state = None # Initialised after multiprocess run

    def __call__(self, datum):
        """
        Modify shared state and return transformed datum.
        """
        phase.SHARED_STATE.acquire()
        phase.SHARED_STATE.value += 1
        phase.SHARED_STATE.release()
        return datum * 2

def test_multiprocess_phase_with_stateful_function():
    """
    Does MultiprocessPhase.run() invoke worker function on each item?

    Uses a *stateful* worker function.
    """
    test_data = [1,2,3,4,5,"mary had a little stateful lamb"]

    shared_state = multiprocessing.Value('i', 0)
    worker = multiprocess_stateful_worker
    test_phase = phase.MultiprocessPhase("MultiStatefulTestPhaseName", worker,
                                         shared_state=shared_state)
    output = test_phase.run(test_data)

    assert shared_state.value == len(test_data)
    # should not save state when worker is a plain-old function
    assert not hasattr(worker, "shared_state")
    assert output == [x * 2 for x in test_data]
    assert test_phase.name == "MultiStatefulTestPhaseName"

def test_multiprocess_phase_with_stateful_functor():
    """
    Does MultiprocessPhase.run() invoke worker functor on each item?

    Uses a *stateful* worker functor.
    """

    test_data = [1,2,3,4,5,"mary had a little stateful lamb"]

    shared_state = multiprocessing.Value('i', 0)
    worker = StatefulWorker()
    test_phase = phase.MultiprocessPhase("MultiStatefulTestPhaseName", worker,
                                         shared_state=shared_state)
    output = test_phase.run(test_data)

    assert shared_state.value == len(test_data)
    assert worker.shared_state.value == len(test_data)
    assert output == [x * 2 for x in test_data]
    assert test_phase.name == "MultiStatefulTestPhaseName"

#
# Progress monitor tests
#

class Progress(object):
    def __init__(self):
        self.count = 0
        self.total_work_units = -42
        self.unit = None
        self.units_seen = []
        self.start_invoked = False
        self.finish_invoked = False

    def set_total_work_units(self, total):
        self.total_work_units = total

    def starting_work_unit(self, unit):
        self.start_invoked = True
        self.unit = unit
        self.units_seen.append(unit)

    def finished_work_unit(self):
        self.finish_invoked = True
        self.count += 1
        self.unit = None

def test_sequential_phase_progress():
    """
    Does progress monitor get called correctly with a sequential phase?
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]

    worker = SequentialWorker()
    progress = Progress()
    test_phase = phase.SequentialPhase("SequentialProgressTest", worker,
                                       progress=progress)
    output = test_phase.run(test_data)

    assert output == [x * 2 for x in test_data]
    assert progress.total_work_units == len(test_data)
    assert progress.units_seen == test_data

def test_multiprocess_phase_progress():
    """
    Does progress monitor work with multiprocess phase?
    """

    test_data = [1,2,3,4,5,"mary had a little lamb"]

    progress = Progress()
    test_phase = phase.MultiprocessPhase("MultiprocessProgressTest",
                                         multiprocess_worker,
                                         progress=progress)
    output = test_phase.run(test_data)

    assert output == [x * 2 for x in test_data]
    assert progress.total_work_units == len(test_data)
    assert progress.start_invoked
    assert progress.finish_invoked
    assert progress.count == len(test_data)
    assert len(progress.units_seen) == len(test_data)
    for unit in test_data:
        assert unit in progress.units_seen

#
# Exception tests
#

class WorkerError(Exception):
    pass

def naughty_worker(datum):
    """
    Worker function that throws an exception.
    """
    raise WorkerError

def test_multiprocess_phase_with_exception():
    """
    Does an exception in a worker get thrown to top-level?
    """
    test_data = [1,2,3,4,5,"mary had a little stateful lamb"]
    test_phase = phase.MultiprocessPhase("MultiException", naughty_worker)
    assert_raises(WorkerError, test_phase.run, test_data)

def test_multiprocess_phase_with_exception_and_progress():
    """
    Does an exception in worker with a progress monitor get thrown to top-level?
    """
    test_data = [1,2,3,4,5,"mary had a little stateful lamb"]
    test_phase = phase.MultiprocessPhase("MultiExceptionProgress",
                                         naughty_worker, progress=Progress())
    assert_raises(WorkerError, test_phase.run, test_data)

#
# Filtering tests
#

def filter_odd(datum):
    return datum if datum % 2 == 0 else None

def check_filter(expected_output, phase):
    """
    Test that running phase on 0..9 produces expected output sequence.
    """
    output = phase.run(range(0, 10))
    assert output == expected_output

def test_sequential_filter():
    """
    Filter out odd numbers using a sequential phase.
    """
    p = phase.SequentialPhase("SequentialFilter", filter_odd,
                                  filter_none=True)
    check_filter([0, 2, 4, 6, 8], p)

def test_multiprocess_filter():
    """
    Filter out odd numbers using a multiprocess phase.
    """
    p = phase.SequentialPhase("MultiprocessFilter", filter_odd,
                              filter_none=True)
    check_filter([0, 2, 4, 6, 8], p)

def test_sequential_nonfilter():
    """
    Ensure sequential phase doesn't filter None by default.
    """
    p = phase.SequentialPhase("SequentialNonFilter", filter_odd)
    check_filter([0, None, 2, None, 4, None, 6, None, 8, None], p)

def test_multiprocess_nonfilter():
    """
    Ensure multiprocess phase doesn't filter None by default.
    Filter out odd numbers using a multiprocess phase.
    """
    p = phase.SequentialPhase("MultiprocessNonFilter", filter_odd)
    check_filter([0, None, 2, None, 4, None, 6, None, 8, None], p)

if __name__ == '__main__':
    import nose
    nose.runmodule()
