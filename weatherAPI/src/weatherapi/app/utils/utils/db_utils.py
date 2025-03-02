import os
import sqlite3
import pandas as pd
import json


def list_location(conn=None):
    """
    List all locations in the database
    
    Args:
        conn: SQLite connection object
        
    Returns:
        dict: Dictionary mapping location names to their IDs
    """
    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    cursor = conn.cursor()

    # Query the database for this location's ID
    cursor.execute("SELECT id, name FROM locations")
    result = cursor.fetchall()

    # Return as a Python dictionary instead of a string
    return {name: id for id, name in result}


def list_latest_forecast(conn=None, return_df=False):
    """
    List the latest forecast for each location for every day
    
    Args:
        conn: SQLite connection object
        return_df: Whether to return the pandas DataFrame along with the records
        
    Returns:
        list: List of forecast records as dictionaries
    """
    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    sql_statement = """
        SELECT *
        FROM forecasts f
        INNER JOIN (
            SELECT DATE(forecast_date) AS day, MAX(forecast_date) AS max_time
            FROM forecasts
            GROUP BY DATE(forecast_date)
        ) sub ON DATE(f.forecast_date) = sub.day AND f.forecast_date = sub.max_time
        ORDER BY f.location_id;
    """
    
    result = pd.read_sql(sql_statement, conn)
    
    # Return Python list of dictionaries instead of JSON string
    records = result.to_dict(orient="records")
    
    if return_df:
        return records, result
    
    return records


def list_avg_temp_l3(conn=None, return_df=False):
    """
    List the average temperature of the last 3 forecasts for each location for every day
    
    Args:
        conn: SQLite connection object
        return_df: Whether to return the pandas DataFrame along with the records
        
    Returns:
        list: List of average temperature records as dictionaries
    """
    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    sql_statement = """
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
    
    result = pd.read_sql(sql_statement, conn)
    
    # Return Python list of dictionaries instead of JSON string
    records = result.to_dict(orient="records")
    
    if return_df:
        return records, result
    
    return records


def get_topn(n=3, conn=None):
    """
    Get the top n locations based on each available metric
    
    Args:
        n: Number of locations to return per metric
        conn: SQLite connection object
        
    Returns:
        dict: Dictionary with column names and top values with locations
    """
    if not conn:
        raise Exception("This function requires a sqlite3 connection as a parameter, user ensures conn.close()")

    sql_statement = "PRAGMA table_info('forecasts');"
    cursor = conn.cursor()

    result = cursor.execute(sql_statement).fetchall()

    column_names = [column[1] for column in result[3:]]
    cursor = conn.cursor()

    result = {}

    for name in column_names:
        # Order by the column, but handle NULL values by using NULLS LAST
        sql_statement = f"""
            SELECT f.{name}, l.name 
            FROM forecasts f, locations l 
            WHERE f.location_id = l.id 
            ORDER BY f.{name} IS NULL, f.{name} DESC 
            LIMIT {n};
        """
        rows = cursor.execute(sql_statement).fetchall()
        # Convert tuples to dictionaries for better readability
        # Explicitly keep NULL values as None
        result[name] = [{"value": value, "location": location} for value, location in rows]

    # Return a Python dictionary instead of a JSON string
    return {
        'result': result,
        'column_names': column_names
    }