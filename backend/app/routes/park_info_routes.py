from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, WebSocket
from app.database.connection import get_park_data_orm
from app.services.optimization import park_recommendation, get_df_results, park_slots_now_func, get_address
from app.database.db import get_db
from app.services.time_functions import get_time_car_park
import pydantic 
import asyncio
import datetime

router = APIRouter()

class UserInput(pydantic.BaseModel):
    first_building: str
    last_building: str
    date_time: str
    user_lng: float = None
    user_lat: float = None

    class Config:
        schema_extra = {
            "example": {
                "first_building": "D1",
                "last_building": "C3",
                "date_time": "2025-06-17 07:50",
                "user_lng": 17.058749,
                "user_lat": 51.110774
            }
        }

@router.get('/building_names')
async def buildings(db: Session = Depends(get_db)):
    df, df_park, df_buildings = get_park_data_orm(db)
    buildings_list = df_buildings['building_name'].tolist()
    print('building list',buildings_list)
    return {'building_names': buildings_list}

@router.get("/map_location")
async def map_location(park_name: str, db: Session = Depends(get_db)):
    df, df_park, df_buildings = get_park_data_orm(db)

    row = df_park[df_park["park_name"] == park_name]

    lat = float(row["park_lat"].values[0])
    lng = float(row["park_lng"].values[0])

    return {"lat": lat, "lng": lng}


@router.websocket('/recommended_park')
async def recommendation(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            request = UserInput(**data)

            df_results = get_df_results(request.date_time)
            park_ids, slots_now = park_slots_now_func()

            recommendation = park_recommendation(
                request.first_building,
                request.last_building,
                df_results=df_results,
                user_lat=request.user_lat,
                user_lng=request.user_lng,
                request_time=request.date_time
            )

            await websocket.send_json({'recommended_park': recommendation})

    except Exception as e:
        print("WebSocket disconnected:", e)

# @router.get('/parking_address')
# async def address(db: Session = Depends(get_db)):
#     return {'parking_address': get_address(recommendation())}


#@router.websocket('/ws/location')
    # df_results = get_df_results(request.date_time)
    # recommendation = park_recommendation(request.first_building, request.last_building, df_results=df_results)
    # return {'recommended_park': recommendation}

