from setup_tests import client, setup_db

def test_create_user(setup_db):
    response = client.post("/users/", json={
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "test@example.com"

def test_login_for_access_token(setup_db):
    client.post("/users/", json={
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password"
    })
    response = client.post("/token", data={
        "username": "test@example.com",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_read_users_me(setup_db):
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
    response = client.get("/users/me/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "test_user"
    assert response.json()["email"] == "test@example.com"
