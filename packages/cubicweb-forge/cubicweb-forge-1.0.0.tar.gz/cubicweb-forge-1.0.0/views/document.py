"""Restructured text view to export content of a forge instance

:organization: Logilab
:copyright: 2007-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.textutils import normalize_text

from cubicweb.view import EntityView
from cubicweb.selectors import implements
from cubicweb.entity import _marker


class ReSTItemView(EntityView):
    __abstract__ = True
    id = 'docitem'
    
    def _title(self, title):
        self.w(u'%s\n%s\n' % (title, self.title_underline*len(title)))

    def paragraph_field(self, entity, attr, **kwargs):
        value = entity.printable_value(attr, format='text/plain', **kwargs)
        if value:
            attrformat = getattr(entity, '%s_format', 'text/plain')
            self.w(u'\n%s\n' % normalize_text(value, 80,
                                              rest=attrformat=='text/rest'))
            
    def field(self, entity, attr, value=_marker, **kwargs):
        if value is _marker:
            value = entity.printable_value(attr, value, format='text/plain',
                                           **kwargs)
            attr = self.req._(attr)
        if value:
            self.w(u':%s: %s\n' % (attr, value))

            
class ProjectDocumentItemView(ReSTItemView):
    __select__ = implements('Project')
    
    templatable = False
    title_underline = '='
    
    def cell_call(self, row, col):
        """ReST view for Project entities"""
        entity = self.complete_entity(row, col)
        self._title(u'%s %s' % (entity.dc_type(), entity.dc_title()))
        self.field(entity, 'url', entity.homepage or entity.absolute_url())
        self.field(entity, 'creation_date', displaytime=False)
        self.paragraph_field(entity, 'summary')
        self.paragraph_field(entity, 'description')
        self.w(u'\n')
        # version (sort by ascending version.num)
        for ver in reversed(entity.reverse_version_of):
            ver.view('docitem', w=self.w)


class VersionDocumentItemView(ReSTItemView):
    __select__ = implements('Version')
    
    templatable = False
    title_underline = '-'

    def cell_call(self, row, col):
        """ReST view for Version entities"""
        entity = self.complete_entity(row, col)
        self._title(u'%s %s (%s)' % (entity.dc_type(), entity.num,
                                     entity.displayable_state))
        if entity.state == 'published':
            self.field(entity, 'publication_date')
        else:
            self.field(entity, 'prevision_date')
            etadate = entity.eta_date()
            if etadate is None:
                etadate = self.req._('n/a')
            else:
                etadate = self.format_date(etadate)
            self.field(entity, self.req._('expected date'), etadate)
        self.paragraph_field(entity, 'description')
        self.w(u'\n')
        for ticket in self.req.execute(entity.tickets_rql()).entities(): 
            ticket.view('docitem', w=self.w)


class TicketDocumentItemView(ReSTItemView):
    __select__ = implements('Ticket')
    
    templatable = False
    title_underline = '~'

    def cell_call(self, row, col):
        """ReST view for Ticket entities"""
        entity = self.complete_entity(row, col)
        self._title(u'%s #%s: %s [%s]' % (entity.dc_type(), entity.eid, entity.title,
                                          self.req._(entity.priority)))
        self.field(entity, 'type')
        self.field(entity, 'load')
        self.field(entity, self.req._('state'), entity.displayable_state)
        self.paragraph_field(entity, 'description')
        self.w(u'\n')
        if entity.reverse_comments:
            self.w(u'%s ::\n\n' % self.req._('Comment_plural'))
            for comment in entity.reverse_comments:
                for line in comment.view('fullthreadtext_descending').splitlines():
                    self.w(u'  ' + line + '\n')
            self.w(u'\n')
        

class DocumentView(EntityView):
    id = 'document'
    __select__ = implements('Project', 'Version', 'Ticket')
    
    title = _('document')
    templatable = False
    content_type = 'text/plain'
    
    def set_request_content_type(self):
        """overriden to set a .txt filename"""
        self.req.set_content_type(self.content_type, filename='cubicwebexport.txt')
        
    def cell_call(self, row, col):
        self.wview('docitem', self.rset, row=row, col=col)
        
    def call(self):
        self.w(u'.. -*- coding: %s -*-\n\n' % self.req.encoding.lower())
        for i in xrange(self.rset.rowcount):
            self.cell_call(row=i, col=0)
