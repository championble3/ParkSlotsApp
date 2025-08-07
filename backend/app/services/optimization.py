import pandas as pd
import datetime
from app.services.model_prediction import predict_slots
from app.services.time_functions import get_time_car_park, get_time_park_building
from app.database.connection import get_park_data_orm
from app.database.db import get_db
from sqlalchemy.orm import Session
from app.services.time_functions import time_parsing

db_gen = get_db()
db = next(db_gen)
try:
    df, df_park_info, df_buildings_info = get_park_data_orm(db)
finally:
    db_gen.close()

def get_df_results(input_date: str):
    input_date_dt = time_parsing(input_date)
    print('First input', input_date)
    print("Input string:", input_date_dt)
    #input_date_dt = datetime.datetime.strptime(input_date, "%Y-%m-%d %H:%M")
    park_ids = [4, 2, 5, 6, 7]
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

def park_recommendation(first_building,last_building,df_results):

    time_car_park = get_time_car_park()
    
    equation_dict = {}
    parkings = df_park_info['park_id'].values.tolist()
    park_slots = get_park_prediction(df_results)
 
    alfa = 10 
    beta = 30
    for park_id in parkings:

        totals = df_park_info[df_park_info['park_id'] == park_id]['park_total'].values

        time_park_building = get_time_park_building(park_id,first_building)
        time_building_park = get_time_park_building(park_id,last_building)
        car_park_time = time_car_park[f"car_{park_id}"]
        park_slots_available = park_slots[f"{park_id}"]
        print(f"Car park : {park_id}")
        print(park_slots_available)

        r = car_park_time/((park_slots_available/totals[0])*beta + 1)
        if park_slots_available > 0:
            equation = time_park_building + time_building_park + car_park_time + (alfa * r)
            equation_dict[park_id] = equation

    return min(equation_dict, key=equation_dict.get)

first_building = 'D1'
last_building = 'C3'
df_results = get_df_results('2025-06-17 07:50')
print(df_results.shape)
equation_dict = park_recommendation(first_building, last_building, df_results)
print(equation_dict)
print(f'Best park:{equation_dict}')
