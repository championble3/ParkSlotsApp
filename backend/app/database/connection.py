import os
import pyodbc
import pandas as pd
import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, Base, read_parks, read_park_info, read_buildings_info

def get_park_data_orm(db: Session):
    parks = read_parks(db)
    park_info = read_park_info(db)
    buildings_info = read_buildings_info(db)

    # here are df dicts
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
