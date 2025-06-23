class AddBusinessHoursToRestaurants < ActiveRecord::Migration[8.0]
  def change
    add_column :restaurants, :business_hours, :text
  end
end
