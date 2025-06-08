import json
import pandas as pd
import requests
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
import os
import psycopg2
import psycopg2.extras
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GooglePlacesTacoCollector:
    def __init__(self, api_key: str):
        """
        Initialize the Google Places API taco data collector

        Args:
            api_key: Your Google Places API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.base_url = "https://maps.googleapis.com/maps/api"

        # Default coordinates (from your first curl - San Antonio, TX)
        self.default_lat = 29.4241
        self.default_lng = -98.4936
        self.default_radius = 10000  # 10km radius

        # Rate limiting
        self.request_delay = 0.1  # 100ms between requests to respect API limits

        # Database connection
        self.db_connection = None
        self.setup_database_connection()

        # Create database tables
        if self.db_connection:
            self.create_database_tables()

    def setup_database_connection(self):
        """Setup PostgreSQL database connection"""
        try:
            self.db_connection = psycopg2.connect(
                host="localhost",
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                port="5432"
            )
            self.db_connection.autocommit = True
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            self.db_connection = None

    def create_database_tables(self):
        """Create the required database tables if they don't exist"""
        if not self.db_connection:
            logger.error("No database connection available")
            return False

        try:
            cursor = self.db_connection.cursor()

            # Drop and recreate restaurants table with Google fields
            cursor.execute("DROP TABLE IF EXISTS photos CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS reviews CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS tacos CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS restaurants CASCADE;")

            # Create restaurants table with Google rating and price level
            cursor.execute("""
                CREATE TABLE restaurants (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL,
                    street_address TEXT,
                    city TEXT,
                    state TEXT,
                    zip TEXT,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION,
                    phone TEXT,
                    website TEXT,
                    yelp_id TEXT,
                    google_rating DECIMAL(2,1),
                    google_price_level INTEGER,
                    google_user_ratings_total INTEGER,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Create tacos table
            cursor.execute("""
                CREATE TABLE tacos (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
                    name TEXT,
                    description TEXT,
                    price_cents INTEGER,
                    calories INTEGER,
                    tortilla_type TEXT,
                    protein_type TEXT,
                    is_vegan BOOLEAN DEFAULT FALSE,
                    is_bulk BOOLEAN DEFAULT FALSE,
                    is_daily_special BOOLEAN DEFAULT FALSE,
                    available_from TIME,
                    available_to TIME,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Create photos table
            cursor.execute("""
                CREATE TABLE photos (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    taco_id UUID REFERENCES tacos(id) ON DELETE CASCADE,
                    user_id UUID,
                    url TEXT NOT NULL,
                    is_user_uploaded BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Create reviews table (for future use)
            cursor.execute("""
                CREATE TABLE reviews (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID,
                    taco_id UUID REFERENCES tacos(id) ON DELETE CASCADE,
                    content TEXT,
                    submitted_at TIMESTAMP DEFAULT NOW(),
                    verified_location BOOLEAN DEFAULT FALSE,
                    gps_latitude DOUBLE PRECISION,
                    gps_longitude DOUBLE PRECISION,
                    fullness_rating INTEGER CHECK (fullness_rating BETWEEN 1 AND 5),
                    authenticity_id UUID,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            cursor.close()
            logger.info("Database tables created successfully")
            return True

        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            return False

    def close_database_connection(self):
        """Close database connection"""
        if self.db_connection:
            self.db_connection.close()
            logger.info("Database connection closed")

    def search_taco_places(self, lat: float = None, lng: float = None,
                           radius: int = None, keyword: str = "bean and cheese taco") -> List[Dict]:
        """
        Search for places serving bean and cheese tacos using Google Places Nearby Search API

        Args:
            lat: Latitude (defaults to San Antonio)
            lng: Longitude (defaults to San Antonio)
            radius: Search radius in meters (default 10km)
            keyword: Search keyword (default "bean and cheese taco")

        Returns:
            List of place dictionaries from API response
        """
        # Use defaults if not provided
        lat = lat or self.default_lat
        lng = lng or self.default_lng
        radius = radius or self.default_radius

        url = f"{self.base_url}/place/nearbysearch/json"

        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': 'restaurant',
            'keyword': keyword,
            'key': self.api_key
        }

        all_places = []
        next_page_token = None

        while True:
            if next_page_token:
                params['pagetoken'] = next_page_token
                # Google requires a delay before using next_page_token
                time.sleep(2)

            try:
                logger.info(f"Searching for bean and cheese taco places near ({lat}, {lng}) with radius {radius}m")
                response = self.session.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if data.get('status') != 'OK':
                    logger.warning(f"API returned status: {data.get('status')} - {data.get('error_message', '')}")
                    break

                places = data.get('results', [])
                all_places.extend(places)
                logger.info(f"Found {len(places)} places in this batch. Total so far: {len(all_places)}")

                # Check for next page
                next_page_token = data.get('next_page_token')
                if not next_page_token:
                    break

                # Remove pagetoken for next iteration if it exists
                params.pop('pagetoken', None)

            except requests.RequestException as e:
                logger.error(f"Error searching places: {e}")
                break

            time.sleep(self.request_delay)

        logger.info(f"Total places found: {len(all_places)}")
        return all_places

    def search_bean_cheese_taco_places(self, lat: float = None, lng: float = None,
                                       radius: int = None) -> List[Dict]:
        """
        Enhanced search specifically for bean and cheese tacos using multiple search strategies

        Args:
            lat: Latitude (defaults to San Antonio)
            lng: Longitude (defaults to San Antonio)
            radius: Search radius in meters (default 10km)

        Returns:
            List of unique places that likely serve bean and cheese tacos
        """
        all_places = []
        seen_place_ids = set()

        # Multiple search terms to find bean and cheese taco spots
        search_terms = [
            "bean and cheese taco",
            "bean cheese taco",
            "breakfast taco",
            "mexican restaurant bean taco",
            "taqueria bean cheese",
            "tex mex bean cheese taco"
        ]

        for term in search_terms:
            logger.info(f"Searching with term: '{term}'")
            places = self.search_taco_places(lat, lng, radius, term)

            # Filter for unique places
            for place in places:
                place_id = place.get('place_id')
                if place_id and place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    all_places.append(place)

            # Small delay between different search terms
            time.sleep(0.5)

        logger.info(f"Found {len(all_places)} unique places across all search terms")
        return all_places

    def filter_bean_cheese_candidates(self, places: List[Dict]) -> List[Dict]:
        """
        Filter places to focus on those most likely to serve bean and cheese tacos

        Args:
            places: List of place dictionaries from search

        Returns:
            Filtered list of places likely to have bean and cheese tacos
        """
        filtered_places = []

        # Keywords that indicate likely bean and cheese taco availability
        positive_keywords = [
            'taco', 'taqueria', 'mexican', 'tex-mex', 'breakfast',
            'burrito', 'bean', 'cheese', 'tortilla', 'authentic',
            'traditional', 'local', 'familia', 'casa', 'el', 'la', 'los'
        ]

        # Keywords that might indicate less likely candidates
        negative_keywords = [
            'pizza', 'burger', 'chinese', 'thai', 'sushi', 'italian',
            'steakhouse', 'seafood', 'bbq', 'wings', 'bar', 'club'
        ]

        for place in places:
            name = place.get('name', '').lower()
            types = place.get('types', [])

            # Convert types to string for keyword checking
            types_str = ' '.join(types).lower()
            combined_text = f"{name} {types_str}".lower()

            # Score based on positive keywords
            positive_score = sum(1 for keyword in positive_keywords if keyword in combined_text)
            negative_score = sum(1 for keyword in negative_keywords if keyword in combined_text)

            # Include if it has positive indicators and minimal negative indicators
            if positive_score > 0 and negative_score == 0:
                place['bean_cheese_likelihood_score'] = positive_score
                filtered_places.append(place)
            elif positive_score >= 2 and negative_score <= 1:  # High positive score can override some negative
                place['bean_cheese_likelihood_score'] = positive_score - negative_score
                filtered_places.append(place)

        # Sort by likelihood score (highest first)
        filtered_places.sort(key=lambda x: x.get('bean_cheese_likelihood_score', 0), reverse=True)

        logger.info(f"Filtered to {len(filtered_places)} places likely to serve bean and cheese tacos")
        return filtered_places

    def extract_taco_specific_data(self, place_details: Dict, restaurant_id: str) -> List[Dict]:
        """
        Extract potential taco menu items from reviews and description text
        Focus on finding bean and cheese taco mentions

        Args:
            place_details: Detailed place data from details API
            restaurant_id: The restaurant UUID to link tacos to restaurant

        Returns:
            List of potential taco items found in reviews/descriptions
        """
        tacos_data = []

        # Look through reviews for taco mentions
        reviews = place_details.get('reviews', [])

        bean_cheese_indicators = [
            'bean and cheese', 'bean cheese', 'beans and cheese',
            'refried bean', 'breakfast taco', 'simple taco',
            'basic taco', 'vegetarian taco'
        ]

        found_bean_cheese = False
        taco_mentions = []

        for review in reviews:
            text = review.get('text', '').lower()

            # Check for bean and cheese mentions
            for indicator in bean_cheese_indicators:
                if indicator in text:
                    found_bean_cheese = True
                    taco_mentions.append({
                        'mention_text': indicator,
                        'review_rating': review.get('rating', 0),
                        'full_review': text[:200] + '...' if len(text) > 200 else text
                    })

        # If we found bean and cheese mentions, create a taco entry
        if found_bean_cheese:
            taco_data = {
                'id': str(uuid.uuid4()),  # Generate UUID for taco
                'restaurant_id': restaurant_id,
                'name': 'Bean and Cheese Taco',
                'description': f"Traditional bean and cheese taco. Mentioned in {len(taco_mentions)} reviews.",
                'price_cents': None,       # We don't have price data from Google
                'calories': None,          # We don't have calorie data
                'tortilla_type': 'flour',  # Common for bean and cheese tacos
                'protein_type': 'none',    # Bean and cheese typically don't have meat
                'is_vegan': False,         # Has cheese
                'is_bulk': False,          # Default
                'is_daily_special': False, # Default
                'available_from': None,    # We don't have time data
                'available_to': None,      # We don't have time data
                'mention_count': len(taco_mentions),  # Extra field for our analysis
            }

            tacos_data.append(taco_data)

        return tacos_data

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific place using Google Places Details API

        Args:
            place_id: The place_id from the search results

        Returns:
            Dictionary with detailed place information
        """
        url = f"{self.base_url}/place/details/json"

        # Request specific fields that match our database schema
        fields = [
            'name', 'formatted_address', 'formatted_phone_number',
            'website', 'rating', 'reviews', 'price_level',
            'opening_hours', 'geometry', 'place_id', 'photos'
        ]

        params = {
            'place_id': place_id,
            'fields': ','.join(fields),
            'key': self.api_key
        }

        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'OK':
                logger.warning(f"Details API returned status: {data.get('status')} for place_id: {place_id}")
                return None

            return data.get('result', {})

        except requests.RequestException as e:
            logger.error(f"Error getting place details for {place_id}: {e}")
            return None

    def extract_restaurant_data(self, place: Dict, details: Dict = None) -> Dict:
        """
        Extract restaurant data that matches our database schema

        Args:
            place: Basic place data from search
            details: Detailed place data from details API

        Returns:
            Dictionary with restaurant data for our schema
        """
        # Use details if available, otherwise fall back to basic place data
        source = details if details else place

        # Extract address components
        address = source.get('formatted_address', '')
        address_parts = address.split(', ') if address else []

        # Try to parse address components
        street_address = address_parts[0] if len(address_parts) > 0 else ''
        city = address_parts[1] if len(address_parts) > 1 else ''
        state_zip = address_parts[2] if len(address_parts) > 2 else ''

        # Parse state and zip from "State ZIP" format
        state = ''
        zip_code = ''
        if state_zip:
            parts = state_zip.split(' ')
            if len(parts) >= 2:
                state = parts[0]
                zip_code = parts[1]

        # Extract coordinates
        geometry = source.get('geometry', {})
        location = geometry.get('location', {})

        restaurant_data = {
            'id': str(uuid.uuid4()),  # Generate UUID for restaurant
            'place_id': source.get('place_id', ''),  # Keep for reference but not in DB schema
            'name': source.get('name', ''),
            'street_address': street_address,
            'city': city,
            'state': state,
            'zip': zip_code,
            'latitude': location.get('lat', 0),
            'longitude': location.get('lng', 0),
            'phone': source.get('formatted_phone_number', ''),
            'website': source.get('website', ''),
            'yelp_id': None,  # This is Google data, not Yelp
            # NEW GOOGLE FIELDS
            'google_rating': source.get('rating'),
            'google_price_level': source.get('price_level'),
            'google_user_ratings_total': source.get('user_ratings_total'),
            'bean_cheese_likelihood_score': 0,  # Will be set later, not in DB
        }

        return restaurant_data

    def extract_reviews_data(self, place_details: Dict, restaurant_place_id: str) -> List[Dict]:
        """
        Extract review data from place details

        Args:
            place_details: Detailed place data from details API
            restaurant_place_id: The place_id to link reviews to restaurant

        Returns:
            List of review dictionaries
        """
        reviews = place_details.get('reviews', [])
        reviews_data = []

        for review in reviews:
            review_data = {
                'restaurant_place_id': restaurant_place_id,
                'author_name': review.get('author_name', ''),
                'author_url': review.get('author_url', ''),
                'rating': review.get('rating', 0),
                'text': review.get('text', ''),
                'time': review.get('time', 0),
                'relative_time_description': review.get('relative_time_description', ''),
                'language': review.get('language', ''),
            }

            # Convert timestamp to readable date
            if review_data['time']:
                try:
                    review_data['review_date'] = datetime.fromtimestamp(review_data['time']).isoformat()
                except:
                    review_data['review_date'] = ''
            else:
                review_data['review_date'] = ''

            reviews_data.append(review_data)

        return reviews_data

    def extract_photos_data(self, place_details: Dict, taco_id: str) -> List[Dict]:
        """
        Extract photo data from place details

        Args:
            place_details: Detailed place data from details API
            taco_id: The taco UUID to link photos to taco

        Returns:
            List of photo dictionaries
        """
        photos = place_details.get('photos', [])
        photos_data = []

        for photo in photos:
            # Construct photo URL using the photo_reference
            photo_url = ''
            if photo.get('photo_reference'):
                photo_url = f"{self.base_url}/place/photo?maxwidth=400&photoreference={photo['photo_reference']}&key={self.api_key}"

            photo_data = {
                'id': str(uuid.uuid4()),  # Generate UUID for photo
                'taco_id': taco_id,
                'user_id': None,  # These are from Google, not users
                'url': photo_url,
                'is_user_uploaded': False,  # These are from Google, not users
            }

            photos_data.append(photo_data)

        return photos_data

    def insert_restaurant_to_db(self, restaurant_data: Dict) -> bool:
        """
        Insert restaurant data into PostgreSQL database

        Args:
            restaurant_data: Dictionary containing restaurant information

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db_connection:
            logger.error("No database connection available")
            return False

        try:
            cursor = self.db_connection.cursor()

            insert_query = """
                INSERT INTO restaurants (id, name, street_address, city, state, zip, latitude, longitude, 
                                       phone, website, yelp_id, google_rating, google_price_level, 
                                       google_user_ratings_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """

            cursor.execute(insert_query, (
                restaurant_data['id'],
                restaurant_data['name'],
                restaurant_data['street_address'],
                restaurant_data['city'],
                restaurant_data['state'],
                restaurant_data['zip'],
                restaurant_data['latitude'],
                restaurant_data['longitude'],
                restaurant_data['phone'],
                restaurant_data['website'],
                restaurant_data['yelp_id'],
                restaurant_data.get('google_rating'),
                restaurant_data.get('google_price_level'),
                restaurant_data.get('google_user_ratings_total')
            ))

            cursor.close()
            rating_text = f"Rating: {restaurant_data.get('google_rating', 'N/A')}"
            price_text = f"Price Level: {restaurant_data.get('google_price_level', 'N/A')}"
            logger.info(f"Inserted restaurant: {restaurant_data['name']} ({rating_text}, {price_text})")
            return True

        except Exception as e:
            logger.error(f"Error inserting restaurant {restaurant_data.get('name', 'Unknown')}: {e}")
            return False

    def insert_taco_to_db(self, taco_data: Dict) -> bool:
        """
        Insert taco data into PostgreSQL database

        Args:
            taco_data: Dictionary containing taco information

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db_connection:
            logger.error("No database connection available")
            return False

        try:
            cursor = self.db_connection.cursor()

            insert_query = """
                INSERT INTO tacos (id, restaurant_id, name, description, price_cents, calories, 
                                 tortilla_type, protein_type, is_vegan, is_bulk, is_daily_special, 
                                 available_from, available_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """

            cursor.execute(insert_query, (
                taco_data['id'],
                taco_data['restaurant_id'],
                taco_data['name'],
                taco_data['description'],
                taco_data['price_cents'],
                taco_data['calories'],
                taco_data['tortilla_type'],
                taco_data['protein_type'],
                taco_data['is_vegan'],
                taco_data['is_bulk'],
                taco_data['is_daily_special'],
                taco_data['available_from'],
                taco_data['available_to']
            ))

            cursor.close()
            logger.info(f"Inserted taco: {taco_data['name']} for restaurant {taco_data['restaurant_id']}")
            return True

        except Exception as e:
            logger.error(f"Error inserting taco {taco_data.get('name', 'Unknown')}: {e}")
            return False

    def insert_photo_to_db(self, photo_data: Dict) -> bool:
        """
        Insert photo data into PostgreSQL database

        Args:
            photo_data: Dictionary containing photo information

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.db_connection:
            logger.error("No database connection available")
            return False

        try:
            cursor = self.db_connection.cursor()

            insert_query = """
                INSERT INTO photos (id, taco_id, user_id, url, is_user_uploaded)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """

            cursor.execute(insert_query, (
                photo_data['id'],
                photo_data['taco_id'],
                photo_data['user_id'],
                photo_data['url'],
                photo_data['is_user_uploaded']
            ))

            cursor.close()
            logger.info(f"Inserted photo for taco {photo_data['taco_id']}")
            return True

        except Exception as e:
            logger.error(f"Error inserting photo: {e}")
            return False

    def insert_review_to_db(self, review_data: Dict, restaurant_id: str) -> bool:
        """
        Insert review data into existing reviews table structure
        """
        if not self.db_connection:
            logger.error("No database connection available")
            return False

        try:
            cursor = self.db_connection.cursor()

            # We'll need to modify the existing reviews table to accommodate Google reviews
            # Add columns for Google review data
            try:
                cursor.execute("""
                    ALTER TABLE reviews 
                    ADD COLUMN IF NOT EXISTS author_name TEXT,
                    ADD COLUMN IF NOT EXISTS author_url TEXT,
                    ADD COLUMN IF NOT EXISTS google_rating INTEGER,
                    ADD COLUMN IF NOT EXISTS review_text TEXT,
                    ADD COLUMN IF NOT EXISTS review_time BIGINT,
                    ADD COLUMN IF NOT EXISTS relative_time_description TEXT,
                    ADD COLUMN IF NOT EXISTS language TEXT,
                    ADD COLUMN IF NOT EXISTS review_date TIMESTAMP,
                    ADD COLUMN IF NOT EXISTS restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE;
                """)
            except Exception as alter_error:
                logger.warning(f"Could not alter reviews table: {alter_error}")

            insert_query = """
                INSERT INTO reviews (restaurant_id, author_name, author_url, google_rating, 
                                   review_text, review_time, relative_time_description, 
                                   language, review_date, content)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """

            cursor.execute(insert_query, (
                restaurant_id,
                review_data.get('author_name', ''),
                review_data.get('author_url', ''),
                review_data.get('rating', 0),
                review_data.get('text', ''),
                review_data.get('time', 0),
                review_data.get('relative_time_description', ''),
                review_data.get('language', ''),
                review_data.get('review_date', None),
                review_data.get('text', '')  # Also populate the existing content field
            ))

            cursor.close()
            logger.info(f"Inserted review by {review_data.get('author_name', 'Unknown')} for restaurant {restaurant_id}")
            return True

        except Exception as e:
            logger.error(f"Error inserting review by {review_data.get('author_name', 'Unknown')}: {e}")
            return False


    def collect_all_data(self, lat: float = None, lng: float = None,
                         radius: int = None, save_to_db: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Complete bean and cheese taco data collection workflow

        Args:
            lat: Latitude for search center
            lng: Longitude for search center
            radius: Search radius in meters
            save_to_db: Whether to save data to database (default True)

        Returns:
            Tuple of (restaurants_df, tacos_df, reviews_df, photos_df)
        """
        logger.info("Starting bean and cheese taco data collection...")

        # Step 1: Search for places that might serve bean and cheese tacos
        places = self.search_bean_cheese_taco_places(lat, lng, radius)

        if not places:
            logger.warning("No places found")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Step 2: Filter for most likely candidates
        filtered_places = self.filter_bean_cheese_candidates(places)

        if not filtered_places:
            logger.warning("No suitable places found after filtering")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Step 3: Get detailed information for each place
        restaurants_data = []
        tacos_data = []
        reviews_data = []
        photos_data = []

        for i, place in enumerate(filtered_places):
            place_id = place.get('place_id')
            if not place_id:
                continue

            logger.info(f"Processing place {i+1}/{len(filtered_places)}: {place.get('name', 'Unknown')} (Score: {place.get('bean_cheese_likelihood_score', 0)})")

            # Get detailed information
            details = self.get_place_details(place_id)

            # Extract restaurant data
            restaurant_data = self.extract_restaurant_data(place, details)
            restaurant_data['bean_cheese_likelihood_score'] = place.get('bean_cheese_likelihood_score', 0)
            restaurants_data.append(restaurant_data)

            # Save restaurant to database
            if save_to_db:
                self.insert_restaurant_to_db(restaurant_data)

            # Extract taco, reviews and photos if details available
            if details:
                # Look for bean and cheese taco mentions
                place_tacos = self.extract_taco_specific_data(details, restaurant_data['id'])
                tacos_data.extend(place_tacos)

                # Save tacos to database and collect photos for each taco
                for taco in place_tacos:
                    if save_to_db:
                        self.insert_taco_to_db(taco)

                    # Extract photos for this taco
                    taco_photos = self.extract_photos_data(details, taco['id'])
                    photos_data.extend(taco_photos)

                    # Save photos to database
                    if save_to_db:
                        for photo in taco_photos:
                            self.insert_photo_to_db(photo)

                place_reviews = self.extract_reviews_data(details, place_id)
                reviews_data.extend(place_reviews)
                if save_to_db:
                    for review in place_reviews:
                        self.insert_review_to_db(review, restaurant_data['id'])

            # Rate limiting
            time.sleep(self.request_delay)

        # Create DataFrames
        restaurants_df = pd.DataFrame(restaurants_data)
        tacos_df = pd.DataFrame(tacos_data)
        reviews_df = pd.DataFrame(reviews_data)
        photos_df = pd.DataFrame(photos_data)

        logger.info(f"Collection complete: {len(restaurants_df)} restaurants, {len(tacos_df)} bean & cheese tacos found, {len(reviews_df)} reviews, {len(photos_df)} photos")

        if save_to_db:
            logger.info("Data has been saved to PostgreSQL database")

        return restaurants_df, tacos_df, reviews_df, photos_df

    def save_data(self, restaurants_df: pd.DataFrame, tacos_df: pd.DataFrame,
                  reviews_df: pd.DataFrame, photos_df: pd.DataFrame,
                  base_filename: str = 'bean_cheese_taco_data'):
        """
        Save all DataFrames to CSV files

        Args:
            restaurants_df: Restaurant data
            tacos_df: Bean and cheese taco data
            reviews_df: Reviews data
            photos_df: Photos data
            base_filename: Base filename for CSV files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not restaurants_df.empty:
            filename = f"{base_filename}_restaurants_{timestamp}.csv"
            restaurants_df.to_csv(filename, index=False)
            logger.info(f"Restaurants data saved to {filename}")

        if not tacos_df.empty:
            filename = f"{base_filename}_tacos_{timestamp}.csv"
            tacos_df.to_csv(filename, index=False)
            logger.info(f"Bean and cheese tacos data saved to {filename}")

        if not reviews_df.empty:
            filename = f"{base_filename}_reviews_{timestamp}.csv"
            reviews_df.to_csv(filename, index=False)
            logger.info(f"Reviews data saved to {filename}")

        if not photos_df.empty:
            filename = f"{base_filename}_photos_{timestamp}.csv"
            photos_df.to_csv(filename, index=False)
            logger.info(f"Photos data saved to {filename}")

    def display_summary(self, restaurants_df: pd.DataFrame, tacos_df: pd.DataFrame,
                        reviews_df: pd.DataFrame, photos_df: pd.DataFrame):
        """Display a summary of collected bean and cheese taco data"""
        print(f"\n=== BEAN AND CHEESE TACO DATA COLLECTION SUMMARY ===")
        print(f"Restaurants found: {len(restaurants_df)}")
        print(f"Bean & cheese tacos identified: {len(tacos_df)}")
        print(f"Reviews collected: {len(reviews_df)}")
        print(f"Photos found: {len(photos_df)}")

        if not restaurants_df.empty:
            # Show Google rating and price level stats
            if 'google_rating' in restaurants_df.columns:
                avg_rating = restaurants_df['google_rating'].dropna().mean()
                if not pd.isna(avg_rating):
                    print(f"\nAverage Google rating: {avg_rating:.1f}")

            if 'google_price_level' in restaurants_df.columns:
                price_levels = restaurants_df['google_price_level'].dropna().value_counts().to_dict()
                if price_levels:
                    print(f"Price levels: {price_levels}")

            if 'google_user_ratings_total' in restaurants_df.columns:
                total_reviews = restaurants_df['google_user_ratings_total'].dropna().sum()
                if total_reviews > 0:
                    print(f"Total Google ratings: {int(total_reviews)}")

            print(f"Average likelihood score: {restaurants_df['bean_cheese_likelihood_score'].mean():.1f}")
            print(f"Most common cities: {restaurants_df['city'].value_counts().head(3).to_dict()}")
            print(f"Most common states: {restaurants_df['state'].value_counts().head(3).to_dict()}")

            print(f"\n=== TOP 10 RESTAURANTS BY BEAN & CHEESE LIKELIHOOD ===")
            # Include Google rating and price level in display
            display_cols = ['name', 'bean_cheese_likelihood_score', 'city', 'state']
            if 'google_rating' in restaurants_df.columns:
                display_cols.insert(2, 'google_rating')
            if 'google_price_level' in restaurants_df.columns:
                display_cols.insert(3, 'google_price_level')

            top_restaurants = restaurants_df.nlargest(10, 'bean_cheese_likelihood_score')[display_cols]
            print(top_restaurants.to_string(index=False))

        if not tacos_df.empty:
            print(f"\n=== BEAN AND CHEESE TACO FINDINGS ===")
            print(f"Total review mentions: {tacos_df['mention_count'].sum()}")
            print(f"Average mentions per taco: {tacos_df['mention_count'].mean():.1f}")

            # Show restaurants where bean and cheese tacos were found
            print(f"\n=== RESTAURANTS WITH CONFIRMED BEAN & CHEESE TACOS ===")
            if not restaurants_df.empty:
                confirmed_restaurants = restaurants_df[
                    restaurants_df['id'].isin(tacos_df['restaurant_id'])
                ][['name', 'city', 'state', 'google_rating', 'google_price_level', 'bean_cheese_likelihood_score']]
                print(confirmed_restaurants.to_string(index=False))

        print(f"\n🌮 SUCCESS: Your database has been seeded with {len(restaurants_df)} restaurants and {len(tacos_df)} bean & cheese tacos!")
        print(f"📊 Database location: localhost:5432/{os.getenv('POSTGRES_DB')}")
        print(f"🔗 Ready for your Rails application!")
        print(f"\n📈 Google Places Data Captured:")
        print(f"   • Restaurant ratings and price levels")
        print(f"   • {len(reviews_df)} customer reviews")
        print(f"   • Business hours and contact info")


# Example usage
def main():
    # Load environment variables
    load_dotenv()

    # Your Google Places API key
    API_KEY = os.getenv("APIKEY")

    if not API_KEY:
        logger.error("APIKEY not found in environment variables")
        return None, None, None, None

    # Initialize collector
    collector = GooglePlacesTacoCollector(API_KEY)

    if not collector.db_connection:
        logger.error("Failed to connect to database")
        return None, None, None, None

    try:
        # Option 1: Use default San Antonio coordinates for bean and cheese tacos
        print("Collecting bean and cheese taco data for San Antonio...")
        restaurants_df, tacos_df, reviews_df, photos_df = collector.collect_all_data()

        # Option 2: Use custom coordinates (example: Austin, TX)
        # austin_lat, austin_lng = 30.2672, -97.7431
        # print("Collecting bean and cheese taco data for Austin...")
        # restaurants_df, tacos_df, reviews_df, photos_df = collector.collect_all_data(austin_lat, austin_lng, radius=15000)

        # Display summary
        collector.display_summary(restaurants_df, tacos_df, reviews_df, photos_df)

        # Save to CSV files
        collector.save_data(restaurants_df, tacos_df, reviews_df, photos_df)

        return restaurants_df, tacos_df, reviews_df, photos_df

    finally:
        # Always close the database connection
        collector.close_database_connection()

if __name__ == "__main__":
    restaurants_df, tacos_df, reviews_df, photos_df = main()