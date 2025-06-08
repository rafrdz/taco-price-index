class CreateRestaurants < ActiveRecord::Migration[8.0]
  def change
    create_table :restaurants do |t|
      t.string :name
      t.string :street_address
      t.string :city
      t.string :state
      t.string :zip
      t.decimal :latitude
      t.decimal :longitude
      t.string :phone
      t.string :website
      t.string :yelp_id

      t.timestamps
    end
  end
end
