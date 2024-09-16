from setup_tests import client, setup_db
from datetime import datetime
from app.main import check_reminders  

def test_set_reminder(setup_db):
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
        "title": "Task without reminder",
        "description": "Task description",
        "completed": False,
        "deadline": "2024-09-15T13:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    
    task_id = task_response.json()["id"]
    
    response = client.put(f"/tasks/{task_id}/set_reminder", json={
        "reminder_time": "2024-09-15T12:00:00"
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["reminder_time"] == "2024-09-15T12:00:00"
    assert response.json()["reminder_sent"] is False


