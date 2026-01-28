#!/usr/bin/env python3
"""
Standalone WhatsApp Webhook Server for Tanzania Service Chatbot
Handles both Ghala and Meta WhatsApp webhooks

🧪 TESTING CONFIGURATION WARNING:
This file contains test-specific code and configurations that should NOT be used in production:
- Hardcoded test phone numbers
- Simplified security measures
- Test environment responses

For production deployment:
1. Remove test phone number validations
2. Implement proper authentication
3. Add rate limiting and security measures
4. Use production-grade responses
5. Implement comprehensive logging

⚠️  SECURITY NOTICE: This is a development/testing environment only!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'tanzania_services.db')

class DatabaseManager:
    """SQLite database manager for Tanzania Services chatbot"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    whatsapp_number TEXT UNIQUE NOT NULL,
                    name TEXT,
                    language TEXT DEFAULT 'en',
                    location_lat REAL,
                    location_lng REAL,
                    location_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    preferences TEXT,  -- JSON string for user preferences
                    session_token TEXT,
                    token_expires TIMESTAMP
                )
            ''')

            # Service providers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,  -- restaurant, medical, beauty, auto
                    whatsapp_number TEXT,
                    phone TEXT,
                    email TEXT,
                    location_lat REAL NOT NULL,
                    location_lng REAL NOT NULL,
                    location_name TEXT NOT NULL,
                    address TEXT,
                    description TEXT,
                    price_range TEXT,  -- e.g., "15000-45000"
                    rating REAL DEFAULT 0.0,
                    review_count INTEGER DEFAULT 0,
                    operating_hours TEXT,  -- JSON string
                    services_offered TEXT,  -- JSON string
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_documents TEXT,  -- JSON string
                    business_license TEXT,
                    owner_name TEXT,
                    owner_contact TEXT
                )
            ''')

            # Bookings/Appointments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    provider_id INTEGER NOT NULL,
                    service_type TEXT NOT NULL,
                    booking_date DATE NOT NULL,
                    booking_time TIME NOT NULL,
                    status TEXT DEFAULT 'pending',  -- pending, confirmed, completed, cancelled
                    notes TEXT,
                    total_amount REAL,
                    payment_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (provider_id) REFERENCES service_providers (id)
                )
            ''')

            # Reviews table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    provider_id INTEGER NOT NULL,
                    booking_id INTEGER,
                    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (provider_id) REFERENCES service_providers (id),
                    FOREIGN KEY (booking_id) REFERENCES bookings (id)
                )
            ''')

            # User sessions/messages history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    whatsapp_number TEXT NOT NULL,
                    message_type TEXT NOT NULL,  -- text, location, image, etc.
                    message_content TEXT,
                    bot_response TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            # Insert sample data if tables are empty
            self._insert_sample_data(cursor)

            conn.commit()
            logger.info("Database initialized successfully")

    def _insert_sample_data(self, cursor):
        """Insert sample service providers for testing"""
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM service_providers")
        if cursor.fetchone()[0] == 0:
            sample_providers = [
                {
                    'name': 'Beach Banda Restaurant',
                    'category': 'restaurant',
                    'phone': '+255712345678',
                    'location_lat': -6.7924,
                    'location_lng': 39.2727,
                    'location_name': 'Oyster Bay, Masaki Area, Dar es Salaam',
                    'address': 'Masaki Peninsula Road, Oyster Bay',
                    'description': 'Excellent seafood restaurant with ocean views',
                    'price_range': '15000-45000',
                    'rating': 4.2,
                    'review_count': 25,
                    'operating_hours': json.dumps({
                        'monday': '11:00-23:00',
                        'tuesday': '11:00-23:00',
                        'wednesday': '11:00-23:00',
                        'thursday': '11:00-23:00',
                        'friday': '11:00-23:00',
                        'saturday': '11:00-23:00',
                        'sunday': '11:00-23:00'
                    }),
                    'services_offered': json.dumps(['seafood', 'grilled fish', 'lobster', 'prawns', 'local cuisine']),
                    'is_verified': True,
                    'owner_name': 'John Mgaya',
                    'owner_contact': '+255712345678'
                },
                {
                    'name': 'Aga Khan Hospital',
                    'category': 'medical',
                    'phone': '+255222115151',
                    'location_lat': -6.8167,
                    'location_lng': 39.2892,
                    'location_name': 'Ohio Street, City Center, Dar es Salaam',
                    'address': 'P.O. Box 2289, Dar es Salaam',
                    'description': 'Multi-specialty hospital with 24/7 emergency services',
                    'price_range': '25000-50000',
                    'rating': 4.6,
                    'review_count': 45,
                    'operating_hours': json.dumps({
                        'monday': '00:00-23:59',
                        'tuesday': '00:00-23:59',
                        'wednesday': '00:00-23:59',
                        'thursday': '00:00-23:59',
                        'friday': '00:00-23:59',
                        'saturday': '00:00-23:59',
                        'sunday': '00:00-23:59'
                    }),
                    'services_offered': json.dumps(['emergency care', 'surgery', 'maternity', 'pediatrics', 'internal medicine']),
                    'is_verified': True,
                    'owner_name': 'Aga Khan Health Services',
                    'owner_contact': '+255222115151'
                },
                {
                    'name': 'Masaki Hair Studio & Spa',
                    'category': 'beauty',
                    'phone': '+255713456789',
                    'location_lat': -6.7915,
                    'location_lng': 39.2742,
                    'location_name': 'Masaki Area, Dar es Salaam',
                    'address': 'Masaki Shopping Center',
                    'description': 'Premium salon with full beauty services and spa treatments',
                    'price_range': '8000-35000',
                    'rating': 4.4,
                    'review_count': 32,
                    'operating_hours': json.dumps({
                        'monday': '10:00-20:00',
                        'tuesday': '10:00-20:00',
                        'wednesday': '10:00-20:00',
                        'thursday': '10:00-20:00',
                        'friday': '10:00-20:00',
                        'saturday': '10:00-20:00',
                        'sunday': '12:00-18:00'
                    }),
                    'services_offered': json.dumps(['haircuts', 'coloring', 'spa treatments', 'manicure', 'pedicure', 'facial treatments']),
                    'is_verified': True,
                    'owner_name': 'Fatima Omar',
                    'owner_contact': '+255713456789'
                }
            ]

            for provider in sample_providers:
                cursor.execute('''
                    INSERT INTO service_providers
                    (name, category, phone, location_lat, location_lng, location_name, address,
                     description, price_range, rating, review_count, operating_hours,
                     services_offered, is_verified, owner_name, owner_contact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    provider['name'], provider['category'], provider['phone'],
                    provider['location_lat'], provider['location_lng'], provider['location_name'],
                    provider['address'], provider['description'], provider['price_range'],
                    provider['rating'], provider['review_count'], provider['operating_hours'],
                    provider['services_offered'], provider['is_verified'],
                    provider['owner_name'], provider['owner_contact']
                ))

    # User management methods
    def register_user(self, whatsapp_number: str, name: str = None) -> Optional[Dict]:
        """Register a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if user already exists
                cursor.execute("SELECT * FROM users WHERE whatsapp_number = ?", (whatsapp_number,))
                existing_user = cursor.fetchone()

                if existing_user:
                    # Update existing user
                    cursor.execute('''
                        UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE whatsapp_number = ?
                    ''', (name, whatsapp_number))
                    conn.commit()
                    return dict(existing_user)

                # Create new user
                cursor.execute('''
                    INSERT INTO users (whatsapp_number, name) VALUES (?, ?)
                ''', (whatsapp_number, name))

                user_id = cursor.lastrowid
                conn.commit()

                # Get the created user
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None

        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return None

    def get_user_by_number(self, whatsapp_number: str) -> Optional[Dict]:
        """Get user by WhatsApp number"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE whatsapp_number = ?", (whatsapp_number,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def update_user_location(self, whatsapp_number: str, lat: float, lng: float, location_name: str = None):
        """Update user location"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET location_lat = ?, location_lng = ?, location_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE whatsapp_number = ?
                ''', (lat, lng, location_name, whatsapp_number))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating user location: {e}")
            return False

    # Service provider methods
    def get_service_providers(self, category: str = None, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get service providers with optional category filter"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if category:
                    cursor.execute('''
                        SELECT * FROM service_providers
                        WHERE category = ? AND is_active = TRUE
                        ORDER BY rating DESC, review_count DESC
                        LIMIT ? OFFSET ?
                    ''', (category, limit, offset))
                else:
                    cursor.execute('''
                        SELECT * FROM service_providers
                        WHERE is_active = TRUE
                        ORDER BY rating DESC, review_count DESC
                        LIMIT ? OFFSET ?
                    ''', (limit, offset))

                providers = cursor.fetchall()
                return [dict(provider) for provider in providers]
        except Exception as e:
            logger.error(f"Error getting service providers: {e}")
            return []

    def search_providers_near_location(self, lat: float, lng: float, category: str = None, radius_km: float = 5.0) -> List[Dict]:
        """Search for providers near a location"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Simple distance calculation (not as accurate as proper geospatial, but works for demo)
                query = '''
                    SELECT *,
                           ((location_lat - ?) * (location_lat - ?)) + ((location_lng - ?) * (location_lng - ?)) as distance_squared
                    FROM service_providers
                    WHERE is_active = TRUE
                '''

                params = [lat, lat, lng, lng]

                if category:
                    query += ' AND category = ?'
                    params.append(category)

                query += ' ORDER BY distance_squared ASC LIMIT 10'

                cursor.execute(query, params)
                providers = cursor.fetchall()

                # Calculate actual distance and filter by radius
                result = []
                for provider in providers:
                    provider_dict = dict(provider)
                    distance = self._calculate_distance(lat, lng, provider_dict['location_lat'], provider_dict['location_lng'])
                    if distance <= radius_km:
                        provider_dict['distance_km'] = round(distance, 1)
                        result.append(provider_dict)

                return result
        except Exception as e:
            logger.error(f"Error searching providers: {e}")
            return []

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        import math

        R = 6371  # Earth's radius in kilometers

        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)

        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2) * math.sin(dlng/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    # Booking methods
    def create_booking(self, user_id: int, provider_id: int, service_type: str, booking_date: str, booking_time: str, notes: str = None) -> Optional[Dict]:
        """Create a new booking"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO bookings (user_id, provider_id, service_type, booking_date, booking_time, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, provider_id, service_type, booking_date, booking_time, notes))

                booking_id = cursor.lastrowid
                conn.commit()

                # Get the created booking
                cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
                booking = cursor.fetchone()
                return dict(booking) if booking else None
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            return None

    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Get user's bookings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT b.*, sp.name as provider_name, sp.category, sp.location_name
                    FROM bookings b
                    JOIN service_providers sp ON b.provider_id = sp.id
                    WHERE b.user_id = ?
                    ORDER BY b.created_at DESC
                ''', (user_id,))
                bookings = cursor.fetchall()
                return [dict(booking) for booking in bookings]
        except Exception as e:
            logger.error(f"Error getting user bookings: {e}")
            return []

    # Review methods
    def add_review(self, user_id: int, provider_id: int, rating: int, comment: str = None, booking_id: int = None) -> bool:
        """Add a review for a service provider"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO reviews (user_id, provider_id, booking_id, rating, comment)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, provider_id, booking_id, rating, comment))

                # Update provider rating
                self._update_provider_rating(cursor, provider_id)

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding review: {e}")
            return False

    def _update_provider_rating(self, cursor, provider_id: int):
        """Update provider's average rating and review count"""
        cursor.execute('''
            SELECT AVG(rating) as avg_rating, COUNT(*) as review_count
            FROM reviews
            WHERE provider_id = ?
        ''', (provider_id,))

        result = cursor.fetchone()
        if result:
            avg_rating = result['avg_rating'] or 0.0
            review_count = result['review_count'] or 0

            cursor.execute('''
                UPDATE service_providers
                SET rating = ?, review_count = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (round(avg_rating, 1), review_count, provider_id))

    def get_provider_reviews(self, provider_id: int, limit: int = 5) -> List[Dict]:
        """Get reviews for a provider"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT r.*, u.name as user_name
                    FROM reviews r
                    JOIN users u ON r.user_id = u.id
                    WHERE r.provider_id = ?
                    ORDER BY r.created_at DESC
                    LIMIT ?
                ''', (provider_id, limit))
                reviews = cursor.fetchall()
                return [dict(review) for review in reviews]
        except Exception as e:
            logger.error(f"Error getting provider reviews: {e}")
            return []

    def get_provider_by_id(self, provider_id: int) -> Optional[Dict]:
        """Get a service provider by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM service_providers WHERE id = ?", (provider_id,))
                provider = cursor.fetchone()
                return dict(provider) if provider else None
        except Exception as e:
            logger.error(f"Error getting provider: {e}")
            return None

    # Message history
    def log_message(self, whatsapp_number: str, message_type: str, message_content: str, bot_response: str = None, user_id: int = None):
        """Log message for analytics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO message_history (user_id, whatsapp_number, message_type, message_content, bot_response)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, whatsapp_number, message_type, message_content, bot_response))
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging message: {e}")

# Initialize database
db = DatabaseManager()

app = Flask(__name__)

# Enable CORS for all origins (required for ngrok/webhook access)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-App-Id"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# ===== WEBHOOK ROUTES =====

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Verify webhook with WhatsApp provider (Meta or Ghala)
    This endpoint handles the initial webhook verification
    """
    from env_config import Config

    # Get the appropriate webhook token based on provider
    if Config.WHATSAPP_PROVIDER == 'meta':
        webhook_token = Config.WHATSAPP_WEBHOOK_TOKEN
    elif Config.WHATSAPP_PROVIDER == 'ghala':
        webhook_token = Config.GHALA_WEBHOOK_TOKEN
    else:
        webhook_token = 'tanzania_service_bot'

    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    logger.info(f"Webhook verification attempt - Mode: {mode}, Token: {token[:10]}...")

    if mode == 'subscribe' and token == webhook_token:
        logger.info("✅ Webhook verified successfully!")
        return challenge, 200
    else:
        logger.warning("❌ Webhook verification failed")
        return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    """
    Handle incoming WhatsApp messages from both providers
    """
    try:
        data = request.get_json()
        logger.info(f"📨 Received webhook data from {request.remote_addr}")

        if not data:
            logger.warning("No data received")
            return jsonify({'status': 'error', 'message': 'No data'}), 400

        if 'messages' in data:
            print("Ghala WhatsApp - received")
            return handle_ghala_whatsapp(data)

        # Route based on configured provider since Ghala may use Meta's webhook format
        from env_config import Config

        if Config.WHATSAPP_PROVIDER == 'meta':
            if 'object' in data and data['object'] == 'whatsapp_business_account':
                return handle_meta_whatsapp(data)
            else:
                logger.warning(f"Meta provider configured but received non-Meta format: {list(data.keys())}")
                return jsonify({'status': 'error', 'message': 'Invalid Meta format'}), 400
        elif Config.WHATSAPP_PROVIDER == 'ghala':
            # Ghala may send in Meta format or Ghala format
            if 'object' in data and data['object'] == 'whatsapp_business_account':
                print("Ghala WhatsApp (Meta format) - received")
                return handle_ghala_whatsapp_via_meta(data)
            elif 'messages' in data:
                return handle_ghala_whatsapp(data)
            else:
                logger.warning(f"Unknown Ghala webhook format: {list(data.keys())}")
                return jsonify({'status': 'error', 'message': 'Unknown Ghala format'}), 400
        else:
            logger.warning(f"Unknown provider configured: {Config.WHATSAPP_PROVIDER}")
            return jsonify({'status': 'error', 'message': 'Unknown provider'}), 400

    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def handle_directions_request(text):
    """
    Handle specific directions requests to named locations
    """
    text_lower = text.lower()

    # Restaurant directions
    if 'beach banda' in text_lower:
        maps_url = "https://www.google.com/maps/dir/?api=1&destination=Beach+Banda+Restaurant+Oyster+Bay+Dar+es+Salaam"
        return f"""🗺️ *Directions to Beach Banda Restaurant*

📍 *Location:* Oyster Bay, Masaki Area, Dar es Salaam
🗺️ *Coordinates:* -6.7924, 39.2727 (approx.)
🚗 *Address:* Masaki Peninsula Road, Oyster Bay

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~15-20 minutes
• Cost: TZS 5,000-8,000
• Look for the blue building with ocean views

🚌 *By Public Transport:*
• Take daladala route 23 or 24 to Masaki
• Get off at Oyster Bay stop
• Walk 200m towards the beach

🕐 *Business Hours:* 11:00 AM - 11:00 PM
☎️ *Contact:* Call ahead for reservations

🌐 *Open in Google Maps:* {maps_url}
📱 *Tap the link above to get turn-by-turn directions!*

💡 *Navigation Tip:* The restaurant is right on the beach with excellent ocean views. Parking available on-site.

🍽️ *Quick Actions:*
• Reply "call Beach Banda" to get their number
• Reply "menu" for food recommendations
• Reply "restaurants" for more dining options

Would you like me to help you with anything else? 🍽️"""

    elif 'terrace' in text_lower:
        maps_url = "https://www.google.com/maps/dir/?api=1&destination=The+Terrace+Restaurant+Masaki+Dar+es+Salaam"
        return f"""🗺️ *Directions to The Terrace Restaurant & Bar*

📍 *Location:* Masaki Peninsula, Dar es Salaam
🗺️ *Coordinates:* -6.7892, 39.2751 (approx.)
🚗 *Address:* The Kilimanjaro Hotel, Masaki

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~12-18 minutes
• Cost: TZS 6,000-10,000
• Located in the Kilimanjaro Hotel complex

🚌 *By Public Transport:*
• Take daladala to Masaki roundabout
• Continue walking towards the peninsula
• Look for the hotel entrance

🕐 *Business Hours:* 12:00 PM - 12:00 AM
☎️ *Contact:* Part of Kilimanjaro Hotel - call hotel reception

🌐 *Open in Google Maps:* {maps_url}
📱 *Tap the link above to get turn-by-turn directions!*

💡 *Navigation Tip:* Elegant rooftop dining with panoramic views of the Indian Ocean. Valet parking available.

🥂 *Quick Actions:*
• Reply "call Terrace" to get hotel number
• Reply "book table" for reservation help
• Reply "restaurants" for more dining options

Would you like me to help you with anything else? 🥂"""

    # Medical facility directions
    elif 'aga khan' in text_lower or 'aga khan hospital' in text_lower:
        maps_url = "https://www.google.com/maps/dir/?api=1&destination=Aga+Khan+Hospital+Dar+es+Salaam"
        return f"""🗺️ *Directions to Aga Khan Hospital Dar es Salaam*

📍 *Location:* Ohio Street, City Center, Dar es Salaam
🗺️ *Coordinates:* -6.8167, 39.2892 (approx.)
🚗 *Address:* P.O. Box 2289, Dar es Salaam

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• Most accessible location in CBD
• Cost: TZS 2,000-5,000 from nearby areas
• Clearly marked hospital entrance

🚌 *By Public Transport:*
• Multiple daladala routes stop nearby
• Walking distance from most city center locations
• Well-known landmark in the business district

🚨 *Emergency Services:* 24/7 Emergency Department
☎️ *Contact:* +255 22 211 5151 (Main) / +255 22 211 5152 (Emergency)

🌐 *Open in Google Maps:* {maps_url}
📱 *Tap the link above to get turn-by-turn directions!*

💡 *Navigation Tip:* Large modern hospital with clear signage. Emergency entrance on the side street. Ample parking available.

🏥 *Quick Actions:*
• Reply "emergency" for urgent care info
• Reply "appointment" for booking help
• Reply "medical clinics" for more healthcare options

For emergencies, proceed directly to the hospital. 🏥"""

    elif 'masaki medical' in text_lower:
        maps_url = "https://www.google.com/maps/dir/?api=1&destination=Masaki+Medical+Centre+Dar+es+Salaam"
        return f"""🗺️ *Directions to Masaki Medical Centre*

📍 *Location:* Masaki Area, Dar es Salaam
🗺️ *Coordinates:* -6.7901, 39.2738 (approx.)
🚗 *Address:* Masaki Commercial Area

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~15-20 minutes
• Cost: TZS 5,000-8,000
• Look for the medical center signage

🚌 *By Public Transport:*
• Take daladala route 23 or 24 to Masaki
• Get off at Masaki commercial area
• Short walk to the medical center

🕐 *Business Hours:* 8:00 AM - 8:00 PM (Mon-Sat)
☎️ *Contact:* +255 XX XXX XXXX
🚨 *Emergency:* 24/7 services available

🌐 *Open in Google Maps:* {maps_url}
📱 *Tap the link above to get turn-by-turn directions!*

💡 *Navigation Tip:* Modern medical facility in the commercial area. Easy parking and clear signage.

🏥 *Quick Actions:*
• Reply "call Masaki Medical" for contact info
• Reply "appointment" for booking help
• Reply "medical clinics" for more healthcare options

Would you like me to help you with anything else? 🏥"""

    # Hair salon directions
    elif 'masaki hair' in text_lower:
        maps_url = "https://www.google.com/maps/dir/?api=1&destination=Masaki+Hair+Studio+Spa+Dar+es+Salaam"
        return f"""🗺️ *Directions to Masaki Hair Studio & Spa*

📍 *Location:* Masaki Area, Dar es Salaam
🗺️ *Coordinates:* -6.7915, 39.2742 (approx.)
🚗 *Address:* Masaki Shopping Center

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~15-20 minutes
• Cost: TZS 5,000-8,000
• Located in Masaki shopping complex

🚌 *By Public Transport:*
• Take daladala to Masaki roundabout
• Walk to the shopping center
• Look for beauty salon signage

🕐 *Business Hours:* 10:00 AM - 8:00 PM (Mon-Sun)
☎️ *Contact:* +255 XX XXX XXXX (Call for appointment)

🌐 *Open in Google Maps:* {maps_url}
📱 *Tap the link above to get turn-by-turn directions!*

💡 *Navigation Tip:* Premium salon in upscale shopping area. Professional styling and spa services available.

✂️ *Quick Actions:*
• Reply "call Masaki Hair" for appointment
• Reply "services" to see available treatments
• Reply "hair salons" for more beauty options

Would you like me to help you with anything else? ✂️"""

    else:
        # Generic directions response for unrecognized places
        place_name = text.replace('directions to', '').replace('direction', '').strip()
        return f"""🗺️ *Directions Request for "{place_name}"*

I don't have specific directions for "{place_name}" in my database, but I can help you find similar services!

🇹🇿 *Try these options:*

🍽️ *For Restaurants:*
• "restaurants" - Browse dining options
• "direction Beach Banda" or "directions to Beach Banda" - Popular seafood restaurant

🏥 *For Medical Services:*
• "medical clinics" - Find healthcare facilities
• "direction Aga Khan Hospital" or "directions to Aga Khan Hospital" - Major hospital

✂️ *For Beauty Services:*
• "hair salons" - Find beauty salons
• "direction Masaki Hair Studio" or "directions to Masaki Hair Studio" - Premium salon

💡 *Alternative:* Share your current location, and I'll recommend the best services near you!

What type of service are you looking for? 📍"""

def handle_call_request(text):
    """
    Handle contact/call requests for specific services
    """
    text_lower = text.lower()

    if 'beach banda' in text_lower:
        return """📞 *Beach Banda Restaurant Contact Info*

☎️ *Phone:* +255 XX XXX XXXX
📧 *Email:* info@beachbanda.co.tz
🌐 *Website:* www.beachbanda.co.tz

🕐 *Business Hours:*
• Lunch: 11:00 AM - 3:00 PM
• Dinner: 6:00 PM - 11:00 PM
• Bar: Until 12:00 AM

💡 *Call now to make a reservation or ask about availability!*

Would you like me to help you with directions or menu information? 🍽️"""

    elif 'terrace' in text_lower:
        return """📞 *The Terrace Restaurant & Bar Contact Info*

☎️ *Phone:* +255 XX XXX XXXX (Hotel Reception)
📧 *Email:* reservations@kilimanjarohotel.com
🌐 *Website:* www.kilimanjarohotel.com

🕐 *Business Hours:*
• Lunch: 12:00 PM - 3:00 PM
• Dinner: 6:00 PM - 11:00 PM
• Bar: Until 12:00 AM

💡 *Part of Kilimanjaro Hotel - call reception for reservations!*

Would you like me to help you with directions or hotel information? 🥂"""

    elif 'aga khan' in text_lower or 'aga khan hospital' in text_lower:
        return """📞 *Aga Khan Hospital Dar es Salaam*

☎️ *Main Line:* +255 22 211 5151
🚨 *Emergency:* +255 22 211 5152
📧 *Email:* info@akhst.org
🌐 *Website:* www.akhst.org

🕐 *Services:*
• 24/7 Emergency Department
• Appointments: 8:00 AM - 5:00 PM
• Specialist consultations available

⚕️ *Departments:*
• Emergency Medicine
• Internal Medicine
• Surgery
• Pediatrics
• Obstetrics & Gynecology

💡 *For appointments, call the main line and ask for the relevant department.*

Would you like me to help you with directions or emergency information? 🏥"""

    elif 'masaki medical' in text_lower:
        return """📞 *Masaki Medical Centre Contact Info*

☎️ *Phone:* +255 XX XXX XXXX
🚨 *Emergency:* +255 XX XXX XXXX (24/7)
📧 *Email:* info@masakimc.co.tz

🕐 *Services:*
• General Practice
• Pediatrics
• Diagnostics
• Minor Procedures

💡 *Call for appointments or emergency services!*

Would you like me to help you with directions? 🏥"""

    elif 'masaki hair' in text_lower:
        return """📞 *Masaki Hair Studio & Spa Contact Info*

☎️ *Phone:* +255 XX XXX XXXX
📧 *Email:* info@masakihair.co.tz
🌐 *Website:* www.macakihair.co.tz

🕐 *Business Hours:*
• Monday-Saturday: 10:00 AM - 8:00 PM
• Sunday: 12:00 PM - 6:00 PM

💇‍♀️ *Services:*
• Haircuts & Styling
• Color Treatments
• Spa Services
• Beauty Treatments

💡 *Call now to book your appointment!*

Would you like me to help you with directions or see available services? ✂️"""

    else:
        service_name = text.replace('call', '').replace('contact', '').strip()
        return f"""📞 *Contact Request for "{service_name}"*

I don't have the direct contact information for "{service_name}" in my database, but I can help you find similar services!

🇹🇿 *Try these options:*

🍽️ *For Restaurants:*
• "restaurants" - Browse dining options
• "call Beach Banda" - Restaurant contact

🏥 *For Medical Services:*
• "medical clinics" - Find healthcare facilities
• "call Aga Khan Hospital" - Hospital contact

✂️ *For Beauty Services:*
• "hair salons" - Find beauty salons
• "call Masaki Hair Studio" - Salon contact

💡 *Need contact info?* Reply with the specific service name!

What type of service contact information do you need? 📞"""

def handle_appointment_request(text):
    """
    Handle appointment booking requests
    """
    return """📅 *Appointment Booking Service*

🇹🇿 *Book appointments for Tanzanian services:*

🏥 *Medical Appointments:*
• Reply "medical appointment" for clinic bookings
• Reply "dental appointment" for dental care
• Reply "specialist appointment" for specialist care

✂️ *Beauty Appointments:*
• Reply "hair appointment" for salon booking
• Reply "spa appointment" for spa treatments
• Reply "nail appointment" for manicure/pedicure

💡 *How booking works:*
1. Choose your service type above
2. I'll provide contact information
3. Call directly to book your appointment
4. Confirm date, time, and any requirements

⚡ *Popular Services:*
• General check-ups
• Hair styling & treatments
• Dental cleanings
• Specialist consultations

What type of appointment would you like to book? 📅"""

def handle_emergency_request(text):
    """
    Handle emergency service requests
    """
    return """🚨 *Emergency Services in Tanzania*

🇹🇿 *Critical Emergency Numbers:*

🚑 *Emergency Hotline:* 112 (All emergencies)
🚔 *Police:* 112 or 255 22 211 XXXX
🚒 *Fire Department:* 114
🏥 *Medical Emergency:* 112

🆘 *Medical Emergencies:*
• Heart attack or chest pain
• Severe bleeding
• Difficulty breathing
• Loss of consciousness
• Severe injuries

🏥 *Nearest Emergency Facilities:*

🏥 *Aga Khan Hospital*
📍 Ohio Street, City Center
☎️ +255 22 211 5152 (Emergency)
🕐 24/7 Emergency Services
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Aga+Khan+Hospital+Dar+es+Salaam

🏥 *Muhimbili National Hospital*
📍 Upanga Area
☎️ Emergency Department
🕐 24/7 Emergency Services
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Muhimbili+National+Hospital+Dar+es+Salaam

💡 *What to do in an emergency:*
1. Stay calm and call 112
2. Give your exact location
3. Describe the emergency clearly
4. Follow dispatcher instructions

⚠️ *For immediate life-threatening emergencies, go directly to the nearest hospital!*

Are you experiencing a medical emergency right now? 🚨"""

def handle_booking_request(text, user):
    """Handle booking/appointment requests"""
    if not user:
        return "📝 *Registration Required*\n\nPlease start a conversation with 'hi' or 'hello' to register first!"

    text_lower = text.lower()

    # Parse booking request - try to extract service and provider
    booking_info = parse_booking_request(text_lower)

    if not booking_info:
        return """📅 *Book an Appointment*

🇹🇿 *How to book:*

1️⃣ *Tell me what service:* "book restaurant" or "book medical"
2️⃣ *Specify the provider:* "book at Beach Banda" or "book at Aga Khan"
3️⃣ *Include date/time:* "book tomorrow at 2pm"

💡 *Examples:*
• "book restaurant at Beach Banda tomorrow 7pm"
• "book medical appointment at Aga Khan next Monday"
• "book hair appointment at Masaki Hair Studio"

📝 *Available Services:*
🍽️ Restaurants | 🏥 Medical | ✂️ Beauty | 🏪 Auto Repair

What would you like to book? 📅"""

    try:
        # Create booking in database
        booking = db.create_booking(
            user_id=user['id'],
            provider_id=booking_info['provider_id'],
            service_type=booking_info['service_type'],
            booking_date=booking_info['date'],
            booking_time=booking_info['time'],
            notes=booking_info.get('notes', '')
        )

        if booking:
            provider = db.get_provider_by_id(booking['provider_id'])
            return f"""✅ *Booking Confirmed!*

📅 *Booking Details:*
🎯 *Service:* {booking['service_type'].title()}
🏢 *Provider:* {provider['name'] if provider else 'Service Provider'}
📆 *Date:* {booking['booking_date']}
🕐 *Time:* {booking['booking_time']}
📊 *Status:* {booking['status'].title()}
🆔 *Booking ID:* #{booking['id']}

💡 *Next Steps:*
• You'll receive a confirmation call/text
• Arrive 10 minutes early
• Bring any required documents

❌ *Need to cancel?* Reply "cancel booking #{booking['id']}"

Would you like to add this to your calendar? 📅"""
        else:
            return "❌ *Booking Failed*\n\nSorry, I couldn't create your booking. Please try again or contact the service provider directly."

    except Exception as e:
        logger.error(f"Booking error: {e}")
        return "❌ *Booking Error*\n\nThere was an issue creating your booking. Please try again later."

def parse_booking_request(text):
    """Parse booking request to extract booking information"""
    # This is a simple parser - in production, you'd use NLP
    text_lower = text.lower()

    # Extract service type
    service_type = None
    if 'restaurant' in text_lower:
        service_type = 'restaurant'
    elif 'medical' in text_lower or 'clinic' in text_lower:
        service_type = 'medical'
    elif 'hair' in text_lower or 'beauty' in text_lower or 'salon' in text_lower:
        service_type = 'beauty'
    elif 'auto' in text_lower or 'repair' in text_lower:
        service_type = 'auto'

    if not service_type:
        return None

    # Try to find provider
    provider_id = None
    if 'beach banda' in text_lower:
        provider_id = 1  # Beach Banda Restaurant
    elif 'aga khan' in text_lower:
        provider_id = 2  # Aga Khan Hospital
    elif 'masaki hair' in text_lower:
        provider_id = 3  # Masaki Hair Studio

    if not provider_id:
        return None

    # Extract date/time (simplified)
    booking_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')  # Tomorrow by default
    booking_time = '14:00'  # 2 PM by default

    # Try to parse time mentions
    if 'tomorrow' in text_lower:
        booking_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'today' in text_lower:
        booking_date = datetime.now().strftime('%Y-%m-%d')

    # Parse time (very basic)
    import re
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        ampm = time_match.group(3)

        if ampm and ampm.lower() == 'pm' and hour != 12:
            hour += 12
        elif ampm and ampm.lower() == 'am' and hour == 12:
            hour = 0

        booking_time = f"{hour:02d}:{minute:02d}"

    return {
        'service_type': service_type,
        'provider_id': provider_id,
        'date': booking_date,
        'time': booking_time,
        'notes': f"Booked via WhatsApp chatbot - {text}"
    }

def handle_review_request(text, user):
    """Handle review/rating requests"""
    if not user:
        return "⭐ *Registration Required*\n\nPlease start a conversation with 'hi' or 'hello' to register first!"

    text_lower = text.lower()

    # Check if they want to see reviews or add a review
    if 'see reviews' in text_lower or 'read reviews' in text_lower:
        # Extract provider name
        provider_id = None
        if 'beach banda' in text_lower:
            provider_id = 1
        elif 'aga khan' in text_lower:
            provider_id = 2
        elif 'masaki hair' in text_lower:
            provider_id = 3

        if provider_id:
            reviews = db.get_provider_reviews(provider_id, limit=3)
            provider = db.get_provider_by_id(provider_id)

            if provider and reviews:
                response = f"⭐ *Reviews for {provider['name']}*\n\n"
                response += f"📊 *Overall Rating:* {provider['rating']}/5 ({provider['review_count']} reviews)\n\n"

                for review in reviews:
                    response += f"⭐ *{review['rating']}/5* by {review.get('user_name', 'Anonymous')}\n"
                    if review['comment']:
                        response += f"💬 \"{review['comment'][:100]}{'...' if len(review['comment']) > 100 else ''}\"\n"
                    response += f"📅 {review['created_at'][:10]}\n\n"

                response += "💡 *Want to leave a review?* Reply \"review [provider name] [rating] [comment]\""
                return response

        return "⭐ *See Reviews*\n\nTell me which service you'd like to see reviews for:\n\n• \"reviews Beach Banda\"\n• \"reviews Aga Khan Hospital\"\n• \"reviews Masaki Hair Studio\""

    # Parse review submission
    import re
    review_match = re.search(r'review\s+(\w+(?:\s+\w+)*)\s+(\d)\s+(.+)', text_lower)
    if review_match:
        provider_name = review_match.group(1).lower()
        rating = int(review_match.group(2))
        comment = review_match.group(3)

        if not (1 <= rating <= 5):
            return "⭐ *Invalid Rating*\n\nPlease use a rating between 1-5 stars."

        # Find provider
        provider_id = None
        if 'beach banda' in provider_name:
            provider_id = 1
        elif 'aga khan' in provider_name:
            provider_id = 2
        elif 'masaki hair' in provider_name:
            provider_id = 3

        if provider_id and db.add_review(user['id'], provider_id, rating, comment):
            return f"✅ *Review Submitted!*\n\n⭐ *{rating}/5 stars* for {provider_name.title()}\n💬 \"{comment}\"\n\nThank you for your feedback! It helps other users find great services. 🙏"
        else:
            return "❌ *Review Failed*\n\nSorry, I couldn't submit your review. Please try again."

    return """⭐ *Leave a Review*

🇹🇿 *How to review a service:*

📝 *Format:* "review [provider] [rating 1-5] [comment]"

💡 *Examples:*
• "review Beach Banda 5 Excellent seafood!"
• "review Aga Khan Hospital 4 Good service"
• "review Masaki Hair Studio 5 Amazing experience"

📊 *To see reviews:* "see reviews [provider name]"

Which service would you like to review? ⭐"""

def handle_view_bookings(user):
    """Handle viewing user's bookings"""
    if not user:
        return "📅 *Registration Required*\n\nPlease start a conversation with 'hi' or 'hello' to register first!"

    bookings = db.get_user_bookings(user['id'])

    if not bookings:
        return """📅 *No Bookings Found*

You don't have any upcoming bookings.

🇹🇿 *Ready to book?*
• "book restaurant" - Reserve a table
• "book medical appointment" - Schedule healthcare
• "book hair appointment" - Book beauty services

What would you like to book? 📅"""

    response = f"📅 *Your Bookings ({len(bookings)} total)*\n\n"

    for booking in bookings[:5]:  # Show last 5 bookings
        status_emoji = {
            'pending': '⏳',
            'confirmed': '✅',
            'completed': '✔️',
            'cancelled': '❌'
        }.get(booking['status'], '❓')

        response += f"{status_emoji} *Booking #{booking['id']}*\n"
        response += f"🎯 {booking['service_type'].title()} at {booking['provider_name']}\n"
        response += f"📆 {booking['booking_date']} at {booking['booking_time']}\n"
        response += f"📍 {booking['location_name']}\n"
        response += f"📊 Status: {booking['status'].title()}\n\n"

    response += "💡 *Manage bookings:*\n• \"cancel booking #[id]\" to cancel\n• \"reschedule booking #[id]\" to change"

    return response

def handle_meta_whatsapp(data):
    """
    Handle Meta WhatsApp webhook format
    """
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    messages = change.get('value', {}).get('messages', [])
                    contacts = change.get('value', {}).get('contacts', [])

                    for message in messages:
                        sender_id = message.get('from')
                        message_type = message.get('type')

                        logger.info(f"Meta WhatsApp - {message_type} from {sender_id}")

                        # 🔓 OPEN ACCESS: Allow all senders for demo purposes
                        # ⚠️  WARNING: This allows anyone to send messages!
                        # PRODUCTION SECURITY REQUIREMENTS:
                        # 1. Implement proper user authentication
                        # 2. Add rate limiting (max 1000 messages/hour per user)
                        # 3. Validate phone number ownership
                        # 4. Add spam protection
                        # 5. Log all interactions for audit purposes

                        logger.info(f"✅ Open access - sender: {sender_id} (DEMO ENVIRONMENT)")

                        if message_type == 'text':
                            text = message.get('text', {}).get('body', '')
                            response = process_message(text, sender_id)
                            send_meta_reply(sender_id, response)

                        elif message_type == 'location':
                            location = message.get('location', {})
                            lat = location.get('latitude')
                            lng = location.get('longitude')

                            # Save location to database
                            try:
                                from osm_integration import OpenStreetMapIntegration
                                osm = OpenStreetMapIntegration()
                                location_name = osm.reverse_geocode(lat, lng)
                            except:
                                location_name = f"Coordinates: {lat:.4f}, {lng:.4f}"

                            db.update_user_location(sender_id, lat, lng, location_name)

                            # Log location message
                            db.log_message(sender_id, 'location', f"{lat},{lng}", user_id=user.get('id') if user else None)

                            # Create location pin message
                            location_pin = f"""📍 *Location Received!*

🗺️ *Your Coordinates:* {lat:.4f}, {lng:.4f}
🏷️ *Location:* {location_name}

🌐 *View on Google Maps:* https://www.google.com/maps?q={lat},{lng}
📱 *Tap here to open in Maps app*

🇹🇿 *Tanzania Services Near You:*

Based on your shared location, I can help you find:

🍽️ *Restaurants within 5km*
🏥 *Medical clinics within 5km*
✂️ *Beauty salons within 5km*
🏪 *Auto repair services within 5km*

💡 *Quick Commands:*
• "restaurants near me" - Find dining options
• "medical clinics near me" - Healthcare facilities
• "hair salons near me" - Beauty services
• "auto repair near me" - Car services

🚀 *Get Started:*
Reply with any of the commands above, or tell me what you're looking for!

📍 Your location has been saved for accurate recommendations."""

                            send_meta_reply(sender_id, location_pin)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error handling Meta WhatsApp: {e}")
        return jsonify({'status': 'error'}), 500

def handle_ghala_whatsapp_via_meta(data):
    """
    Handle Ghala WhatsApp webhook when it comes in Meta format
    (Ghala sometimes uses Meta's webhook format but we reply using Ghala API)
    """
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    messages = change.get('value', {}).get('messages', [])
                    contacts = change.get('value', {}).get('contacts', [])

                    for message in messages:
                        sender_id = message.get('from')
                        message_type = message.get('type')

                        logger.info(f"Ghala WhatsApp (Meta format) - {message_type} from {sender_id}")

                        # 🔓 OPEN ACCESS: Allow all senders for demo purposes
                        # ⚠️  WARNING: This allows anyone to send messages!

                        logger.info(f"✅ Open access - sender: {sender_id} (GHALA VIA META FORMAT)")

                        if message_type == 'text':
                            text = message.get('text', {}).get('body', '')
                            response = process_message(text, sender_id)
                            logger.info(f"📤 Would send Ghala reply to {sender_id}: {response[:100]}...")
                            # TODO: Fix Ghala API endpoint issue - temporarily disabled
                            send_ghala_reply(sender_id, response)

                        elif message_type == 'location':
                            location = message.get('location', {})
                            lat = location.get('latitude')
                            lng = location.get('longitude')

                            # Save location to database
                            try:
                                from osm_integration import OpenStreetMapIntegration
                                osm = OpenStreetMapIntegration()
                                location_name = osm.reverse_geocode(lat, lng)
                            except:
                                location_name = f"Coordinates: {lat:.4f}, {lng:.4f}"

                            db.update_user_location(sender_id, lat, lng, location_name)

                            # Log location message
                            db.log_message(sender_id, 'location', f"{lat},{lng}", user_id=user.get('id') if user else None)

                            location_response = f"""📍 *Location Received!*

🗺️ *Your Coordinates:* {lat:.4f}, {lng:.4f}
🏷️ *Location:* {location_name}

🌐 *View on Google Maps:* https://www.google.com/maps?q={lat},{lng}
📱 *Tap here to open in Maps app*

🇹🇿 *Tanzania Services Near You:*

Based on your shared location, I can help you find:

🍽️ *Restaurants within 5km*
🏥 *Medical clinics within 5km*
✂️ *Beauty salons within 5km*
🏪 *Auto repair services within 5km*

💡 *Quick Commands:*
• "restaurants near me" - Find dining options
• "medical clinics near me" - Healthcare facilities
• "hair salons near me" - Beauty services
• "auto repair near me" - Car services

🚀 *Get Started:*
Reply with any of the commands above, or tell me what you're looking for!

📍 Your location has been saved for accurate recommendations."""
                            logger.info(f"📤 Would send Ghala reply to {sender_id}: {location_response[:100]}...")
                            # TODO: Fix Ghala API endpoint issue - temporarily disabled
                            send_ghala_reply(sender_id, location_response)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error handling Ghala WhatsApp (Meta format): {e}")
        return jsonify({'status': 'error'}), 500

def handle_ghala_whatsapp(data):
    """
    Handle Ghala WhatsApp webhook format
    """
    try:
        for message in data.get('messages', []):
            sender_id = message.get('from')
            message_type = message.get('type')

            logger.info(f"Ghala WhatsApp - {message_type} from {sender_id}")

            if message_type == 'text':
                text = message.get('text', {}).get('body', '')
                response = process_message(text, sender_id)
                send_ghala_reply(sender_id, response)

            elif message_type == 'location':
                location = message.get('location', {})
                lat = location.get('latitude')
                lng = location.get('longitude')

                # Save location to database
                try:
                    from osm_integration import OpenStreetMapIntegration
                    osm = OpenStreetMapIntegration()
                    location_name = osm.reverse_geocode(lat, lng)
                except:
                    location_name = f"Coordinates: {lat:.4f}, {lng:.4f}"

                db.update_user_location(sender_id, lat, lng, location_name)

                # Log location message
                db.log_message(sender_id, 'location', f"{lat},{lng}", user_id=user.get('id') if user else None)

                location_response = f"""📍 *Location Received!*

🗺️ *Your Coordinates:* {lat:.4f}, {lng:.4f}
🏷️ *Location:* {location_name}

🌐 *View on Google Maps:* https://www.google.com/maps?q={lat},{lng}
📱 *Tap here to open in Maps app*

🇹🇿 *Tanzania Services Near You:*

Based on your shared location, I can help you find:

🍽️ *Restaurants within 5km*
🏥 *Medical clinics within 5km*
✂️ *Beauty salons within 5km*
🏪 *Auto repair services within 5km*

💡 *Quick Commands:*
• "restaurants near me" - Find dining options
• "medical clinics near me" - Healthcare facilities
• "hair salons near me" - Beauty services
• "auto repair near me" - Car services

🚀 *Get Started:*
Reply with any of the commands above, or tell me what you're looking for!

📍 Your location has been saved for accurate recommendations."""
                send_ghala_reply(sender_id, location_response)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error handling Ghala WhatsApp: {e}")
        return jsonify({'status': 'error'}), 500

def process_message(text, sender_id):
    """
    Process incoming message and generate response
    This is where you integrate with your chatbot logic
    """
    text = text.lower().strip()

    # Register/get user from database
    user = db.get_user_by_number(sender_id)
    if not user:
        # Auto-register new user
        user = db.register_user(sender_id)
        if user:
            logger.info(f"New user registered: {sender_id} (ID: {user['id']})")

    user_id = user['id'] if user else None

    # Log the incoming message
    db.log_message(sender_id, 'text', text, user_id=user_id)

    # Simple response logic (replace with your chatbot)
    if 'hi' in text or 'hello' in text or 'habari' in text:
        response = """🇹🇿 *Tanzania Service Assistant* 🤖

Habari! Welcome to Tanzania's AI-powered service discovery platform!

🎯 *I can help you find:*

🍽️ *Restaurants & Dining* - Local favorites & fine dining
🏥 *Medical Clinics* - Healthcare & emergency services
✂️ *Beauty Salons* - Hair styling & spa treatments
🏪 *Auto Repair* - Car maintenance & mechanics

🚀 *Quick Start Commands:*
• *"restaurants"* - Browse dining options
• *"medical clinics"* - Find healthcare facilities
• *"hair salons"* - Locate beauty services
• *"auto repair"* - Find car services

📍 *Get Personalized Results:*
Send me your location for services near you!

💡 *Pro Tips:*
• Use specific terms: "Italian restaurants" or "emergency clinics"
• Ask for directions: "directions to [place name]"
• Get contact info: "call [service name]"
• Book appointments: "book [service]"
• Leave reviews: "review [service]"

What service are you looking for today? 🌟"""

        # Log the welcome response
        db.log_message(sender_id, 'bot_response', response, user_id=user_id)

        return response

    elif 'restaurant' in text or 'food' in text:
        return """🍽️ *Recommended Restaurants in Dar es Salaam*

Here are some highly-rated dining options in your area:

🥘 *Beach Banda Restaurant*
📍 Oyster Bay, Masaki Area
💰 Average meal: TZS 15,000-45,000
📏 Distance: ~2.3 km
⭐ Rating: 4.2/5 (Excellent seafood)
🕐 Open: 11:00 AM - 11:00 PM
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Beach+Banda+Restaurant+Oyster+Bay+Dar+es+Salaam

🥂 *The Terrace Restaurant & Bar*
📍 Masaki Peninsula, Dar es Salaam
💰 Average meal: TZS 25,000-60,000
📏 Distance: ~1.8 km
⭐ Rating: 4.5/5 (Fine dining experience)
🕐 Open: 12:00 PM - 12:00 AM
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=The+Terrace+Restaurant+Masaki+Dar+es+Salaam

🍲 *Addis Ababa Restaurant*
📍 Samora Avenue, City Center
💰 Average meal: TZS 12,000-35,000
📏 Distance: ~4.1 km
⭐ Rating: 4.0/5 (Ethiopian & International)
🕐 Open: 10:00 AM - 10:00 PM
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Addis+Ababa+Restaurant+Samora+Avenue+Dar+es+Salaam

💡 *Quick Actions:*
• Reply "directions to Beach Banda" for navigation
• Reply "call Beach Banda" for reservations
• Reply "menu" for food recommendations

🚀 *Share your location* for personalized restaurant recommendations near you!

Would you like me to show more options or help with reservations? 🗺️"""

    elif 'medical' in text or 'clinic' in text or 'hospital' in text or 'health' in text:
        return """🏥 *Healthcare Facilities in Dar es Salaam*

Here are reputable medical facilities in your area:

🏥 *Masaki Medical Centre*
📍 Masaki Area, Dar es Salaam
💰 Consultation: TZS 15,000-30,000
📏 Distance: ~2.1 km
⭐ Rating: 4.3/5 (General Practice)
🕐 Hours: 8:00 AM - 8:00 PM (Mon-Sat)
☎️ Emergency: +255 XX XXX XXXX (24/7)
🏥 Services: General medicine, pediatrics, diagnostics
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Masaki+Medical+Centre+Dar+es+Salaam

🏥 *Aga Khan Hospital Dar es Salaam*
📍 Ohio Street, City Center
💰 Consultation: TZS 25,000-50,000
📏 Distance: ~3.8 km
⭐ Rating: 4.6/5 (Multi-specialty hospital)
🕐 Hours: 24/7 Emergency Services
☎️ Main: +255 22 211 5151
🏥 Services: Complete medical care, surgery, maternity
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Aga+Khan+Hospital+Dar+es+Salaam

🏥 *Muhimbili National Hospital*
📍 Upanga Area, Dar es Salaam
💰 Public rates (affordable care)
📏 Distance: ~5.2 km
⭐ Rating: 3.8/5 (National referral center)
🕐 Hours: 24/7 Emergency Services
☎️ Emergency: +255 XX XXX XXXX
🏥 Services: Full hospital services, specialist care
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Muhimbili+National+Hospital+Dar+es+Salaam

⚠️ *Emergency Services:*
For medical emergencies, call 112 or visit the nearest facility immediately!

💡 *Quick Actions:*
• Reply "directions to Aga Khan Hospital" for navigation
• Reply "emergency" for urgent care information
• Reply "appointment" for booking help

🚑 *Emergency Hotline:* Call 112 for immediate assistance

Do you need immediate assistance or appointment booking? 🗺️"""

    elif 'hair' in text or 'salon' in text or 'beauty' in text:
        return """✂️ *Beauty & Hair Salons in Dar es Salaam*

Here are professional beauty services in your area:

✂️ *Kinondoni Beauty Salon*
📍 Kinondoni Area, Dar es Salaam
💰 Services: TZS 5,000-25,000
📏 Distance: ~1.9 km
⭐ Rating: 4.1/5 (Local favorite)
🕐 Hours: 9:00 AM - 7:00 PM (Mon-Sat)
💇‍♀️ Services: Haircuts, styling, treatments, braiding
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Kinondoni+Beauty+Salon+Dar+es+Salaam

✂️ *Masaki Hair Studio & Spa*
📍 Masaki Area, Dar es Salaam
💰 Services: TZS 8,000-35,000
📏 Distance: ~2.4 km
⭐ Rating: 4.4/5 (Premium salon)
🕐 Hours: 10:00 AM - 8:00 PM (Mon-Sun)
💅 Services: Full beauty services, spa treatments
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=Masaki+Hair+Studio+Spa+Dar+es+Salaam

✂️ *City Center Cuts & Styles*
📍 Samora Avenue, CBD
💰 Services: TZS 3,000-15,000
📏 Distance: ~4.0 km
⭐ Rating: 3.9/5 (Affordable & quick)
🕐 Hours: 8:00 AM - 6:00 PM (Mon-Sat)
✂️ Services: Quick cuts, styling, men's grooming
🌐 Directions: https://www.google.com/maps/dir/?api=1&destination=City+Center+Cuts+Styles+Samora+Avenue+Dar+es+Salaam

💡 *Quick Actions:*
• Reply "directions to Masaki Hair Studio" for navigation
• Reply "appointment" to book a time
• Reply "services" to see available treatments

✨ *Popular Services:*
• 💇‍♀️ Haircuts & styling
• 💅 Manicure & pedicure
• 🧴 Spa treatments
• 💆‍♀️ Facial treatments

Would you like to book an appointment or see more options? 🗺️"""

    elif 'direction' in text.lower() or 'directions to' in text.lower():
        # Handle specific directions requests
        return handle_directions_request(text)

    elif 'call' in text.lower():
        # Handle call/contact requests
        return handle_call_request(text)

    elif 'appointment' in text.lower() or 'book' in text.lower():
        # Handle appointment booking requests
        return handle_appointment_request(text)

    elif 'emergency' in text.lower():
        # Handle emergency requests
        return handle_emergency_request(text)

    elif 'book' in text.lower() or 'booking' in text.lower() or 'appointment' in text.lower():
        # Handle booking requests
        return handle_booking_request(text, user)

    elif 'review' in text.lower() or 'rate' in text.lower():
        # Handle review requests
        return handle_review_request(text, user)

    elif 'my bookings' in text.lower() or 'my appointments' in text.lower():
        # Handle viewing user's bookings
        return handle_view_bookings(user)

    elif 'near me' in text.lower():
        # Handle location-based service requests using database
        if not user or not user.get('location_lat'):
            return """📍 *Location Required*

I need your location to find services near you!

🇹🇿 *Please share your location:*
• Tap the 📎 (attachment) icon in WhatsApp
• Select "Location"
• Share your current location

Once I have your location, I can find the best services nearby! 🗺️"""

        user_lat = user['location_lat']
        user_lng = user['location_lng']

        if 'restaurant' in text:
            restaurants = db.search_providers_near_location(user_lat, user_lng, 'restaurant', 5.0)
            if not restaurants:
                return "🍽️ *No restaurants found near your location within 5km. Try expanding your search area!*"

            response = f"🍽️ *Restaurants Near You ({len(restaurants)} found)*\n\n"
            for restaurant in restaurants[:3]:  # Show top 3
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={restaurant['location_lat']},{restaurant['location_lng']}"
                response += f"🥘 *{restaurant['name']}*\n"
                response += f"📍 ~{restaurant['distance_km']} km away - {restaurant['location_name']}\n"
                response += f"⭐ Rating: {restaurant['rating']}/5 ({restaurant['review_count']} reviews)\n"
                response += f"💰 Average meal: TZS {restaurant['price_range']}\n"
                response += f"🌐 Directions: {maps_url}\n\n"

            response += "💡 *Get directions:*\nReply with \"directions to [restaurant name]\"\n\n"
            response += "Would you like to see more options or get directions? 🗺️"
            return response

        elif 'medical' in text or 'clinic' in text:
            medical_facilities = db.search_providers_near_location(user_lat, user_lng, 'medical', 5.0)
            if not medical_facilities:
                return "🏥 *No medical facilities found near your location within 5km. Try expanding your search area!*"

            response = f"🏥 *Medical Facilities Near You ({len(medical_facilities)} found)*\n\n"
            for facility in medical_facilities[:3]:
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={facility['location_lat']},{facility['location_lng']}"
                response += f"🏥 *{facility['name']}*\n"
                response += f"📍 ~{facility['distance_km']} km away - {facility['location_name']}\n"
                response += f"⭐ Rating: {facility['rating']}/5 ({facility['review_count']} reviews)\n"
                response += f"💰 Consultation: TZS {facility['price_range']}\n"
                response += f"🌐 Directions: {maps_url}\n\n"

            response += "⚠️ *Emergency:* Call 112 or visit nearest facility immediately!\n\n"
            response += "💡 *Get directions:*\nReply with \"directions to [facility name]\"\n\n"
            response += "Do you need immediate assistance? 🏥"
            return response

        elif 'hair' in text or 'salon' in text:
            salons = db.search_providers_near_location(user_lat, user_lng, 'beauty', 5.0)
            if not salons:
                return "✂️ *No beauty salons found near your location within 5km. Try expanding your search area!*"

            response = f"✂️ *Beauty Salons Near You ({len(salons)} found)*\n\n"
            for salon in salons[:3]:
                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={salon['location_lat']},{salon['location_lng']}"
                response += f"✂️ *{salon['name']}*\n"
                response += f"📍 ~{salon['distance_km']} km away - {salon['location_name']}\n"
                response += f"⭐ Rating: {salon['rating']}/5 ({salon['review_count']} reviews)\n"
                response += f"💰 Services: TZS {salon['price_range']}\n"
                response += f"🌐 Directions: {maps_url}\n\n"

            response += "💡 *Get directions:*\nReply with \"directions to [salon name]\"\n\n"
            response += "Would you like to book an appointment? 📅"
            return response

        else:
            return """📍 *Location-Based Services*

I can find services near your shared location!

🇹🇿 *Available Services:*

🍽️ *"restaurants near me"* - Dining options
🏥 *"medical clinics near me"* - Healthcare facilities
✂️ *"hair salons near me"* - Beauty services

💡 *Tip:* Share your location first, then ask for services near you!

What type of service are you looking for? 📍"""

    elif 'location' in text or 'directions' in text:
        return """🗺️ *Navigation & Directions Service*

I can provide detailed directions and location pins for any service in Dar es Salaam.

📋 *How to get directions:*

1️⃣ *Find a service first:*
• "restaurants" - Browse dining options
• "medical clinics" - Find healthcare facilities
• "hair salons" - Locate beauty services

2️⃣ *Request directions:*
• "direction Beach Banda" or "directions to Beach Banda"
• "direction Aga Khan Hospital" or "directions to Aga Khan Hospital"
• "direction Masaki Hair Studio" or "directions to Masaki Hair Studio"

3️⃣ *Share your location:*
Send your current GPS location for personalized recommendations and accurate distances.

💡 *Example:*
User: "restaurants"
Bot: [Shows restaurant list]
User: "directions to Beach Banda"
Bot: [Sends location pin with navigation]

Would you like me to help you find a specific service first? 📍"""

    else:
        response = f"""🤔 I didn't quite understand your request: "{text[:50]}..."

🇹🇿 *Tanzania Service Assistant - Available Commands:*

🍽️ *Dining & Restaurants*
• "restaurants" - Find places to eat
• "restaurants near me" - Find dining nearby
• "direction [restaurant name]" - Get navigation

🏥 *Healthcare Services*
• "medical clinics" - Find healthcare facilities
• "medical clinics near me" - Find healthcare nearby
• "direction [clinic name]" - Get hospital directions

✂️ *Beauty & Personal Care*
• "hair salons" - Find beauty salons
• "hair salons near me" - Find beauty services nearby
• "direction [salon name]" - Get salon directions

📅 *Bookings & Appointments*
• "book [service]" - Make an appointment
• "my bookings" - View your bookings
• "review [service]" - Leave a review

🗺️ *Navigation Help*
• Share your GPS location for personalized recommendations
• Use "direction [place]" for any location

💡 *Pro Tips:*
• Be specific: "Italian restaurants" or "emergency clinics"
• Share location for accurate distances
• Use service names exactly as shown

How can I assist you with services in Tanzania today? 📍"""

    # Log the bot response
    db.log_message(sender_id, 'bot_response', response, user_id=user_id)

    return response

def send_meta_reply(recipient_id, message):
    """
    Send reply via Meta WhatsApp API
    """
    from env_config import Config

    if not Config.WHATSAPP_ACCESS_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
        logger.error("Meta WhatsApp credentials not configured")
        return False

    import requests

    url = f"https://graph.facebook.com/v18.0/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Meta reply sent to {recipient_id}")
            return True
        else:
            logger.error(f"❌ Meta reply failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Meta reply error: {e}")
        return False

def send_ghala_reply(recipient_id, message):
    """
    Send reply via Ghala WhatsApp API
    """
    from env_config import Config

    if not Config.GHALA_APP_ID or not Config.GHALA_APP_SECRET:
        logger.error("Ghala credentials not configured")
        return False

    import requests

    url = f"https://graph.facebook.com/v24.0/{Config.GHALA_APP_ID}/messages"

    payload = {
        "to": recipient_id,
         "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {Config.GHALA_APP_SECRET}",
        "Content-Type": "application/json",
        # "X-App-Id": Config.GHALA_APP_ID
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Ghala reply sent to {recipient_id}")
            return True
        else:
            logger.error(f"❌ Ghala reply failed: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            logger.error(f"Request URL: {url}")
            logger.error(f"Request headers: {headers}")
            logger.error(f"Request payload: {payload}")
            return False
    except Exception as e:
        logger.error(f"❌ Ghala reply error: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from env_config import Config

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Tanzania Service Chatbot Webhook',
        'provider': Config.WHATSAPP_PROVIDER,
        'configured': Config.is_whatsapp_configured()
    })

@app.route('/', methods=['GET'])
def home():
    """Home page with webhook information"""
    from env_config import Config

    provider = Config.WHATSAPP_PROVIDER.upper() if Config.WHATSAPP_PROVIDER else 'UNKNOWN'

    return f"""
    <h1>🇹🇿 Tanzania Service Chatbot Webhook</h1>
    <h2>Provider: {provider}</h2>

    <h3>Webhook Endpoints:</h3>
    <ul>
        <li><strong>GET /webhook</strong> - Webhook verification</li>
        <li><strong>POST /webhook</strong> - Incoming WhatsApp messages</li>
        <li><strong>GET /health</strong> - Health check</li>
    </ul>

    <h3>Configuration Status:</h3>
    <ul>
        <li>Provider: {provider}</li>
        <li>Configured: {'✅ Yes' if Config.is_whatsapp_configured() else '❌ No'}</li>
    </ul>

    <h3>Setup Instructions:</h3>
    <ol>
        <li>Configure your webhook URL in your WhatsApp provider dashboard</li>
        <li>Set environment variables with your credentials</li>
        <li>Test with the /health endpoint</li>
        <li>Send test messages to your WhatsApp number</li>
    </ol>

    <p><strong>Need help?</strong> Check the setup guide or contact support.</p>
    """

# ===== MAIN =====
if __name__ == '__main__':
    from env_config import Config

    print("🇹🇿 Tanzania Service Chatbot Webhook Server")
    print("=" * 60)

    # Show configuration status
    print(f"📱 WhatsApp Provider: {Config.WHATSAPP_PROVIDER.upper()}")
    print(f"✅ Configured: {'Yes' if Config.is_whatsapp_configured() else 'No'}")

    if Config.is_whatsapp_configured():
        print("🎉 Ready to receive WhatsApp messages!")
    else:
        print("⚠️  WhatsApp not configured - set credentials first:")
        print("   Run: python setup_environment.py")
        print("   Or set environment variables manually")

    print()
    print("🌐 Webhook URLs:")
    print("   GET  /webhook  - Webhook verification")
    print("   POST /webhook  - Incoming messages")
    print("   GET  /health   - Health check")
    print("   GET  /         - This page")
    print()
    print("🚀 Starting server on http://0.0.0.0:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=False)
