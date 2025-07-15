class UserFavorite < ApplicationRecord
  belongs_to :user
  belongs_to :restaurant, counter_cache: :user_favorites_count

  validates :user_id, uniqueness: { scope: :restaurant_id }
end
