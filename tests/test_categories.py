from setup_tests import client, setup_db

def test_create_category(setup_db):
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
    response = client.post("/categories/", json={
        "name": "Work"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Work"

def test_read_categories(setup_db):
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
    client.post("/categories/", json={
        "name": "Work"
    }, headers={"Authorization": f"Bearer {token}"})
    response = client.get("/categories/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Work"

def test_delete_category(setup_db):
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
    category_response = client.post("/categories/", json={
        "name": "Work"
    }, headers={"Authorization": f"Bearer {token}"})
    category_id = category_response.json()["id"]
    response = client.delete(f"/categories/{category_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == category_id
