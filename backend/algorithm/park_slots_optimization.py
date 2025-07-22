import pandas as pd
import pyodbc
import torch 
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import random
import numpy as np
import joblib
import datetime
import openrouteservice
import os 
from dotenv import load_dotenv

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

df['time_park_extract'] = pd.to_datetime(df['time_park'], format='%H:%M')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df['Year'] = df['date'].dt.year
df['Month'] = df['date'].dt.month
df['Day'] = df['date'].dt.day
df['Weekday'] = df['date'].dt.weekday
df['Hour'] = df['time_park_extract'].dt.hour
df['Minute'] = df['time_park_extract'].dt.minute
df['datetime'] = df.apply(lambda row: datetime.datetime.combine(row['date'], row['time_park_extract'].time()), axis=1)

# ---------- PREDICTION MODEL ----------

class RegressionModel(nn.Module):
    def __init__(self, input_size):
        super(RegressionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.fc2 = nn.Linear(32, 8)
        self.fc3 = nn.Linear(8, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x) 
        return x

model = RegressionModel(input_size=7)
model.load_state_dict(torch.load('park_slots_pred_model.pth'))
model.eval()
x_scaler = joblib.load('x_scaler.pkl')
y_scaler = joblib.load('y_scaler.pkl')

def predict_slots(single_input_row):
    input_array = np.array(single_input_row).reshape(1, -1).astype('float32')
    input_scaled = x_scaler.transform(input_array)
    input_tensor = torch.tensor(input_scaled, dtype=torch.float32)

    with torch.no_grad():
        model.eval()
        prediction = model(input_tensor)
    prediction_unscaled = y_scaler.inverse_transform(prediction.numpy())
    value = int(round(prediction_unscaled[0][0]))
    return value if value >= 0 else 0

# ---------- HERE WILL BE THE DATE FROM APP -----------
input_date = datetime.datetime(2025, 6, 17, 7, 50)
input_date = input_date.strftime("%Y-%m-%d %H:%M")
df_results = df[df['datetime'].dt.strftime("%Y-%m-%d %H:%M") == input_date][['park_id','Year','Month','Day','Weekday','Hour','Minute']]

def get_park_prediction(df_results):
    parking_prediction_dict = {}

    for num in range(len(df_results)):
        df_results.drop
        output = predict_slots(df_results.iloc[num])
        park_name = f"park_{int(df_results.iloc[num]['park_id'])}"
        parking_prediction_dict[park_name] = output
    return parking_prediction_dict

# ---------- TIME FUNCTIONS -----------

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

# ---------- OPTIMIZATION FUNCTION -----------  

def get_park_optimization(first_building, last_building, df_results):

    equation_dict = {}
    parks = df_park_info['park_id'].values.tolist()
    car_park_times = get_time_car_park()
    park_slots = get_park_prediction(df_results)
    
    alfa = 10 
    beta = 30
    for park in parks:
        totals = df_park_info[df_park_info['park_id'] == park]['park_total'].values

        park_building_times = get_time_park_building(park,first_building)
        building_park_times = get_time_park_building(park,last_building)
        print(car_park_times.head())
        car_park_time = car_park_times[f"car_{park}"]
        park_slots_available = park_slots[f"{park}"]
        print(f"Car park : {park}")
        print(park_slots_available)
        r = car_park_time/((park_slots_available/totals[0])*beta + 1)# risk score
        if park_slots_available > 0:
            equation = park_building_times + building_park_times + car_park_time + (alfa * r)
            equation_dict[park] = equation

    return equation_dict

# Optimization function 

first_building = 'D1'
last_building = 'C3'
df_results = df[df['datetime'].dt.strftime("%Y-%m-%d %H:%M") == input_date][['park_id','Year','Month','Day','Weekday','Hour','Minute']]

equation_dict = get_park_optimization(first_building, last_building, df_results)
print(equation_dict)
print(f'Best park:{min(equation_dict, key=equation_dict.get)}')


