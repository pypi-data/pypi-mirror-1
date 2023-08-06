import os
import glob
from StringIO import StringIO

from logilab.common.testlib import TestCase, unittest_main
from twill import commands as twc
from twill.unit import TestInfo
from twill.parse import _execute_script # , execute_file

# from cubes.forgeserve import runserver
from forgeserve import get_starturl
from cubicweb.devtools.cwtwill import has_link

def execute_scenario(filename, **kwargs):
    """based on twill.parse.execute_file, but inserts cubicweb extensions"""
    stream = StringIO('extend_with cubicweb.devtools.cubicwebtwill\n' + file(filename).read())
    kwargs['source'] = filename
    _execute_script(stream, **kwargs)


class LiveTest(TestCase):

    def test_scenarios(self):
        self.skip("skipped for now")
        for filename in glob.glob('scenarios/*.twill'):
            print "executing", filename
            execute_scenario(filename, initial_url=get_starturl())

    def test_login_appears(self):
        self.skip("skipped for now")
        twc.go(get_starturl())
        has_link('logout')
        has_link('admin')


if __name__ == '__main__':
    unittest_main()
