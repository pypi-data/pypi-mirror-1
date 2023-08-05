"""
how should persistance work?  what's the real goal...

i want to be able to stop a release manager and restart it.
i want registrations to persist across restarts.
i want a clean way to interrogate remote sources for viability.
i MAY want to archive configs.
i MAY want to build history chains of installs.
"""

import sqlalchemy
from sqlalchemy.ext.sessioncontext import SessionContext
from sqlalchemy.ext.assignmapper import assign_mapper

import datetime

import cPickle as Pickle
import os

from releasemanager.config import KlassBuilder

class Persistence(object):
    def __init__(self, config, plugin_dir):
        self._config = config
        self._pluginPath = plugin_dir
        dburi = str(self._config.db_uri)
        db_type = str(self._config.db_type).lower()
        engine = sqlalchemy.create_engine(dburi, pool_recycle=3600)
        metadata = sqlalchemy.BoundMetaData(engine)
        self.ctx = SessionContext(sqlalchemy.create_session)
        self.session = self.ctx.current        
        # build history and registrations
        registrations = history = None
        if db_type == "mysql":
            from mysql_tables import make_tables
            registrations, history, transactions = make_tables(metadata)
        else:
            registrations, history, transactions = self.make_tables_from_plugin(db_type, metadata)

        assign_mapper(self.ctx, self.Registration, registrations)
        assign_mapper(self.ctx, self.Transaction, transactions)
        assign_mapper(self.ctx, self.History, history, properties=dict(
            transaction = sqlalchemy.relation(self.Transaction, lazy=False, private=False),
        ))


    class Registration(object):
        """registration object"""
        def load(self):
            real_data = Pickle.loads(str(self.data))
            return real_data
    
        def store(self, raw_data):
            data = Pickle.dumps(raw_data)
            self.data = data
    
    class History(object):
        """history object, has a child of transaction"""
        
    class Transaction(object):
        """transaction to be queried against"""
        
    
    
    @property
    def plugins(self):
        """cached so we don't build it till we need it"""
        if hasattr(self, "_plugins"):
            return self._plugins
        plugins = {}
        for f in os.listdir(self._pluginPath):
            if f.startswith("plugin_persist_"):
                p = KlassBuilder(f, self._pluginPath)(instantiate=True)
                plugins[str(p._config.db_type)] = p
        self._plugins = plugins
        return self._plugins
    
    
    def make_tables_from_plugin(self, db_type, metadata):
        registrations = history = None
        if db_type in self.plugins:
            registrations, history, transactions = self.plugins[db_type].make_tables(metadata)
        return (registrations, history, transactions)