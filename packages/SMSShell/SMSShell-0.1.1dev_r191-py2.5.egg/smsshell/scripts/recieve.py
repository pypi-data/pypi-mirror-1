#!/usr/bin/python
# -*- coding: utf-8 -*-
#receive.py

"""receive.py - script that processes messages received thru kannel

AUTHOR: Emanuel Gardaya Calso

"""

import urllib

from base import *
import message_filter
import message_response

recipient = NUMBER

def save(sender, msg):
    entry = model.Message(
            recipient=recipient,
            sender=urllib.unquote_plus(sender),
            message=urllib.unquote_plus(msg),
            folder=INBOX,
        )
    model.Session.save(entry)
    model.Session.commit()
    message_filter.go_thru_filters(entry)
    return

def find_response(sender, msg):
    m_args = msg.split(' ')
    response = model.Session.query(model.Response).filter_by(keyword=m_args[0])
    return response

def process_response(sender, msg, entry):
    m_args = msg.split(' ')
    if entry.action == 'search':
        response = process_response_search(m_args, entry)
    elif entry.action == 'show':
        response = process_response_show(m_args, entry)
    elif entry.action == 'delete':
        response = process_response_delete(m_args, entry)
    elif entry.action == 'edit':
        response = process_response_edit(m_args, entry)
    else:
        response = None
    return response

def process_response_delete(m_args, entry):
    table = getattr(model, entry.table)
    entry = model.Session.query(table).get(m_args[1])
    model.Session.delete(entry)
    model.Session.commit()
    return '%s Successfully deleted.' % entry

def process_response_edit(m_args, entry):
    r_args = entry.argument
    table = getattr(model, entry.table)
    if len(m_args)-2 != len(r_args):
        print 'Invalid number of arguments'
        return 'Invalid number of arguments'
    entry = model.get(table, m_args[1])
    cnt = 1
    for arg in r_args:
        col = arg.field
        cnt += 1
        value = m_args[cnt].replace(space_sub, ' ')
        setattr(entry, col, value)
    model.Session.update(entry)
    model.Session.commit()
    return '%s Successfully edited.' % entry

def process_response_search(m_args, entry):
    r_args = entry.argument
    table = getattr(model, entry.table)
    if len(m_args)-1 != len(r_args):
        return 'Invalid number of arguments'
    query = model.Session.query(table)
    s_args = {}
    cnt = 0
    for arg in r_args:
        col = arg.field
        cnt += 1
        s_args[str(col)] = m_args[cnt].replace(space_sub, ' ')
    entries = query.filter_by(**s_args)
    if len(list(entries)) == 0:
        return 'Not found'
    response = '%s ids: ' % entry.table
    for entry in entries:
        response += str(entry.id)
    return response

def process_response_show(m_args, entry):
    r_args = entry.argument
    table = getattr(model, entry.table)
    #if len(m_args)-2 != len(r_args):
    #    return 'Invalid number of arguments'
    entry = model.Session.query(table).get(m_args[1])
    response = 'ID: %s\n' % entry.id
    for arg in r_args:
        col = arg.field
        response += '%s: %s\n' % (col.replace('_', ' ').title(), getattr(entry, col))
    return response

def reply(sender, msg):
    entry = model.Message(
            folder=3,
            message=msg,
            sender=recipient,
            recipient=sender,
        )
    model.Session.save(entry)
    model.Session.commit()
    return

def main():
    global model
    model = setup()
    message_filter.model = model
    message_response.model = model
    sender = argv[1]
    msg = urllib.unquote_plus(argv[2])
    msg = msg.replace('�', ' ').replace(u'\xfb', ' ').replace(u'\xfc', ' ')
    message_response.find_response(sender, msg)
    save(sender, msg)
    return


if __name__ == '__main__':
    main()

