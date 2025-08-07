import datetime
import openrouteservice
from app.database.connection import get_park_data_orm
from app.database.db import SessionLocal

db = SessionLocal()
df, df_park_info, df_buildings_info = get_park_data_orm(db)

def get_time_car_park_dummy(df):
    #dummy times
    car_park_times = {
        'car_park_4': 8,
        'car_park_2': 10,
        'car_park_5': 9,
        'car_park_6': 5,
        'car_park_7': 13
    }
    return car_park_times

def get_time_car_park():
    #dummy times
    car_park_times = {
        'car_park_4': 8,
        'car_park_2': 10,
        'car_park_5': 9,
        'car_park_6': 5,
        'car_park_7': 13
    }
    return car_park_times

def get_time_park_building(park_id,building):

    client = openrouteservice.Client(key='5b3ce3597851110001cf6248176f9a7b12e74f60aeefb8e62f29a9ea')
    park_lng = df_park_info[df_park_info['park_id'] == park_id]['park_lng'].values[0]
    park_lat = df_park_info[df_park_info['park_id'] == park_id]['park_lat'].values[0]

    building_lng = df_buildings_info[df_buildings_info['building_name'] == building]['building_lng'].values[0]
    building_lat = df_buildings_info[df_buildings_info['building_name'] == building]['building_lat'].values[0]

    park_cords = (park_lng,park_lat)
    building_cords = (building_lng,building_lat)

    route = client.directions([park_cords,building_cords], profile='foot-walking')
    duration = route['routes'][0]['summary']['duration'] / 60

    return duration

def time_parsing(date_time_str: str):
    try:
        if date_time_str.endswith('Z'):
            date_time_str = date_time_str[:-1]
            dt_object = datetime.datetime.fromisoformat(date_time_str)
            return dt_object
        else:
            dt_object = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            return dt_object
    except ValueError as e:
        print(f"[ERROR] Nieprawidłowy format daty: {date_time_str}")
        raise e

    