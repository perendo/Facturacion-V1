def test_products_crud(client, auth_headers):
    r = client.post("/api/v1/products", json={"name": "Widget", "unit_price": "10.50", "tax_rate": "21.00", "unit": "unidad"}, headers=auth_headers)
    assert r.status_code == 201
    pid = r.json()["id"]

    r2 = client.get("/api/v1/products", headers=auth_headers)
    assert len(r2.json()) == 1

    r3 = client.put(f"/api/v1/products/{pid}", json={"unit_price": "12.00"}, headers=auth_headers)
    assert r3.status_code == 200
    assert float(r3.json()["unit_price"]) == 12.0

    r4 = client.delete(f"/api/v1/products/{pid}", headers=auth_headers)
    assert r4.status_code == 204