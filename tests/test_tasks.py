from setup_tests import client, setup_db

def test_create_task(setup_db):
    client.post("/users/", json={
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    })
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    response = client.post("/tasks/", json={
        "title": "New Task",
        "description": "Task description",
        "completed": False,
        "deadline": "2024-09-15T13:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Task"
    assert response.json()["description"] == "Task description"

def test_read_tasks(setup_db):
    client.post("/users/", json={
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    })
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    client.post("/tasks/", json={
        "title": "Task 1",
        "description": "Task description",
        "completed": False,
        "deadline": "2024-09-15T13:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/tasks/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Task 1"

def test_update_task(setup_db):
    client.post("/users/", json={
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    })
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    task_response = client.post("/tasks/", json={
        "title": "Task 1",
        "description": "Task description",
        "completed": False,
        "deadline": "2024-09-15T13:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    task_id = task_response.json()["id"]
    response = client.put(f"/tasks/{task_id}", json={
        "title": "Updated Task",
        "completed": True
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["completed"] is True

def test_delete_task(setup_db):
    client.post("/users/", json={
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    })
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    task_response = client.post("/tasks/", json={
        "title": "Task 1",
        "description": "Task description",
        "completed": False,
        "deadline": "2024-09-15T13:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    task_id = task_response.json()["id"]
    response = client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == task_id
