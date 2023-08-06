"""filter_message.py - tool to filter a given message entry

AUTHOR: Emanuel Gardaya Calso

"""

import os
import commands
import urllib
from base import *

def go_thru_filters(entry):
    for condition in model.list(model.FilterCondition):
        entry = go_thru_filter(condition, entry)
    model.Session.update(entry)
    model.Session.commit()
    return entry

def go_thru_filter(condition, entry):
    if condition.filter is None:
        return entry
    column = condition.field
    match,keyword = condition.condition.split(':')
    value = getattr(entry, column)
    if match.lower() == 'is':
        if value == keyword:
            filter = model.get(model.Filter, condition.filter)
            entry = apply_filter(filter, entry)
    elif match.lower() == 'has':
        if value.find(keyword) > -1:
            filter = model.get(model.Filter, condition.filter)
            entry = apply_filter(filter, entry)
    elif match.lower() == 'starts':
        if value.startswith(keyword):
            filter = model.get(model.Filter, condition.filter)
            entry = apply_filter(filter, entry)
    elif match.lower() == 'ends':
        if value.endswith(keyword):
            filter = model.get(model.Filter, condition.filter)
            entry = apply_filter(filter, entry)
    return entry

def apply_filter(filter, entry):
    if filter.archive is True:
        entry.folder = ARCHIVE
    for action in filter.action:
        entry = apply_filter_action(action, entry)
    for label in filter.label:
        entry = apply_filter_label(label, entry)
    return entry

def apply_filter_label(label, entry):
    if label not in entry.label:
        entry.label.append(label)
    return entry

def apply_filter_action(action, entry):
    if action.action == 'reply':
        reply(entry, action.details)
    elif action.action == 'visit':
        visit(entry, action)
    elif action.action == 'run':
        run(entry, action)
    elif action.action == 'query':
        query(entry, action)
    return entry

def reply(received, message):
    sender=received.recipient
    recipient=received.sender
    msg_len = len(message)
    if msg_len <= 160:
        send(sender, recipient, message)
    elif msg_len > 160:
        for cnt in range(0, msg_len/160):
            start = (cnt*160) - 160
            end = (cnt*160)
            msg = message[start:end]
            send(sender, recipient, msg)
    model.Session.commit()
    return

def send(sender, recipient, message):
    entry = model.Message(
            folder=OUTBOX,
            message=message,
            sender=sender,
            recipient=recipient,
        )
    model.Session.save(entry)
    return entry

def visit(entry, action):
    url = '%s?sender=%s&recipient=%s&message=%s' % (
            action.details,
            entry.sender,
            entry.recipient,
            entry.message,
        )
    urllib.FancyURLopener().open(url)

def run(entry, action):
    cmd = '%s %s "%s"' % (action.details, entry.sender, entry.message)
    output = commands.getoutput(cmd)
    reply(entry, output)
    return entry

def query(entry, action):
    m_args = entry.message.split(' ')
    query = action.details
    for cnt in range(1, len(m_args)):
        query = query.replace('%' + str(cnt),  m_args[cnt])
    cmd = '''mysql forte -u root -e '%s' ''' % query
    output = commands.getoutput(cmd)
    reply(entry, output)
    return entry

