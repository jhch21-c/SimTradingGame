import sqlite3


def wipe_all_records():
    # Connect to the SQLite database
    conn = sqlite3.connect("exchange.db")
    cursor = conn.cursor()

    # Retrieve the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Delete all records from each table
    for table_name in tables:
        cursor.execute(f"DELETE FROM {table_name[0]};")
        print(f"All records from table {table_name[0]} deleted.")

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()
    print("All records have been wiped.")


# Example usage
wipe_all_records()
import sqlite3


def wipe_all_but_first_record():
    # Connect to the SQLite database
    conn = sqlite3.connect("stock_prices.db")
    cursor = conn.cursor()

    # Retrieve the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Delete all records but the first one from each table
    for table_name in tables:
        # Get the rowid of the first record
        cursor.execute(f'SELECT rowid FROM "{table_name[0]}" LIMIT 1;')
        first_record_rowid = cursor.fetchone()

        if first_record_rowid:
            # Delete all records except the first one
            cursor.execute(
                f'DELETE FROM "{table_name[0]}" WHERE rowid NOT IN (SELECT rowid FROM "{table_name[0]}" LIMIT 1);')
            print(f'All records except the first one from table {table_name[0]} deleted.')
        else:
            print(f'Table {table_name[0]} is empty.')

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()
    print("All records except the first one have been wiped.")


# Example usage
wipe_all_but_first_record()
