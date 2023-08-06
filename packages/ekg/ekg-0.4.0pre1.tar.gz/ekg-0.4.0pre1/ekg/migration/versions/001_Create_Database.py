from sqlalchemy import *
from migrate import *

meta = MetaData(migrate_engine)

mbox_sources = Table('mbox_sources', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

mailmen = Table('mailmen', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

mboxfacts = Table('mboxfacts', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

mboxmailmen = Table('mboxmailmen', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

fpmailmen = Table('fpmailmen', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

sources = Table('sources', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
  Column('type', Text(length=None, convert_unicode=False, assert_unicode=None),  nullable=False),
  Column('cache_file', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('cache_url', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('size', Integer()),
  Column('identifier', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('month', DateTime(timezone=False)),
  Column('stream_id', Integer()),
)

fhmailman = Table('fhmailman', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

facts = Table('facts', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
  Column('type', Text(length=None, convert_unicode=False, assert_unicode=None),  nullable=False),
  Column('sender_name', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('sender_handle', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('sender', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('sender_domain', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('message_id', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('date', DateTime(timezone=False)),
  Column('subject', Text(length=None, convert_unicode=False, assert_unicode=None)),
  Column('source_id', Integer()),
)

streams = Table('streams', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
  Column('type', Text(length=None, convert_unicode=False, assert_unicode=None),  nullable=False),
  Column('name', Text(length=None, convert_unicode=False, assert_unicode=None)),
)

rhmailmainsources = Table('rhmailmainsources', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

rhmailmen = Table('rhmailmen', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)

rhmailmanfacts = Table('rhmailmanfacts', meta,
  Column('id', Integer(),  primary_key=True, nullable=False),
)


def upgrade():
    meta.create_all(migrate_engine)

def downgrade():
    meta.drop_all(migrate_engine)
