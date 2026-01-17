#!/usr/bin/env python3
"""
Data models for the Location-Based Service Search Chatbot
Shared data structures used across modules.
"""

import math
from typing import Tuple
from dataclasses import dataclass
from enum import Enum


class BudgetRange(Enum):
    """Budget categories"""
    LOW_COST = "low-cost"
    MID_RANGE = "mid-range"
    PREMIUM = "premium"


@dataclass
class Location:
    """Location data structure"""
    latitude: float
    longitude: float
    name: str = ""
    landmark: str = ""

    def distance_to(self, other: 'Location') -> float:
        """Calculate distance between two locations using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(self.latitude)
        lon1_rad = math.radians(self.longitude)
        lat2_rad = math.radians(other.latitude)
        lon2_rad = math.radians(other.longitude)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c


@dataclass
class ServiceProvider:
    """Service provider data structure"""
    id: str
    name: str
    service_type: str
    location: Location
    price_range: Tuple[float, float]  # (min_price, max_price)
    rating: float
    description: str
    accessibility: str  # "walking", "public_transport", "vehicle"
    contact_info: str
    operating_hours: str
