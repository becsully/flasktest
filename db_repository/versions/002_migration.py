from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
basic = Table('basic', pre_meta,
    Column('drug_id', INTEGER, primary_key=True, nullable=False),
    Column('ndc', VARCHAR(length=11)),
    Column('p_name', VARCHAR(length=64)),
    Column('company', VARCHAR(length=64)),
)

companies = Table('companies', post_meta,
    Column('company_id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
    Column('drug_id', Integer),
)

drugs = Table('drugs', post_meta,
    Column('drug_id', Integer, primary_key=True, nullable=False),
    Column('ndc', String(length=11)),
    Column('p_name', String(length=64)),
    Column('s_name', String(length=64)),
    Column('unit', String(length=64)),
    Column('otc', String(length=12)),
    Column('b_or_g', String(length=12)),
    Column('company_id', Integer),
    Column('package', String(length=64)),
    Column('description', String(length=128)),
    Column('earliest_price', Float),
    Column('curr_price', Float),
)

prices = Table('prices', post_meta,
    Column('price_id', Integer, primary_key=True, nullable=False),
    Column('drug_id', Integer),
    Column('price', Float),
    Column('start_date', Date),
    Column('end_date', Date),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['basic'].drop()
    post_meta.tables['companies'].create()
    post_meta.tables['drugs'].create()
    post_meta.tables['prices'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['basic'].create()
    post_meta.tables['companies'].drop()
    post_meta.tables['drugs'].drop()
    post_meta.tables['prices'].drop()
