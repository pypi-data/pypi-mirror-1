from logilabvm.lib import show, start, VMError
from logilabvm.lib.test import init, clear
import unittest

class TestStart(unittest.TestCase):
    def setUp(self):
        clear.run()
        init.run()

    def tearDown(self):
        clear.run()

    def testOneVm(self):
        """
        test to start one VM
        """
        start.run([init.OPENVZ[0], init.KVM[0]])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 2)
        self.assertTrue(init.OPENVZ[0] in [ el['name'] for el in self.result ])

    def testSelection(self):
        """
        test to start a selection of VM
        """
        start.run([init.OPENVZ[0], init.KVM[0]])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 2)
        self.assertTrue(init.OPENVZ[0] in [ el['name'] for el in self.result ])
        self.assertTrue(init.KVM[0] in [ el['name'] for el in self.result ])

    def testNotInactive(self):
        """
        test to start a VM that is not inactive
        """
        start.run([init.OPENVZ[0],])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 1)
        self.assertRaises(VMError, start.run, [init.OPENVZ[0],])
        self.assertRaises(VMError, start.run, ["undefinedvm",])

    def testAll(self):
        """
        test to start all VMs
        """
        start.run(["--all",])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), len(init.OPENVZ + init.KVM)) 
        for vm in init.OPENVZ + init.KVM:
            self.assertTrue(vm in [ el['name'] for el in self.result ])

if __name__ == "__main__":
    unittest.main()
