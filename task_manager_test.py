import json
import os
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

    inputs = iter(["My new task", "todo"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    class DummyDateTimeModule:
        class datetime:
            @staticmethod
            def now():
                import datetime as real
                return real.datetime(2020, 1, 1, 12, 0, 0)

    monkeypatch.setattr(task_manager, "datetime", DummyDateTimeModule)

    # Call createTask and assert a file was created with expected task
    task_manager.createTask()
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

    # Update description flow: choose option 1 then provide new description
    inputs = iter(["1", "changed desc"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))
    task_manager.updateTask(0)
    with open(tmp_path / "tasks_list.json", "r") as f:
        updated = json.load(f)
    assert updated[0]["description"] == "changed desc"

    # Update status flow: choose option 2 then provide new status
    inputs = iter(["2", "in-progress"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))
    task_manager.updateTask(0)
    with open(tmp_path / "tasks_list.json", "r") as f:
        updated = json.load(f)
    assert updated[0]["status"] == "in-progress"


def test_createTask_id_collision_demo(tmp_path, monkeypatch):
    """Demonstrates current behavior: `createTask` uses `len(tasks)` which can collide with existing IDs."""
    monkeypatch.chdir(tmp_path)
    # Existing tasks with ids 0 and 2 (gap at 1)
    tasks = [
        {"id": 0, "description": "a", "status": "todo", "createdAt": "t", "updatedAt": "t"},
        {"id": 2, "description": "b", "status": "todo", "createdAt": "t", "updatedAt": "t"}
    ]
    write_tasks_file(tmp_path, tasks)

    inputs = iter(["New", "todo"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    class DummyDateTimeModule:
        class datetime:
            @staticmethod
            def now():
                import datetime as real
                return real.datetime(2020, 1, 1, 12, 0, 0)

    monkeypatch.setattr(task_manager, "datetime", DummyDateTimeModule)

    task_manager.createTask()
    with open(tmp_path / "tasks_list.json", "r") as f:
        after = json.load(f)

    # New behavior: task id should be max(existing)+1 (i.e., 3)
    ids = [t["id"] for t in after]
    assert 0 in ids and 2 in ids
    assert 3 in ids


def test_main_exit_immediately(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    # Provide input '8' to exit immediately
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: "8")
    task_manager.main()
    out = capsys.readouterr().out
    assert "Task Manager Menu" in out
    assert "Exiting Menu" in out


def test_main_create_and_exit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    called = {"create": False}
    def fake_create():
        called["create"] = True
    monkeypatch.setattr(task_manager, "createTask", fake_create)

    inputs = iter(["1", "8"])  # choose create, then exit
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    task_manager.main()
    assert called["create"] is True


def test_main_update_and_delete_flows(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    captured = {}

    def fake_update(id):
        captured["update_id"] = id

    def fake_delete(id):
        captured["delete_id"] = id

    monkeypatch.setattr(task_manager, "updateTask", fake_update)
    monkeypatch.setattr(task_manager, "deleteTask", fake_delete)

    # Sequence: update (2) with id 42, delete (3) with id 99, then exit (8)
    inputs = iter(["2", "42", "3", "99", "8"])
    monkeypatch.setattr("builtins.input", lambda *args, **kwargs: next(inputs))

    task_manager.main()
    assert captured.get("update_id") == 42
    assert captured.get("delete_id") == 99
