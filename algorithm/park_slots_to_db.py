import requests 
import json 
import pandas as pd 
from datetime import datetime, timedelta 
import pyodbc

#15:28 41!!!

server = 'TOMASZ' 
database = 'pwr_park_db'
user = 'tomek' 
password = '063900'
driver='ODBC Driver 17 for SQL Server'
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={user};PWD={password}'

url = 'https://iparking.pwr.edu.pl/modules/iparking/scripts/ipk_operations.php'

headers = {
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://iparking.pwr.edu.pl/"
}

payload_info  = {
        "o": "get_parks",
        "i": 2
    }

response_info = requests.post(url, headers=headers, data=json.dumps(payload_info))
response_data_info = response_info.json()
parking_id = [i['id'] for i in response_data_info['places']]
print(parking_id)
for id in parking_id:
    payload = {
        "o": "get_park",
        "i": id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response_data = response.json()
    time_park = response_data["slots"]["labels"]
    park_slots = response_data["slots"]["data"]
    date = datetime.today()
    df = pd.DataFrame({'time_park':time_park, 'park_slots':park_slots,'date':date.strftime("%Y-%m-%d"),'park_id':id})
    
    try:
        conn = pyodbc.connect(connection_string)
        print("Połączenie z bazą danych MS SQL (pyodbc) udane!")
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        if sqlstate == '28000':
            print("Błąd uwierzytelnienia. Sprawdź nazwę użytkownika i hasło.")
        elif sqlstate == '01000':
            print("Błąd sterownika lub serwera. Sprawdź nazwę serwera i sterownik ODBC.")
        else:
            print(f"Błąd połączenia z bazą danych (pyodbc): {ex}")
        exit()

    cursor = conn.cursor() 
    for i in range(len(df)):
        sql_query = f"""
            INSERT INTO park_table (time_park, park_slots, date, park_id)
            VALUES ('{time_park[i]}', {park_slots[i]}, '{date.strftime('%Y-%m-%d')}', {id})
        """
        print(f'Dodano do bazy danych VALUES ({time_park[i]},{park_slots[i]},{date.strftime("%Y-%m-%d")},{id})')
        try:
            cursor.execute(sql_query)
            conn.commit()
        except pyodbc.Error as e:
            print(f"Błąd wykonania zapytania SQL: {e}")
            conn.close() 
            exit() 

