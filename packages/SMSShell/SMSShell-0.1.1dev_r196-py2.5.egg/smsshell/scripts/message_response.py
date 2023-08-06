"""filter_message.py - tool to filter a given message entry

AUTHOR: Emanuel Gardaya Calso

"""

import os
import urllib
from base import *


def find_response(sender, msg):
    m_args = msg.split(' ')
    print 'find_response', m_args
    for entry in model.list(model.Response).filter_by(keyword=m_args[0]):
        process_response(sender, m_args, entry)
    model.Session.commit()
    return

def process_response(sender, m_args, response):
    print 'process_response', sender, m_args, response
    if response.action == 'show':
        response = response_show(sender, m_args, response)
    elif response.action == 'search':
        response = response_search(sender, m_args, response)
    elif response.action == 'edit':
        response = response_edit(sender, m_args, response)
    elif response.action == 'delete':
        response = response_delete(sender, m_args, response)
    else:
        response = response
    return response

def response_show(sender, m_args, response):
    print 'response_show', sender, m_args
    r_def = response.default
    r_args = response.argument
    r_value = response.value
    table = custom_env.classes[response.table]
    query = custom_env.session.query(table)
    cnt = 0
    s_args = {}
    entries = []
    for arg in r_args:
        cnt += 1
        col = arg.field
        try:
            m_val = m_args[cnt]
        except IndexError:
            return send_err(sender, m_args)
        s_args[str(col)] = m_val.replace(space_sub, ' ')
    entries = query.filter_by(**s_args)
    if len(list(entries)) == 0:
        msg = 'No entry for %s where:%s' % (
                m_args[0],
                '\n'.join(('\n%s: %s' % (k,v) for k,v in s_args.iteritems())),
            )
        send_msg(sender, msg)
        return response
    for entry in entries:
        send_entry(sender, entry, r_value)
    return response

def send_entry(recipient, entry, outputs):
    print 'send_entry', recipient, entry, outputs
    msg = ''
    outs = []
    for output in outputs:
        outs.append((output.priority, output.label, output.field))
    outs.sort()
    for out in outs:
        label = out[1]
        field = out[2]
        value = getattr(entry, field)
        msg += '%s:%s\n' % (label, value)
    message = model.Message(
            folder = OUTBOX,
            sender = NUMBER,
            recipient = recipient,
            message = msg,
        )
    model.Session.save(message)
    print 'Saved to Outbox'
    return message

def send_err(recipient, m_args):
    msg = 'Invalid number of arguments for %s' % m_args[0]
    message = send_msg(recipient, msg)
    return message

def send_msg(recipient, msg):
    message = model.Message(
            folder = OUTBOX,
            sender = NUMBER,
            recipient = recipient,
            message = msg,
        )
    model.Session.save(message)
    print 'Saved to Outbox'
    return message

