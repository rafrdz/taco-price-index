ENV["BUNDLE_GEMFILE"] ||= File.expand_path("../Gemfile", __dir__)

require "bundler/setup" # Set up gems listed in the Gemfile.

# Set up Rails environment
ENV["RAILS_ENV"] ||= "development"

# Load the Rails application.
require_relative "application" # Speed up boot time by caching expensive operations.
