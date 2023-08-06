from lamson import server
import datetime
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import mapper


def configure_fsm_table():
    url = 'sqlite:///tests/test.db'
    metadata = MetaData()

    db = server.Database(metadata, url)
    db.configure()
    db.create()

    return db.session()

session = configure_fsm_table()
