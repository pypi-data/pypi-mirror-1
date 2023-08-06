from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import mapper
from lamson import fsm
import datetime

metadata = MetaData()
fsm.default_table(metadata)
