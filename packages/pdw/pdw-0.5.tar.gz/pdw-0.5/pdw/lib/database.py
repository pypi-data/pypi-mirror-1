from pylons.database import create_engine

import elixir

metadata = elixir.metadata
objectstore = elixir.objectstore
session_context = objectstore.context
engine = None

def connect(dburi=None, echo = None):
    """
    Connects engine to metadata 
    """
    global engine
    engine = create_engine(dburi, echo)
    metadata.connect(engine)
    # do not want to call this every time we start up and connect as tables may
    # already exist
    # elixir.setup_all()

def resync():
    """
    Renews SQLAlchemy session with current thread
    """
    del session_context.current

def flush_all():
    """
    Flushes all changes to database
    """
    objectstore.flush()

# Uncomment these lines if you want to use the "autoload" option with your Elixir models
#if not metadata.is_bound():
#    elixir.delay_setup = True

__all__ = ['metadata', 'objectstore', 'session_context', 'engine', 'connect', 'resync', 'flush_all']
