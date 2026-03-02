def test_register_user(client):
    response = client.post("/users", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_username(client):
    client.post("/users", json={"username": "alice", "password": "secret123"})
    response = client.post("/users", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_valid_credentials(client):
    client.post("/users", json={"username": "alice", "password": "secret123"})
    response = client.post("/users/login", json={"username": "alice", "password": "secret123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/users", json={"username": "alice", "password": "secret123"})
    response = client.post("/users/login", json={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/users/login", json={"username": "ghost", "password": "x"})
    assert response.status_code == 401


def test_delete_user_requires_auth(client):
    response = client.delete("/users/1")
    assert response.status_code == 401


def test_secure_route_with_token(client):
    client.post("/users", json={"username": "alice", "password": "secret123"})
    login = client.post("/users/login", json={"username": "alice", "password": "secret123"})
    token = login.json()["access_token"]
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "alice" in response.json()["message"]


def test_secure_route_without_token(client):
    response = client.get("/secure")
    assert response.status_code == 401


def test_delete_other_user_forbidden(client):
    client.post("/users", json={"username": "alice", "password": "secret123"})
    client.post("/users", json={"username": "bob", "password": "password1"})
    login = client.post("/users/login", json={"username": "alice", "password": "secret123"})
    token = login.json()["access_token"]
    # alice (id=1) tries to delete bob (id=2)
    response = client.delete("/users/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
