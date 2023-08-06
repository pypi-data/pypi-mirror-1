# Copyright 2009, Red Hat, Inc
# Copyright 2009, Yaakov Nemoy
#
# This software may be freely redistributed under the terms of the GNU
# general public license, version 2 or higher.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from __future__ import with_statement

import re
import copy
import codecs
import gzip
import mailbox
import dateutil
import datetime

import dateutil.parser as dup
import httplib as http
import urlparse as up
import urlgrabber as ug

from urlgrabber.grabber import URLGrabber
from re import compile
from os import makedirs
from os.path import join

import sqlalchemy
import sqlalchemy.orm.attributes

from sqlalchemy import create_engine, Table, MetaData, Table, Column,\
    Integer, Text, DateTime
from sqlalchemy.exceptions import InvalidRequestError
from sqlalchemy.orm import mapper, sessionmaker, scoped_session, relation
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from util import iter_in_transaction, pwd, htmlentitydecoder

engine = None #create_engine('sqlite:///sqllite.db') #, echo=True)
metadata = MetaData()
Session = scoped_session(sessionmaker(autoflush=False))#, bind=engine))

class Hell(Exception): pass

def get_engine(dburi=None):
    global engine
    if engine:
        return engine
    elif dburi:
        engine = create_engine(dburi) #, echo=True)
        Session.configure(bind=engine)
        return engine
    else:
        raise Hell


stream_classes = dict()

def register_stream(cls, name):
    global stream_classes
    stream_classes[name] = cls


class MetaSqlBase(DeclarativeMeta):
    def __init__(cls, name, bases, attrs):
        DeclarativeMeta.__init__(cls, name, bases, attrs)
        sql_attrs = dict()
        unique_sql_attrs = dict()
        for attr in dir(cls):
            attr_obj = getattr(cls, attr)
            if isinstance(attr_obj, Column) \
                    or isinstance(attr_obj,
                                  sqlalchemy.orm.attributes.InstrumentedAttribute) \
                    or getattr(attr_obj, "_sql_attribute", False):
                sql_attrs[attr] = True
        unique_sql_attrs = cls.define_unique(unique_sql_attrs)
        cls._validate_remote = cls._clear_inv_keys_func(sql_attrs)
        cls._unique_remote = cls._clear_inv_keys_func(unique_sql_attrs)

    def _clear_inv_keys_func(self, v_keys):

        def clear_inv_keys(remote):
            v_remote = copy.copy(remote)
            for key in remote.iterkeys():
                if key not in v_keys:
                    del v_remote[key]
            return v_remote
        return staticmethod(clear_inv_keys)


class SqlBase(object):
    __metaclass__ = MetaSqlBase
    _decl_class_registry = dict()

    @classmethod
    def create_or_update(cls, **remote):
        try:
            sql_obj = session.query(cls)\
                .filter_by(**cls._unique_remote(remote))\
                .one()
            if sql_obj.needs_update(remote):
                sql_obj.update_props(**cls._validate_remote(remote))
                sql_obj.update(remote)
        except InvalidRequestError, e:
            sql_obj = cls(**cls._validate_remote(remote))
            session.add(sql_obj)
            sql_obj.update(remote)
        return sql_obj

    def update_props(self, **keys):
        self.__dict__.update(keys)

    def needs_update(self, remote):
        raise NotImplementedError

    def update(self, remote):
        raise NotImplementedError

    @staticmethod
    def define_unique(d):
        return d

Base = declarative_base(metadata=metadata, cls=SqlBase, metaclass=MetaSqlBase)


class MetaStream(type(Base)):
    def __init__(cls, name, bases, attrs):
        source = name.lower()
        cls.source = source
        type(Base).__init__(cls, name, bases, attrs)
        register_stream(cls, source)


class Stream(Base):
    __metaclass__ = MetaStream
    __tablename__ = 'streams'
    id = Column('id', Integer, primary_key=True)
    type = Column('type', Text, nullable=False)
    name = Column('name', Text)
    __mapper_args__ = dict(polymorphic_on = type, polymorphic_identity="stream")

    @property
    def source_class(self):
        return Source

    @staticmethod
    def define_unique(d):
        Base.define_unique(d)
        d['type'] = True
        d['name'] = True
        return d

    def needs_update(self, remote):
        return True

    def remote_iter(self):
        raise NotImplementedError

    @property
    def cache(self):
        return join(self.source, self.name)

    def update(self, remote):
        with pwd(CACHE_DIR):
            try:
                makedirs(self.cache)
            except OSError, e:
                print e
            remotes = self.remote_iter()
            for remote in iter_in_transaction(session, remotes):
                self.source_class.create_or_update(**remote)


class Mailman(Stream):
    __tablename__ = 'mailmen'
    id = Column('id', Integer, ForeignKey('streams.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='mailman', inherits=Stream)

    @property
    def archive(self):
        raise NotImplementedError

    @property
    def listinfo(self):
        raise NotImplementedError

    def url(self, month):
        raise NotImplementedError

    def mbox(self, month):
        print 'deprecated usage'
        return self.url(month)

    def cached_source(self, month):
        return join(self.cache, month)

class RHMailman(Mailman):
    __tablename__ = 'rhmailmen'
    id = Column('id', Integer, ForeignKey('mailmen.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='rhmailman', inherits=Mailman)

    regex = compile(r"""<a href=\"(?P<url>(?P<year>\d{4})-(?P<month>\w*?)/thread.html)\">\[ Thread \]""", re.I | re.S)
    def remote_iter(self):
        conn = URLGrabber(reget='check_timestamp',
                          user_agent='jemoeder/2.0',
                          prefix='http://www.redhat.com',
                          retry=0)

        site = self.archive
        html = ug.urlopen(site).read()
        matches = self.regex.finditer(html)
        match_dicts = (match.groupdict() for match in matches)

        for match_dict in match_dicts:
            match_dict['cache_url'] = self.url(match_dict['url'])
            match_dict['cache_file'] = match_dict['url'].replace('/', '-')
            match_dict['identifier'] = "%s-%s" % ( match_dict['year'], match_dict['month'])
            match_dict['stream'] = self
            match_dict['month'] = dup.parse('%s %s' % (match_dict['month'], match_dict['year']))

            resp = conn.urlread(up.urlsplit(match_dict['cache_url']).path)
            match_dict['size'] = len(resp)
            yield match_dict

    @property
    def source_class(self):
        return RHMailmanSource

    @property
    def archive(self):
        return 'https://www.redhat.com/archives/%s/' % self.name

    @property
    def listinfo(self):
        return 'https://www.redhat.com/mailman/listinfo/%s/' % self.name

    def url(self, month):
        return self.archive + month


class MBoxMailman(Mailman):
    __tablename__ = 'mboxmailmen'
    id = Column('id', Integer, ForeignKey('mailmen.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='mboxmailman')

    @property
    def source_class(self):
        return MBoxSource

    def remote_iter(self):
        site = self.archive
        html = ug.urlopen(site).read()
        matches = self.regex.finditer(html)
        match_dicts = (match.groupdict() for match in matches)
        for match_dict in match_dicts:
            match_dict['cache_url'] = self.url(match_dict['mbox'])
            match_dict['cache_file'] = match_dict['mbox']
            match_dict['identifier'] = match_dict['mbox']
            match_dict['stream'] = self
            match_dict['month'] = dup.parse('%s %s' % (match_dict['month'], match_dict['year']))
            if type(match_dict['size']) is str:
                match_dict['size'] = int(match_dict['size'])
            yield match_dict


class FHMailman(MBoxMailman):
    __tablename__ = 'fhmailman'
    id = Column('id', Integer, ForeignKey('mboxmailmen.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='fhmailman')

    regex = compile(r"""<td>(?P<month>\w*?) (?P<year>\d{4}):</td>.*?<A href="(?P<mbox>(?P=year)-(?P=month).txt.gz)".*?text (?P<size>\d.*?) (KB|bytes)""", re.I | re.S)

    @property
    def archive(self):
        return 'https://fedorahosted.org/pipermail/%s/' % self.name

    @property
    def listinfo(self):
        return 'https://fedorahosted.org/mailman/listinfo/%s/' % self.name

    def url(self, month):
        return self.archive + month

class FPMailman(MBoxMailman):
    __tablename__ = 'fpmailmen'
    id = Column('id', Integer, ForeignKey('mboxmailmen.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='fpmailman')

    regex = compile(r"""<td>(?P<month>\w*?) (?P<year>\d{4}):</td>.*?<A href="(?P<mbox>(?P=year)-(?P=month).txt.gz)".*?text (?P<size>\d.*?)(KB|bytes)""", re.I | re.S)

    @property
    def archive(self):
        return 'http://lists.fedoraproject.org/pipermail/%s/' % self.name

    @property
    def listinfo(self):
        return 'https://admin.fedoraproject.org/mailman/listinfo/%s' % self.name

    def url(self, month):
        return self.archive + month


class Source(Base):
    __tablename__ = 'sources'
    id         = Column('id', Integer, primary_key=True)
    type = Column('type', Text, nullable=False)
    cache_file = Column('cache_file', Text)
    cache_url  = Column('cache_url', Text)
    size       = Column('size', Integer)
    identifier = Column('identifier', Text)
    month      = Column('month', DateTime)
    stream_id  = Column('stream_id', Integer,
                        ForeignKey('streams.id'), index=True)
    stream     = relation(Stream, primaryjoin=stream_id==Stream.id,
                                 backref='sources', order_by=month)
    __mapper_args__ = dict(polymorphic_on = type, polymorphic_identity="source")

    @property
    def fact(self):
        return Fact

    @staticmethod
    def define_unique(d):
        Base.define_unique(d)
        d['identifier'] = True
        d['stream'] = True
        return d

    @property
    def cache_location(self):
        return join(self.stream.cache, self.cache_file)

    @property
    def cache_dir(self):
        return join(self.stream.cache, self.identifier)

    def needs_update(self, remote):
        return not (self.size == remote['size'])

    def cache_source(self, url):
        location = self.cache_location
        url_loc = ug.urlgrab(url, filename=location)

    def update(self, remote):
        self.cache_source(remote['cache_url'])


class MBoxSource(Source):
    __tablename__ = 'mbox_sources'
    id = Column('id', Integer, ForeignKey('sources.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='mbox_source')

    @property
    def fact(self):
        return MBoxFact

    def update(self, remote):
        self.cache_source(remote['cache_url'])

        mbox = self.mbox
        for email in iter_in_transaction(session, mbox):
            email = dict(email.items())
            try:
                email['message_id'] = email['Message-ID']
                email['sender'] = email['From']
                email['sender_domain'] = self.fact.domain_from_sender(email['sender'])
                email['source'] = self
                # sometimes these fields are blank, which is kinda ok, because it's a garbage message
                # but dateutil can't handle None, so we have to use this hack
                try:
                    email['date'] = dup.parse(email['Date'] or str(datetime.datetime.min)).replace(day=1)
                except ValueError:
                    print "TODO: Fix bad date parsing!"
                    email['date'] = datetime.datetime.min
                email['subject'] = email['Subject']
                self.fact.create_or_update(**email)
            except KeyError:
                continue

    #TODO: This needs to be abstracted a bit
    @property
    def mbox(self):
        with pwd(self.stream.cache):
            path_in = self.cache_file
            try:
                f_in = gzip.open(path_in, 'rb')
                path_out = path_in.replace('.gz', '')
                f_out = open(path_out, 'wb')
                f_out.writelines(f_in)
            except IOError, e:
                return mailbox.mbox(path_in)
            finally:
                f_out.close()
                f_in.close()
            return mailbox.mbox(path_out)


class RHMailmanSource(Source):
    __tablename__ = 'rhmailmainsources'
    id = Column('id', Integer, ForeignKey('sources.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='rhmailmansource')

    regex = compile(r'''<li><strong><a name="\d*" href="(?P<message>msg(?P<number>\d*).html)">.*?<em>(?P<name>.*?)</em>''', re.I | re.S)
    regex_from = compile(r'''<li><em>From</em>: (?P<from>.*?)</li>''', re.I)
    regex_date = compile(r'''<li><em>Date</em>: (?P<date>.*?)</li>''', re.I)
    regex_message_id = compile(r'''<!--X-Message-Id: (?P<message_id>.*?) -->''', re.I)
    regex_subject = compile(r'''<!--X-Subject: (?P<subject>.*?) -->''', re.I)

    def __init__(self, **keys):
        Source.__init__(self, **keys)
        try:
            makedirs(self.cache_dir)
        except OSError, e:
            print e

    @property
    def fact(self):
        return RHMailmanFact

    def update(self, remote):
        self.cache_source(remote['cache_url'])

        conn = URLGrabber(reget='check_timestamp',
                          user_agent='jemoeder/2.0',
                          prefix='http://www.redhat.com',
                          retry=0)

        month_page = codecs.open(self.cache_location, encoding='utf_8').read()
        matches = self.regex.finditer(month_page)
        emails = (match.groupdict() for match in matches)
        for email in emails:
            url = self.stream.archive + self.identifier + '/' + email['message']
            loc = join(self.stream.cache, self.identifier, email['message'])

            url_split = up.urlsplit(url)
            url_path = url_split.path
            print url_path
            email_data = conn.urlread(url_path)
            print len(email_data)
            with file(loc, 'w') as f:
                f.write(email_data)

#             url_loc = urlretrieve(url, loc)
#             email_data = htmlentitydecoder(codecs.open(loc, encoding='utf_8').read())

            try:
                email['sender'] = self.regex_from.search(email_data).group('from')
            except AttributeError:
                email['sender'] = 'nobody@example.com'
            email['date'] = self.regex_date.search(email_data).group('date')
            email['message_id'] = self.regex_message_id.search(email_data).group('message_id')
            email['subject'] = self.regex_subject.search(email_data).group('subject')
            email['source'] = self
            try:
                email['date'] = dup.parse(email['date'])
            except ValueError:
                print "TODO: Fix bad date parsing!"
                email['date'] = datetime.datetime.min
            self.fact.create_or_update(**email)



class Fact(Base):
    __tablename__ = 'facts'
    id         = Column('id', Integer, primary_key=True)
    type = Column('type', Text, nullable=False)
    sender_name = Column('sender_name', Text, index=True)
    sender_handle = Column('sender_handle', Text, index=True)
    sender     = Column('sender', Text, index=True)
    sender_domain = Column('sender_domain', Text, index=True)
    message_id = Column('message_id', Text, index=True)
    date       = Column('date', DateTime)
    subject    = Column('subject', Text)
    source_id  = Column('source_id', Integer,
                        ForeignKey('sources.id'), index=True)
    source     = relation(Source, primaryjoin=source_id==Source.id,
                                 backref='facts')
    __mapper_args__ = dict(polymorphic_on = type, polymorphic_identity="fact")

    @staticmethod
    def define_unique(d):
        Base.define_unique(d)
        d['sender'] = True
        d['message_id'] = True
        d['source'] = True
        return d

    def needs_update(self, remote):
        return False

    def update(self, remote):
        return None

    @classmethod
    def domain_from_sender(cls, sender):
        raise NotImplementedError


class MBoxFact(Fact):
    __tablename__ = 'mboxfacts'
    id = Column('id', Integer, ForeignKey('facts.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='mboxfact')

    domain_regex = re.compile(r'.*at (.*?) \(.*\)')

    @classmethod
    def domain_from_sender(cls, sender):
        return cls.domain_regex.findall(sender)[0]

class RHMailmanFact(Fact):
    __tablename__ = 'rhmailmanfacts'
    id = Column('id', Integer, ForeignKey('facts.id'), primary_key=True)
    __mapper_args__ = dict(polymorphic_identity='rhmailmanfact')

    domain_regex = re.compile(r"""(?P<name>[^<]*?)@(?P<domain>[^>]*)>?""")
    domain_regex2 = re.compile(r"""(?P<name>.*) at (?P<domain>\S*)""")

    @classmethod
    def domain_from_sender(cls, sender):
        try:
            return cls.domain_regex.search(sender).group('domain')
        except AttributeError, e:
            return cls.domain_regex2.search(sender).group('domain')


session = Session()

__all__ = ['Stream', 'FPMailman', 'FHMailman', 'RHMailman', 'Source',
           'Fact', 'session', 'Session', 'metadata', 'engine',
           'stream_classes', 'get_engine']
