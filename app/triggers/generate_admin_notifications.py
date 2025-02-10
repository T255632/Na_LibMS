from sqlalchemy import text
from models import db
from sqlalchemy.exc import ProgrammingError
from psycopg2.errors import DuplicateObject

def create_notification_triggers():
    # SQL for creating the notification trigger function
    trigger_function_sql = """
    CREATE OR REPLACE FUNCTION generate_admin_notification() 
    RETURNS trigger AS $$
    BEGIN
        -- Handle Insert operation
        IF (TG_OP = 'INSERT') THEN
            IF (TG_TABLE_NAME = 'members') THEN
                INSERT INTO notifications (message, member_id, role, created_at)
                VALUES ('A new member has been added: ' || NEW.name || ' (Membership Number: ' || NEW.membership_number || ')', NEW.member_id, 'Member', NOW());
            ELSIF (TG_TABLE_NAME = 'staff') THEN
                INSERT INTO notifications (message, staff_id, role, created_at)
                VALUES ('A new staff member has been added: ' || NEW.name || ' (Role: ' || NEW.role || ')', NEW.staff_id, 'Staff', NOW());
            ELSIF (TG_TABLE_NAME = 'library_resources') THEN
                INSERT INTO notifications (message, resource_id, role, created_at)
                VALUES ('A new library resource has been added: ' || NEW.title || ' (Resource Type: ' || NEW.resource_type || ')', NEW.resource_id, 'Staff', NOW());
            ELSIF (TG_TABLE_NAME = 'borrowing_rules') THEN
                INSERT INTO notifications (message, rule_id, role, created_at)
                VALUES ('A new borrowing rule has been added: ' || NEW.resource_type || ' (Max Borrow Duration: ' || NEW.max_borrow_duration || ')', NEW.rule_id, 'Staff', NOW());
            END IF;
        
        -- Handle Update operation
        ELSIF (TG_OP = 'UPDATE') THEN
            IF (TG_TABLE_NAME = 'members') THEN
                INSERT INTO notifications (message, member_id, role, created_at)
                VALUES ('Member information has been updated: ' || NEW.name || ' (Membership Number: ' || NEW.membership_number || ')', NEW.member_id, 'Member', NOW());
            ELSIF (TG_TABLE_NAME = 'staff') THEN
                INSERT INTO notifications (message, staff_id, role, created_at)
                VALUES ('Staff information has been updated: ' || NEW.name || ' (Role: ' || NEW.role || ')', NEW.staff_id, 'Staff', NOW());
            ELSIF (TG_TABLE_NAME = 'library_resources') THEN
                INSERT INTO notifications (message, resource_id, role, created_at)
                VALUES ('Library resource has been updated: ' || NEW.title || ' (Resource Type: ' || NEW.resource_type || ')', NEW.resource_id, 'Staff', NOW());
            ELSIF (TG_TABLE_NAME = 'borrowing_rules') THEN
                INSERT INTO notifications (message, rule_id, role, created_at)
                VALUES ('Borrowing rule has been updated: ' || NEW.resource_type || ' (Max Borrow Duration: ' || NEW.max_borrow_duration || ')', NEW.rule_id, 'Staff', NOW());
            END IF;
        
        -- Handle Delete operation
        ELSIF (TG_OP = 'DELETE') THEN
            IF (TG_TABLE_NAME = 'members') THEN
                -- Check if the member still exists before inserting a notification
                IF EXISTS (SELECT 1 FROM members WHERE member_id = OLD.member_id) THEN
                    INSERT INTO notifications (message, member_id, role, created_at)
                    VALUES ('A member has been deleted: ' || OLD.name || ' (Membership Number: ' || OLD.membership_number || ')', OLD.member_id, 'Member', NOW());
                END IF;
            ELSIF (TG_TABLE_NAME = 'staff') THEN
                -- Check if the staff still exists before inserting a notification
                IF EXISTS (SELECT 1 FROM staff WHERE staff_id = OLD.staff_id) THEN
                    INSERT INTO notifications (message, staff_id, role, created_at)
                    VALUES ('A staff member has been deleted: ' || OLD.name || ' (Role: ' || OLD.role || ')', OLD.staff_id, 'Staff', NOW());
                END IF;
            ELSIF (TG_TABLE_NAME = 'library_resources') THEN
                -- Check if the library resource still exists before inserting a notification
                IF EXISTS (SELECT 1 FROM library_resources WHERE resource_id = OLD.resource_id) THEN
                    INSERT INTO notifications (message, resource_id, role, created_at)
                    VALUES ('A library resource has been deleted: ' || OLD.title || ' (Resource Type: ' || OLD.resource_type || ')', OLD.resource_id, 'Staff', NOW());
                END IF;
            ELSIF (TG_TABLE_NAME = 'borrowing_rules') THEN
                -- Check if the borrowing rule still exists before inserting a notification
                IF EXISTS (SELECT 1 FROM borrowing_rules WHERE rule_id = OLD.rule_id) THEN
                    INSERT INTO notifications (message, rule_id, role, created_at)
                    VALUES ('A borrowing rule has been deleted: ' || OLD.resource_type || ' (Max Borrow Duration: ' || OLD.max_borrow_duration || ')', OLD.rule_id, 'Staff', NOW());
                END IF;
            END IF;
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

    # SQL for creating the triggers
    triggers_sql = """
    -- Drop existing triggers if they exist
    DROP TRIGGER IF EXISTS notify_library_resources_insert ON library_resources;
    DROP TRIGGER IF EXISTS notify_library_resources_update ON library_resources;
    DROP TRIGGER IF EXISTS notify_library_resources_delete ON library_resources;

    DROP TRIGGER IF EXISTS notify_members_insert ON members;
    DROP TRIGGER IF EXISTS notify_members_update ON members;
    DROP TRIGGER IF EXISTS notify_members_delete ON members;

    DROP TRIGGER IF EXISTS notify_staff_insert ON staff;
    DROP TRIGGER IF EXISTS notify_staff_update ON staff;
    DROP TRIGGER IF EXISTS notify_staff_delete ON staff;

    DROP TRIGGER IF EXISTS notify_borrowing_rules_insert ON borrowing_rules;
    DROP TRIGGER IF EXISTS notify_borrowing_rules_update ON borrowing_rules;
    DROP TRIGGER IF EXISTS notify_borrowing_rules_delete ON borrowing_rules;

    -- Create triggers for library_resources table
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

    -- Create triggers for members table
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

    -- Create triggers for staff table
    CREATE TRIGGER notify_staff_insert
    AFTER INSERT ON staff
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_staff_update
    AFTER UPDATE ON staff
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_staff_delete
    AFTER DELETE ON staff
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    -- Create triggers for borrowing_rules table
    CREATE TRIGGER notify_borrowing_rules_insert
    AFTER INSERT ON borrowing_rules
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_borrowing_rules_update
    AFTER UPDATE ON borrowing_rules
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();

    CREATE TRIGGER notify_borrowing_rules_delete
    AFTER DELETE ON borrowing_rules
    FOR EACH ROW
    EXECUTE FUNCTION generate_admin_notification();
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

