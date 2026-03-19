from os import path
from models.base import Base
from database.session_manager import engine
from models import user, expense, budget, category

connection_options ={
    "schema_translate_map" :  {"finbot":None}
}

def create_db():
    """Database creation method check if the db file exists and creates if not"""
    Base.metadata.create_all(engine.execution_options(**connection_options))

