from logilabvm.lib import show, start
from logilabvm.lib.test import init, clear
import unittest

class TestShow(unittest.TestCase):
    def setUp(self):
        clear.run()
        init.run()

    def tearDown(self):
        clear.run()

    def testAll(self):
        """
        test to list all VMs
        """
        # should be all
        self.result = show.run(["--all",])
        self.assertEqual(len(self.result), len(init.OPENVZ + init.KVM))
        for self.vm in self.result:
            self.assertTrue(self.vm['name'] in init.OPENVZ + init.KVM)
        # should be none
        clear.run()
        self.result = show.run(["--all",])
        self.assertEqual(len(self.result), 0)

    def testInactive(self):
        """
        test to list inactive VMs
        """
        # should be all inactive
        self.result = show.run(["--inactive",])
        self.assertEqual(len(self.result), len(init.OPENVZ + init.KVM))
        # should be 2 inactive
        start.run([init.OPENVZ[0], init.KVM[0]])
        self.result = show.run(["--inactive",])
        self.assertEqual(len(self.result), len(init.OPENVZ + init.KVM) - 2)
        # should be none inactive
        start.run(["--all",])
        self.result = show.run(["--inactive",])
        self.assertEqual(len(self.result), 0)

    def testActive(self):
        """
        test to list active VMs
        """
        # should be all inactive
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 0)
        # should be 2 active
        start.run([init.OPENVZ[0], init.KVM[0]])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 2)
        # should be none inactive
        start.run(["--all",])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), len(init.OPENVZ + init.KVM))

if __name__ == "__main__":
    unittest.main()
