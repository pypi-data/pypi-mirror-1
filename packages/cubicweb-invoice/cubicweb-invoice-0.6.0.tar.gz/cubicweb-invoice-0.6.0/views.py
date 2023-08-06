"""template-specific forms/views/actions/components"""
from cubicweb.web import uicfg
uicfg.autoform_section.tag_subject_of(('Invoice', 'credit_account', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Invoice', 'debit_account', '*'), 'muledit', 'attributes')
uicfg.autoform_section.tag_subject_of(('Invoice', 'credit_account', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Invoice', 'debit_account', '*'), 'muledit', 'attributes')
