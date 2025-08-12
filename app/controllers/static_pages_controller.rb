# app/controllers/static_pages_controller.rb

class StaticPagesController < ApplicationController
  allow_unauthenticated_access :home

  def home
  end
end
