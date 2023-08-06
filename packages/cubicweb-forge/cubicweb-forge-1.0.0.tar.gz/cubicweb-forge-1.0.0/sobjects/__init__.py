"""server side objects"""
from cubicweb.sobjects.notification import RecipientsFinder
from cubicweb.selectors import implements

class InterestedInRecipientsFinder(RecipientsFinder):
    __select__ = implements('Version', 'Ticket', 'Comment', 'TestInstance',
                            'Card', 'File', 'Image')

    def recipients(self):
        """Returns the project's interested people (entities)"""
        proj = self.entity(0).project
        if proj is not None:
            rql = ('Any X,E,A WHERE X interested_in P, P eid %(p)s, X in_state S, '
                   'S name "activated", X primary_email E, E address A')
            # use unsafe_execute since user don't necessarily have access to
            # all users which should be notified
            rset = self.req.unsafe_execute(rql, {'p': proj.eid}, 'p',
                                           build_descr=True, propagate=True)
            return [(u.get_email(), u.property_value('ui.language'))
                    for u in rset.entities()]
        return super(InterestedInRecipientsFinder, self).recipients()
