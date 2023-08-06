# postcreate script. You could setup a workflow here for example

waiting_command  = add_state(_('waiting command'), 'Invoice', initial=True)
planned = add_state(_(u'planned'),  'Invoice')
toissue = add_state(_(u'to issue'), 'Invoice')
tosend  = add_state(_(u'to send'),  'Invoice')
sent    = add_state(_(u'sent'),     'Invoice')
payed   = add_state(_(u'payed'),    'Invoice')

add_transition(_('command received'), 'Invoice', (waiting_command,), planned)
add_transition(_(u'work done'), 'Invoice', (planned,), toissue)
add_transition(_(u'issue'),     'Invoice', (toissue,), tosend)
add_transition(_(u'send'),      'Invoice', (tosend,), sent)
add_transition(_(u'pay'),       'Invoice', (sent,), payed)
