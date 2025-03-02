# main.py

from fastapi import FastAPI
from app.utils.utils.db_utils import *
import sqlite3


app = FastAPI()

db_path = "data/weather.db"


conn = sqlite3.connect(db_path)

@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello World"}


#List locations
@app.post("/locations", tags=["root"])
async def root():

    return {list_location(conn)}

#List the latest forecast for each location for every day
@app.post("/latest_forecast_daily", tags=["root"])
async def root():

    return {list_latest_forecast(conn)}

#List the average the_temp of the last 3 forecasts for each location for every day
@app.post("/avg_temp_l3_daily", tags=["root"])
async def root():

    return {list_avg_temp_l3(conn)}

#Get the top n locations based on each available metric where n is a parameter given to the API call.

@app.get("/top n_locations", tags=["root"])
async def root():
    #TODO get N from GET request
    
    return {get_topn(conn=conn, n=2)}