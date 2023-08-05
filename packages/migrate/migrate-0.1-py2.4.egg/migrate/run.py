"""Each migration script must import everything in this file."""
from sqlalchemy import *
from migrate.changeset import *
from migrate.versioning import logengine

__all__=[
    'engine',
]

engine = create_engine(None,strategy='logsql')
