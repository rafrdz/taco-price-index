class User < ApplicationRecord
  has_secure_password
  has_many :sessions, dependent: :destroy

  # Rails login
  normalizes :email_address, with: ->(e) { e.strip.downcase }
  validates :email_address, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :password, length: { minimum: 6 }, if: -> { }
end
