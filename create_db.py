import os
import datetime as dt
import meteomatics.api as api
from dotenv import load_dotenv
import sqlite3
import glob
import pandas as pd
from pathlib import Path


load_dotenv()
db_path = os.getenv("DB_PATH")

if db_path==None:
        db_path="weatherAPI/src/weatherapi/data/weather.db"



#List the average the_temp of the last 3 forecasts for each location for every day

locations = {
    "limasol" : {'coords':[(34.68529,33.033266)]},
    "larnaca" : {'coords':[(34.92361,33.623618)]},
    "nicosia" : {'coords':[(35.17465,33.363878)]}
}

def get_weather_forecast(coord, name, save=False, delta_D = 7, interval_H=1):

    model = 'mix'
    startdate = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    delta = 7
    enddate = startdate + dt.timedelta(days=delta_D)
    interval = dt.timedelta(hours=interval_H)
    parameters = [ "t_2m:C", "precip_1h:mm", "prob_precip_1h:p", "wind_speed_10m:ms", "relative_humidity_2m:p", "frost_depth:cm", "sunshine_duration_1h:min", "global_rad:W" ]

    rename_mappings = {original : original.split(":")[0] for original in parameters}
    rename_mappings["validdate"]= "forecast_date"
    df = api.query_time_series(coord, startdate, enddate, interval,\
                               parameters, username, password, model=model)
    
    df = df.reset_index()   .drop(labels=['lat','lon'], axis=1)\
                            .rename(columns=rename_mappings)
    if save:
        df.to_csv(f"data/{name}_+{delta}Days.csv",index=False)
    
    return df


def populate_dict():    
    for location_name, items in locations.items():
        coords =  items['coords']
        locations[location_name]['data']=get_weather_forecast(coord=coords, name = location_name,save=True,delta_D=7)




def create_database(db_path=db_path):
    """Create the SQLite database and tables"""
    with open('schema.sql', 'r') as f:

        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)

    conn.commit()
    conn.close()

    print(f"Database created at {db_path}")


def populate_location_tbl(db_path=db_path, locations = locations):
    """
    Populate DB
    """
    # Sample locations - replace with your actual locations
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for location_name, item in locations.items():
        coord = item['coords']
        cursor.execute("""
            INSERT INTO locations (name, latitude, longitude)
            VALUES (?, ?, ?)
        """, (
            location_name,
            coord[0][0],
            coord[0][1],
        ))
    
    conn.commit()
    conn.close()
    print(f"Loaded {len(locations)} locations into database")


def add_dict_sql_mapping(db_path=db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # For each location in the dictionary
    for location_name in locations.keys():
        # Convert location name to title case for consistent matching
        
        # Query the database for this location's ID
        cursor.execute("SELECT id FROM locations WHERE name = ?", (location_name,))
        result = cursor.fetchone()
        
        if result:
            # Add the ID to the location dictionary
            locations[location_name]['id'] = result[0]


    conn.close()

    return locations


def populate_forecast_tbl(db_path=db_path, csv_dir="./data", locations= locations):
    """
    Load forecast data from CSV files
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM locations")
    location_names_db = [name[0] for name in cursor.fetchall()]  
    
    total_records = 0
    
    for location_name, items in locations.items():

        csv_path = f"data/{location_name}_+7Days.csv"
        
        
        if location_name not in location_names_db:
            print(f"Warning: Location '{location_name}' not found in database. Skipping file {csv_path}")
            continue
        
        location_id = locations[location_name]['id']
        
        # Load CSV data
        df = pd.read_csv(csv_path)

        df['location_id']=location_id
        try:
            df.to_sql(
                'forecasts', 
                conn, 
                if_exists='append',  # Append to table if it exists
                index=False,        # Don't use DataFrame index
                chunksize=100,     # Process in chunks for better performance
                method='multi'      # Improves performance for multiple rows
            )
        except:
            print('error in adding entries')
            continue

        total_records += len(df)
    
    conn.close()
    print(f"Loaded {total_records} forecast records into database")


if __name__ == "__main__":

    load_dotenv()

    username = os.getenv('METEOMATICS_USERNAME')
    password = os.getenv('METEOMATICS_PASSWORD')


    Path("data/").mkdir( exist_ok=True)

    create_database(db_path=db_path)
    populate_dict()
    populate_location_tbl(db_path=db_path)
    locations = add_dict_sql_mapping(db_path=db_path)

    populate_forecast_tbl(db_path=db_path)




