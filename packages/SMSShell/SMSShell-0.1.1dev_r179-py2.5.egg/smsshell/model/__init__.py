
from datetime import datetime
from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import mapper, relation

import smsshell.lib.helpers as h


Session = scoped_session(sessionmaker(autoflush=True, transactional=True,
    bind=config['pylons.g'].sa_engine))

meta = MetaData()


address = Table('address', meta,
        Column('id', Integer, primary_key=True),
        Column('contact', Integer, ForeignKey('contact.id')),
        Column('address', UnicodeText, default=''),
        Column('comment', UnicodeText, default=''),
    )

argument = Table('argument', meta,
        Column('id', Integer, primary_key=True),
        Column('priority', Integer, default=0),
        Column('field', Unicode(32), default=''),
        Column('response', Integer, ForeignKey('response.id')),
    )

contact = Table('contact', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(32), unique=True),
    )

estate = Table('estate', meta,
        Column('id', Integer, primary_key=True),
        Column('number', Unicode(8), default=''),
        Column('lot', Unicode(32), default=''),
        Column('block', Unicode(32), default=''),
        Column('street', Unicode(32), default=''),
        Column('subdivision', Unicode(32), default=''),
        Column('village', Unicode(32), default=''),
        Column('barangay', Unicode(32), default=''),
        Column('area', Unicode(32), default=''),
        Column('town_city', Unicode(32), default=''),
        Column('province', Unicode(32), default=''),
        Column('region', Unicode(32), default=''),
        Column('zip_code', Unicode(32), default=''),
        Column('unit_type', Unicode(32), default=''),
    )

folder = Table('folder', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(32), unique=True),
        Column('comment', UnicodeText, default=''),
    )

filter = Table('filter', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(64), unique=True),
        Column('archive', Boolean, default=False),
        Column('active', Boolean, default=True),
        Column('comment', UnicodeText, default=''),
    )

filter_action = Table('filter_action', meta,
        Column('id', Integer, primary_key=True),
        Column('filter', Integer, ForeignKey('filter.id')),
        Column('action', Unicode(64), default=''),
        Column('details', UnicodeText, default=''),
    )

filter_condition = Table('filter_condition', meta,
        Column('id', Integer, primary_key=True),
        Column('filter', Integer, ForeignKey('filter.id')),
        Column('field', Unicode(64), default=''),
        Column('condition', Unicode(128), default=''),
    )

filter_label = Table('filter_label', meta,
        Column('id', Integer, primary_key=True),
        Column('filter', Integer, ForeignKey('filter.id')),
        Column('label', Integer, ForeignKey('label.id')),
    )

label = Table('label', meta,
        Column('id', Integer, primary_key=True),
        Column('name', Unicode(32), unique=True),
        Column('comment', UnicodeText, default=''),
    )

message = Table('message', meta,
        Column('id', Integer, primary_key=True),
        Column('sender', Unicode(32)),
        Column('recipient', Unicode(32)),
        Column('message', UnicodeText, default=''),
        Column('folder', Integer, ForeignKey('folder.id')),
        Column('modified', DateTime, default=datetime.now),
        Column('created', DateTime, default=datetime.now),
    )

message_label = Table('message_label', meta,
        Column('id', Integer, primary_key=True),
        Column('label', Integer, ForeignKey('label.id')),
        Column('message', Integer, ForeignKey('message.id')),
    )

phone = Table('phone', meta,
        Column('id', Integer, primary_key=True),
        Column('contact', Integer, ForeignKey('contact.id')),
        Column('number', Unicode(32)),
        Column('comment', UnicodeText, default=''),
    )

query = Table('query', meta,
        Column('id', Integer, primary_key=True),
        Column('table', Unicode(32), default=''),
        Column('query', UnicodeText, default=''),
    )

response = Table('response', meta,
        Column('id', Integer, primary_key=True),
        Column('keyword', Unicode(32), default=''),
        Column('table', Unicode(32), default=''),
        Column('action', Unicode(32), default=''),
        Column('active', Boolean, default=True),
        Column('comment', UnicodeText, default=''),
    )

response_argument = Table('response_argument', meta,
        Column('id', Integer, primary_key=True),
        Column('priority', Integer, default=0),
        Column('field', Unicode(32), default=''),
        Column('response', Integer, ForeignKey('response.id')),
    )

response_default = Table('response_default', meta,
        Column('id', Integer, primary_key=True),
        Column('field', Unicode(32), default=''),
        Column('value', Unicode(64), default=''),
        Column('response', Integer, ForeignKey('response.id')),
    )

response_value = Table('response_value', meta,
        Column('id', Integer, primary_key=True),
        Column('priority', Integer, default=0),
        Column('label', Unicode(64), default=''),
        Column('field', Unicode(32), default=''),
        Column('response', Integer, ForeignKey('response.id')),
    )

standard_reply = Table('standard_reply', meta,
        Column('id', Integer, primary_key=True),
        Column('keyword', Unicode(32), default=''),
        Column('message', UnicodeText, default=''),
    )


def list(cls):
    return Session.query(cls)

def get(cls, id):
    return Session.query(cls).get(id)


class Base(object):
    def __str__(self):
        return '<%s %s>' % (self.__class__.__name__, self.id)

    def __init__(self, **kw):
        for k,v in kw.iteritems():
            setattr(self, k, v)

class Address(Base):
    pass

class Argument(Base):
    pass

class Contact(Base):
    pass

class Estate(Base):
    pass

class Filter(Base):
    pass

class FilterAction(Base):
    pass

class FilterCondition(Base):
    pass

class FilterLabel(Base):
    pass

class Folder(Base):
    pass

class Label(Base):
    pass

class Message(Base):
    pass

class MessageLabel(Base):
    def __str__(self):
        return '<%s Message: %s Label: %s>' % (
                self.__class__.__name__,
                self.message,
                self.label,
            )

class Phone(Base):
    pass

class Response(Base):
    pass

class ResponseArgument(Base):
    pass

class ResponseDefault(Base):
    pass

class ResponseValue(Base):
    pass


mapper(Address, address)
mapper(Contact, contact, properties=dict(
        address=relation(Address),
        phone=relation(Phone),
    ))
mapper(Estate, estate)
mapper(Folder, folder, properties=dict(
        message=relation(Message),
    ))
mapper(Label, label, properties=dict(
        message=relation(Message, secondary=message_label),
    ))
mapper(Message, message, properties=dict(
        label=relation(Label, secondary=message_label),
    ))
mapper(MessageLabel, message_label)
mapper(Phone, phone)
mapper(Argument, argument)
mapper(ResponseArgument, response_argument)
mapper(ResponseDefault, response_default)
mapper(ResponseValue, response_value)
mapper(Response, response, properties=dict(
        argument=relation(ResponseArgument),
        default=relation(ResponseDefault),
        value=relation(ResponseValue),
    ))
mapper(FilterAction, filter_action)
mapper(FilterCondition, filter_condition)
mapper(FilterLabel, filter_label)
mapper(Filter, filter, properties=dict(
        action=relation(FilterAction),
        condition=relation(FilterCondition),
        label=relation(Label, secondary=filter_label),
    ))


