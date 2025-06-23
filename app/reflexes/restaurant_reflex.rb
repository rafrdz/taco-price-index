class RestaurantReflex < ApplicationReflex
  before_reflex do
    @restaurant = Restaurant.find(params[:restaurantId])
  end

  def toggle_favorite
    if params[:isFavorite]
      current_user.favorite_restaurants.delete(@restaurant)
    else
      current_user.favorite_restaurants << @restaurant
    end

    morph :nothing
  end
end
