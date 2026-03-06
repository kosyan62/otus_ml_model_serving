import logging


def _register(client, username="alice", password="secret123", email="alice@example.com"):
    return client.post("/auth/register", json={"username": username, "email": email, "password": password})


def _login(client, username="alice", password="secret123"):
    return client.post("/auth/login", json={"username": username, "password": password})


def _token(client, username="alice", password="secret123"):
    _register(client, username, password)
    return _login(client, username, password).json()["access_token"]


# register

def test_register_user(client):
    response = _register(client)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_username(client):
    _register(client)
    response = _register(client)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_duplicate_email(client):
    _register(client)
    response = _register(client, username="bob")  # same email, different username
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


# login

def test_login_valid_credentials(client):
    _register(client)
    response = _login(client)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    _register(client)
    response = client.post("/auth/login", json={"username": "alice", "password": "wrongpass"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/auth/login", json={"username": "ghost", "password": "password1"})
    assert response.status_code == 401


# /me

def test_me_returns_profile(client):
    token = _token(client)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"


def test_me_without_token(client):
    response = client.get("/me")
    assert response.status_code == 401


# /predict

def test_predict_with_token(client):
    token = _token(client)
    response = client.post(
        "/predict",
        json={"Pregnancies": 2, "Glucose": 140, "BMI": 35.5, "Age": 32},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["prediction"] in (0, 1)


def test_predict_without_token(client):
    response = client.post("/predict", json={"Pregnancies": 2, "Glucose": 140, "BMI": 35.5, "Age": 32})
    assert response.status_code == 401


def test_predict_invalid_input(client):
    token = _token(client)
    response = client.post(
        "/predict",
        json={"Pregnancies": -1, "Glucose": 140, "BMI": 35.5, "Age": 32},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


# /admin

def test_admin_metrics_requires_admin(client):
    token = _token(client)  # user role
    response = client.get("/admin/metrics", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_delete_requires_auth(client):
    response = client.delete("/admin/users/1")
    assert response.status_code == 401


def test_admin_delete_requires_admin_role(client):
    token = _token(client)  # user role
    response = client.delete("/admin/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# /secure

def test_secure_route_with_token(client):
    token = _token(client)
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "alice" in response.json()["message"]


def test_secure_route_without_token(client):
    response = client.get("/secure")
    assert response.status_code == 401


def test_login_returns_expires_in(client):
    _register(client)
    response = _login(client)
    assert response.status_code == 200
    data = response.json()
    assert "expires_in" in data
    assert isinstance(data["expires_in"], int)
    assert data["expires_in"] > 0


def test_predict_returns_valid_class(client):
    token = _token(client)
    response = client.post(
        "/predict",
        json={"Pregnancies": 2, "Glucose": 140, "BMI": 35.5, "Age": 32},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in (0, 1)


def test_access_denial_is_logged(client, caplog):
    token = _token(client)  # user role
    with caplog.at_level(logging.WARNING, logger="app.auth"):
        client.get("/admin/metrics", headers={"Authorization": f"Bearer {token}"})
    assert any("Access denied" in r.message for r in caplog.records)
