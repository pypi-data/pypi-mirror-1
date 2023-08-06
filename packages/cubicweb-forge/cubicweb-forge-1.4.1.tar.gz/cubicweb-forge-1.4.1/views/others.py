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
