import requests 
import json 

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

    response_info = requests.post(url, headers=headers, data=json.dumps(payload_info))
    response_data_info = response_info.json()

    park_ids = [int(response_data_info['places'][id]['parking_id']) for id in range(len(response_data_info['places']))]
    slots = []
    for loop_id in range(len(response_data_info['places'])):
        response_data_info['places'][loop_id]['liczba_miejsc']
        slots.append(response_data_info['places'][loop_id]['liczba_miejsc'])
    return park_ids,slots
