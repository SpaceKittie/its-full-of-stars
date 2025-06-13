"""
API client for fetching astronaut data from the SpaceDevs API.

This module provides the AstronautsStrategy class which fetches all astronaut data,
handling pagination and rate-limiting.
"""
from __future__ import annotations
import logging
import time
from typing import List, Dict, Any
import requests
from include.utils.api_strategy import ApiStrategy

logger = logging.getLogger(__name__)

ASTRONAUTS_API_URL = "https://ll.thespacedevs.com/2.2.0/astronaut/?limit=100"


class AstronautsStrategy(ApiStrategy):
    """
    Fetches all astronaut data from the paginated Space Devs API.
    """
    def fetch_data(self) -> List[Dict[str, Any]]:
        logger.info("Fetching all astronaut data from paginated Space Devs API...")
        
        all_astronauts = []
        url = ASTRONAUTS_API_URL
        
        while url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                all_astronauts.extend(data.get("results", []))
                
                url = data.get("next")
                if url:
                    logger.info(f"Fetching next page: {url}")
                    logger.info("Rate limit requires a 4-minute delay before the next request.")
                    time.sleep(241)
            except Exception as e:
                logger.error(f"Could not fetch Space Devs astronaut data from {url}: {e}")
                break 

        logger.info(f"Fetched a total of {len(all_astronauts)} astronauts from Space Devs API.")
        return all_astronauts

    def to_dict(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return data 