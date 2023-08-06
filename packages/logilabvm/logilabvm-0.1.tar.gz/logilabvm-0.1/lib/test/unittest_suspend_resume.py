from logilabvm.lib import suspend, resume, start, VMError
from logilabvm.lib.test import init, clear
import unittest

class TestSuspendResume(unittest.TestCase):
    def setUp(self):
        clear.run()
        init.run()

    def tearDown(self):
        clear.run()

    def testSuspend(self):
        start.run([init.KVM[0],])
        result = suspend.run([init.KVM[0],])
        self.assertTrue(not result['value'])

    def testResume(self):
        start.run([init.KVM[0],])
        suspend.run([init.KVM[0],])
        result = resume.run([init.KVM[0],])
        self.assertTrue(not result['value'])

    def testFailSuspend(self):
        self.assertRaises(VMError, suspend.run, init.KVM[0])

    def testFailResume(self):
        self.assertRaises(VMError, resume.run, init.KVM[0])

if __name__ == "__main__":
    unittest.main()
