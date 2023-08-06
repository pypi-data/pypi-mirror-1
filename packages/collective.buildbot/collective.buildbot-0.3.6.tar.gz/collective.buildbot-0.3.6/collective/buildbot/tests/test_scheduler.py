import unittest
from buildbot.changes.changes import Change
from collective.buildbot.scheduler import SVNScheduler

class TestScheduler(unittest.TestCase):
    def testSchedulerDoesNotModifyChangeObject(self):
        """
        SVNScheduler must not change the branch of the incoming change, 
        as that one is being used in the next scheduler again
        """
        c = Change('nobody', ['/dev/null'], "no comment", 
                   branch = "collective.buildbot/trunk")
        sched = SVNScheduler("test", ['ignores'], \
                             'https....collective.buildbot/trunk')
        sched.addChange(c)
        self.assertTrue(c.branch)
