# Task-tracker

Task tracker project used to track and manage your tasks. This is a simple command line interface (CLI) to track what you need to do, what you have done, and what you are currently working on.

## Features

- CRUD (Create, Add, Update, Delete) Operations for tasks
- List all tasks operation
- List all tasks operation for each possible status
- Local storage for storing tasks using JSON file
- Command-line argument interface (no interactive menu required)

## Running locally

To run this project locally, use positional arguments and flags:

```bash
python task_manager.py create "Buy milk" todo
python task_manager.py update 0 --status done
python task_manager.py list
python task_manager.py delete 0
python task_manager.py help
```

## Usage

### Create a task

```bash
python task_manager.py create "<description>" <status>
# Status can be: todo, in-progress, done

# Example:
python task_manager.py create "Buy groceries" todo
```

### List tasks

```bash
python task_manager.py list                 # List all tasks
python task_manager.py list-completed       # List completed tasks (status: done)
python task_manager.py list-uncompleted     # List uncompleted tasks (status: not done)
python task_manager.py list-in-progress     # List in-progress tasks
```

### Update a task

```bash
python task_manager.py update <id> [--description "<new_desc>"] [--status <new_status>]

# Example:
python task_manager.py update 0 --status in-progress
python task_manager.py update 0 --description "Updated description"
python task_manager.py update 0 --description "New desc" --status done
```

### Delete a task

```bash
python task_manager.py delete <id>

# Example:
python task_manager.py delete 0
```

### Get help

```bash
python task_manager.py help
```

## Project URL

https://github.com/Soren100mark/task-tracker
