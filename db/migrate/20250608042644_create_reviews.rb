class CreateReviews < ActiveRecord::Migration[8.0]
  def change
    create_table :reviews do |t|
      t.references :restaurant, null: false, foreign_key: true
      t.string :author_name
      t.string :author_url
      t.integer :google_rating
      t.text :review_text
      t.bigint :review_time
      t.string :relative_time_description
      t.string :language
      t.datetime :review_date
      t.text :content

      t.timestamps
    end
  end
end
