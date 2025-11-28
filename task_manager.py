# Task Tracker - Soren Hundertmark
import json
import datetime
import os
import sys

def main():
    """Parse CLI arguments and dispatch to appropriate command."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    try:
        match command:
            case "create":
                if len(sys.argv) < 4:
                    print("Usage: python task_manager.py create <description> <status>")
                    sys.exit(1)
                description = sys.argv[2]
                status = sys.argv[3]
                createTask(description, status)
            case "update":
                if len(sys.argv) < 3:
                    print("Usage: python task_manager.py update <id> [--description <desc>] [--status <status>]")
                    sys.exit(1)
                task_id = int(sys.argv[2])
                updateTask(task_id, sys.argv[3:])
            case "delete":
                if len(sys.argv) < 3:
                    print("Usage: python task_manager.py delete <id>")
                    sys.exit(1)
                task_id = int(sys.argv[2])
                deleteTask(task_id)
            case "list":
                listAllTasks()
            case "list-completed":
                listAllCompleted()
            case "list-uncompleted":
                listAllUncompleted()
            case "list-in-progress":
                listAllInProgress()
            case "help":
                print_usage()
            case _:
                print(f"Unknown command: {command}")
                print_usage()
                sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid argument. {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def print_usage():
    """Print usage information."""
    print("""
Task Manager CLI

Usage:
  python task_manager.py <command> [options]

Commands:
  create <description> <status>          Create a new task
                                         Status: todo, in-progress, done
  update <id> [--description <desc>]     Update a task's description
             [--status <status>]         Update a task's status
  delete <id>                            Delete a task
  list                                   List all tasks
  list-completed                         List all completed tasks
  list-uncompleted                       List all uncompleted tasks
  list-in-progress                       List all in-progress tasks
  help                                   Show this help message

Examples:
  python task_manager.py create "Buy milk" todo
  python task_manager.py update 0 --status done
  python task_manager.py delete 1
  python task_manager.py list
""")

def createTask(description, status):
    # Creates task and adds it to task_list
    # Validate status
    if status not in ["todo", "in-progress", "done"]:
        raise ValueError(f"Invalid status '{status}'. Must be: todo, in-progress, or done")

    # Get current date and time, then format to strftime
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # Check if file exists and load if it does
    tasks = loadTasks()

    # Assign a new ID as max(existing ids) + 1 to avoid collisions
    if tasks:
        existing_ids = [t.get("id", -1) for t in tasks]
        new_id = max(existing_ids) + 1
    else:
        new_id = 0

    task = {
        "id": new_id,
        "description": description,
        "status": status,
        "createdAt": now_str,
        "updatedAt": now_str
    }

    # Assign next ID and append to tasks
    tasks.append(task)

    # Write list into file
    with open("tasks_list.json", "w") as f:
        json.dump(tasks, f, indent=4)

    print(f"Task added! (ID: {task['id']})")

def updateTask(task_id, args):
    """Update a task by ID with optional --description and --status flags."""
    if not args:
        print(f"No updates provided. Usage: python task_manager.py update {task_id} [--description <desc>] [--status <status>]")
        return

    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == "--description" and i + 1 < len(args):
            updateTaskDescription(task_id, args[i + 1])
            i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            updateStatus(task_id, args[i + 1])
            i += 2
        else:
            i += 1
        
def listAllTasks():
    tasks = loadTasks()

    if not tasks:
        print("No tasks found.")
        return

    print("Listing all tasks:\n")
    for task in tasks:
        print(f"ID: {task['id']}")
        print(f"Description: {task['description']}")
        print(f"Status: {task['status']}")
        print(f"Created At: {task['createdAt']}")
        print(f"Updated At: {task['updatedAt']}\n")

def listAllCompleted():
    tasks = loadTasks()

    completed_tasks = [task for task in tasks if task["status"] == "done"]

    if not completed_tasks:
        print("No completed tasks found.")
        return

    print("Listing all completed tasks:\n")
    for task in completed_tasks:
        printTask(task)

def listAllUncompleted():
    tasks = loadTasks()

    uncompleted_tasks = [task for task in tasks if task["status"] != "done"]

    if not uncompleted_tasks:
        print("No uncompleted tasks found.")
        return

    print("Listing all uncompleted tasks:\n")
    for task in uncompleted_tasks:
        printTask(task)

def listAllInProgress():
    tasks = loadTasks()

    in_progress_tasks = [task for task in tasks if task["status"] == "in-progress"]

    if not in_progress_tasks:
        print("No in-progress tasks found.")
        return

    print("Listing all in-progress tasks:\n")
    for task in in_progress_tasks:
        printTask(task)

#-----------------------------------------------------------------------

# Helper functions

def getTaskByID(id):
    if os.path.exists("tasks_list.json"):
        with open("tasks_list.json", "r") as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                print("Unable to retrieve task. Tasks file is empty or corrupted.")
                return None
    else:
        print(f"No task file found.")
        return None

    for task in tasks:
        if task["id"] == id:
            return task
        
    print(f"No task found with ID {id}")
    return None

def updateTaskDescription(id, description):
    # Load existing file
    with open("tasks_list.json", "r") as f:
        tasks = json.load(f)

    updated = False
    for task in tasks:
        if task["id"] == id:
            task["description"] = description
            task["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = True
            break
    
    if updated:
        # Write task with new description
        with open("tasks_list.json", "w") as f:
            json.dump(tasks, f, indent=4)
        print(f"Task {task['id']} successfully updated.")
    else:
        print(f"No task found with ID: {id}")   

def updateStatus(id, status):
    if status != "todo" and status != "in-progress" and status != "done":
        print("That is not a valid status. Status must be todo, in-progress, or done.")
        return
    
    # Load existing file
    with open("tasks_list.json", "r") as f:
        tasks = json.load(f)

    updated = False
    for task in tasks:
        if task["id"] == id:
            task["status"] = status
            task["updatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = True
            break
    
    if updated:
        # Write task with new description
        with open("tasks_list.json", "w") as f:
            json.dump(tasks, f, indent=4)
        print(f"Task {id} sucessfully updated.")
    else:
        print(f"No task found with ID: {id}")

def deleteTask(id_to_delete):
    # Get task
    getTaskByID(id_to_delete)
    # Remove task
    tasks = loadTasks()

    # Filter out task with specific ID
    new_tasks = [task for task in tasks if task["id"] != id_to_delete]

    if len(new_tasks) == len(tasks):
        print(f"No task found with ID {id_to_delete}")
        return

    # Write updated list back to file
    with open("tasks_list.json", "w") as f:
        json.dump(new_tasks, f, indent=4)
    
    print(f"Task {id_to_delete} has successfully been deleted.")

def printTask(task):
    print(f"ID: {task['id']}")
    print(f"Description: {task['description']}")
    print(f"Status: {task['status']}")
    print(f"Created At: {task['createdAt']}")
    print(f"Updated At: {task['updatedAt']}\n")

def loadTasks():
    if os.path.exists("tasks_list.json"):
        with open("tasks_list.json", "r") as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                tasks = []
    else:
        tasks = []
    return tasks
    

#-----------------------------------------------------------------------


if __name__ == "__main__":
    main()
