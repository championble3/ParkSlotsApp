from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends
from app.database.connection import get_park_data_orm
from app.services.optimization import park_recommendation, get_df_results
from app.database.db import get_db
import pydantic 

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
                "user_lng": 19.934,
                "user_lat": 50.061
            }
        }

@router.get('/parks')
async def buildings(db: Session = Depends(get_db)):
    df, df_park, df_buildings = get_park_data_orm(db)
    buildings_list = df_buildings['building_name'].tolist()
    return {'buildings': buildings_list}

@router.post('/recommended_park')
async def recommendation(request: UserInput, db: Session = Depends(get_db)):
    df_results = get_df_results(request.date_time)
    recommendation = park_recommendation(request.first_building, request.last_building, df_results=df_results)
    return {'recommended_park': recommendation}

