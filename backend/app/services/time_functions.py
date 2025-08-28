import datetime
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
    #dummy times
    # car_park_times = {
    #     'car_park_4': 8,
    #     'car_park_2': 10,
    #     'car_park_5': 9,
    #     'car_park_6': 5,
    #     'car_park_7': 18
    # }
    # return car_park_times

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

    