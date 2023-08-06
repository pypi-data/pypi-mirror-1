import logging

from smsshell.lib.base import *

log = logging.getLogger(__name__)

class ContactChildList(ChildList):
    def __init__(self, parent, field, details):
        self.parent = parent
        self.field = field
        self.details = details
        self.table = details['table']
        self.columns = details['columns']
        self.children = getattr(parent, field)

    def save_custom(self, kw):
        if not kw.has_key('number'):
            return
        for prefix in g.prefixes:
            kw['number'] = h.strip_prefix(kw['number']).replace(' ', '')
        return

    def save(self, id=None, **kw):
        self.save_custom(kw)
        if id is None:
            entry = self.table(**kw)
            self.children.append(entry)
            model.Session.save_or_update(self.parent)
        else:
            entry = model.get(self.table, id)
            for k,v in kw.iteritems():
                setattr(entry, k, v)
            model.Session.save_or_update(entry)
        return


class ContactController(ListController):
    table = model.Contact
    children = dict(
            phone = dict(
                    table = model.Phone,
                    columns = ('number',),
                ),
            address = dict(
                    table = model.Address,
                    columns = ('address',),
                ),
        )

    def _save_children(self, entry, **kw):
        for field, children in self.children.iteritems():
            child_list = ContactChildList(entry, field, children)
            child_list.multi_save(**kw)
        return entry


