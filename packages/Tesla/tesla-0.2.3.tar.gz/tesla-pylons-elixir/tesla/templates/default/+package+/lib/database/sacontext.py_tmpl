"""An organizer for SQLAlchemy applications with optional Pylons support.

STATUS 2007/07/02:
  - SAContext 0.2.1 is current version.
  - SAContext passes test suite (test_sacontext.py).
  - PylonsSAContext.parse_engine_poptions passes test suite.
  - PylonsSAContext needs testing in Pylons applications.
  - Constructor args and .add_engine args are tentative and subject to change.
  - The strategies may be refactored or removed.

SAContext is basically a container for your engines, metadatas, and sessions.
It helps build applications quickly and avoids common mistakes.  It supports
multiple databases within one application but may not be suitable for highly
complex applications that switch between entire sets of engines at various
times.  We're doing further research to determine the limits of SAContext's
scalability.  

See the class and module docstrings for usage.  A test suite is available as a
companion module (test_sacontext.py).

SAContext home page:  http://sluggo.scrapping.cc/python/

Copyright (c) 2007 by Mike Orr <sluggoster@gmail.com> and Michael Bayer
<mike_mp@zzzcomputing.com>.  Permission to copy & modify granted under the MIT
license (http://opensource.org/licenses/mit-license.php).

CHANGELOG
=========
* 0.2.1 MO
  - Change imports for forward compatibility with SQLAlchemy 0.4.
  - .session_context is now a public attribute.
  - 'dburi' in a Pylons config file is now 'uri': sqlalchemy.default.uri.
  - Fix variable names in .get_engine and .bind_table.
  - Several of these are thanks to Waldemar Osuch's patch.

* 0.2.0 MO
  - Add 'config' argument to PylonsSAContext.__init__ & .add_engine.
  - Fix variable name in PylonsSAContext.__init.

* 0.1.0 (2007-06-??) MO
  - Initial unstable release.
"""

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import create_session
from sqlalchemy.ext.sessioncontext import SessionContext

DEFAULT = "default"  # Default engine key.

def asbool(obj):
    """Borrowed from PasteDeploy-1.3/paste/deploy/converters.py
       (c) 2005 by Ian Bicking, MIT license.
    """
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)

def merge(*dicts):
    """Merge several dicts into one.  Key collisions are resolved in favor of
       the left most dict.  `None` arguments are allowed and ignored.
    """
    ret = {}
    for dic in reversed(dicts):
        if dic:
            ret.update(dic)
    return ret

          
#### SAContext class for any application ####
class SAContext(object):
    """I organize a SQLAlchemy application's database engines, metadatas, and
       sessions under one convenient object.

       Usage::

            # Connect to an engine.  The URI is mandatory but should be a 
            # keyword arg.
            sac = SAContext(uri="sqlite://")    # A SQLite memory database.
            
            # Or pass additional engine options.
            sac = SAContext(uri="mysql://...", engine_options={"echo": True})

            # The metadata for this engine has automatically been created.
            users = Table("Users", sac.metadata, Column(...))

            # Or reflect the columns from an existing database table.
            users = Table("Users", sac.metadata, autoload=True)

            # ORM operations are managed by a hidden SessionContext that
            # automatically exposes a thread-specific session.
            sac.session.flush()

            # 'sac.query' is a shortcut for 'sac.session.query'.
            # (Use .list() instead of .all() in SQLALchemy < 0.3.9.)
            records = sac.query(User).filter_by(...).all()

            # Mappers can use the SessionContext extension this way.
            # Note: the extension is optional, not required.
            mapper(User, users, extension=sac.ext)

            # You can connect to multiple databases.
            sac.add_engine(key="logs", uri="mysql://...")

            # Each engine has its own bound metadata.
            access_log = Table("Access", sac.get_metadata("logs"), ...)

            # To access a non-default engine, do this.
            sac.get_engine("logs").echo = True

            # If you're using assign_mapper you'll need the session context.
            assign_mapper(sac.session_context, ...)
    """

    def __init__(self, uri, engine_options=None, strategy=None): 
        """Create an SAContext.

           uri: string: a SQLAlchemy database URI.
           engine_options: dict: extra args for sqlalchemy.create_engine().
           strategy: a strategy instance, or None for the default strategy.
               Strategies currently available are BoundMetaDataStrategy
               (default) and BoundSessionStrategy.
        """
        self._engines = {}
        self._metadatas = {}
        if strategy is None:
            self._strategy = BoundMetaDataStrategy()
        else:
            self._strategy = strategy
        self.session_context = SessionContext(
            lambda: self._strategy.create_session(self),
            self._get_session_scope)
        self.add_engine(DEFAULT, uri=uri, engine_options=engine_options)

    def add_engine(self, key, uri, engine_options=None):
        if engine_options is None:
            engine_options = {}
        engine = create_engine(uri, **engine_options)
        self._engines[key] = engine
        self._metadatas[key] = self._strategy.create_metadata(key, self)

    def get_connectable(self, key=DEFAULT):
        return self._strategy.get_connectable(key, self)

    def get_engine(self, key=DEFAULT):
        return self._engines[key]

    def get_metadata(self, key=DEFAULT):
        return self._metadatas[key]

    #### Properties
    @property
    def engine(self):
        return self._engines[DEFAULT]

    @property
    def metadata(self):
        return self._metadatas[DEFAULT]
    
    meta = metadata

    @property
    def connectable(self):
        return self.get_connectable()
    
    @property
    def ext(self):
        return self.session_context.mapper_extension

    @property
    def session(self):
        return self.session_context.current

    @property
    def query(self):
        return self.session_context.current.query

    #### Private methods
    def _get_session_scope(self):
        return None


#### PylonsSAContext class for Pylons applications ####
class PylonsSAContext(SAContext):
    """I'm a subclass of SAContext that can read engine options from a
       Pylons config dict.
    """

    def __init__(self, uri=None, engine_options=None, 
        engine_defaults=None, strategy=None, config_key=DEFAULT, config=None):
        if not uri:
            uri, engine_options = self.get_engine_options(
                config_key=config_key,
                override=engine_options, defaults=engine_defaults, 
                config=config)
        SAContext.__init__(self, uri=uri, engine_options=engine_options,
            strategy=strategy)

    def add_engine(self, key, uri=None, engine_options=None,
        engine_defaults=None, config_key=DEFAULT, config=None):
        """Add a database engine named `key`.

           If a URI is specified, add an engine based on it and
           `engine_options`.  The other arguments are ignored.

           If `uri` is not specified, add an engine based on the 'config' dict
           or the current Pylons configuration.  See `.parse_engine_options()`
           for details.

           'engine_options' and 'engine_defaults' are dicts of keyword
           arguments for sqlalchemy.create_engine().  The values are passed
           as-is without type conversion.  The difference between the two args
           is the Pylons configuration overrides 'engine_defaults', but
           'engine_options' overrides the Pylons configuration.
        """
        if not uri:
            uri, engine_options = self.get_engine_options(key=config_key,
                override=engine_options, defaults=engine_defaults,
                config=config)
        SAContext.add_engine(self, key, uri, engine_options=engine_options)

    def get_engine_options(self, config_key=DEFAULT, override=None, 
        defaults=None, config=None):
        """Called by .__init__ and .add_engine."""
        if config is None:
            config = self.get_app_config()
        uri, options = self.parse_engine_options(config, config_key)
        if not uri:
            full_key = "sqlalchemy.%s.uri" % config_key
            raise KeyError("no '%s' variable in config file" % full_key)
        engine_options = merge(override, options, defaults)
        return uri, engine_options

    @staticmethod
    def get_app_config():
        """Get the Pylons 'app_conf' dict for the currently-running application.

           This is a static method so it can be called standalone.
        """
        import pylons.config as config
        if not hasattr(config, "__getitem__"):  # Pylons 0.9.5
            from paste.deploy import CONFIG as config
        return config

    @staticmethod
    def parse_engine_options(config, config_key=DEFAULT):
        """Parse the database URI and engine options from a dict that's 
           equivalent to Pylons 'app_config'.  
           
           Returns a tuple:
               [0] string: the database URI, or None if not found.
               [1] dict: keyword arguments for sqlalchemy.create_engine().
                   Values that are known to be boolean/int based on the
                   SQLAlchemy manual are converted to the appropriate types.

           For example, say your Pylons .ini file looks like this:

               [app_conf]
               sqlalchemy.default.uri = sqlite:////tmp/mydb.sqlite
               sqlalchemy.default.echo = false
               sqlalchemy.default.pool_recycle = 3600
               sqlalchemy.database2.uri = mysql://user:pw@example.com/mydb

           Assume `config` is a dict corresponding to the above .ini file.
           Calling `self.parse_engine_options(config)` returns::

               ("sqlite:///tmp/mydb.sqlite", {
                   "echo": False, 
                   "pool_recycle": 3600})

           Calling `self.parse_engine_options(config, "database2")` returns::

               ("mysql://usr:pw/example.com/mydb", {})

           Calling `self.parse_engine_options(config, "MISSING")` returns::

                (None, {})

           This is a static method so it can be called standalone.
        """
        prefix = "sqlalchemy.%s." % config_key
        prefix_len = len(prefix)
        uri = None
        options = {}
        for full_key in config.iterkeys():
            if not full_key.startswith(prefix):
                continue
            value = config[full_key]
            option = full_key[prefix_len:]
            if option in BOOL_OPTIONS:
                value = asbool(value)
            elif option in INT_OPTIONS:
                try:
                    value = int(value)
                except ValueError:
                    reason = "config variable '%s' is non-numeric"
                    raise KeyError(reason % full_key)
            if option == "uri":
                uri = value
            else:
                options[option] = value
        return uri, options

    #### Private methods
    def _get_session_scope(self):
        """Return the id keying the current database session's scope.

        The session is particular to the current Pylons application -- this
        returns an id generated from the current thread and the current Pylons
        application's Globals object at pylons.g (if one is registered).

        Copied from pylons.database in Pylons 0.9.5.
        """
        import thread
        import pylons
        try:
            app_scope_id = str(id(pylons.g._current_obj()))
        except TypeError:
            app_scope_id = ''
        return '%s|%i' % (app_scope_id, thread.get_ident())


BOOL_OPTIONS = set([
    "convert_unicode",
    "echo",
    "echo_pool",
    "threaded",
    "use_ansi",
    "use_oids",
    ])

INT_OPTIONS = set([
    "max_overflow",
    "pool_size",
    "pool_recycle",
    "pool_timeout",
    ])



#### Private strategy classes ####        
class ContextualStrategy(object):
    """Abstract base class."""

    def create_session(self, context):
        raise NotImplementedError("subclass responsibility")

    def create_metadata(self, key, context):
        raise NotImplementedError("subclass responsibility")

    def get_connectable(self, key, context):
        raise NotImplementedError("subclass responsibility")

class BoundMetaDataStrategy(ContextualStrategy):
    """A strategy that binds the engine to the metadata.  This is the
       simplest strategy and the default, and is recommended for most
       purposes.
    """
    def create_session(self, context):
        return create_session()

    def create_metadata(self, key, context):
        return MetaData(engine=context.get_engine(key))

    def get_connectable(self, key, context):
        return context.get_engine(key)

class BoundSessionStrategy(ContextualStrategy):
    """A strategy that binds the engine to the session.  If you don't know
       what that means, you don't want this.

       TODO: document further.
    """

    def __init__(self, connectionbound=False, binds=None):
        """
           connectionbound: bool: ???
           binds: list of SQLAlchemy tables and mappers: ??? 
        """
        self.binds = []
        if binds is not None:
            for key in binds:
                if isinstance(key, Table):
                    self.bind_table(key, binds[key])
                else:
                    self.bind_mapper(key, binds[key])

        self.connectionbound = connectionbound

    def bind_mapper(self, mapper, engine_key):
        """Private method called by .__init__."""
        self.binds.append('bind_mapper', mapper, engine_key)

    def bind_table(self, table, engine_key):
        """Private method called by .__init__."""
        self.binds.append('bind_table', table, engine_key)

    def create_session(self, context):
        if self.connectionbound:
            bind_to = context.get_engine().connect()
        else:
            bind_to = context.get_engine()
        session = create_session(bind_to=bind_to)

        # set up mapper/table -specific binds
        # TODO: in the case of "connectionbound", 
        # need to organize the connections here so that one 
        # connection per engine key
        for bind_func, source, engine_key in self.binds:
            bindto = context.get_engine(engine_key)
            if self.connectionbound:
                bindto = bindto.connect()
            getattr(session, bind_func)(source, bindto)
        return session

    def create_metadata(self, key, context):
        return MetaData()

    def get_connectable(self, key, context):
        # TODO: get "key" in here somehow, needs additional state stored
        # in order to get correct "bind" from the Session
        return context.session.bind_to
