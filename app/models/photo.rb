class Photo < ApplicationRecord
  belongs_to :taco

  validates :url, presence: true
  validates :url, format: { with: URI.regexp(%w[http https]), message: "must be a valid URL" }
end
