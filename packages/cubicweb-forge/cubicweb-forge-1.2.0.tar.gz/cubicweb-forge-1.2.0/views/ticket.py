"""views for Ticket entities

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import (one_line_rset, implements)
from cubicweb.web import component
from cubicweb.web.views import tabs

from cubes.tracker.views import ticket as tracker


# primary view and tabs ########################################################

class TicketPrimaryView(tracker.TicketPrimaryView):
    ticket_attributes = ('type', 'priority', 'load', 'load_left', 'description')

    def render_entity_title(self, entity):
        self.w(u'<div class="titleGroup">')
        title = xml_escape(entity.dc_title())
        self.w(u'<h2><span class="%s %s">%s</span><span class="state"> [%s]</span></h2>\n'
               % (entity.priority, entity.type, title,
                  xml_escape(self.req._(entity.state))))
        nc = self.vreg['components'].select_object('notification', self.req,
                                                   rset=self.rset)
        if nc:
            nc.render(w=self.w)
        self.w(u'</div>')


class TicketTestCardVComponent(component.RelatedObjectsVComponent):
    """display project's test cards"""
    id = 'tickettests'
    __select__ = component.RelatedObjectsVComponent.__select__ & implements('Ticket')

    rtype = 'test_case_for'
    target = 'subject'

    title = _('Test cards')
    context = 'navcontentbottom'
    order = 30


class TicketScreenshotsView(tabs.EntityRelationView):
    """display ticket's screenshots """
    id = 'ticketscreenshots'
    __select__ = one_line_rset() & tabs.EntityRelationView.__select__ & implements('Ticket')

    rtype = 'attachment'
    target = 'object'

    title = _('Attached Documents')
    vid = 'gallery'


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (TicketPrimaryView,))
    vreg.register_and_replace(TicketPrimaryView, tracker.TicketPrimaryView)
