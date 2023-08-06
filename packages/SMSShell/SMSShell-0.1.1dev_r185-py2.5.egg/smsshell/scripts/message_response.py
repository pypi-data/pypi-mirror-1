"""filter_message.py - tool to filter a given message entry

AUTHOR: Emanuel Gardaya Calso

"""

import os
import urllib
from base import *


def find_response(sender, msg):
    m_args = msg.split(' ')
    for entry in model.list(model.Response).filter_by(keyword=m_args[0]):
        process_response(sender, msg, entry)
    return

def process_response(sender, msg, response):
    m_args = msg.split(' ')
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
        s_args[str(col)] = m_args[cnt].replace(space_sub, ' ')
    entries = query.filter_by(**s_args)
    if len(list(entries)) == 0:
        return response
    for entry in entries:
        send_entry(sender, entry, r_value)
    return response

def send_entry(sender, entry, outputs):
    msg = ''
    outs = []
    for output in outputs:
        outs.append((output.priority, output.label, output.field))
    outs.sort()
    for out in outs:
        label = out[1]
        field = out[2]
        value = getattr(entry, field)
        msg += '%s:%s' % (label, value)
    message = model.Message(
            folder = OUTBOX,
            sender = NUMBER,
            recipient = sender,
            message = msg,
        )
    model.Session.save(message)
    return message

