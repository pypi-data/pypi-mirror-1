# Standard library imports
import unittest
import sys
from StringIO import StringIO
import os
import tempfile
import shutil

# Custom library imports
import load2010
import intertie2010


class ScriptSandbox(unittest.TestCase):
    def setUp(self):
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        self._old_cwd = os.getcwd()

        self._tempdir = tempfile.mkdtemp()
        os.chdir(self._tempdir)
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        def errorhander(function, path, execinfo):
            raise OSError('Cannot delete tempfile at ' + path)

        stdout = sys.stdout
        stderr = sys.stderr

        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr
        os.chdir(self._old_cwd)

        # Delete temp directory
        shutil.rmtree(self._tempdir, onerror = errorhander)


class TestLoad2010(ScriptSandbox):
    def test_main(self):
        self.assertEquals(load2010.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 1000)


class TestIntertie2010(ScriptSandbox):
    def test_main(self):
        self.assertEquals(intertie2010.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 1000)


if __name__ == '__main__':
    unittest.main()

