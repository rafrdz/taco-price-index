class FixCheckUserExistsForUuid < ActiveRecord::Migration[8.0]
  def up
    execute <<-SQL
      CREATE OR REPLACE FUNCTION check_user_exists()
      RETURNS TRIGGER AS $$
      BEGIN
        IF NEW.user_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM users WHERE id = NEW.user_id) THEN
          RAISE EXCEPTION 'User with id % does not exist', NEW.user_id;
        END IF;
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;
    SQL
  end

  def down
    # nothing to do - previous version cast to bigint, we won't revert
  end
end
