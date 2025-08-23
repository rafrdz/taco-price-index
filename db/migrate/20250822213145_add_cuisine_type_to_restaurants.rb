class AddCuisineTypeToRestaurants < ActiveRecord::Migration[8.0]
  def change
    add_column :restaurants, :cuisine_type, :string
  end
end
