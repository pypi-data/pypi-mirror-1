from petsc4py import PETSc
import unittest
import sys, os, tempfile

# --------------------------------------------------------------------

class TestLog(unittest.TestCase):

    def setUp(self):
        PETSc.Log.begin()
        # register classes
        self.classA = PETSc.Log.classRegister('Class A')
        self.classB = PETSc.Log.classRegister('Class B')
        # register events
        self.event1 = PETSc.Log.eventRegister('Event 1') # no class
        self.event2 = PETSc.Log.eventRegister('Event 2') # no class
        self.eventA = PETSc.Log.eventRegister('Event A', self.classA)
        self.eventB = PETSc.Log.eventRegister('Event B', self.classB)
        # register stages
        self.stage1 = PETSc.Log.stageRegister('Stage 1')
        self.stage2 = PETSc.Log.stageRegister('Stage 2')

    def tearDown(self):
        if '-v' in sys.argv:
            sys.stdout.write('\n')
            PETSc.Log.printSummary('stdout')
        else:
            fname = tempfile.mktemp()
            PETSc.Log.printSummary(fname)
            summary = open(fname).read()
            os.remove(fname)

    def testLoggin(self):
        # -----
        self._run_events() # main stage
        self._run_stages() # user stages
        # -----
        for event in self._get_events():
            PETSc.Log.eventDeactivate(event)
            PETSc.Log.eventSetActive(event, False)
        self._run_events() # should not be logged
        for event in self._get_events():
            PETSc.Log.eventActivate(event)
            PETSc.Log.eventSetActive(event, True)
        # -----
        for cookie in self._get_classes():
            PETSc.Log.classDeactivate(cookie)
            PETSc.Log.classSetActive(cookie, False)
        self._run_events() # A and B should not be logged
        for cookie in self._get_classes():
            PETSc.Log.classActivate(cookie)
            PETSc.Log.classSetActive(cookie, True)
        # -----
        for stage in self._get_stages():
            PETSc.Log.stageDeactivate(stage)
            PETSc.Log.stageSetActive(stage, False)
        self._run_stages() # should not be logged
        for stage in self._get_stages():
            PETSc.Log.stageActivate(stage)
            PETSc.Log.stageSetActive(stage, True)
        # -----
        self._run_events()
        self._run_stages()


    def _run_stages(self):
        for stage in self._get_stages():
            self._run_events(stage)

    def _get_stages(self):
        return (self.stage1, self.stage2)

    def _get_classes(self):
        return (self.classA, self.classB)

    def _get_events(self):
        return (self.event1, self.event2,
                self.eventA, self.eventB)

    def _run_events(self, stage=None):
        if stage is not None:
            PETSc.Log.stagePush(stage)
        self._events_begin()
        self._events_end()
        if stage is not None:
            PETSc.Log.stagePop()

    def _events_begin(self):
        for event in self._get_events():
            PETSc.Log.eventBegin(event)

    def _events_end(self):
        for event in reversed(self._get_events()):
            PETSc.Log.eventEnd(event)

# --------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

