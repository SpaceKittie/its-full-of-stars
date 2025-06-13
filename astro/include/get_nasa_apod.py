"""
API client for fetching NASA Astronomy Picture of the Day (APOD) data.

This module provides the NasaApodStrategy class which fetches the APOD
from NASA's public API and returns it as a list of dictionaries.
"""
import requests
import pandas as pd
from include.utils.api_strategy import ApiStrategy
from airflow.models import Variable
import logging

try:
    API_KEY = Variable.get("nasa_api_key")
except KeyError:
    API_KEY = "DEMO_KEY"

NASA_APOD_API_URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"

class NasaApodStrategy(ApiStrategy):
    """
    Fetches NASA Astronomy Picture of the Day (APOD) data.

    This strategy retrieves the APOD from NASA's API and returns it as a list of records.
    """
    def fetch_data(self) -> list[dict]:
        logging.info("Fetching data from NASA APOD API...")
        try:
            response = requests.get(NASA_APOD_API_URL)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame([{
                'COPYRIGHT': data.get('copyright'),
                'APOD_DATE': data.get('date'),
                'EXPLANATION': data.get('explanation'),
                'HD_URL': data.get('hdurl'),
                'MEDIA_TYPE': data.get('media_type'),
                'SERVICE_VERSION': data.get('service_version'),
                'TITLE': data.get('title'),
                'URL': data.get('url')
            }])
            logging.info("Data fetched and processed successfully.")
            return df.to_dict('records')
        except requests.RequestException as e:
            logging.error(f"Error fetching NASA APOD data: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error in NasaApodStrategy: {e}")
            return []
