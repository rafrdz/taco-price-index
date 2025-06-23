class FrontendPagesController < ApplicationController
  before_action :authenticate_user!, except: [:map, :restaurant_details]

  def map
    @restaurants = Restaurant.all
    @user = Current.session&.user
    @is_favorited = @user&.favorite_restaurants.exists?(@restaurant) if @user
    @favorite_count = @restaurant.favorite_count if @restaurant
  end

  def restaurant_details
    @restaurant = Restaurant.find(params[:id])
    @tacos = @restaurant.tacos
    @photos = @restaurant.photos
    @reviews = @restaurant.reviews
    @user = Current.session&.user
    @is_favorited = @user&.favorite_restaurants.exists?(@restaurant) if @user
    @favorite_count = @restaurant.favorite_count
  end
end
