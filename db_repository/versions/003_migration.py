from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
drugs = Table('drugs', pre_meta,
    Column('drug_id', INTEGER, primary_key=True, nullable=False),
    Column('ndc', VARCHAR(length=11)),
    Column('p_name', VARCHAR(length=64)),
    Column('s_name', VARCHAR(length=64)),
    Column('unit', VARCHAR(length=64)),
    Column('otc', VARCHAR(length=12)),
    Column('b_or_g', VARCHAR(length=12)),
    Column('company_id', INTEGER),
    Column('package', VARCHAR(length=64)),
    Column('description', VARCHAR(length=128)),
    Column('earliest_price', FLOAT),
    Column('curr_price', FLOAT),
)

companies = Table('companies', pre_meta,
    Column('company_id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=64)),
    Column('drug_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['drugs'].columns['curr_price'].drop()
    pre_meta.tables['drugs'].columns['earliest_price'].drop()
    pre_meta.tables['companies'].columns['drug_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['drugs'].columns['curr_price'].create()
    pre_meta.tables['drugs'].columns['earliest_price'].create()
    pre_meta.tables['companies'].columns['drug_id'].create()
