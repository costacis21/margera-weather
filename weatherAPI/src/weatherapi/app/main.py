# main.py

from fastapi import FastAPI, Path, Query, HTTPException
from app.utils.utils.db_utils import *
import sqlite3
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

# Define Pydantic models for responses
class LocationsResponse(BaseModel):
    """Response model for locations endpoint"""
    locations: Dict[str, int] = Field(
        ..., 
        description="Dictionary mapping location names to their IDs",
        example={"limasol": 1, "larnaca": 2, "nicosia": 3}
    )

class ForecastEntry(BaseModel):
    """Model for a single forecast entry"""
    id: int
    location_id: int
    forecast_date: str
    t_2m: float = Field(..., description="Temperature at 2 meters in Celsius")
    precip_1h: float = Field(..., description="Precipitation amount in the last hour in mm")
    prob_precip_1h: float = Field(..., description="Probability of precipitation in the last hour (0-100)")
    wind_speed_10m: float = Field(..., description="Wind speed at 10 meters in m/s")
    relative_humidity_2m: float = Field(..., description="Relative humidity at 2 meters in %")
    frost_depth: Optional[float] = Field(None, description="Frost depth in meters")
    sunshine_duration_1h: float = Field(..., description="Sunshine duration in the last hour in hours")
    global_rad: float = Field(..., description="Global radiation in W/m²")
    day: str = Field(..., description="Date of the forecast in YYYY-MM-DD format")
    max_time: str = Field(..., description="Timestamp of the latest forecast")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 9,
                "location_id": 1,
                "forecast_date": "2025-03-02 23:00:00+00:00",
                "t_2m": 12.4,
                "precip_1h": 0,
                "prob_precip_1h": 1,
                "wind_speed_10m": 1.8,
                "relative_humidity_2m": 80.3,
                "frost_depth": None,
                "sunshine_duration_1h": 0.0,
                "global_rad": 0.0,
                "day": "2025-03-02",
                "max_time": "2025-03-02 23:00:00+00:00"
            }
        }

class ForecastsResponse(BaseModel):
    """Response model for latest forecasts endpoint"""
    latest_forecasts: List[ForecastEntry]

class AverageTemperatureEntry(BaseModel):
    """Model for an average temperature entry"""
    day: str = Field(..., description="Date in YYYY-MM-DD format")
    location_name: str = Field(..., description="Name of the location")
    avg_t_2m: float = Field(..., description="Average temperature at 2 meters in Celsius")

    class Config:
        json_schema_extra = {
            "example": {
                "day": "2025-03-02",
                "location_name": "limasol",
                "avg_t_2m": 12.5
            }
        }

class AverageTemperaturesResponse(BaseModel):
    """Response model for average temperatures endpoint"""
    average_temperatures: List[AverageTemperatureEntry]

class LocationMetricValue(BaseModel):
    """Model for a location's metric value"""
    value: Optional[float] = Field(None, description="Value of the metric (can be null for some metrics)")
    location: str

    class Config:
        json_schema_extra = {
            "example": {
                "value": 16.7,
                "location": "nicosia"
            }
        }

class TopLocationsResult(BaseModel):
    """Result component of the top locations response"""
    result: Dict[str, List[LocationMetricValue]]
    column_names: List[str]

class TopLocationsResponse(BaseModel):
    """Response model for top locations endpoint"""
    top_locations: TopLocationsResult

    class Config:
        json_schema_extra = {
            "example": {
                "top_locations": {
                    "result": {
                        "t_2m": [
                            {"value": 16.7, "location": "nicosia"},
                            {"value": 15.1, "location": "larnaca"}
                        ],
                        "wind_speed_10m": [
                            {"value": 8.4, "location": "limasol"},
                            {"value": 7.2, "location": "larnaca"}
                        ]
                    },
                    "column_names": ["t_2m", "precip_1h", "wind_speed_10m", "relative_humidity_2m"]
                }
            }
        }

# Create app with documentation
app = FastAPI(
    title="Weather Forecast API",
    description="""
    This API provides access to weather forecast data for various locations in Cyprus.
    
    ## Features
    * List all available locations
    * Get the latest forecasts for each location
    * Get average temperatures from the last 3 forecasts
    * Find top locations based on various metrics
    
    ## How to use
    1. Browse the available endpoints below
    2. Try them out using the interactive documentation
    3. Use the returned data in your applications
    
    ## Available Metrics
    The following weather metrics are available:
    - t_2m: Temperature at 2 meters (°C)
    - precip_1h: Precipitation amount in the last hour (mm)
    - prob_precip_1h: Probability of precipitation (%)
    - wind_speed_10m: Wind speed at 10 meters (m/s)
    - relative_humidity_2m: Relative humidity at 2 meters (%)
    - sunshine_duration_1h: Sunshine duration in the last hour (h)
    - global_rad: Global radiation (W/m²)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

db_path = "data/weather.db"
conn = sqlite3.connect(db_path)

@app.get("/", 
    tags=["Root"],
    summary="Welcome endpoint",
    description="Returns a welcome message for the API"
)
async def root():
    """
    Root endpoint that returns a simple welcome message.
    
    Returns:
        dict: A welcome message with API information
    """
    return {
        "message": "Welcome to the Weather Forecast API",
        "docs": "Visit /docs for interactive API documentation",
        "endpoints": [
            "/locations",
            "/latest_forecast_daily",
            "/avg_temp_l3_daily",
            "/top_locations/{n}"
        ]
    }


@app.get("/locations", 
    tags=["Locations"],
    summary="List all locations",
    description="Returns a list of all locations available in the database with their IDs",
    response_model=LocationsResponse,
    response_description="Dictionary mapping location names to their IDs"
)
async def list_locations():
    """
    List all available locations in the database.
    
    Returns:
        LocationsResponse: Dictionary mapping location names to their IDs
    """
    try:
        locations = list_location(conn)
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/latest_forecast_daily", 
    tags=["Forecasts"],
    summary="Latest daily forecasts",
    description="Returns the latest forecast for each location for every day",
    response_model=ForecastsResponse,
    response_description="List of latest forecasts for each day"
)
async def get_latest_forecast():
    """
    Get the latest forecast for each location for every day.
    
    Returns:
        ForecastsResponse: Latest forecast data for each location by day
    """
    try:
        forecasts = list_latest_forecast(conn)
        return {"latest_forecasts": forecasts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/avg_temp_l3_daily", 
    tags=["Forecasts"],
    summary="Average temperature from last 3 forecasts",
    description="Returns the average temperature of the last 3 forecasts for each location for every day",
    response_model=AverageTemperaturesResponse,
    response_description="List of average temperatures for each location by day"
)
async def get_avg_temp():
    """
    Get the average temperature from the last 3 forecasts for each location by day.
    
    Returns:
        AverageTemperaturesResponse: Average temperature data for each location by day
    """
    try:
        avg_temps = list_avg_temp_l3(conn)
        return {"average_temperatures": avg_temps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/top_locations/{n}", 
    tags=["Locations"],
    summary="Top N locations by metrics",
    description="Returns the top N locations based on each available metric",
    response_model=TopLocationsResponse,
    response_description="Top N locations for each weather metric"
)
async def get_top_locations(
    n: int = Path(
        ..., 
        description="Number of top locations to return", 
        gt=0,
        le=10,
        example=3,
        title="Number of locations"
    )
):
    """
    Get the top N locations based on each available weather metric.
    
    The endpoint returns locations with the highest values for each metric
    available in the forecasts table (temperature, humidity, etc.)
    
    Parameters:
        n (int): Number of top locations to return, must be greater than 0 and less than or equal to 10
    
    Returns:
        TopLocationsResponse: Top N locations for each metric
    """
    try:
        top_locs = get_topn(conn=conn, n=n)
        return {"top_locations": top_locs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")