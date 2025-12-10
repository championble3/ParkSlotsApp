import datetime
from datetime import time
import openrouteservice
from app.database.connection import get_park_data_orm
from app.database.db import SessionLocal
import os 

db = SessionLocal()
df, df_park_info, df_buildings_info = get_park_data_orm(db)

def get_time_car_park(park_id_list,user_lat,user_lng):

    duration_dict = {}

    for park_id in park_id_list:
        park_id = f'park_{park_id}'
        client = openrouteservice.Client(key=os.getenv('ORSKEY'))
        park_lng = df_park_info[df_park_info['park_id'] == park_id]['park_lng'].values[0]
        park_lat = df_park_info[df_park_info['park_id'] == park_id]['park_lat'].values[0]

        park_cords = (park_lng,park_lat)
        user_cords = (user_lng,user_lat)

        route = client.directions([park_cords,user_cords], profile='driving-car')
        duration = route['routes'][0]['summary']['duration'] / 60

        duration_dict[park_id] = duration

    return duration_dict

def get_time_park_building(park_id,building):

    client = openrouteservice.Client(key=os.getenv('ORSKEY'))
    park_lng = df_park_info[df_park_info['park_id'] == park_id]['park_lng'].values[0]
    park_lat = df_park_info[df_park_info['park_id'] == park_id]['park_lat'].values[0]

    building_lng = df_buildings_info[df_buildings_info['building_name'] == building]['building_lng'].values[0]
    building_lat = df_buildings_info[df_buildings_info['building_name'] == building]['building_lat'].values[0]

    park_cords = (park_lng,park_lat)
    building_cords = (building_lng,building_lat)

    route = client.directions([park_cords,building_cords], profile='foot-walking')
    duration = route['routes'][0]['summary']['duration'] / 60


    current_time = datetime.datetime.now().time()  

    if park_id == 'park_6':
        intervals_minus_2 = [
            (time(7, 15), time(7, 30)),
            (time(9,  0), time(9, 30)),
            (time(11, 0), time(11, 30)),
            (time(13, 0), time(13, 30)),
        ]

        in_interval = any(start <= current_time <= end for start, end in intervals_minus_2)

        if in_interval:
            duration -= 4
        else:
            duration -= 8


    return duration

def time_parsing(date_time_str: str) -> datetime.datetime:
    try:
        if date_time_str.endswith('Z'):
            return datetime.datetime.fromisoformat(date_time_str.replace("Z", "+00:00"))
        elif 'T' in date_time_str:
            return datetime.datetime.fromisoformat(date_time_str)
        else:
            return datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
    except ValueError as e:
        print(f"[ERROR] Nieprawidłowy format daty: {date_time_str}")
        raise e

    