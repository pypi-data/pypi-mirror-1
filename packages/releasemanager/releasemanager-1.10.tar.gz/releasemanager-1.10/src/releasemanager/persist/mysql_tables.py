from sqlalchemy import *

def make_tables(metadata):
    registrations = Table('registrations', metadata,
        Column('id', Integer, primary_key=True), 
        Column('type', String(128), nullable=False),
        Column('location', String(64), nullable=False),
        Column('data', BLOB, nullable=False),
        Column('registered_at', DateTime, nullable=False),
    )
  
    history = Table('history', metadata,
        Column('id', Integer, primary_key=True),
        Column('transaction_id', Integer, ForeignKey("transactions.id"), nullable=False),
        Column('action', String(128), nullable=False),
        Column('project', String(255), nullable=False),
        Column('success', Boolean, nullable=False),
        Column('message', String(255), nullable=False),
        Column('username', String(128), nullable=False),
        Column('occurred', DateTime, nullable=False)
    )
    
    transactions = Table('transactions', metadata,
        Column('id', Integer, primary_key=True),
        Column('status', String(32), nullable=False),
        Column('started_at', DateTime),
        Column('completed_at', DateTime),
    )    
    
    return (registrations, history, transactions)