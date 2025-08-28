import pandas as pd
import datetime
from app.services.model_prediction import predict_slots
from app.services.time_functions import get_time_car_park, get_time_park_building
from app.database.connection import get_park_data_orm
from app.database.db import get_db
from sqlalchemy.orm import Session
from app.services.time_functions import time_parsing
import json 
import requests
import numpy as np

db_gen = get_db()
db = next(db_gen)
try:
    df, df_park_info, df_buildings_info = get_park_data_orm(db)
finally:
    db_gen.close()

def park_slots_now_func():
    url = 'https://iparking.pwr.edu.pl/modules/iparking/scripts/ipk_operations.php'

    headers = {
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://iparking.pwr.edu.pl/"
    }

    payload_info  = {
            "o": "get_parks",
            "i": 2
        }
    try:
        response_info = requests.post(url, headers=headers, data=json.dumps(payload_info))
        response_data_info = response_info.json()

        park_ids = [int(response_data_info['places'][id]['parking_id']) for id in range(len(response_data_info['places']))]
        slots = []

        for loop_id in range(len(response_data_info['places'])):
            response_data_info['places'][loop_id]['liczba_miejsc']
            slots.append(response_data_info['places'][loop_id]['liczba_miejsc'])

        return park_ids,slots
    except Exception as e:
        print('Issue with connecting to the API:',e)
        return [],[]

park_ids, slots_now = park_slots_now_func()

def get_df_results(input_date: str):
    input_date_dt = time_parsing(input_date)
    #input_date_dt = datetime.datetime.strptime(input_date, "%Y-%m-%d %H:%M")
    
    df_result = []

    for park_id in park_ids:
        row = {
            'park_id': park_id,
            'Year': input_date_dt.year,
            'Month': input_date_dt.month,
            'Day': input_date_dt.day,
            'Weekday': input_date_dt.weekday(),
            'Hour': input_date_dt.hour,
            'Minute': input_date_dt.minute
        }
        df_result.append(row)

    df_results = pd.DataFrame(df_result)
    print(df_results)
    return df_results

def get_park_prediction(df_results):
    parking_prediction_dict = {}

    for num in range(len(df_results)):
        df_results.drop
        output = predict_slots(df_results.iloc[num])
        park_name = f"park_{int(df_results.iloc[num]['park_id'])}"
        parking_prediction_dict[park_name] = output
    return parking_prediction_dict

def park_recommendation(first_building, last_building, df_results, user_lat, user_lng, request_time: str):
    print(park_ids)
    time_car_park = get_time_car_park(park_ids, user_lat, user_lng)

    park_slots_now_dict = {}
    park_slots_now = slots_now

    # Bazowy czas startowy (czas zapytania)
    base_dt = time_parsing(request_time)

    if park_slots_now == []:
        parkings = df_park_info['park_id'].values.tolist()
        park_slots_pred = get_park_prediction(df_results)
        print('park slots predicted:', park_slots_pred)
        alfa = 10
        beta = 30
        equation_dict = {}

        for park_id in parkings:
            totals = df_park_info[df_park_info['park_id'] == park_id]['park_total'].values

            time_park_building = get_time_park_building(park_id, first_building)
            time_building_park = get_time_park_building(park_id, last_building)
            car_park_time = time_car_park[park_id]

            arrival_dt = base_dt + datetime.timedelta(minutes=car_park_time)
            df_results_pred = get_df_results(arrival_dt.isoformat())
            park_slots_available_pred = get_park_prediction(df_results_pred)[park_id]

            r = car_park_time / ((park_slots_available_pred / totals[0]) * beta + 1)
            if park_slots_available_pred > 0:
                equation = time_park_building + time_building_park + car_park_time + (alfa * r)
                equation_dict[park_id] = equation

        print(equation_dict)
        print('Only recommendation used, no live slots')
        return min(equation_dict, key=equation_dict.get)

    else:
        for id, park_slot_now_loop in zip(park_ids, park_slots_now):
            park_slots_now_dict[id] = park_slot_now_loop

        equation_dict = {}
        parkings = df_park_info['park_id'].values.tolist()
        alfa = 10
        beta = 30
        
        for park_id in parkings:
            totals = df_park_info[df_park_info['park_id'] == park_id]['park_total'].values

            time_park_building = get_time_park_building(park_id, first_building)
            time_building_park = get_time_park_building(park_id, last_building)
            car_park_time = time_car_park[park_id]

            arrival_dt = base_dt + datetime.timedelta(minutes=car_park_time)
            df_results_pred = get_df_results(arrival_dt.isoformat())
            park_slots_available_pred = get_park_prediction(df_results_pred)[park_id]

            park_slots_available = int(park_slots_now_dict[int(park_id.split('_')[1])])
            print('park slots pred:',park_slots_available_pred)
            print('park slots now:',park_slots_available)
            gamma = np.exp(car_park_time * (-0.1))
            a_eff = gamma * park_slots_available + (1 - gamma) * park_slots_available_pred

            r = car_park_time / ((a_eff / totals[0]) * beta + 1)
            if a_eff > 0:
                equation = time_park_building + time_building_park + car_park_time + (alfa * r)
                equation_dict[park_id] = equation

        print(equation_dict)
        print('Live slots used with recommendation')
        return min(equation_dict, key=equation_dict.get)



