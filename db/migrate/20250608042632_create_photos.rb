class CreatePhotos < ActiveRecord::Migration[8.0]
  def change
    create_table :photos do |t|
      t.references :taco, null: false, foreign_key: true
      t.uuid :user_id
      t.string :url
      t.boolean :is_user_uploaded

      t.timestamps
    end
  end
end
