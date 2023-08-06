"""filter_message.py - tool to filter a given message entry

AUTHOR: Emanuel Gardaya Calso

"""

import os
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
        url = '%s?sender=%s&recipient=%s&message=%s' % (
                action.details,
                entry.sender,
                entry.recipient,
                entry.message,
            )
        urllib.FancyURLopener().open(url)
    elif action.action == 'run':
        cmd = '%s %s "%s"' % (action.details, entry.sender, entry.message)
        os.system(cmd)
    return entry

def reply(received, message):
    entry = model.Message(
            folder=OUTBOX,
            message=message,
            sender=received.recipient,
            recipient=received.sender,
        )
    model.Session.save(entry)
    model.Session.commit()
    return entry

