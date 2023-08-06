import logging

from smsshell.lib.base import *

log = logging.getLogger(__name__)

class ResponseController(ListController):
    table = model.Response
    children = dict(
            argument = dict(
                    table=model.ResponseArgument,
                    columns=('priority', 'field'),
                    label='User Input',
                ),
            default = dict(
                    table=model.ResponseDefault,
                    columns=('field', 'value'),
                ),
            value = dict(
                    table=model.ResponseValue,
                    columns=('priority', 'label', 'field'),
                    label='Output',
                ),
        )

    def edit(self, id):
        self._dbg('edit')
        self._details(request.params['id'])
        return render('/response/edit.mako')

    def edit0(self, id):
        self._dbg('edit')
        self._details(request.params['id'])
        return render('/response_edit.mako')

    def add0(self):
        self._dbg('add')
        self._add()
        return render('/response_edit.mako')

    def save0(self):
        self._dbg('save')
        all_args = dict(request.params)
        response_args = {}
        argument_args = {}
        self._dbg('save', all_args.keys())
        for k,v in all_args.iteritems():
            self._dbg('save', k)
            if k in self.table.c.keys():
                response_args[k] = v
            else:
                argument_args[k] = v
        entry = self._save(request.params.get('id', None), response_args)
        self.save_children(entry.id, **argument_args)
        redirect_to('list')
        return 'Saved'

    def save_children0(self, e_id, **kw):
        self._dbg('save_children', dir(self.table.argument))
        for cnt in range (1, 11):
            if kw['field-%s' % cnt] != '':
                if kw['id-%s' % cnt] == '':
                    self.save_new_child(e_id, kw['field-%s' % cnt], cnt)
                else:
                    self.save_old_child(e_id, kw['id-%s' % cnt], kw['field-%s' % cnt], cnt)
        return

    def save_new_child0(self, e_id, field, priority):
        entry = model.Argument(
                field=field,
                priority=priority,
                response=e_id,
            )
        model.Session.save_or_update(entry)
        model.Session.commit()
        return

    def save_old_child0(self, e_id, id, field, priority):
        entry = model.Session.query(model.Argument).get(id)
        entry.field = field
        entry.priority = priority
        model.Session.save_or_update(entry)
        model.Session.commit()
        return


