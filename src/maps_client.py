import os
import logging
from typing import Optional, Dict, List, Tuple
import googlemaps
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class GoogleMapsClient:
    """Client for Google Maps API integration."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = googlemaps.Client(key=self.api_key)
                logger.info("Google Maps client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps client: {e}")
                self.client = None
        else:
            logger.warning("Google Maps API key not found. Maps features will be limited.")
    
    def is_available(self) -> bool:
        """Check if Google Maps client is available."""
        return self.client is not None
    
    def geocode_address(self, address: str) -> Optional[str]:
        """
        Geocode an address to get a normalized location string.
        
        Args:
            address: The address to geocode
            
        Returns:
            Normalized address string or None if failed
        """
        if not self.is_available():
            return address  # Return original if Maps not available
        
        try:
            results = self.client.geocode(address)
            if results and len(results) > 0:
                # Get the formatted address from the first result
                formatted = results[0].get('formatted_address', address)
                
                # Also extract neighborhood/area info if available
                components = results[0].get('address_components', [])
                neighborhood = None
                for component in components:
                    types = component.get('types', [])
                    if 'neighborhood' in types or 'sublocality' in types:
                        neighborhood = component.get('long_name')
                        break
                
                if neighborhood and neighborhood not in formatted:
                    return f"{neighborhood}, {formatted}"
                
                return formatted
            
            return address
            
        except Exception as e:
            logger.error(f"Geocoding failed for '{address}': {e}")
            return address
    
    def find_geographic_center(self, addresses: List[str]) -> Optional[Tuple[float, float]]:
        """
        Find the geographic center point of multiple addresses.
        
        Args:
            addresses: List of address strings
            
        Returns:
            Tuple of (latitude, longitude) or None if failed
        """
        if not self.is_available() or not addresses:
            return None
        
        locations = []
        
        # Geocode each address
        for address in addresses:
            try:
                results = self.client.geocode(address)
                if results and len(results) > 0:
                    location = results[0]['geometry']['location']
                    locations.append((location['lat'], location['lng']))
            except Exception as e:
                logger.error(f"Failed to geocode '{address}': {e}")
                continue
        
        if not locations:
            return None
        
        # Calculate center point (simple average for now)
        avg_lat = sum(loc[0] for loc in locations) / len(locations)
        avg_lng = sum(loc[1] for loc in locations) / len(locations)
        
        return (avg_lat, avg_lng)
    
    def search_nearby_venues(self, location: Tuple[float, float], 
                           venue_type: str = "restaurant", 
                           radius: int = 2000) -> List[Dict]:
        """
        Search for venues near a location.
        
        Args:
            location: Tuple of (latitude, longitude)
            venue_type: Type of venue to search for
            radius: Search radius in meters
            
        Returns:
            List of venue dictionaries
        """
        if not self.is_available():
            return []
        
        try:
            results = self.client.places_nearby(
                location=location,
                radius=radius,
                type=venue_type,
                language='en'
            )
            
            venues = []
            for place in results.get('results', [])[:10]:  # Top 10 results
                venue = {
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'rating': place.get('rating'),
                    'price_level': place.get('price_level'),
                    'types': place.get('types', []),
                    'place_id': place.get('place_id')
                }
                venues.append(venue)
            
            return venues
            
        except Exception as e:
            logger.error(f"Venue search failed: {e}")
            return []
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific place.
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Dictionary with place details or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            result = self.client.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'formatted_phone_number', 
                       'website', 'rating', 'opening_hours', 'price_level']
            )
            
            return result.get('result')
            
        except Exception as e:
            logger.error(f"Failed to get place details: {e}")
            return None