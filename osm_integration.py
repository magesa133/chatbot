#!/usr/bin/env python3
"""
OpenStreetMap Integration Module for Tanzania/Dar es Salaam
Provides geocoding, reverse geocoding, and real map data services.
"""

try:
    import requests
    import overpy
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    OSM_AVAILABLE = True
except ImportError:
    print("Warning: OpenStreetMap dependencies not available. Using fallback mode.")
    OSM_AVAILABLE = False

from typing import Dict, List, Optional, Tuple
from data_models import Location, ServiceProvider
import time
import json


class OpenStreetMapIntegration:
    """Handles OpenStreetMap integration for Tanzania/Dar es Salaam"""

    def __init__(self):
        if not OSM_AVAILABLE:
            self.geolocator = None
            self.overpass_api = None
        else:
            # Initialize geolocator with Tanzania focus
            self.geolocator = Nominatim(user_agent="tanzania-service-chatbot", timeout=10)

            # Initialize Overpass API for OpenStreetMap queries
            self.overpass_api = overpy.Overpass()

        # Dar es Salaam center coordinates
        self.dar_center = (-6.7924, 39.2083)

        # Cache for geocoding results
        self.geocode_cache = {}
        self.reverse_cache = {}

    def geocode_location(self, location_text: str) -> Optional[Location]:
        """
        Convert location text to coordinates using OpenStreetMap Nominatim API
        Focused on Tanzania/Dar es Salaam
        """
        if not OSM_AVAILABLE:
            print("OpenStreetMap geocoding not available - using fallback")
            return None

        # Check cache first
        if location_text in self.geocode_cache:
            return self.geocode_cache[location_text]

        try:
            # Add Tanzania context to improve results
            if "dar" in location_text.lower() or "es salaam" in location_text.lower():
                query = f"{location_text}, Dar es Salaam, Tanzania"
            elif not any(word in location_text.lower() for word in ["tanzania", "dar es salaam"]):
                query = f"{location_text}, Dar es Salaam, Tanzania"
            else:
                query = location_text

            location = self.geolocator.geocode(query)

            if location:
                result = Location(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    name=location_text.title(),
                    landmark=self._extract_landmark(location.address)
                )

                # Cache the result
                self.geocode_cache[location_text] = result
                return result

        except Exception as e:
            print(f"Geocoding error for '{location_text}': {e}")

        return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to location name using reverse geocoding
        """
        if not OSM_AVAILABLE:
            return None

        cache_key = f"{lat:.4f},{lon:.4f}"

        if cache_key in self.reverse_cache:
            return self.reverse_cache[cache_key]

        try:
            location = self.geolocator.reverse((lat, lon), language='en')

            if location:
                address = location.address
                self.reverse_cache[cache_key] = address
                return address

        except Exception as e:
            print(f"Reverse geocoding error for ({lat}, {lon}): {e}")

        return None

    def _extract_landmark(self, address: str) -> str:
        """Extract landmark or neighborhood from address"""
        if not address:
            return ""

        # Common Dar es Salaam landmarks and areas
        landmarks = [
            "Kilimanjaro Avenue", "Samora Avenue", "Uhuru Road", "Azikiwe Street",
            "Masaki", "Mikocheni", "Kinondoni", "Ilala", "Temeke", "Ubungo",
            "Mlimani City", "Posta", "Jamhuri", "Mnazi Mmoja",
            "Kariakoo Market", "Mombasa Road", "Bagamoyo Road"
        ]

        address_lower = address.lower()
        for landmark in landmarks:
            if landmark.lower() in address_lower:
                return landmark

        return "Dar es Salaam"

    def get_service_providers_from_osm(self, service_type: str, user_location: Location,
                                      max_distance_km: float = 10.0) -> List[ServiceProvider]:
        """
        Query OpenStreetMap for real service providers in Dar es Salaam
        """
        if not OSM_AVAILABLE:
            print("OpenStreetMap queries not available - returning empty list")
            return []

        providers = []

        # Map service types to OpenStreetMap tags
        osm_queries = {
            "auto_repair": [
                '["shop"="car_repair"]',
                '["shop"="car"]',
                '["amenity"="car_wash"]',
                '["shop"="tyres"]'
            ],
            "medical": [
                '["amenity"="hospital"]',
                '["amenity"="clinic"]',
                '["amenity"="doctors"]',
                '["amenity"="pharmacy"]'
            ],
            "hair_salon": [
                '["shop"="hairdresser"]',
                '["shop"="beauty"]'
            ],
            "restaurant": [
                '["amenity"="restaurant"]',
                '["amenity"="cafe"]',
                '["amenity"="fast_food"]'
            ],
            "plumbing": [
                '["craft"="plumber"]',
                '["shop"="hardware"]'
            ],
            "electrical": [
                '["craft"="electrician"]',
                '["shop"="electronics"]'
            ],
            "cleaning": [
                '["shop"="laundry"]',
                '["office"="estate_agent"]'  # Cleaning services
            ],
            "tutoring": [
                '["amenity"="school"]',
                '["amenity"="college"]',
                '["amenity"="university"]'
            ]
        }

        if service_type not in osm_queries:
            return providers

        # Calculate bounding box around user location
        lat, lon = user_location.latitude, user_location.longitude
        # Approximate 1 degree ~ 111 km
        lat_offset = max_distance_km / 111.0
        lon_offset = max_distance_km / (111.0 * abs(lat))  # Adjust for latitude

        bbox = f"{lat - lat_offset},{lon - lon_offset},{lat + lat_offset},{lon + lon_offset}"

        for tag in osm_queries[service_type]:
            try:
                # Query OpenStreetMap using Overpass API
                query = f"""
                [out:json][timeout:25];
                (
                  node{tag}({bbox});
                  way{tag}({bbox});
                  relation{tag}({bbox});
                );
                out center;
                """

                result = self.overpass_api.query(query)

                for node in result.nodes:
                    if hasattr(node, 'tags') and 'name' in node.tags:
                        provider_location = Location(
                            latitude=node.lat,
                            longitude=node.lon,
                            name=node.tags.get('name', 'Unknown'),
                            landmark=self._extract_landmark_from_tags(node.tags)
                        )

                        distance = user_location.distance_to(provider_location)

                        if distance <= max_distance_km:
                            provider = ServiceProvider(
                                id=f"osm_{service_type}_{len(providers)}",
                                name=node.tags.get('name', f'{service_type.replace("_", " ").title()} Service'),
                                service_type=service_type,
                                location=provider_location,
                                price_range=self._estimate_price_range(service_type),
                                rating=self._estimate_rating(node.tags),
                                description=self._generate_description(node.tags, service_type),
                                accessibility=self._determine_accessibility(distance),
                                contact_info=node.tags.get('phone', node.tags.get('contact:phone', '+255-XXX-XXXXXX')),
                                operating_hours=node.tags.get('opening_hours', 'Mon-Sat 8AM-6PM')
                            )
                            providers.append(provider)

                # Limit results to avoid overwhelming the user
                if len(providers) >= 20:
                    break

                # Be respectful to the API
                time.sleep(1)

            except Exception as e:
                print(f"Error querying OSM for {service_type}: {e}")
                continue

        return providers

    def _extract_landmark_from_tags(self, tags: Dict) -> str:
        """Extract landmark information from OSM tags"""
        if 'addr:street' in tags:
            return tags['addr:street']
        elif 'addr:suburb' in tags:
            return tags['addr:suburb']
        elif 'addr:neighbourhood' in tags:
            return tags['addr:neighbourhood']
        else:
            return "Dar es Salaam"

    def _estimate_price_range(self, service_type: str) -> Tuple[float, float]:
        """Estimate price range based on service type for Tanzania"""
        price_ranges = {
            "auto_repair": (10000, 50000),  # TZS
            "medical": (5000, 20000),
            "hair_salon": (3000, 15000),
            "restaurant": (5000, 25000),
            "plumbing": (5000, 20000),
            "electrical": (3000, 15000),
            "cleaning": (2000, 10000),
            "tutoring": (5000, 20000)
        }
        return price_ranges.get(service_type, (5000, 20000))

    def _estimate_rating(self, tags: Dict) -> float:
        """Estimate rating based on available tags"""
        # In real implementation, this could come from review services
        # For now, return a reasonable default
        return 4.0

    def _generate_description(self, tags: Dict, service_type: str) -> str:
        """Generate description from OSM tags"""
        name = tags.get('name', 'Service Provider')
        description = f"{name} - {service_type.replace('_', ' ').title()} services"

        if 'opening_hours' in tags:
            description += f". Hours: {tags['opening_hours']}"

        return description

    def _determine_accessibility(self, distance: float) -> str:
        """Determine accessibility based on distance"""
        if distance <= 1.0:
            return "walking"
        elif distance <= 5.0:
            return "public_transport"
        else:
            return "vehicle"

    def get_nearby_landmarks(self, user_location: Location, max_distance_km: float = 5.0) -> List[str]:
        """Get nearby landmarks from OpenStreetMap"""
        if not OSM_AVAILABLE:
            return []

        landmarks = []

        try:
            # Query for tourist attractions, shops, amenities
            lat, lon = user_location.latitude, user_location.longitude
            lat_offset = max_distance_km / 111.0
            lon_offset = max_distance_km / (111.0 * abs(lat))

            bbox = f"{lat - lat_offset},{lon - lon_offset},{lat + lat_offset},{lon + lon_offset}"

            query = f"""
            [out:json][timeout:25];
            (
              node["tourism"]({bbox});
              node["historic"]({bbox});
              node["amenity"="place_of_worship"]({bbox});
              node["shop"="mall"]({bbox});
            );
            out;
            """

            result = self.overpass_api.query(query)

            for node in result.nodes:
                if hasattr(node, 'tags') and 'name' in node.tags:
                    distance = geodesic((user_location.latitude, user_location.longitude),
                                      (node.lat, node.lon)).km
                    if distance <= max_distance_km:
                        landmarks.append(f"{node.tags['name']} ({distance:.1f}km)")

            # Limit to top 5 landmarks
            landmarks = landmarks[:5]

        except Exception as e:
            print(f"Error getting nearby landmarks: {e}")

        return landmarks


# Tanzania-specific location data and helpers
class TanzaniaLocations:
    """Tanzania-specific location data and utilities"""

    # Major cities and their coordinates
    MAJOR_CITIES = {
        "dar es salaam": (-6.7924, 39.2083),
        "dodoma": (-6.1730, 35.7419),  # Capital
        "mwanza": (-2.5167, 32.9000),
        "arusha": (-3.3667, 36.6833),
        "mbeya": (-8.9000, 33.4500),
        "morogoro": (-6.8167, 37.6667),
        "tanga": (-5.0667, 39.1000),
        "kigoma": (-4.8833, 29.6333),
        "tabora": (-5.0167, 32.8000),
        "iringa": (-7.7667, 35.7000),
        "singida": (-4.8167, 34.7500),
        "liuli": (-11.0833, 34.6333),
        "musoma": (-1.5000, 33.8000),
        "songea": (-10.6833, 35.6500),
        "mpanda": (-6.3667, 31.0500)
    }

    # Dar es Salaam districts and areas
    DAR_ES_SALAAM_AREAS = {
        "kinondoni": (-6.7667, 39.1667),
        "ilala": (-6.8167, 39.1833),
        "temeke": (-6.8667, 39.2500),
        "ubungo": (-6.7833, 39.2333),
        "kigamboni": (-6.8333, 39.3167),
        "masaki": (-6.7333, 39.2833),
        "mikocheni": (-6.7667, 39.2333),
        "mlimini city": (-6.7667, 39.2167),
        "posta": (-6.8167, 39.2833),
        "jamhuri": (-6.8000, 39.2833),
        "mnazi mmoja": (-6.8167, 39.2833),
        "kariakoo": (-6.8167, 39.2667),
        "uhuru road": (-6.8167, 39.2833),
        "samora avenue": (-6.8167, 39.2833),
        "kilimanjaro avenue": (-6.8167, 39.2833),
        "azikiwe street": (-6.8167, 39.2833)
    }

    # Common landmarks in Dar es Salaam
    DAR_LANDMARKS = {
        "julius nyerere international airport": (-6.8781, 39.2026),
        "port of dar es salaam": (-6.8167, 39.2833),
        "national museum": (-6.1667, 39.2167),
        "state house": (-6.8000, 39.2833),
        "uhuru monument": (-6.8167, 39.2833),
        "kariakoo market": (-6.8167, 39.2667),
        "mlimani city shopping mall": (-6.7667, 39.2167),
        "slipway": (-6.8167, 39.2833),
        "cocacola kwanza road": (-6.8167, 39.2833),
        "garden avenue": (-6.8167, 39.2833)
    }

    @classmethod
    def get_location_from_text(cls, text: str) -> Optional[Location]:
        """Parse Tanzania-specific location text"""
        text_lower = text.lower().strip()

        # Check major cities
        for city, (lat, lon) in cls.MAJOR_CITIES.items():
            if city in text_lower or city.replace(" ", "") in text_lower:
                return Location(lat, lon, city.title(), city.title())

        # Check Dar es Salaam areas
        for area, (lat, lon) in cls.DAR_ES_SALAAM_AREAS.items():
            if area in text_lower or area.replace(" ", "") in text_lower:
                return Location(lat, lon, area.title(), f"Dar es Salaam - {area.title()}")

        # Check landmarks
        for landmark, (lat, lon) in cls.DAR_LANDMARKS.items():
            if any(word in text_lower for word in landmark.split()):
                return Location(lat, lon, landmark.title(), landmark.title())

        return None


# Currency conversion helper (Tanzanian Shilling to USD)
def tzs_to_usd(amount_tzs: float) -> float:
    """Convert Tanzanian Shilling to USD (approximate rate)"""
    # Current approximate rate: 1 USD = ~2300 TZS
    return amount_tzs / 2300.0


def usd_to_tzs(amount_usd: float) -> float:
    """Convert USD to Tanzanian Shilling"""
    return amount_usd * 2300.0
