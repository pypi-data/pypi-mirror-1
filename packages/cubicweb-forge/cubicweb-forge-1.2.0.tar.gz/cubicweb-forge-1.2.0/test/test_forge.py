"""forge test application"""

from cubicweb.devtools.testlib import AutomaticWebTest
from cubicweb.devtools.testlib import vreg_instrumentize, print_untested_objects


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('TestInstance',)
    ignored_relations = ('nosy_list',)

    def post_populate(self, cursor):
        self.commit()
        for version in cursor.execute('Version X').entities():
            version.change_state('published')

def setup_module(*args):
    vreg_instrumentize(AutomaticWebTest)

def teardown_module(options, results):
    if not options.exitfirst or not (results.errors or results.failures):
        print_untested_objects(AutomaticWebTest)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
