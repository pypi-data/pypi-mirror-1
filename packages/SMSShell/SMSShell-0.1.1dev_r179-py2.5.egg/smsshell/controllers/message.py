"""Message Controller

AUTHOR: Emanuel Gardaya Calso

Last Modified:
    2008-03-17
    2008-03-18

"""

import logging
import urllib

from smsshell.lib.base import *

log = logging.getLogger(__name__)


def get_labels():
    return model.list(model.Label).order_by(model.Label.c.name)

def get_contacts():
    return model.list(model.Contact).order_by(model.Contact.c.name)

class MessageController(ListController):
    table = model.Message
    parent = dict(
            folder = dict(
                table = model.Folder,
                column = 'name',
            )
        )
    properties = (
            ('label', 'name', model.Label),
        )
    list_functions = (
            'delete',
        )
    entry_functions = (
            'details',
            'delete',
        )

    def _init_custom(self):
        c.columns_hidden.add('modified')
        c.column_descriptions['created'] = 'Received'

    def _list(self):
        c.entries = self.query
        if 'show_label' in request.params:
            label = model.get(model.Label, request.params['show_label'])
            c.entries = c.entries.filter_by(label=label)

    def _multi(self):
        self._dbg('_multi', request.params.dict_of_lists())
        ids = self._multi_get_ids()
        function=request.params['function']
        if function == g.function_delete:
            self._multi_delete(ids)
        elif function == 'Add Label':
            self._multi_label_add(ids)
        elif function == 'Remove Label':
            self._multi_label_rem(ids)
        elif function == 'Archive':
            self._multi_archive(ids)
        #args = ['select=%s' % id for id in ids]
        del request.params['function']
        args = []
        for k,v in request.params.iteritems():
            args.append('%s=%s' % (k,v))
        redirect_to(str('list?%s' % '&'.join(args)))
        return

    def _multi_archive(self, ids):
        self._dbg('_multi_archive', ids)
        map(self.archive, ids)

    def _multi_label_add(self, ids):
        self._dbg('_multi_label_add', ids)
        map(self.label_add, ids)

    def _multi_label_rem(self, ids):
        self._dbg('_multi_label_rem', ids)
        map(self.label_rem, ids)

    def add(self):
        self._dbg('add')
        self._add()
        return render('/message/compose.mako')

    def archive(self, id):
        entry = model.Session.query(c.table).get(id)
        entry.folder = g.folder_archive
        model.Session.update(entry)
        model.Session.commit()

    def edit(self, id):
        self._dbg('edit')
        self._details(request.params['id'])
        return render('/message/compose.mako')

    def label_add(self, id):
        entry = model.Session.query(c.table).get(id)
        label = model.Session.query(model.Label).get(request.params['label'])
        entry.label.append(label)
        model.Session.update(entry)
        model.Session.commit()

    def label_rem(self, id):
        entry = model.Session.query(c.table).get(id)
        label = model.Session.query(model.Label).get(request.params['label'])
        try:
            entry.label.remove(label)
        except ValueError:
            return
        model.Session.update(entry)
        model.Session.commit()
        return

    def list(self):
        self._dbg('list')
        c.contacts = get_contacts()
        c.labels = get_labels()
        self._list_params()
        self._list_query()
        self._list()
        return render('/message/list.mako')
    index=list

    def reply(self, id):
        self._dbg('edit')
        self._details(request.params['id'])
        old_entry = c.entry
        c.entry = c.table(
                recipient=old_entry.sender,
                sender=old_entry.recipient,
            )
        c.id = None
        return render('/message/compose.mako')

    def save(self):
        self._dbg('save')
        try:
            id = request.params['id']
        except KeyError:
            id = None
        entry = self._save(id, request.params)
        self._dbg('save', entry.id)
        try:
            label = request.params['show_label']
        except KeyError:
            label = ''
        redirect_to('list', show_label=label)
        return 'Saved'

    def show_contacts(self):
        recipient = request.params['recipient']
        c.selected = []
        for a in recipient.split(' '):
            c.selected.append(h.strip_prefix(a))
        if '' in c.selected:
            c.selected.remove('')
        c.phones = model.list(model.Phone)
        c.phones = c.phones.filter(model.Contact.c.id==model.Phone.c.contact)
        c.phones = c.phones.order_by(model.Contact.c.name)
        c.contacts = model.list(model.Contact)
        return render('/message/show_contacts.mako')

    def add_rem_num(self):
        number = request.params['number']
        recipient = request.params['recipient']
        c.numbers = list(h.strip_prefix(a) for a in recipient.split(' '))
        if number in c.numbers:
            c.numbers.remove(number)
        else:
            c.numbers.append(number)
        if '' in c.numbers:
            c.numbers.remove('')
        c.phones = model.list(model.Phone)
        c.phones = c.phones.filter(model.Contact.c.id==model.Phone.c.contact)
        c.phones = c.phones.order_by(model.Contact.c.name)
        c.contacts = model.list(model.Contact)
        c.selected = c.numbers
        return render('/message/recipient_field.mako')


