"""
API client for fetching the current location of the International Space Station (ISS).

This module provides the IssLocationStrategy class which fetches the current
geographic coordinates of the ISS using the Open Notify API.
"""
import logging
from typing import Dict, List, Any
import pandas as pd
import requests
from include.utils.api_strategy import ApiStrategy

logger = logging.getLogger(__name__)

ISS_API_URL = "http://api.open-notify.org/iss-now.json"

class IssLocationStrategy(ApiStrategy):
    """
    Fetches the current location of the International Space Station (ISS).

    This strategy retrieves the current latitude, longitude, and timestamp
    of the ISS from the Open Notify API (http://open-notify.org/).
    """
    def fetch_data(self) -> List[Dict[str, Any]]:
        logger.info("Fetching current ISS location from %s", ISS_API_URL)
        try:
            response = requests.get(ISS_API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            position_data = {
                'LATITUDE': float(data['iss_position']['latitude']),
                'LONGITUDE': float(data['iss_position']['longitude']),
                'API_TIMESTAMP': int(data['timestamp'])
            }

            df = pd.DataFrame([position_data])
            logger.info("Successfully fetched ISS location data")
            return df.to_dict('records')
            
        except requests.RequestException as e:
            logger.error("Failed to fetch ISS location: %s", str(e))
            return []
            
        except (KeyError, ValueError) as e:
            logger.error("Unexpected data format in API response: %s", str(e))
            return []
            
        except Exception as e:
            logger.error("Unexpected error in IssLocationStrategy: %s", str(e))
            return []