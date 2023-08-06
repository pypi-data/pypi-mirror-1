from cubicweb.schema import format_constraint

class Invoice(EntityType):
    num = String(required=True, fulltextindexed=True, indexed=True,
                 constraints=[SizeConstraint(16)],
                 description=_('invoice number'))
    emit_date = Date(description=_('emission date'))
    pay_date = Date(description=_('payment date'))
    type = String(required=True, internationalizable=True,
                  constraints=[StaticVocabularyConstraint((_('invoice'), _('expenses'), _('credit')))],
                  description=_("invoice type"), default='invoice')
    amount = Float(description=_('total amount without taxes'), required=True)
    taxes = Float(description=_('taxes on total amount'), required=True)

    credit_account = SubjectRelation('Account', cardinality='?*',
                                     description=_('account to credit'))
    debit_account = SubjectRelation('Account', cardinality='?*',
                                    description=_('account to debit'))
    in_state = SubjectRelation('State', cardinality='1*',
                               constraints=[RQLConstraint('O state_of ET, S is ET')])
    wf_info_for = ObjectRelation('TrInfo', cardinality='1*', composite='object')


class Account(EntityType):
    permissions = {'read': ('users', 'managers'),
                   'add': ('managers', ),
                   'update': ('managers',),
                   'delete': ('managers',),
                   }
    label = String(required=True, maxsize=128)
    account = String(required=True, maxsize=16)

