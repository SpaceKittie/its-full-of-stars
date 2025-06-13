"""
API client for fetching data about people currently in space from Open Notify.
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any
import requests
from include.utils.api_strategy import ApiStrategy

logger = logging.getLogger(__name__)

IN_SPACE_URL = "http://api.open-notify.org/astros.json"

class InSpaceStrategy(ApiStrategy):
    """
    Fetches the list of astronauts currently in space from Open Notify's API.
    """
    def fetch_data(self) -> List[Dict[str, Any]]:
        logger.info("Fetching in space data from Open Notify API...")
        try:
            response = requests.get(IN_SPACE_URL)
            response.raise_for_status()
            data = response.json()
            people_in_space = data.get("people", [])
            logger.info(f"Fetched {len(people_in_space)} people in space.")
            return people_in_space
        except Exception as e:
            logger.error(f"Could not fetch in space data: {e}")
            return []

    def to_dict(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return data 