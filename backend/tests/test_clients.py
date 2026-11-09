def test_clients_crud(client, auth_headers):
    # unauthorized
    client.cookies.clear()
    assert client.get("/api/v1/clients").status_code == 401

    r = client.post("/api/v1/clients", json={"name": "Acme", "email": "acme@test.com"}, headers=auth_headers)
    assert r.status_code == 201
    cid = r.json()["id"]

    r2 = client.get("/api/v1/clients", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()) == 1

    r3 = client.get(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert r3.status_code == 200
    assert r3.json()["name"] == "Acme"

    r4 = client.put(f"/api/v1/clients/{cid}", json={"name": "Acme2"}, headers=auth_headers)
    assert r4.status_code == 200
    assert r4.json()["name"] == "Acme2"

    r5 = client.delete(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert r5.status_code == 204

    r6 = client.get(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert r6.status_code == 404