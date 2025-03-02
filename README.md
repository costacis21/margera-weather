# Instructions for DB creation:

1. Clone this repository:
    ```bash
    git clone https://github.com/costacis21/margera-weather.git
    ```
2. Change directories: 
    ```bash
    cd margera-weather
    ```

3. Create a new python environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4. Create a [Meteomatics API account](https://www.meteomatics.com/en/sign-up-weather-api-test-account/)

5. Create a .env file containing the following variables:
    ```bash
    METEOMATICS_USERNAME="YOUR-METEOMATICS-USERNAME"
    METEOMATICS_PASSWORD="YOUR-METEOMATICS-PASSWORD"
    DB_PATH="weather.db"
    ```

6. Run script 
    ```bash
    python create_db.py
    ```


# Instructions for local hosting

1. Move to app directory:
    ```bash
    cd weatherAPI/src/weatherapi/
    ```

2. Run uvicorn webservice:
    ```bash
    uvicorn app.main:app --reload
    ```


# Instructions for hosting on gcp
> Requires google-cloud-sdk 

1. Authenticate with gcloud and set variables
    ```bash
    gcloud auth login
    gcloud config set project PROJECT_ID
    gcloud config set run/region europe-north1
    gcloud auth configure-docker
    ```

> Must be in this directory `weatherAPI/src/weatherapi/`
2. Deploy!
    ```bash
    gcloud run deploy sample --port 8080 --source .
    ```


