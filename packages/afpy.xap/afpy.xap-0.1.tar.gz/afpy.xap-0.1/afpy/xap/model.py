import os
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from afpy.xap.settings import SQLURI

Base = declarative_base()

class IndexData(Base):
    __tablename__ = 'xap_index_data'
    docid = Column(String(100), primary_key=True)
    language_iso = Column(String(2))
    data = Column(TEXT())

class RemoveData(Base):
    __tablename__ = 'xap_remove_data'
    docid = Column(String(100), primary_key=True)

class Statistics(Base):
    __tablename__ = 'xap_statistics'
    query = Column(String(200), primary_key=True)
    count = Column(Integer)

metadata = Base.metadata
engine = create_engine(SQLURI)
#, convert_unicode=True)
metadata.create_all(engine)
Session = sessionmaker(bind=engine, autoflush=True, autocommit=False)

session = Session()


