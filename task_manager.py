# Task Tracker - Soren Hundertmark
import json
import datetime
import os

def main():
    running = True
    while running:
        menu()
        operation = input()
        match operation:
            case "1":
                createTask()
            case "2":
                id_to_update = int(input("Please provide the ID for the task you want to update: "))
                updateTask(id_to_update)
            case "3":
                id_to_delete = int(input("Please provide the ID for the task you want to delete: "))
                deleteTask(id_to_delete)
            case "4":
                listAllTasks()
            case "5":
                listAllCompleted()
            case "6":
                listAllUncompleted()
            case "7":
                listAllInProgress()
            case "8":
                print("Exiting Menu...")
                running = False

    


def menu():
    # Menu with various operations
    print("----------------------------------------------\n")
    print("Task Manager Menu\n")
    print("Select the operation you want to perform: \n")
    print("(1) Create task")
    print("(2) Update task")
    print("(3) Delete task")
    print("(4) List all tasks")
    print("(5) List all completed tasks")
    print("(6) List all uncompleted tasks")
    print("(7) List all tasks in-progress")
    print("(8) Exit Menu\n")
    print("----------------------------------------------")

def createTask():
    # Creates task and adds it to task_list
    print("Enter a description for your task: ")
    description = input()

    while True:
        print("Enter a status for your task (todo, in-progress, done): ")
        status = input()
        if status in ["todo", "in-progress", "done"]:
            break
        print("Invalid input. Please enter a valid status.")

    # Get current date and time, then format to strftime
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # Check if file exists and load if it does
    tasks = loadTasks()

    new_id = len(tasks)

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

def updateTask(id_to_update):
    # Get task with matching ID, if exists
    getTaskByID(id_to_update)

    # Modify selected task
    # Can only modify description and status
    modify_key = input("To modify task enter: "
    "\n(1) To update description"
    "\n(2) To update status"
    "\n(3) To exit\n")
    match modify_key:
        case "1":
            new_description = input("Enter your task's new description: ")
            updateTaskDescription(id_to_update, new_description)
        case "2":
            new_status = input("Enter your task's new status (todo, in-progress, done): ")
            updateStatus(id_to_update, new_status)
        case "3":
            print("Exiting...")
            return
        
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


main()
