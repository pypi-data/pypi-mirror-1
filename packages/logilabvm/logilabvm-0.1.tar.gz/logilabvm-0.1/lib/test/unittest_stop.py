from logilabvm.lib import show, start, stop, VMError
from logilabvm.lib.test import init, clear
import unittest

class TestStop(unittest.TestCase):
    def setUp(self):
        clear.run()
        init.run()

    def tearDown(self):
        clear.run()

    def testOneVm(self):
        """
        test to stop one VM
        """
        start.run([init.OPENVZ[0], init.KVM[0]])
        stop.run(["--force", init.OPENVZ[0]])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 1)
        self.assertTrue(init.OPENVZ[0] not in [ el['name'] for el in self.result ])

    def testSelection(self):
        """
        test to stop a selection of VM
        """
        start.run([init.OPENVZ[0], init.OPENVZ[1], init.KVM[0]])
        test = stop.run(["--force", init.OPENVZ[0], init.OPENVZ[1]])
        self.result = show.run(["--active",])
        self.assertEqual(len(self.result), 1)
        self.assertTrue(init.OPENVZ[0] not in [ el['name'] for el in self.result ])
        self.assertTrue(init.OPENVZ[1] not in [ el['name'] for el in self.result ])
        self.assertTrue(init.KVM[0] in [ el['name'] for el in self.result ])

    def testNotInactive(self):
        """
        test to stop a VM that is not active
        """
        self.result = show.run(["--active",])
        self.assertRaises(VMError, stop.run, ["--force", init.OPENVZ[0]])

    def testAll(self):
        """
        test to stop all VMs
        """
        start.run(["--all",])
        stop.run(["--force", "--all"])
        self.result = show.run(["--inactive",])
        self.assertEqual(len(self.result), len(init.OPENVZ + init.KVM))
        for vm in init.OPENVZ + init.KVM:
            self.assertTrue(vm in [ el['name'] for el in self.result ])

if __name__ == "__main__":
    unittest.main()
