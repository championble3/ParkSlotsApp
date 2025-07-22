from sqlalchemy import create_engine,Column, Integer, String, Date, Time, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os 
from dotenv import load_dotenv
import urllib

load_dotenv()

server = os.getenv('DB_SERVER', 'TOMASZ')
database = os.getenv('DB_DATABASE', 'pwr_park_db')  
user = os.getenv('DB_USER', 'tomek')
password = os.getenv('DB_PASSWORD', '063900')
driver = 'ODBC Driver 17 for SQL Server'

params = urllib.parse.quote_plus(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password}')

DATABASEURL = f'mssql+pyodbc:///?odbc_connect={params}'

engine = create_engine(DATABASEURL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():   
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ParkTable(Base):
    __tablename__ = 'park_table'
    __table_args__ = {'schema': 'dbo'}    
    id = Column(Integer, primary_key=True)
    park_id = Column(Integer)
    date = Column(Date)
    time_park = Column(String)
    park_slots = Column(Integer)

class ParkInfo(Base):
    __tablename__ = 'park_info'
    __table_args__ = {'schema': 'dbo'}

    park_id = Column(Integer, primary_key=True)
    park_name = Column(String)
    park_lng = Column(Float)
    park_lat = Column(Float)
    park_total = Column(Integer)

class BuildingsInfo(Base):
    __tablename__ = 'buildings'
    __table_args__ = {'schema': 'dbo'}
    
    building_id = Column(Integer, primary_key=True)
    building_name = Column(String)
    building_lng = Column(Float)
    building_lat = Column(Float)

def read_parks(db: Session):
    return db.query(ParkTable).all()

def read_park_info(db: Session):
    return db.query(ParkInfo).all()

def read_buildings_info(db: Session):
    return db.query(BuildingsInfo).all()

