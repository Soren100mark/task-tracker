import json
import os
import sys
import pytest

import task_manager


def write_tasks_file(path, tasks):
    with open(path / "tasks_list.json", "w") as f:
        json.dump(tasks, f, indent=4)


def test_loadTasks_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Ensure no file exists
    if (tmp_path / "tasks_list.json").exists():
        (tmp_path / "tasks_list.json").unlink()

    tasks = task_manager.loadTasks()
    assert tasks == []


def test_getTaskByID_found_and_not_found(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    sample = [{"id": 0, "description": "a", "status": "todo", "createdAt": "2020-01-01 00:00:00", "updatedAt": "2020-01-01 00:00:00"}]
    write_tasks_file(tmp_path, sample)

    found = task_manager.getTaskByID(0)
    assert found is not None
    assert found["description"] == "a"

    not_found = task_manager.getTaskByID(5)
    assert not_found is None
    captured = capsys.readouterr()
    assert "No task found with ID 5" in captured.out


def test_updateStatus_valid_and_invalid(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tasks = [
        {"id": 0, "description": "t", "status": "todo", "createdAt": "2020-01-01 00:00:00", "updatedAt": "2020-01-01 00:00:00"}
    ]
    write_tasks_file(tmp_path, tasks)

    # Valid update
    task_manager.updateStatus(0, "done")
    with open(tmp_path / "tasks_list.json", "r") as f:
        updated = json.load(f)
    assert updated[0]["status"] == "done"
    assert updated[0]["updatedAt"] != "2020-01-01 00:00:00"

    # Invalid status
    task_manager.updateStatus(0, "invalid-status")
    captured = capsys.readouterr()
    assert "That is not a valid status" in captured.out


def test_updateTaskDescription_updates_file(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tasks = [
        {"id": 0, "description": "old", "status": "todo", "createdAt": "2020-01-01 00:00:00", "updatedAt": "2020-01-01 00:00:00"}
    ]
    write_tasks_file(tmp_path, tasks)

    task_manager.updateTaskDescription(0, "new desc")
    with open(tmp_path / "tasks_list.json", "r") as f:
        updated = json.load(f)
    assert updated[0]["description"] == "new desc"
    assert updated[0]["updatedAt"] != "2020-01-01 00:00:00"


def test_deleteTask_removes_task(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tasks = [
        {"id": 0, "description": "a", "status": "todo", "createdAt": "t", "updatedAt": "t"},
        {"id": 1, "description": "b", "status": "todo", "createdAt": "t", "updatedAt": "t"}
    ]
    write_tasks_file(tmp_path, tasks)

    task_manager.deleteTask(0)
    with open(tmp_path / "tasks_list.json", "r") as f:
        remaining = json.load(f)
    assert len(remaining) == 1
    assert remaining[0]["id"] == 1


def test_createTask_appends_task(tmp_path, monkeypatch):
    # Prepare empty dir and control inputs + datetime
    monkeypatch.chdir(tmp_path)

    class DummyDateTimeModule:
        class datetime:
            @staticmethod
            def now():
                import datetime as real
                return real.datetime(2020, 1, 1, 12, 0, 0)

    monkeypatch.setattr(task_manager, "datetime", DummyDateTimeModule)

    # Call createTask with arguments instead of mocking input
    task_manager.createTask("My new task", "todo")
    with open(tmp_path / "tasks_list.json", "r") as f:
        tasks = json.load(f)

    assert len(tasks) == 1
    t = tasks[0]
    assert t["description"] == "My new task"
    assert t["status"] == "todo"
    assert t["createdAt"] == "2020-01-01 12:00:00"


def test_listAll_variants_print_expected_tasks(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    tasks = [
        {"id": 0, "description": "one", "status": "todo", "createdAt": "t", "updatedAt": "t"},
        {"id": 1, "description": "two", "status": "in-progress", "createdAt": "t", "updatedAt": "t"},
        {"id": 2, "description": "three", "status": "done", "createdAt": "t", "updatedAt": "t"}
    ]
    write_tasks_file(tmp_path, tasks)

    # listAllTasks
    task_manager.listAllTasks()
    out = capsys.readouterr().out
    assert "Listing all tasks" in out
    assert "Description: one" in out and "Description: two" in out and "Description: three" in out

    # listAllCompleted
    task_manager.listAllCompleted()
    out = capsys.readouterr().out
    assert "Description: three" in out and "Description: one" not in out

    # listAllUncompleted
    task_manager.listAllUncompleted()
    out = capsys.readouterr().out
    assert "Description: one" in out and "Description: two" in out and "Description: three" not in out

    # listAllInProgress
    task_manager.listAllInProgress()
    out = capsys.readouterr().out
    assert "Description: two" in out and "Description: one" not in out


def test_updateTask_interactive_flows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tasks = [
        {"id": 0, "description": "orig", "status": "todo", "createdAt": "t", "updatedAt": "t"}
    ]
    write_tasks_file(tmp_path, tasks)

    # Update description flow using CLI args
    task_manager.updateTask(0, ["--description", "changed desc"])
    with open(tmp_path / "tasks_list.json", "r") as f:
        updated = json.load(f)
    assert updated[0]["description"] == "changed desc"

    # Update status flow using CLI args
    task_manager.updateTask(0, ["--status", "in-progress"])
    with open(tmp_path / "tasks_list.json", "r") as f:
        updated = json.load(f)
    assert updated[0]["status"] == "in-progress"


def test_createTask_id_collision_demo(tmp_path, monkeypatch):
    """Tests safe ID allocation: `createTask` uses `max(existing_ids)+1` to avoid collisions."""
    monkeypatch.chdir(tmp_path)
    # Existing tasks with ids 0 and 2 (gap at 1)
    tasks = [
        {"id": 0, "description": "a", "status": "todo", "createdAt": "t", "updatedAt": "t"},
        {"id": 2, "description": "b", "status": "todo", "createdAt": "t", "updatedAt": "t"}
    ]
    write_tasks_file(tmp_path, tasks)

    class DummyDateTimeModule:
        class datetime:
            @staticmethod
            def now():
                import datetime as real
                return real.datetime(2020, 1, 1, 12, 0, 0)

    monkeypatch.setattr(task_manager, "datetime", DummyDateTimeModule)

    task_manager.createTask("New", "todo")
    with open(tmp_path / "tasks_list.json", "r") as f:
        after = json.load(f)

    # New behavior: task id should be max(existing)+1 (i.e., 3)
    ids = [t["id"] for t in after]
    assert 0 in ids and 2 in ids
    assert 3 in ids


def test_main_exit_immediately(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    # Provide sys.argv with help command to show usage
    monkeypatch.setattr(sys, "argv", ["task_manager.py", "help"])
    task_manager.main()
    out = capsys.readouterr().out
    assert "Task Manager CLI" in out


def test_main_create_command(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    # Simulate: python task_manager.py create "Test task" todo
    monkeypatch.setattr(sys, "argv", ["task_manager.py", "create", "Test task", "todo"])
    task_manager.main()
    
    # Verify task was created
    with open(tmp_path / "tasks_list.json", "r") as f:
        tasks = json.load(f)
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Test task"
    assert tasks[0]["status"] == "todo"


def test_main_update_and_delete_flows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # Create initial task
    monkeypatch.setattr(sys, "argv", ["task_manager.py", "create", "Original", "todo"])
    task_manager.main()
    
    # Update the task
    monkeypatch.setattr(sys, "argv", ["task_manager.py", "update", "0", "--description", "Updated"])
    task_manager.main()
    
    with open(tmp_path / "tasks_list.json", "r") as f:
        tasks = json.load(f)
    assert tasks[0]["description"] == "Updated"
    
    # Delete the task
    monkeypatch.setattr(sys, "argv", ["task_manager.py", "delete", "0"])
    task_manager.main()
    
    with open(tmp_path / "tasks_list.json", "r") as f:
        tasks = json.load(f)
    assert len(tasks) == 0
