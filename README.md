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
    python -m venv venv & pip install -r requirements.txt
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




