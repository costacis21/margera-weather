import os
import sqlite3
import pandas as pd
import json



#List locations


def list_location(conn = None):
    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    cursor = conn.cursor()

    # Query the database for this location's ID
    cursor.execute("SELECT id, name FROM locations")
    result = cursor.fetchall()

    result = {name:id for id,name in result}
  
    return str(result)



#List the latest forecast for each location for every day


def list_latest_forecast(conn = None,return_df=False):

    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    sql_statement="""
        SELECT *
        FROM forecasts f
        INNER JOIN (
            SELECT DATE(forecast_date) AS day, MAX(forecast_date) AS max_time
            FROM forecasts
            GROUP BY DATE(forecast_date)
        ) sub ON DATE(f.forecast_date) = sub.day AND f.forecast_date = sub.max_time
        ORDER BY f.location_id;
    """
    
    result = pd.read_sql(sql_statement,conn)

    if return_df:
        return result.to_json(orient="records"),result
    
    return result.to_json(orient="records")

#List the average the_temp of the last 3 forecasts for each location for every day

def list_avg_temp_l3(conn = None,return_df=False):
    
    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    sql_statement="""
        WITH RankedRecords AS (
            SELECT 
                DATE(forecast_date) AS day,
                location_id,
                t_2m,
                ROW_NUMBER() OVER (
                    PARTITION BY DATE(forecast_date), location_id 
                    ORDER BY forecast_date DESC
                ) AS row_num
            FROM forecasts
        )
        SELECT 
            day,
            locations.name AS location_name,
            AVG(t_2m) AS avg_t_2m
        FROM RankedRecords, locations
        WHERE row_num <= 3 AND locations.id = RankedRecords.location_id
        GROUP BY day, location_id
        ORDER BY location_id, day;
    """
    
    result = pd.read_sql(sql_statement,conn)

    if return_df:
        return result.to_json(orient="records"),result
    
    return result.to_json(orient="records")



#Get the top n locations based on each available metric where n is a parameter given to the API call.

def get_topn(n=3, conn = None):
    """
    Returns result in a tuple of {column_name : [tuple(value,locations.name), ] }, column_names=[list]
    """

    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    sql_statement="PRAGMA table_info('forecasts');"
    cursor = conn.cursor()

    result = cursor.execute(sql_statement).fetchall()

    column_names = [column[1] for column in result[3:]]


    cursor = conn.cursor()

    result = {}

    for name in column_names:
 
        sql_statement=f"SELECT f.{name}, l.name FROM forecasts f, locations l WHERE f.location_id= l.id ORDER BY f.{name} DESC LIMIT {n};"
        result[name] = cursor.execute(sql_statement).fetchall()


    result = {'result':result,'column_names':column_names}
  
    
    return json.dumps(result) 




