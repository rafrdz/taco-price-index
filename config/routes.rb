Rails.application.routes.draw do
  root "static_pages#home"

  get "frontend_pages_featured_spotlight", to: "frontend_pages#featured_spotlight"
  get "frontend_pages_restaurant_leaderboard", to: "frontend_pages#restaurant_leaderboard"
  get "frontend_pages_map", to: "frontend_pages#map"
  get "frontend_pages_user_profile", to: "frontend_pages#user_profile"

  # Authentication routes
  resource :session
  resource :registration, only: [:new, :create]
  resources :passwords, param: :token

  # Test routes
  get "test/map", to: "test#map_test", as: "test_map"

  resources :users, param: :token
  resources :restaurants do
    resources :tacos
    resources :photos
    resources :reviews
    post "toggle_favorite", on: :member
    
    # Delivery and pickup routes
    get "delivery", on: :member
    get "pickup", on: :member

    # Test route for map debugging
    get "map_test", on: :collection
  end
  resources :favorites, only: [ :index ]

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Defines the root path route ("/")
  # root "posts#index"
end
