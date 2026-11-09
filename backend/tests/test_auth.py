def test_register_login_me(client):
    r = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "Secret123", "full_name": "A"})
    assert r.status_code == 201
    assert r.json()["email"] == "a@b.com"

    r2 = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "Secret123"})
    assert r2.status_code == 400

    r3 = client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert r3.status_code == 401

    r4 = client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "Secret123"})
    assert r4.status_code == 200
    token = r4.json()["access_token"]
    r5 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r5.status_code == 200
    assert r5.json()["email"] == "a@b.com"
