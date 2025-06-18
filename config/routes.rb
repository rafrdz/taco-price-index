Rails.application.routes.draw do
  get "frontend_pages/map"
  get "frontend_pages/restaurant_details"
  get "frontend_pages/restaurant_review_form"
  get "frontend_pages/user_profile"
  get "frontend_pages/featured_spotlight"
  get "frontend_pages/restaurant_leaderboard"
  get "frontend_pages/catering_bulk_order"
  get "static_pages/home"
  resource :session
  resources :passwords, param: :token
  resources :restaurants
  resources :tacos
  resources :photos
  resources :reviews
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  root 'static_pages#home'


  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Render dynamic PWA files from app/views/pwa/* (remember to link manifest in application.html.erb)
  # get "manifest" => "rails/pwa#manifest", as: :pwa_manifest
  # get "service-worker" => "rails/pwa#service_worker", as: :pwa_service_worker

  # Defines the root path route ("/")
  # root "posts#index"
end
