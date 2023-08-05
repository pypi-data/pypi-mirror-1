#  Copyright (C) 2007 Yannick Gingras <ygingras@ygingras.net>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sqlalchemy import *
from sqlalchemy.ext.assignmapper import assign_mapper
from pylons.database import create_engine
from pylons.database import session_context as ctx

from datetime import datetime
from dateutil.relativedelta import relativedelta

import uuid
import hmac
from hashlib import sha256
from gazest.lib.request_util import get_client_ip, taguri

# FIXME: this is presentation stuff, it might need to move to other layers
import webhelpers as h

meta = MetaData()

def soon():
    return datetime.utcnow() + relativedelta(days=3)

from sqlalchemy import types, exceptions
class Enum(types.TypeDecorator):
    '''Implement columns with a discrete, finite set of possible values'''
    # not fully tested, it comes from
    #   http://www.sqlalchemy.org/trac/wiki/UsageRecipes/Enum

    impl = types.Unicode
    
    def __init__(self, values, empty_to_none=False):      
        """Emulate an Enum type.
        
        values : a list of values that are valid for this column
        empty_to_none : treat the empty string '' as None
        """

        if values is None or len(values) is 0:
            raise exceptions.AssertionError('Enum requires a list of values')
        self.empty_to_none = empty_to_none
        self.values = values[:]
        # the length of the string/unicode column should be the longest string
        # in values
        size = max([len(v) for v in values if v is not None])
        super(Enum, self).__init__(size)        
        
        
    def convert_bind_param(self, value, engine):
        if self.empty_to_none and value is '':
            value = None
        if value not in self.values:
            raise exceptions.AssertionError('"%s" not in Enum.values' % value)
        return super(Enum, self).convert_bind_param(value, engine)
        
        
    def convert_result_value(self, value, engine):
        if value not in self.values:
            raise exceptions.AssertionError('"%s" not in Enum.values' % value)
        return super(Enum, self).convert_result_value(value, engine)


USER_RANKS = ["alchemist", "thaumaturge", "warlock", "wizard", "lich", "god"]
RANK_LVLS = dict(map(reversed, enumerate(USER_RANKS)))

users_table = Table('users', meta,
                    Column('id', Integer, primary_key=True),
                    Column('creat_date', DateTime,
                           default=datetime.utcnow),
                    Column('name', Unicode, nullable=True, unique=True), 
                    Column('username', Unicode, nullable=False, unique=True), 
                    Column('email', Unicode, nullable=True, unique=True),
                    Column('openid', Unicode, nullable=True, unique=True),
                    Column('authtype', 
                           Enum(["email", "openid"]), 
                           nullable=False),
                    Column('status', 
                           Enum(["conf_pending", "active"]), 
                           nullable=False, 
                           default="conf_pending"),

                    # password is hashed
                    Column('password', Unicode, nullable=True),
                    Column('salt', Unicode, nullable=True),
                    
                    Column('rank', Integer, nullable=False, default=0),
                    )

class User(object):
    def check_password(self, password):
        return self.password == self.hash_password(password)

    def hash_password(self, password):
        return hmac.new(self.salt, password).hexdigest()
    
    def set_password(self, password):
        self.salt = str(uuid.uuid4())
        self.password = self.hash_password(password)


# in system mail
gazmails_table = Table('gazmails', meta,
                       Column('id', Integer, primary_key=True),
                       Column('creat_date', DateTime,
                              default=datetime.utcnow),
                       Column('subject', Unicode, nullable=True), 
                       Column('body', Unicode, nullable=False, unique=True), 
                       Column('format', 
                              Enum(["plain", "markdown"]), 
                              default="markdown",
                              nullable=False),
                       Column('sender_status', 
                              Enum(["draft", "sent"]), 
                              nullable=False, 
                           default="draft"),
                       Column('reader_status', 
                              Enum(["new", "read", "spam", "deleted"]), 
                              nullable=False, 
                           default="new"),
                       Column('parent_id', Integer,
                              ForeignKey("gazmails.id"), 
                              nullable=True), 
                       Column('from_id', Integer,
                              ForeignKey("users.id"), 
                              nullable=False), 
                       Column('to_id', Integer,
                              ForeignKey("users.id"), 
                              nullable=True), 
                       Column('is_important', Boolean, 
                              nullable=False,
                              default=False),
                       Column('is_replied', Boolean, 
                              nullable=False,
                              default=False),
                       )

class Gazmail(object):
    def render_body(self):
        # TODO: implement other markups
        # FIXME: this definitly is part of the presentation layer...
        return h.markdown(h.escape_once(self.body))


# Revisions are stored in a DAG.  Revisions are the nodes. 
# we use this semantic:
#  http://en.wikipedia.org/wiki/Revision_control#Common_vocabulary
# a revision is the content of one page at a given time
# The mapping is a bit different than the usual Alchemy stuff.  It's
# base on the graph example in the Alchemy distribution.
# A parent is a rev that is modified to get the child.

# all the caching made by the parser should go in the revnode
revnodes_table = Table('revnodes', meta,
                       Column("id", Integer, primary_key=True),
                       Column("body", Unicode, nullable=False),
                       Column("comment", Unicode, nullable=False, default=""),

                       # Each node was once the tip of a page, this is
                       # the page slug at commit time.  Beware, the
                       # node can be in the DAG of other pages, even
                       # as the tip.
                       Column('slug', Unicode, default=""),
                       Column("creat_ip", Unicode, default=get_client_ip),
                       Column("user_id", Integer, ForeignKey("users.id"), 
                              nullable=True),
                       Column("creat_date", DateTime, default=datetime.utcnow),

)
 
revarcs_table = Table('revarcs', meta,
    Column("lower_id", Integer, ForeignKey('revnodes.id'), primary_key=True),
    Column("higher_id", Integer, ForeignKey('revnodes.id'), primary_key=True)
)

class RevNode(object):
    def add_parent(self, othernode):
        RevArc(othernode, self)

    def del_parent(self, othernode):
        # we have to do it that way because we don't have an id yet
        for arc in self.higher_arcs:
            if arc.lower_node == othernode:
                arc.delete()

    def add_child(self, othernode):
        RevArc(self, othernode)

    def children(self):
        return [x.higher_node for x in self.lower_arcs]

    def parents(self):
        return [x.lower_node for x in self.higher_arcs]

    def taguri(self):
        return taguri(self.creat_date, "wiki-rev", self.id)
    

class RevArc(object):
    def __init__(self, low, high):
        self.lower_node = low
        self.higher_node = high


_nodeid = revnodes_table.c.id
assign_mapper(ctx, RevNode, revnodes_table,
              properties={
    'user':relation(User)
    })
assign_mapper(ctx, RevArc, revarcs_table, properties={
    'lower_node':relation(RevNode,
primaryjoin=revarcs_table.c.lower_id==_nodeid, backref='lower_arcs'),
    'higher_node':relation(RevNode,
primaryjoin=revarcs_table.c.higher_id==_nodeid, backref='higher_arcs')
    }
)

# a Namespace is a wiki prefix and a set of default macros

namespaces_table = Table('namespaces', meta,
                         Column('id', Integer, primary_key=True),
                         # how the space is represented in URLs
                         Column('slug', Unicode, nullable=False),
                         # how we access the namespace in wiki-links
                         Column('wikiprefix', Unicode, nullable=False),

                         # for pretty printing only
                         Column('name', Unicode, nullable=False),

                         # stub_page and not_found_page are revnodes,
                         # not pages, to solve the chicken and egg
                         # problem: pages require a namespaces

                         # a new page in this namespace will default
                         # to this content
                         Column('stub_rev_id', Integer,
                                ForeignKey("revnodes.id"), 
                                nullable=False),

                         # what you see when visiting a non-existant
                         # page
                         Column('not_found_rev_id', Integer,
                                ForeignKey("revnodes.id"), 
                                nullable=False), 
                         
                         )

class Namespace(object):
    pass

_revnode_id = revnodes_table.c.id
_stub_id = namespaces_table.c.stub_rev_id
_not_found_id = namespaces_table.c.not_found_rev_id
assign_mapper(ctx, Namespace, namespaces_table,
              properties=dict(stub_rev=relation(RevNode,
                                                 primaryjoin=_stub_id==_revnode_id),
                              not_found_rev=relation(RevNode,
                                                      primaryjoin=_not_found_id==_revnode_id),
                              ),
              )


# a Page is just a pointer in the revision DAG

pages_table = Table('pages', meta,
                    Column('id', Integer, primary_key=True),
                    # for fast lookup
                    Column('slug', Unicode, unique=True, nullable=False),
                    Column('namespace_id', Integer,
                           ForeignKey("namespaces.id"), 
                           nullable=False), 
                    Column('revnode_id', Integer,
                           ForeignKey("revnodes.id"), 
                           nullable=False), 
                    Column("creat_date", DateTime, default=datetime.utcnow),

                          )

class Page(object):
    def taguri(self):
        return taguri(self.creat_date, "wiki-page", self.id)

assign_mapper(ctx, Page, pages_table, 
              properties=dict(rev=relation(RevNode),
                              namespace=relation(Namespace)))


# registration confirmation

def gen_conf_key():
    # TODO: check for clashes
    return str(uuid.uuid4())

confirmations_table = Table('confirmations', meta,
                            Column('id', Integer, primary_key=True),
                            Column('creat_date', DateTime,
                                   default=datetime.utcnow),
                            Column('expiration_date', DateTime,
                                   default=soon),
                            
                            Column('key', Unicode, nullable=False, 
                                   unique=True, 
                                   default=gen_conf_key), 
                            Column('user_id', Integer,
                                   ForeignKey("users.id"), 
                                   nullable=False), 
                            Column('authtype', 
                                   Enum(["email", "openid"]), 
                                   nullable=False),

                          )

class Confirmation(object):
    pass

assign_mapper(ctx, Confirmation, confirmations_table,
              properties=dict(user=relation(User)))


assign_mapper(ctx, Gazmail, gazmails_table, 
              properties=dict(children=relation(Gazmail,
                                                primaryjoin=gazmails_table.c.parent_id==gazmails_table.c.id,
                                                backref=backref("parent", remote_side=[gazmails_table.c.id]),
                                                ),
                              parent=relation(Gazmail,
                                              uselist=False,
                                              remote_side=[gazmails_table.c.id],),
                              ))

_from_id = gazmails_table.c.from_id
_to_id = gazmails_table.c.to_id
_sender_status = gazmails_table.c.sender_status
_reader_status = gazmails_table.c.reader_status

assign_mapper(ctx, User, users_table,
              properties=dict(
        out_mails=relation(Gazmail, 
                          foreign_keys=[gazmails_table.c.from_id], 
                          primaryjoin=_from_id==users_table.c.id,
                          backref="from_user"),
        sent_mails=relation(Gazmail, 
                          foreign_keys=[_from_id], 
                          primaryjoin=and_(_from_id==users_table.c.id,
                                           _sender_status=="sent")),
        draft_mails=relation(Gazmail, 
                             foreign_keys=[gazmails_table.c.from_id], 
                             primaryjoin=and_(_from_id==users_table.c.id,
                                              _sender_status=="draft")),
        

        # all the mails addressed to this user but not all of it is sent yet
        to_mails=relation(Gazmail, 
                          foreign_keys=[_to_id], 
                          primaryjoin=_to_id==users_table.c.id,
                          backref="to_user"),
        recvd_mails=relation(Gazmail, 
                             foreign_keys=[_to_id], 
                             primaryjoin=and_(_to_id==users_table.c.id,
                                              _sender_status=="sent")),
        new_mails=relation(Gazmail, 
                           foreign_keys=[gazmails_table.c.to_id], 
                           primaryjoin=and_(_to_id==users_table.c.id,
                                            _sender_status=="sent", 
                                            _reader_status=="new", 
                                            )),
        inbox_mails=relation(Gazmail, 
                             foreign_keys=[gazmails_table.c.to_id], 
                             primaryjoin=and_(_to_id==users_table.c.id,
                                              _sender_status=="sent", 
                                              or_(_reader_status=="new", 
                                                  _reader_status=="read"), 
                                              )),
       
        
        ))




# IP addr based blocking
# This is really biased toward IPv4 
boycotts_table = Table('boycott', meta,
                       Column('id', Integer, primary_key=True),
                       Column('creat_date', DateTime,
                              default=datetime.utcnow),
                       Column('expiration_date', DateTime,
                              nullable=False),

                       Column('range_start', Integer, nullable=False),
                       Column('range_stop', Integer, nullable=False),
                       Column('range_cidr', Unicode, nullable=False), 

                       Column('reason', Unicode, nullable=False), 
                    
                       Column('instigator_id', Integer,
                                   ForeignKey("users.id"), 
                                   nullable=False), 
                       )

class Boycott(object):
    pass

assign_mapper(ctx, Boycott, boycotts_table,
              properties=dict(instigator=relation(User)))

ABUSE_TYPES = ["spam", "vandalism", "offtopic", "other"]

abuse_reports_table = Table('abuse_reports', meta,
                            Column('id', Integer, primary_key=True),
                            Column('creat_date', DateTime,
                                   default=datetime.utcnow),
                            Column("creat_ip", Unicode,
                                   default=get_client_ip),
                            Column('reporter_id', Integer,
                                   ForeignKey("users.id")), 

                            Column('problem', 
                                   Enum(ABUSE_TYPES), 
                                   nullable=False),
                            
                            Column('rev_id', Integer,
                                ForeignKey("revnodes.id"), 
                                nullable=False),

                            Column('comment', Unicode, nullable=False), 
                       )

class AbuseReport(object):
    pass

assign_mapper(ctx, AbuseReport, abuse_reports_table,
              properties=dict(reporter=relation(User),
                              rev=relation(RevNode)))
