import streamlit.components.v1 as components
import json
from typing import List, Dict, Tuple, Optional


class InteractiveMapComponent:
    """Interactive Google Maps component for Streamlit using JavaScript API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def render_map(self, 
                   participants: List[Dict] = None,
                   venues: List[Dict] = None,
                   center: Tuple[float, float] = (37.7749, -122.4194),  # SF default
                   zoom: int = 12,
                   height: int = 400) -> None:
        """
        Render an interactive Google Map with participants and venues.
        
        Args:
            participants: List of participant data with locations
            venues: List of venue data with coordinates
            center: Map center coordinates (lat, lng)
            zoom: Initial zoom level
            height: Map height in pixels
        """
        
        participants = participants or []
        venues = venues or []
        
        # Prepare data for JavaScript
        map_data = {
            'participants': participants,
            'venues': venues,
            'center': {'lat': center[0], 'lng': center[1]},
            'zoom': zoom
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://maps.googleapis.com/maps/api/js?key={self.api_key}&libraries=places"></script>
            <style>
                #map {{
                    height: {height}px;
                    width: 100%;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .info-window {{
                    font-family: Arial, sans-serif;
                    max-width: 200px;
                }}
                .participant-info {{
                    color: #1f77b4;
                    font-weight: bold;
                }}
                .venue-info {{
                    color: #ff7f0e;
                }}
                .rating {{
                    color: #ffb347;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            
            <script>
                let map;
                let infoWindow;
                const mapData = {json.dumps(map_data)};
                
                function initMap() {{
                    // Initialize map
                    map = new google.maps.Map(document.getElementById("map"), {{
                        zoom: mapData.zoom,
                        center: mapData.center,
                        styles: [
                            {{
                                "featureType": "poi",
                                "elementType": "labels",
                                "stylers": [{{ "visibility": "off" }}]
                            }}
                        ]
                    }});
                    
                    infoWindow = new google.maps.InfoWindow();
                    
                    // Add participant markers
                    mapData.participants.forEach(participant => {{
                        if (participant.lat && participant.lng) {{
                            const marker = new google.maps.Marker({{
                                position: {{ lat: participant.lat, lng: participant.lng }},
                                map: map,
                                title: participant.name,
                                icon: {{
                                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                                        <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="15" cy="15" r="12" fill="#1f77b4" stroke="white" stroke-width="2"/>
                                            <text x="15" y="19" text-anchor="middle" fill="white" font-size="12" font-weight="bold">P</text>
                                        </svg>
                                    `),
                                    scaledSize: new google.maps.Size(30, 30)
                                }}
                            }});
                            
                            marker.addListener("click", () => {{
                                const content = `
                                    <div class="info-window">
                                        <div class="participant-info">${{participant.name}}</div>
                                        <div><strong>Location:</strong> ${{participant.location || 'Unknown'}}</div>
                                        <div><strong>Food Preferences:</strong> ${{participant.food_preferences || 'None specified'}}</div>
                                        <div><strong>Dietary Restrictions:</strong> ${{participant.dietary_restrictions || 'None'}}</div>
                                    </div>
                                `;
                                infoWindow.setContent(content);
                                infoWindow.open(map, marker);
                            }});
                        }}
                    }});
                    
                    // Add venue markers
                    mapData.venues.forEach(venue => {{
                        if (venue.lat && venue.lng) {{
                            const marker = new google.maps.Marker({{
                                position: {{ lat: venue.lat, lng: venue.lng }},
                                map: map,
                                title: venue.name,
                                icon: {{
                                    url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                                        <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="15" cy="15" r="12" fill="#ff7f0e" stroke="white" stroke-width="2"/>
                                            <text x="15" y="19" text-anchor="middle" fill="white" font-size="12" font-weight="bold">R</text>
                                        </svg>
                                    `),
                                    scaledSize: new google.maps.Size(30, 30)
                                }}
                            }});
                            
                            marker.addListener("click", () => {{
                                const rating = venue.rating ? `<div class="rating">★ ${{venue.rating}}/5</div>` : '';
                                const priceLevel = venue.price_level ? `<div>Price: ${{{'$'.repeat(venue.price_level)}}</div>` : '';
                                
                                const content = `
                                    <div class="info-window">
                                        <div class="venue-info"><strong>${{venue.name}}</strong></div>
                                        <div>${{venue.address || 'Address not available'}}</div>
                                        ${{rating}}
                                        ${{priceLevel}}
                                        <div><small>${{venue.types ? venue.types.join(', ') : ''}}</small></div>
                                    </div>
                                `;
                                infoWindow.setContent(content);
                                infoWindow.open(map, marker);
                            }});
                        }}
                    }});
                    
                    // Auto-fit bounds if we have markers
                    if (mapData.participants.length > 0 || mapData.venues.length > 0) {{
                        const bounds = new google.maps.LatLngBounds();
                        
                        mapData.participants.forEach(p => {{
                            if (p.lat && p.lng) bounds.extend(new google.maps.LatLng(p.lat, p.lng));
                        }});
                        
                        mapData.venues.forEach(v => {{
                            if (v.lat && v.lng) bounds.extend(new google.maps.LatLng(v.lat, v.lng));
                        }});
                        
                        map.fitBounds(bounds);
                        
                        // Ensure minimum zoom level
                        google.maps.event.addListenerOnce(map, 'bounds_changed', function() {{
                            if (map.getZoom() > 15) {{
                                map.setZoom(15);
                            }}
                        }});
                    }}
                }}
                
                // Initialize map when page loads
                google.maps.event.addDomListener(window, 'load', initMap);
            </script>
        </body>
        </html>
        """
        
        components.html(html_content, height=height + 20)
    
    def get_participant_coordinates(self, participants: List[Dict], maps_client) -> List[Dict]:
        """
        Get coordinates for participants using the existing maps client.
        
        Args:
            participants: List of participant objects
            maps_client: Existing GoogleMapsClient instance
            
        Returns:
            List of participants with lat/lng coordinates
        """
        enhanced_participants = []
        
        for participant in participants:
            participant_data = {
                'name': participant.get('name', 'Unknown'),
                'location': participant.get('location', ''),
                'food_preferences': participant.get('food_preferences', ''),
                'dietary_restrictions': participant.get('dietary_restrictions', ''),
                'lat': None,
                'lng': None
            }
            
            if participant.get('location') and maps_client and maps_client.is_available():
                try:
                    results = maps_client.client.geocode(participant['location'])
                    if results and len(results) > 0:
                        location = results[0]['geometry']['location']
                        participant_data['lat'] = location['lat']
                        participant_data['lng'] = location['lng']
                except Exception as e:
                    print(f"Failed to geocode {participant['location']}: {e}")
            
            enhanced_participants.append(participant_data)
        
        return enhanced_participants
    
    def get_venue_coordinates(self, venues: List[Dict], maps_client) -> List[Dict]:
        """
        Get coordinates for venues using the existing maps client.
        
        Args:
            venues: List of venue dictionaries
            maps_client: Existing GoogleMapsClient instance
            
        Returns:
            List of venues with lat/lng coordinates
        """
        enhanced_venues = []
        
        for venue in venues:
            venue_data = {
                'name': venue.get('name', 'Unknown Venue'),
                'address': venue.get('address', ''),
                'rating': venue.get('rating'),
                'price_level': venue.get('price_level'),
                'types': venue.get('types', []),
                'place_id': venue.get('place_id'),
                'lat': None,
                'lng': None
            }
            
            if venue.get('place_id') and maps_client and maps_client.is_available():
                try:
                    # Use place details to get coordinates
                    result = maps_client.client.place(
                        place_id=venue['place_id'],
                        fields=['geometry']
                    )
                    
                    if result and 'result' in result:
                        location = result['result']['geometry']['location']
                        venue_data['lat'] = location['lat']
                        venue_data['lng'] = location['lng']
                        
                except Exception as e:
                    print(f"Failed to get coordinates for venue {venue['name']}: {e}")
            
            enhanced_venues.append(venue_data)
        
        return enhanced_venues