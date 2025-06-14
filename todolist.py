import sqlite3
import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(SCRIPT_DIR, 'todo.db')

def get_db_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending', -- 'pending' or 'completed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()

def add_task(description):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
        connection.commit()
        print(f"Task added: '{description}' (ID: {cursor.lastrowid})")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

def view_tasks(status_filter=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    query = "SELECT id, description, status, created_at FROM tasks"
    params = []
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
    query += " ORDER BY created_at DESC"

    try:
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        if not tasks:
            if status_filter:
                print(f"No tasks found with status '{status_filter}'.")
            else:
                print("No tasks found. Add some using the 'add' command!")
            return

        print("\n--- Your To-Do List ---")
        for task in tasks:
            created_time = datetime.datetime.strptime(task['created_at'], '%Y-%m-%d %H:%M:%S')
            formatted_time = created_time.strftime('%Y-%m-%d %H:%M')
            print(f"ID: {task['id']:<3} | Status: {task['status'].capitalize():<10} | Created: {formatted_time}")
            print(f"  Desc: {task['description']}")
            print("-" * 40)
        print("--- End of List ---\n")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

def update_task_status(task_id, new_status):
    if new_status not in ['pending', 'completed']:
        print(f"Invalid status: '{new_status}'. Must be 'pending' or 'completed'.")
        return

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            print(f"Error: Task with ID {task_id} not found.")
            return

        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"Task ID {task_id} marked as {new_status}.")
        else:
            print(f"Task ID {task_id} status was already {new_status} or task not found during update.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            print(f"Error: Task with ID {task_id} not found.")
            return

        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"Task ID {task_id} deleted successfully.")
        else:
            print(f"Error: Task with ID {task_id} not found during deletion.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

def main():
    initialize_database()
    
    print("Welcome to the CLI To-Do List!")
    print("Available commands: add, view, complete, pending, delete, exit")
    print("Examples:")
    print("  add <task description>")
    print("  view [pending|completed]")
    print("  complete <task_id>")
    print("  pending <task_id>")
    print("  delete <task_id>")
    print("  exit")
    print("-" * 30)

    while True:
        user_input = input("\nWhat would you like to do? ").strip().lower()
        parts = user_input.split(maxsplit=1)
        command = parts[0] if parts else ""

        if command == 'exit':
            print("Thanks for using, Goodbye!")
            break
        elif command == 'add':
            if len(parts) > 1:
                description = parts[1]
                add_task(description)
            else:
                print("Error: Please provide a task description. Example: add Buy some milk.")
        elif command == 'view':
            status_filter = None
            if len(parts) > 1:
                filter_arg = parts[1].lower()
                if filter_arg in ['pending', 'completed']:
                    status_filter = filter_arg
                else:
                    print(f"Error：The filter argument is not allowed: '{filter_arg}'。Please use 'pending' or 'completed'.")
                    continue
            view_tasks(status_filter)
        elif command in ['complete', 'pending', 'delete']:
            if len(parts) > 1:
                try:
                    task_id = int(parts[1])
                    if command == 'complete':
                        update_task_status(task_id, 'completed')
                    elif command == 'pending':
                        update_task_status(task_id, 'pending')
                    elif command == 'delete':
                        delete_task(task_id)
                except ValueError:
                    print(f"Error: ID '{parts[1]}' must be a number。 e.g. {command} 1")
                except IndexError:
                    print(f"Error: Please provide a task ID。e.g. {command} 1")
            else:
                print(f"Error: Please provide a task ID。e.g. {command} 1")
        elif command == "":
            continue
        else:
            print(f"Error: Unknown command: '{command}'。")
            print("Avaliable commands: add, view, complete, pending, delete, exit")


if __name__ == "__main__":
    main()