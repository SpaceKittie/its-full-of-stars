"""
API Strategy interface for data extraction from various sources.

This module defines the abstract base class for all API client strategies,
ensuring a consistent interface for different data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ApiStrategy(ABC):
    """
    Abstract base class defining the interface for API data extraction strategies.
    
    Concrete implementations must provide the fetch_data method to retrieve data
    from their respective APIs and return it in a standardized format.
    """
    
    @abstractmethod
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from the API endpoint.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries where each dictionary
                represents a record from the API.
                
        Raises:
            Exception: If the API request fails or returns unexpected data.
        """
        pass