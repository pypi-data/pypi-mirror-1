"""template-specific forms/views/actions/components"""
from logilab.common.decorators import monkeypatch

from cubicweb.web import uicfg, formwidgets as fw
from cubicweb.web.views import basecontrollers

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_afs.tag_subject_of(('Expense', 'spent_for', '*'), 'main', 'attributes')
_afs.tag_subject_of(('Expense', 'spent_for', '*'), 'muledit', 'attributes')
_affk.tag_subject_of(('Expense', 'spent_for', '*'),
                     {'widget': fw.RestrictedAutoCompletionWidget(autocomplete_initfunc='get_concerned_by')})


@monkeypatch(basecontrollers.JSonController)
@basecontrollers.jsonize
def js_get_concerned_by(self):
    return self._cw.execute('DISTINCT Any W,R ORDERBY R WHERE W ref R').rows
