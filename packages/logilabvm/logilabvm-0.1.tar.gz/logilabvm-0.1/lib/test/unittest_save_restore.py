from logilabvm.lib import show, start, stop, archives, save, restore, VMError
from logilabvm.lib.test import init, clear
from tempfile import mkdtemp
from os import listdir
from shutil import rmtree
from os.path import basename, join, exists
from time import sleep
import unittest

class TestArchiving(unittest.TestCase):
    def setUp(self):
        clear.run()
        init.run()
        self.tmpdir = mkdtemp()

    def tearDown(self):
        clear.run()
        rmtree(self.tmpdir)         

    def testSave(self):
        save.run([init.KVM[0],"--path",self.tmpdir])
        self.assertEqual(len(listdir(self.tmpdir)), 1)

    def testRestoreLast(self):
        save.run([init.KVM[0],"--path",self.tmpdir])
        sleep(1)
        save.run([init.KVM[0],"--path",self.tmpdir])
        result = restore.run([init.KVM[0],])
        archives = listdir(self.tmpdir)
        archives.sort()
        archives.reverse()
        self.assertTrue(archives[0] in result['stdout'])

    def testRestoreException(self):
        self.assertRaises(VMError, restore.run, ["--file",join(self.tmpdir, "mytest")])

if __name__ == "__main__":
    unittest.main()
