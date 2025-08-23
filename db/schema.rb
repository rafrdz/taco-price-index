# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 2025_08_22_215019) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "active_storage_attachments", force: :cascade do |t|
    t.string "name", null: false
    t.string "record_type", null: false
    t.bigint "record_id", null: false
    t.bigint "blob_id", null: false
    t.datetime "created_at", null: false
    t.index ["blob_id"], name: "index_active_storage_attachments_on_blob_id"
    t.index ["record_type", "record_id", "name", "blob_id"], name: "index_active_storage_attachments_uniqueness", unique: true
  end

  create_table "active_storage_blobs", force: :cascade do |t|
    t.string "key", null: false
    t.string "filename", null: false
    t.string "content_type"
    t.text "metadata"
    t.string "service_name", null: false
    t.bigint "byte_size", null: false
    t.string "checksum"
    t.datetime "created_at", null: false
    t.index ["key"], name: "index_active_storage_blobs_on_key", unique: true
  end

  create_table "active_storage_variant_records", force: :cascade do |t|
    t.bigint "blob_id", null: false
    t.string "variation_digest", null: false
    t.index ["blob_id", "variation_digest"], name: "index_active_storage_variant_records_uniqueness", unique: true
  end

  create_table "photos", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.uuid "taco_id"
    t.uuid "user_id"
    t.text "url", null: false
    t.boolean "is_user_uploaded", default: true
    t.datetime "created_at", precision: nil, default: -> { "now()" }
  end

  create_table "restaurants", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.text "name", null: false
    t.text "street_address"
    t.text "city"
    t.text "state"
    t.text "zip"
    t.float "latitude"
    t.float "longitude"
    t.text "phone"
    t.text "website"
    t.text "yelp_id"
    t.decimal "google_rating", precision: 2, scale: 1
    t.integer "google_price_level"
    t.integer "google_user_ratings_total"
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
    t.text "business_hours"
    t.text "description"
    t.integer "user_favorites_count", default: 0, null: false
    t.string "cuisine_type"
    t.text "tags"
    t.index ["user_favorites_count"], name: "index_restaurants_on_user_favorites_count"
  end

  create_table "reviews", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.uuid "taco_id"
    t.text "content"
    t.datetime "submitted_at", precision: nil, default: -> { "now()" }
    t.boolean "verified_location", default: false
    t.float "gps_latitude"
    t.float "gps_longitude"
    t.integer "fullness_rating"
    t.uuid "authenticity_id"
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
    t.text "author_name"
    t.text "author_url"
    t.integer "google_rating"
    t.text "review_text"
    t.bigint "review_time"
    t.text "relative_time_description"
    t.text "language"
    t.datetime "review_date", precision: nil
    t.uuid "restaurant_id"
    t.bigint "user_id"
    t.index ["user_id"], name: "index_reviews_on_user_id"
    t.check_constraint "fullness_rating >= 1 AND fullness_rating <= 5", name: "reviews_fullness_rating_check"
  end

  create_table "sessions", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.string "ip_address"
    t.string "user_agent"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_sessions_on_user_id"
  end

  create_table "tacos", id: :uuid, default: -> { "gen_random_uuid()" }, force: :cascade do |t|
    t.uuid "restaurant_id"
    t.text "name"
    t.text "description"
    t.integer "price_cents"
    t.integer "calories"
    t.text "tortilla_type"
    t.text "protein_type"
    t.boolean "is_vegan", default: false
    t.boolean "is_bulk", default: false
    t.boolean "is_daily_special", default: false
    t.time "available_from"
    t.time "available_to"
    t.datetime "created_at", precision: nil, default: -> { "now()" }
    t.datetime "updated_at", precision: nil, default: -> { "now()" }
  end

  create_table "user_favorites", force: :cascade do |t|
    t.bigint "user_id", null: false
    t.uuid "restaurant_id", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id", "restaurant_id"], name: "index_user_favorites_on_user_id_and_restaurant_id", unique: true
    t.index ["user_id"], name: "index_user_favorites_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.string "email_address", null: false
    t.string "password_digest", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.boolean "admin", default: false, null: false
    t.index ["email_address"], name: "index_users_on_email_address", unique: true
  end

  add_foreign_key "active_storage_attachments", "active_storage_blobs", column: "blob_id"
  add_foreign_key "active_storage_variant_records", "active_storage_blobs", column: "blob_id"
  add_foreign_key "photos", "tacos", name: "photos_taco_id_fkey", on_delete: :cascade
  add_foreign_key "reviews", "restaurants", name: "reviews_restaurant_id_fkey", on_delete: :cascade
  add_foreign_key "reviews", "tacos", name: "reviews_taco_id_fkey", on_delete: :cascade
  add_foreign_key "reviews", "users"
  add_foreign_key "sessions", "users"
  add_foreign_key "tacos", "restaurants", name: "tacos_restaurant_id_fkey", on_delete: :cascade
  add_foreign_key "user_favorites", "restaurants"
  add_foreign_key "user_favorites", "users"
end
