import os
from dotenv import load_dotenv

def load_environment():
    """Loads environment variables from .env file"""
    load_dotenv()

def get_db_url(db_config: dict) -> str:
    """Helper to construct SQL Alchemy DB URL from config"""
    import urllib.parse
    
    user = urllib.parse.quote_plus(db_config['username'])
    password = urllib.parse.quote_plus(db_config['password'])
    host = db_config['host']
    port = db_config['port']
    db_name = db_config['database']

    if db_config['db_type'] == 'mysql':
        return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    else:
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
