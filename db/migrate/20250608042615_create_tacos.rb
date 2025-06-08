class CreateTacos < ActiveRecord::Migration[8.0]
  def change
    create_table :tacos do |t|
      t.references :restaurant, null: false, foreign_key: true
      t.string :name
      t.text :description
      t.integer :price_cents
      t.integer :calories
      t.string :tortilla_type
      t.string :protein_type
      t.boolean :is_vegan
      t.boolean :is_bulk
      t.boolean :is_daily_special
      t.time :available_from
      t.time :available_to

      t.timestamps
    end
  end
end
