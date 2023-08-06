"""Custom form for forge

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb.selectors import implements, match_transition
from cubicweb.web.formfields import DateField
from cubicweb.web.views import workflow, editviews

class VersionChangeStateForm(workflow.ChangeStateForm):
    __select__ = implements('Version') & match_transition('publish')

    publication_date = DateField(eidparam=True)

    def form_field_value(self, field, load_bytes=False):
        # using initial on the field doesn't work since it's not considered
        # (entity has an eid)
        if field.name == 'publication_date':
            return self.edited_entity.publication_date or datetime.now()
        return super(VersionChangeStateForm, self).form_field_value(field,
                                                                    load_bytes)


class ShortComboboxView(editviews.ComboboxView):
    """by default combobox view is redirecting to textoutofcontext view
    but in the case of projects we want a shorter view
    """
    __select__ = implements('Project')
    def cell_call(self, row, col):
        self.w(self.entity(row, col).dc_title())
