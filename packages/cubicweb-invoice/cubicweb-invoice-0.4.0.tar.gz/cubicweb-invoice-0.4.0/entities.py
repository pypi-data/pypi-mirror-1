"""this contains the template-specific entities' classes"""

from cubicweb.entities import AnyEntity, fetch_config

class Invoice(AnyEntity):
    id = 'Invoice'
    fetch_attrs, fetch_order = fetch_config(['num'])

    def dc_title(self):
        return u"%s #%s" % (self.type, self.num.upper())

    def dc_long_title(self):
        _ = self.req._
        return u"%s (%s+%s) %s %s, %s %s - %s" % (self.dc_title(),
                                                  self.amount, self.taxes,
                                                  _('emited on'), self.format_date(self.emit_date),
                                                  _('paid on'), self.format_date(self.pay_date),
                                                  self.state)


class Account(AnyEntity):
    id = 'Account'
    fetch_attrs, fetch_order = fetch_config(['label', 'account'])

    def dc_title(self):
        return u'%s - %s' % (self.account, self.label)
