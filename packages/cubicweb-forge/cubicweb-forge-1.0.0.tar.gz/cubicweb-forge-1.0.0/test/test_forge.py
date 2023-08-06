"""forge test application"""

from datetime import date

# must be done before _apptest import
from cubicweb.devtools import _apptest
#_apptest.SYSTEM_RELATIONS += ('for_version', 'instance_of')

from cubicweb.devtools.testlib import WebTest, AutomaticWebTest
from cubicweb.devtools.testlib import vreg_instrumentize, print_untested_objects


class ForgeAutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('TestInstance',)

    def post_populate(self, cursor):
        cursor.execute('SET X in_state S WHERE X is Version, S name "published"')

del AutomaticWebTest

def setup_module(*args):
    vreg_instrumentize(ForgeAutomaticWebTest)

def teardown_module(options, results):
    if not options.exitfirst or not (results.errors or results.failures):
        print_untested_objects(ForgeAutomaticWebTest)


class VersionCalendarViews(WebTest):
    """specific tests for calendar views"""

    def setup_database(self):
	self.add_entity('Version', num=u'0.1.0', publication_date=date(2006, 2, 1))
	self.add_entity('Version', num=u'0.2.0', publication_date=date(2006, 4, 1))
	self.add_entity('Project', name=u"MyProject")
	self.execute('SET V version_of P where V is Version, P is Project')
	self.execute('SET P in_state ST WHERE P is Project, ST name "active development"')
	self.execute('SET V in_state ST WHERE V is Version, ST name "planned"')

    def test_calendars_for_versions(self):
	rset = self.execute('Version V')
	for vid in ('onemonthcal', 'oneweekcal'):
	    yield self.view, vid, rset, rset.req.reset_headers()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
