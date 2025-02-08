from sqlalchemy import text
from models import db
from sqlalchemy.exc import ProgrammingError
from psycopg2.errors import DuplicateObject

def create_notification_triggers():
    trigger_function_sql = """
    CREATE OR REPLACE FUNCTION generate_admin_notification() 
    RETURNS trigger AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            INSERT INTO notifications (message, user_id, role, created_at)
            VALUES ('A new record has been added to ' || TG_TABLE_NAME, NEW.id, 'Admin', NOW());
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO notifications (message, user_id, role, created_at)
            VALUES ('A record has been updated in ' || TG_TABLE_NAME, NEW.id, 'Admin', NOW());
        ELSIF (TG_OP = 'DELETE') THEN
            INSERT INTO notifications (message, user_id, role, created_at)
            VALUES ('A record has been deleted from ' || TG_TABLE_NAME, OLD.id, 'Admin', NOW());
        END IF;
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """
    try:
        # Execute the SQL to create the function
        db.session.execute(text(trigger_function_sql))  # Wrap the raw SQL in text()
        db.session.commit()  # Commit the transaction to save changes
    except ProgrammingError as e:
        print(f"Error creating function: {e}")
        db.session.rollback()  # Rollback in case of error

    triggers_sql = """
    -- Drop triggers if they exist before creating new ones
    DROP TRIGGER IF EXISTS notify_library_resources_insert ON library_resources;
    DROP TRIGGER IF EXISTS notify_library_resources_update ON library_resources;
    DROP TRIGGER IF EXISTS notify_library_resources_delete ON library_resources;

    DROP TRIGGER IF EXISTS notify_members_insert ON members;
    DROP TRIGGER IF EXISTS notify_members_update ON members;
    DROP TRIGGER IF EXISTS notify_members_delete ON members;

    -- Repeat for other tables (staff, borrowing_rules, lending_transactions)

    CREATE TRIGGER notify_library_resources_insert
    AFTER INSERT ON library_resources
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_library_resources_update
    AFTER UPDATE ON library_resources
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_library_resources_delete
    AFTER DELETE ON library_resources
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_members_insert
    AFTER INSERT ON members
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_members_update
    AFTER UPDATE ON members
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_members_delete
    AFTER DELETE ON members
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    -- Repeat for other tables (staff, borrowing_rules, lending_transactions)
    """
    try:
        # Execute the SQL to create the triggers
        db.session.execute(text(triggers_sql))  # Wrap the raw SQL in text()
        db.session.commit()  # Commit the transaction to save changes
    except DuplicateObject as e:
        print(f"Duplicate trigger error: {e}")
        db.session.rollback()  # Rollback in case of error
    except ProgrammingError as e:
        print(f"Error creating triggers: {e}")
        db.session.rollback()  # Rollback in case of error
