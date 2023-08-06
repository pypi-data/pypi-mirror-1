"""some hooks and views to handle notification on forge entity's changes

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.textutils import normalize_text

from cubicweb import RegistryException
from cubicweb.selectors import implements
from cubicweb.sobjects.notification import StatusChangeMixIn, NotificationView

from cubes.comment.hooks import CommentAddedView


class ForgeEmailView(NotificationView):

    def context(self, **kwargs):
        context = NotificationView.context(self, **kwargs)
        entity = self.entity(0)
        proj = entity.project
        description = entity.printable_value('description', format='text/plain')
        description = normalize_text(description, 80)
        context.update({'description': description,
                        'pname': proj.name,
                        'purl': proj.absolute_url()})
        return context

    def subject(self):
        entity = self.entity(0)
        return '[%s] %s' % (entity.project.name, self._subject(entity))

    def _subject(self, entity):
        return '%s %s (%s)' % (entity.dc_type(),
                               self.message,
                               entity.dc_title())


class ProjectStatusChangeView(StatusChangeMixIn, ForgeEmailView):
    __select__ = implements('Project')

    def _subject(self, entity):
        return self.req._(u'project is now in state "%s"') % (
            self.req.__(self._kwargs['current_state']))


class VersionStatusChangeView(StatusChangeMixIn, ForgeEmailView):
    __select__ = implements('Version')

    def _subject(self, entity):
        return self.req._(u'version %(num)s is now in state "%(state)s"') % {
            'num': entity.num,
            'state': self.req.__(self._kwargs['current_state'])}


class BSStatusChangeView(StatusChangeMixIn, ForgeEmailView):
    __select__ = implements('Ticket')

    def _subject(self, entity):
        return self.req._(u'%(etype)s "%(title)s" is now in state "%(state)s"') % {
            'etype': entity.dc_type(), 'title': entity.dc_title(),
            'state': self.req.__(self._kwargs['current_state'])}


class TicketPriorityChangeView(ForgeEmailView):
    id = 'notif_priority_changed'
    __select__ = implements('Ticket')

    content = _("ticket priority changed from %(oldpriority)s to %(newpriority)s")

    def context(self, **kwargs):
        entity = self.entity(0)
        context = ForgeEmailView.context(self, **kwargs)
        context['newpriority'] = entity.priority
        return context

    def _subject(self, entity):
        return self.req._(u'%(etype)s "%(title)s" priority changed from "%(oldpriority)s" to "%(newpriority)s"') % {
            'etype': entity.dc_type(), 'title': entity.dc_title(), 'oldpriority': self._kwargs['oldpriority'],
            'newpriority': entity.priority}


class ProjectAddedView(ForgeEmailView):
    id = 'notif_after_add_entity'
    __select__ = implements('Project')
    content = _("""
A new project was created : #%(eid)s - %(pname)s

Description
-----------
%(description)s

URL
---
%(url)s
""")
    def subject(self):
        return u'%s %s' % (self.req._('new project added:'), self.entity(0).name)


class TicketSubmittedView(ForgeEmailView):
    id = 'notif_after_add_relation_concerns'
    __select__ = implements('Ticket')
    content = _("""
New %(etype)s for project %(pname)s :

#%(eid)s - %(title)s
====================

:type: %(type)s
:priority: %(priority)s
:load: %(load)s

description
-----------
%(description)s

submitter
---------
%(user)s

URL
---
%(url)s
(project URL: %(purl)s)
""")

    def context(self, **kwargs):
        ctx = super(TicketSubmittedView, self).context(**kwargs)
        entity = self.entity(0, 0)
        ctx['type'] = self.req._(entity.type)
        ctx['priority'] = self.req._(entity.priority)
        ctx['load'] = self.format_float(entity.load)
        return ctx

    def _subject(self, entity):
        return '%s (%s)' % (self.req._('New %s' % entity.e_schema),
                            entity.dc_title())


class ForgeCommentAddedView(CommentAddedView):

    def subject(self):
        entity = self.entity(0)
        if entity.project: # may be None if commenting a file used as email attachment
            return u'[%s] %s' % (entity.project.name, CommentAddedView.subject(self))
        return CommentAddedView.subject(self)

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (ForgeCommentAddedView,))
    vreg.register_and_replace(ForgeCommentAddedView, CommentAddedView)
