class StaticPagesController < ApplicationController
  allow_unauthenticated_access :home

  def home
  end
end
