"""views for other forge entity types: License, TestInstance

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import implements
from cubicweb.web.views import primary

from cubicweb.selectors import match_search_state, implements
from cubicweb.web import action
from cubicweb.web.views import baseviews


class LicensePrimaryView(primary.PrimaryView):
    __select__ = implements('License')

    def render_entity_title(self, entity):
        if entity.url:
            title = u'<a href="%s">%s</a>' % (xml_escape(entity.url),
                                              xml_escape(entity.name))
        else:
            title = entity.name
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))


class TestInstancePrimaryView(primary.PrimaryView):
    __select__ = implements('TestInstance')

    def render_entity_title(self, entity):
        title = xml_escape('%s [%s]' % (entity.name, self.req._(entity.state)))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_metadata(self, entity):
        pass

    def render_entity_attributes(self, entity):
        self.w(entity.instance_of[0].view('inlined'))


class TestInstanceOneLineView(baseviews.OneLineView):
    """text representation of a test instance:

    display title and state
    """
    __select__ = implements('TestInstance')
    def cell_call(self, row, col):
        super(TestInstanceOneLineView, self).cell_call(row, col)
        entity = self.entity(row, col)
        self.wdata(u' [%s]' % self.req._(entity.state))


class TestInstanceGenerateBugAction(action.LinkToEntityAction):
    id = 'submitbug'
    __select__ = match_search_state('normal') & implements('TestInstance')
    title = _('add TestInstance generate_bug Ticket subject')
    etype = 'Ticket'
    rtype = 'generate_bug'
    target = 'object'
    def url(self):
        entity = self.rset.get_entity(0, 0)
        linkto = '__linkto=concerns:%s:%s' % (entity.instance_of[0].test_case_of[0].eid, self.target)
        linkto += '&__linkto=generate_bug:%s:subject' % entity.eid
        linkto += '&__linkto=appeared_in:%s:%s' % (entity.for_version[0].eid, self.target)
        return '%s&%s' % (action.LinkToEntityAction.url(self), linkto)
