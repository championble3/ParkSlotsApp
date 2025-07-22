import os
import pyodbc
import pandas as pd
import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, Base, read_parks, read_park_info, read_buildings_info

def get_park_data():
    load_dotenv()  # Load environment variables from .env file
    server = os.getenv('DB_SERVER', 'TOMASZ')
    database = os.getenv('DB_DATABASE', 'pwr_park_db')
    user = os.getenv('DB_USER', 'tomek')
    password = os.getenv('DB_PASSWORD', '063900')
    driver = 'ODBC Driver 17 for SQL Server'
    
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password}'
    
    conn = pyodbc.connect(connection_string)
    
    sql_query = f"""SELECT * FROM park_table"""
    sql_park_info_query = f"""SELECT * FROM park_info"""
    sql_buildings_info_query = f"""SELECT * FROM buildings"""
    df = pd.read_sql_query(sql_query,conn)
    df_park_info = pd.read_sql_query(sql_park_info_query,conn)
    df_buildings_info = pd.read_sql_query(sql_buildings_info_query,conn)
    df['time_park_extract'] = pd.to_datetime(df['time_park'], format='%H:%M')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.month
    df['Day'] = df['date'].dt.day
    df['Weekday'] = df['date'].dt.weekday
    df['Hour'] = df['time_park_extract'].dt.hour
    df['Minute'] = df['time_park_extract'].dt.minute
    df['datetime'] = df.apply(lambda row: datetime.datetime.combine(row['date'], row['time_park_extract'].time()), axis=1)
    conn.close()
    
    return df, df_park_info, df_buildings_info

df, df_park_info, df_buildings_info = get_park_data()
print(df_buildings_info['building_name'].head())

def get_park_data_orm(db: Session):
    parks = read_parks(db)
    park_info = read_park_info(db)
    buildings_info = read_buildings_info(db)

    # tu slowniki do df
    parks_dict = {
        'id': [park.id for park in parks ],
        'park_id': [park.park_id for park in parks],
        'date': [park.date for park in parks],
        'time_park': [park.time_park for park in parks],
        'park_slots': [park.park_slots for park in parks]
    }

    park_info_dict = {
        'park_id': [info.park_id for info in park_info],
        'park_name': [info.park_name for info in park_info],
        'park_lng': [info.park_lng for info in park_info],
        'park_lat': [info.park_lat for info in park_info],
        'park_total': [info.park_total for info in park_info]
    }

    buildings_info_dict = {
        'building_id': [info.building_id for info in buildings_info],
        'building_name': [info.building_name for info in buildings_info],
        'building_lng': [info.building_lng for info in buildings_info],
        'building_lat': [info.building_lat for info in buildings_info]
    }

    df_parks = pd.DataFrame(parks_dict)
    df_park_info = pd.DataFrame(park_info_dict)
    df_buildings_info = pd.DataFrame(buildings_info_dict)

    df_parks['time_park_extract'] = pd.to_datetime(df_parks['time_park'], format='%H:%M')
    df_parks['date'] = pd.to_datetime(df_parks['date'], format='%Y-%m-%d')
    df_parks['Year'] = df_parks['date'].dt.year
    df_parks['Month'] = df_parks['date'].dt.month
    df_parks['Day'] = df_parks['date'].dt.day
    df_parks['Weekday'] = df_parks['date'].dt.weekday
    df_parks['Hour'] = df_parks['time_park_extract'].dt.hour
    df_parks['Minute'] = df_parks['time_park_extract'].dt.minute
    df_parks['datetime'] = df_parks.apply(lambda row: datetime.datetime.combine(row['date'], row['time_park_extract'].time()), axis=1)
    
    return df_parks, df_park_info, df_buildings_info
