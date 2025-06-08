#!/usr/bin/env python3
"""
Export PostgreSQL taco data to Rails-compatible seed files
This script connects to the populated PostgreSQL container and creates a dump for Rails db:seed
"""

import json
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from decimal import Decimal
import re

def connect_to_db():
    """Connect to the populated PostgreSQL container"""
    return psycopg2.connect(
        host="localhost",
        database="tacos_db",
        user="tacos",
        password="tacos_password",
        port="5432",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def clean_unicode_text(text):
    """Clean problematic Unicode for Ruby"""
    if not text:
        return text
    # Remove problematic Unicode that breaks Ruby parsing
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def convert_types(obj):
    """Convert PostgreSQL types to JSON-serializable types"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def export_all_data(cursor):
    """Export all data from populated database"""

    # Export restaurants
    cursor.execute("SELECT * FROM restaurants ORDER BY id")
    restaurants = []
    for row in cursor.fetchall():
        restaurant = {k: convert_types(v) for k, v in dict(row).items()}
        restaurants.append(restaurant)

    # Export tacos
    cursor.execute("SELECT * FROM tacos ORDER BY id")
    tacos = []
    for row in cursor.fetchall():
        taco = {k: convert_types(v) for k, v in dict(row).items()}
        # Handle time fields specially
        if taco.get('available_from'):
            taco['available_from'] = str(taco['available_from'])
        if taco.get('available_to'):
            taco['available_to'] = str(taco['available_to'])
        # Clean description
        if taco.get('description'):
            taco['description'] = clean_unicode_text(taco['description'])
        tacos.append(taco)

    # Export photos
    cursor.execute("SELECT * FROM photos ORDER BY id")
    photos = []
    for row in cursor.fetchall():
        photo = {k: convert_types(v) for k, v in dict(row).items()}
        photos.append(photo)

    # Export reviews
    cursor.execute("SELECT * FROM reviews ORDER BY id")
    reviews = []
    for row in cursor.fetchall():
        review = {k: convert_types(v) for k, v in dict(row).items()}
        # Clean Unicode from text fields
        for field in ['review_text', 'content', 'author_name']:
            if review.get(field):
                review[field] = clean_unicode_text(review[field])
        reviews.append(review)

    return restaurants, tacos, photos, reviews

def create_rails_seeds_rb(restaurants, tacos, photos, reviews):
    """Create Rails seeds.rb file"""

    # Convert to Ruby-safe JSON
    def to_ruby_json(data):
        json_str = json.dumps(data, indent=2, ensure_ascii=True)
        return json_str.replace(': null,', ': nil,').replace(': null}', ': nil}')

    seeds_content = f'''# -*- coding: utf-8 -*-
# Taco Price Index - Seed Data
# Real San Antonio taco data for development

puts "🌮 Seeding Taco Price Index database..."

# Clear existing data
Review.destroy_all if defined?(Review)
Photo.destroy_all if defined?(Photo)
Taco.destroy_all if defined?(Taco)
Restaurant.destroy_all if defined?(Restaurant)

puts "🏪 Creating restaurants..."
restaurants_data = {to_ruby_json(restaurants)}

restaurants_data.each do |attrs|
  Restaurant.create!(attrs.except('created_at', 'updated_at'))
end

puts "✅ Created #{{Restaurant.count}} restaurants"

puts "🌮 Creating tacos..."
tacos_data = {to_ruby_json(tacos)}

tacos_data.each do |attrs|
  Taco.create!(attrs.except('created_at', 'updated_at'))
end

puts "✅ Created #{{Taco.count}} tacos"

puts "📸 Creating photos..."
photos_data = {to_ruby_json(photos)}

photos_data.each do |attrs|
  Photo.create!(attrs.except('created_at', 'updated_at'))
end

puts "✅ Created #{{Photo.count}} photos"

puts "⭐ Creating reviews..."
if defined?(Review)
  reviews_data = {to_ruby_json(reviews)}
  
  reviews_data.each do |attrs|
    attrs['review_date'] = DateTime.parse(attrs['review_date']) if attrs['review_date']
    Review.create!(attrs.except('created_at', 'updated_at'))
  end
  
  puts "✅ Created #{{Review.count}} reviews"
else
  puts "⚠️  Review model not found, skipping reviews"
end

puts "🎉 Database seeding complete!"
puts "📊 Summary: #{{Restaurant.count}} restaurants, #{{Taco.count}} tacos, #{{Photo.count}} photos, #{{Review.count if defined?(Review)}} reviews"
'''

    return seeds_content

def main():
    """Export data from populated container to Rails seeds"""
    print("🚀 Creating Rails seed dump from populated database...")

    # Determine paths
    if os.path.basename(os.getcwd()) == "data_collection":
        seeds_dir = "../db/seeds"
        seeds_file = "../db/seeds.rb"
    else:
        seeds_dir = "db/seeds"
        seeds_file = "db/seeds.rb"

    os.makedirs(seeds_dir, exist_ok=True)

    # Connect and export
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        print("📦 Exporting all data...")
        restaurants, tacos, photos, reviews = export_all_data(cursor)

        print("📝 Creating JSON files...")
        # Save individual JSON files
        with open(f"{seeds_dir}/restaurants.json", "w", encoding='utf-8') as f:
            json.dump(restaurants, f, indent=2, ensure_ascii=False)

        with open(f"{seeds_dir}/tacos.json", "w", encoding='utf-8') as f:
            json.dump(tacos, f, indent=2, ensure_ascii=False)

        with open(f"{seeds_dir}/photos.json", "w", encoding='utf-8') as f:
            json.dump(photos, f, indent=2, ensure_ascii=False)

        with open(f"{seeds_dir}/reviews.json", "w", encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)

        print("🛤️  Creating Rails seeds.rb...")
        # Create seeds.rb
        seeds_content = create_rails_seeds_rb(restaurants, tacos, photos, reviews)
        with open(seeds_file, "w", encoding='utf-8') as f:
            f.write(seeds_content)

        print("✅ Export complete!")
        print(f"📁 Created:")
        print(f"   • {seeds_file}")
        print(f"   • {len(restaurants)} restaurants")
        print(f"   • {len(tacos)} tacos")
        print(f"   • {len(photos)} photos")
        print(f"   • {len(reviews)} reviews")
        print("\n🚀 Other developers can now run: rails db:seed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()