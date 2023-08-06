from pylons import config
from sqlalchemy import Column, MetaData, Table, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.orm import *

# Instantiate meta data manager.
metadata = MetaData()

# Instantiate ORM session manager.
Session = scoped_session(sessionmaker(
    autoflush=True,
    transactional=True,
    # bind=config['pylons.g'].sa_engine
))

def binddb():
    engine = config['pylons.g'].sa_engine
    metadata.bind = engine
    Session.bind = engine
