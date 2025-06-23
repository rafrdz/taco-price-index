class ChangeReviewsUserIdToInteger < ActiveRecord::Migration[8.0]
  def change
    # remove uuid user_id column
    remove_column :reviews, :user_id, :uuid
    # add bigint user reference with foreign key
    add_reference :reviews, :user, null: true, foreign_key: true
  end
end
