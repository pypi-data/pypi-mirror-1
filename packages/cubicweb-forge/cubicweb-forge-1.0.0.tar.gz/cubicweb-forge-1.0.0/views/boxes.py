"""forge components boxes

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from random import randint

from logilab.mtconverter import html_escape

from cubicweb.selectors import implements, rql_condition
from cubicweb.common.uilib import rql_for_eid
from cubicweb.web.box import BoxTemplate, EntityBoxTemplate
from cubicweb.web.htmlwidgets import SideBoxWidget, BoxHtml
from cubicweb.web.views import baseviews, idownloadable, boxes

class ProjectDownloadBox(EntityBoxTemplate):
    id = 'download_box'
    __select__ = (EntityBoxTemplate.__select__ & implements('Project') &
                  rql_condition('NOT X downloadurl NULL, V version_of X,'
                  'V in_state S, S name "published"'))

    def cell_call(self, row, col, **kwargs):
        version = self.entity(row, col).latest_version()
        idownloadable.download_box(self.w, version,
                                   self.req._('download latest version'),
                                   version.tarball_name())


class VersionDownloadBox(idownloadable.DownloadBox):
    __select__ = (EntityBoxTemplate.__select__ & implements('Version') &
                  rql_condition('NOT P downloadurl NULL, X version_of P, '
                                'X in_state S, S name "published"'))

    def cell_call(self, row, col, title=None, **kwargs):
        version = self.entity(row, col)
        super(VersionDownloadBox, self).cell_call(row, col, label=version.tarball_name())


class ImageSideboxView(boxes.SideBoxView):
    id = 'sidebox'
    __select__ = boxes.SideBoxView.__select__ & implements('Image', 'File')

    def call(self, boxclass='sideBox', title=u''):

        self.req.add_css('cubes.file.css')
        box = SideBoxWidget(display_name(self.req, title), self.id)
        entity = self.rset.get_entity(0,0)

        if entity.e_schema == 'Image':
            file_icon = entity.download_url()+'&small=true'
        else:
            file_icon =  self.req.external_resource('FILE_ICON')

        if getattr(entity, 'reverse_screenshot', None):
            gallery_url = '%s/screenshots?selected=%s' % (entity.project.absolute_url(),
                                                          entity.eid)
        elif getattr(entity, 'reverse_attachment', None):
            gallery_url = entity.reverse_attachment[0].absolute_url(vid='ticketscreenshots',
                                                                    selected=entity.eid)
        elif getattr(entity, 'project', None): # documentation file
            # XXX huumm
            gallery_url = '%s/documentation' % entity.project.absolute_url()
        else:
            gallery_url = u'%s%s' % (self.build_url(vid='gallery',
                                                    rql=self.rset.printable_rql()),
                                     '&selected=%s' % entity.eid)
        if len(self.rset) > 1:
            see_all_url = u'[<a href="%s">%s (%s)</a>]' % (html_escape(gallery_url),
                                                           self.req._('see them all'),
                                                           len(self.rset))
        else:
            see_all_url = u''
        html_container = (u'<li class="screenshot">'
                          u'<a href="%s" title="%s"><img alt="" src="%s"/>'
                          u'<br/>%s</a><br/>%s</li>')
        html = html_container % (html_escape(gallery_url),
                                 html_escape(entity.name),
                                 html_escape(file_icon),
                                 html_escape(entity.name),
                                 see_all_url)
        box.items = [BoxHtml(html)]
        box.render(self.w)

