# app/models/restaurant.rb


class Restaurant < ApplicationRecord
  # Associations
  has_many :tacos, dependent: :destroy
  has_many :photos, through: :tacos
  has_many :reviews, dependent: :destroy

  has_many :user_favorites, dependent: :destroy
  has_many :favorited_by, through: :user_favorites, source: :user

  # Validations
  validates :name, presence: true
  validates :street_address, presence: true
  validates :city, presence: true
  validates :state, presence: true
  validates :zip, presence: true
  validates :latitude, presence: true, numericality: true
  validates :longitude, presence: true, numericality: true
  validates :website, format: { with: URI.regexp(%w[http https]), message: "must be a valid URL" }, allow_blank:  true
  validates :google_rating, numericality: true, allow_nil: true
  validates :google_price_level, numericality: true, allow_nil: true
  validates :google_user_ratings_total, numericality: true, allow_nil: true
  validates :cuisine_type, presence: true, allow_nil: true

  # Geocoding
  # Only geocode if we do not already have latitude/longitude
  # This prevents unnecessary external API calls (and related errors)
  geocoded_by :full_address
  after_validation :geocode, if: ->(obj) do
    obj.full_address.present? &&
      (obj.latitude.blank? || obj.longitude.blank?) &&
      (obj.street_address_changed? || obj.city_changed? || obj.state_changed? || obj.zip_changed?)
  end

  # Store business hours as JSON in a text field
  serialize :business_hours, coder: JSON
  
  # Store tags as JSON array in a text field
  serialize :tags, coder: JSON

  # Virtual attribute for simple hours display
  attr_accessor :hours

  # Days of the week for hours display
  DAYS = %w[Sunday Monday Tuesday Wednesday Thursday Friday Saturday].freeze

  def favorite_for?(user)
    user_favorites.exists?(user: user)
  end

  # Returns the number of users who have favorited this restaurant
  # Uses counter_cache for better performance
  def favorite_count
    # If using counter_cache, this will be fast
    respond_to?(:user_favorites_count) ? user_favorites_count : user_favorites.count
  end

  # Returns a formatted string of business hours
  def hours
    return @hours if @hours.present?
    return unless business_hours.present?

    # If we have business_hours as JSON, format them
    if business_hours.is_a?(Hash)
      business_hours.map do |day, hours|
        "#{day}: #{hours}"
      end.join("<br>").html_safe
    else
      # Fallback to simple hours if set
      business_hours
    end
  end

  # Returns hours for a specific day of the week (0-6, where 0 is Sunday)
  def hours_for_day(day_index)
    return unless business_hours.is_a?(Hash)
    day_name = DAYS[day_index % 7]
    business_hours[day_name] || "Closed"
  end

  # Returns the full address for geocoding
  def full_address
    [ street_address, city, state, zip ].compact.join(", ")
  end

  # Returns true if the restaurant is currently open
  def open_now?
    # For testing purposes, create a mix of open and closed restaurants
    # In a real app, this would check actual business hours against current time
    
    # Use the last character of the UUID to create a consistent pattern
    # This will make some restaurants "open" and others "closed"
    last_char = id.to_s.last.downcase
    case last_char
    when '0', '1', '2', '3', '4', '5'  # 6 out of 16 hex chars = ~38% closed
      false
    else                               # 10 out of 16 hex chars = ~62% open
      true
    end
  end

  # Original open_now method
  # def open_now?
  #   return false unless business_hours.is_a?(Hash)
  #
  #   now = Time.current
  #   day_name = DAYS[now.wday]
  #   hours_today = business_hours[day_name]
  #
  #   return false unless hours_today.present? && hours_today != "Closed"
  #
  #   # Simple check - in a real app, you'd want to parse the hours
  #   # and compare with current time
  #   true
  # end

  # Returns a status string (Open/Closed) based on current time
  def status
    open_now? ? "Open Now" : "Closed Now"
  end

  # Returns distance from given coordinates or area information
  def distance_or_area(user_lat = nil, user_lng = nil)
    if user_lat.present? && user_lng.present? && latitude.present? && longitude.present?
      distance_km = distance_between([user_lat, user_lng], [latitude, longitude])
      distance_miles = (distance_km * 0.621371).round(1)
      "#{distance_miles} mi"
    else
      # Fallback to showing city or area
      city.present? ? city : "Location unknown"
    end
  end

  # Helper method to calculate distance between two coordinates
  def distance_between(coord1, coord2)
    # Using Haversine formula
    lat1, lng1 = coord1
    lat2, lng2 = coord2
    
    rad_per_deg = Math::PI / 180  # PI / 180
    rkm = 6371                    # Earth radius in kilometers
    rm = rkm * 1000               # Earth radius in meters
    
    dlat_rad = (lat2 - lat1) * rad_per_deg  # Delta, converted to rad
    dlng_rad = (lng2 - lng1) * rad_per_deg
    
    lat1_rad, lat2_rad = lat1 * rad_per_deg, lat2 * rad_per_deg
    
    a = Math.sin(dlat_rad / 2)**2 + Math.cos(lat1_rad) * Math.cos(lat2_rad) * Math.sin(dlng_rad / 2)**2
    c = 2 * Math.asin(Math.sqrt(a))
    
    rkm * c # Delta in kilometers
  end

  # Returns a formatted area string (e.g., "Downtown", "North Austin")
  def area_display
    # For now, just return the city. In a real app, you might have neighborhood data
    city.present? ? city : "Unknown area"
  end
  
  # Returns the tags array, ensuring it's always an array
  def tag_list
    tags.is_a?(Array) ? tags : []
  end
  
  # Check if restaurant has a specific tag
  def has_tag?(tag)
    tag_list.include?(tag)
  end
  
  # Get all unique tags across all restaurants (class method)
  def self.all_tags
    all_tags = []
    Restaurant.where.not(tags: [nil, '']).find_each do |restaurant|
      if restaurant.tags.is_a?(String)
        parsed = JSON.parse(restaurant.tags) rescue []
        all_tags.concat(parsed) if parsed.is_a?(Array)
      elsif restaurant.tags.is_a?(Array)
        all_tags.concat(restaurant.tags)
      end
    end
    all_tags.uniq.sort
  end
  
  # Get all unique cuisine types (class method)
  def self.all_cuisine_types
    Restaurant.distinct.pluck(:cuisine_type).compact.sort
  end
end
