class AddTagsToRestaurants < ActiveRecord::Migration[8.0]
  def change
    add_column :restaurants, :tags, :text
  end
end
