from pylons.database import create_engine

import elixir

metadata = elixir.metadata
objectstore = elixir.objectstore
context = objectstore.context

def connect(dburi=None, echo = None, setup = True):
    """
    Connects engine to metadata 
    """
    metadata.connect(create_engine(dburi, echo))
    if setup : elixir.setup_all()

def resync():
    """
    Renews SQLAlchemy session with current thread
    """
    del context.current

def flush_all():
    """
    Flushes all changes to database
    """
    objectstore.flush()

def execute(query):
    """
    Executes a single query
    """
    return metadata.engine.text(query).execute()

def create_all(*args, **kw):
    """
    Shortcut for metadata.create_all()
    """
    metadata.create_all(*args, **kw)

def drop_all(*args, **kw):
    """
    Shortcut for metadata.drop_all()
    """
    metadata.drop_all(*args, **kw)

meta = metadata

# Uncomment these lines if you want to use the "autoload" option with your Elixir models
#if not metadata.is_bound():
#    elixir.delay_setup = True

__all__ = ['metadata', 'meta', 'objectstore', 'context', 'create_all','drop_all', 
           'connect', 'resync', 'flush_all', 'execute', 'create_engine']