"""setproctitle module unit test.

Copyright (c) 2009 Daniele Varrazzo <daniele.varrazzo@gmail.com>
"""

import sys
import unittest
from subprocess import Popen, PIPE, STDOUT

class GetProcTitleTestCase(unittest.TestCase):
    def test_runner(self):
        """Test the script execution method."""
        rv = self.run_script("""
            print 10 + 20
            """)
        self.assertEqual(rv, "30\n")

    def test_init_getproctitle(self):
        """getproctitle() returns a sensible value at initial call."""
        rv = self.run_script("""
            import setproctitle
            print setproctitle.getproctitle()
            """,
            args="-u")
        self.assertEqual(rv, sys.executable + " -u\n")

    def test_setproctitle(self):
        """setproctitle() can set the process title, duh."""
        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, world!')

            # TODO: probably to be fixed on other systems
            import os
            print open('/proc/%d/cmdline' % os.getpid()).read().rstrip('\0')
            """)
        self.assertEqual(rv, "Hello, world!\n")

    def test_getproctitle(self):
        """getproctitle() can read the process title back."""
        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, world!')
            print setproctitle.getproctitle()
            """)
        self.assertEqual(rv, "Hello, world!\n")

    def test_environ(self):
        """Check that clobbering environ didn't break env."""
        rv = self.run_script(r"""
            import setproctitle
            setproctitle.setproctitle('Hello, world! ' + 'X' * 1024)

            # set a new env variable, update another one
            import os
            os.environ['TEST_SETENV'] = "setenv-value"
            os.environ['PATH'] = os.environ.get('PATH', '') \
                    + os.pathsep + "fakepath"

            # read the environment from a spawned process hineriting the
            # updated env
            newenv = dict(r.split("=",1)
                    for r in os.popen("env").read().splitlines())

            print setproctitle.getproctitle()
            print newenv['TEST_SETENV']
            print newenv['PATH']
            """)

        title, test, path = rv.splitlines()
        self.assert_(title.startswith("Hello, world! XXXXX"), title)
        self.assertEqual(test, 'setenv-value')
        self.assert_(path.endswith('fakepath'), path)

    def run_script(self, script, args=None):
        """run a script in a separate process.

        if the script completes successfully, return the concatenation of
        ``stdout`` and ``stderr``. else fail.
        """
        cmdline = sys.executable
        if args:
            cmdline = cmdline + " " + args

        script = self._clean_whitespaces(script)
        proc = Popen(cmdline,
                stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                shell=True, close_fds=True)

        out = proc.communicate(script)[0]
        if 0 != proc.returncode:
            print out
            self.fail("test script failed")

        return out

    def _clean_whitespaces(self, script):
        """clean up a script in a string

        Remove the amount of whitelines found in the first nonblank line
        """
        script = script.splitlines(True)
        while script and script[0].isspace():
            script.pop(0)

        if not script:
            raise ValueError("empty script")

        line1 = script[0]
        spaces = script[0][:-len(script[0].lstrip())]
        assert spaces.isspace()

        for i, line in enumerate(script):
            if line.isspace(): continue
            if line.find(spaces) != 0:
                raise ValueError("inconsistent spaces at line %d (%s)"
                        % (i + 1, line.strip()))
            script[i] = line[len(spaces):]

        assert not script[0][0].isspace(), script[0]
        return ''.join(script)

