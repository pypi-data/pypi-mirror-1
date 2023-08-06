"""forge components boxes

:organization: Logilab
:copyright: 2006-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.selectors import implements, score_entity
from cubicweb.web import box, htmlwidgets
from cubicweb.web.views import idownloadable, boxes

class ProjectDownloadBox(box.EntityBoxTemplate):
    id = 'download_box'
    __select__ = (box.EntityBoxTemplate.__select__ & implements('Project') &
                  score_entity(lambda x: x.downloadurl and x.latest_version()))

    def cell_call(self, row, col, **kwargs):
        version = self.rset.get_entity(row, col).latest_version()
        idownloadable.download_box(self.w, version,
                                   self.req._('download latest version'),
                                   version.tarball_name())


class VersionDownloadBox(idownloadable.DownloadBox):
    __select__ = (box.EntityBoxTemplate.__select__ & implements('Version') &
                  score_entity(lambda x: x.project.downloadurl and x.state == 'published'))

    def cell_call(self, row, col, title=None, **kwargs):
        version = self.rset.get_entity(row, col)
        super(VersionDownloadBox, self).cell_call(row, col, label=version.tarball_name())


class ImageSideboxView(boxes.SideBoxView):
    id = 'sidebox'
    __select__ = boxes.SideBoxView.__select__ & implements('Image', 'File')

    def call(self, boxclass='sideBox', title=u''):

        self.req.add_css('cubes.file.css')
        box = htmlwidgets.SideBoxWidget(display_name(self.req, title), self.id)
        entity = self.rset.get_entity(0, 0)
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
            see_all_url = u'[<a href="%s">%s (%s)</a>]' % (xml_escape(gallery_url),
                                                           self.req._('see them all'),
                                                           len(self.rset))
        else:
            see_all_url = u''
        html_container = (u'<li class="screenshot">'
                          u'<a href="%s" title="%s"><img alt="" src="%s"/>'
                          u'<br/>%s</a><br/>%s</li>')
        html = html_container % (xml_escape(gallery_url),
                                 xml_escape(entity.name),
                                 xml_escape(file_icon),
                                 xml_escape(entity.name),
                                 see_all_url)
        box.items = [htmlwidgets.BoxHtml(html)]
        box.render(self.w)

