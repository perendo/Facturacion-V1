import pytest
from decimal import Decimal

from fastapi.testclient import TestClient


def test_integration_health(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_integration_cors_preflight(client):
    r = client.options(
        "/api/v1/clients",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "POST" in r.headers.get("access-control-allow-methods", "")


def test_integration_auth_flow(client):
    r = client.post("/api/v1/auth/register", json={
        "email": "e2e@example.com",
        "password": "password123",
        "full_name": "E2E User",
    })
    assert r.status_code == 201
    assert r.json()["email"] == "e2e@example.com"

    # duplicate
    r2 = client.post("/api/v1/auth/register", json={
        "email": "e2e@example.com",
        "password": "password123",
    })
    assert r2.status_code == 400

    # bad credentials
    r3 = client.post("/api/v1/auth/login", json={
        "email": "e2e@example.com",
        "password": "wrong",
    })
    assert r3.status_code == 401

    r4 = client.post("/api/v1/auth/login", json={
        "email": "e2e@example.com",
        "password": "password123",
    })
    assert r4.status_code == 200
    token = r4.json()["access_token"]
    assert r4.json()["token_type"] == "bearer"

    r5 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r5.status_code == 200
    assert r5.json()["email"] == "e2e@example.com"


def test_integration_clients_crud_and_errors(client, auth_headers):
    # unauthorized
    assert client.get("/api/v1/clients").status_code == 401

    # invalid body
    r = client.post("/api/v1/clients", json={"foo": "bar"}, headers=auth_headers)
    assert r.status_code == 422

    # create
    r = client.post("/api/v1/clients", json={"name": "Acme", "email": "acme@test.com"}, headers=auth_headers)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert r.json()["name"] == "Acme"

    # list
    r2 = client.get("/api/v1/clients", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()) == 1

    # get by id
    r3 = client.get(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert r3.status_code == 200
    assert r3.json()["name"] == "Acme"

    # not found
    assert client.get("/api/v1/clients/99999", headers=auth_headers).status_code == 404

    # update
    r4 = client.put(f"/api/v1/clients/{cid}", json={"name": "Acme2"}, headers=auth_headers)
    assert r4.status_code == 200
    assert r4.json()["name"] == "Acme2"

    # delete
    r5 = client.delete(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert r5.status_code == 204

    # get after delete
    r6 = client.get(f"/api/v1/clients/{cid}", headers=auth_headers)
    assert r6.status_code == 404


def test_integration_products(client, auth_headers):
    r = client.post("/api/v1/products", json={
        "name": "Widget",
        "unit_price": "10.50",
        "tax_rate": "21.00",
        "unit": "unidad",
    }, headers=auth_headers)
    assert r.status_code == 201
    pid = r.json()["id"]
    assert r.json()["name"] == "Widget"

    r2 = client.get("/api/v1/products", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()) == 1

    r3 = client.put(f"/api/v1/products/{pid}", json={"unit_price": "12.00"}, headers=auth_headers)
    assert r3.status_code == 200
    assert float(r3.json()["unit_price"]) == 12.0

    r4 = client.delete(f"/api/v1/products/{pid}", headers=auth_headers)
    assert r4.status_code == 204


def test_integration_invoice_full_flow(client, auth_headers):
    # setup
    c = client.post("/api/v1/clients", json={"name": "Acme"}, headers=auth_headers).json()
    p = client.post("/api/v1/products", json={"name": "Widget", "unit_price": "10.00", "tax_rate": "21.00"}, headers=auth_headers).json()

    # client not found
    bad = client.post("/api/v1/invoices", json={
        "client_id": 99999,
        "issue_date": "2026-01-10",
        "lines": [{"description": "X", "quantity": "1", "unit_price": "5.00", "tax_rate": "21.00"}],
    }, headers=auth_headers)
    assert bad.status_code in (400, 404)

    # create with global discount
    payload = {
        "client_id": c["id"],
        "issue_date": "2026-01-10",
        "global_discount": "0",
        "lines": [
            {"product_id": p["id"], "description": "Widget", "quantity": "2", "unit_price": "10.00", "discount": "0", "tax_rate": "21.00"},
            {"description": "Manual", "quantity": "1", "unit_price": "5.00", "discount": "10", "tax_rate": "10.00"},
        ],
    }
    r = client.post("/api/v1/invoices", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    inv = r.json()
    assert inv["status"] == "draft"
    assert inv["number"].startswith("INV-2026-")
    assert float(inv["subtotal"]) == 24.5
    assert float(inv["tax_total"]) == 4.65
    assert float(inv["total"]) == 29.15
    assert len(inv["lines"]) == 2
    assert isinstance(inv["subtotal"], (int, float))
    iid = inv["id"]

    # get detail
    r2 = client.get(f"/api/v1/invoices/{iid}", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()["lines"]) == 2

    # draft -> sent
    r3 = client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "sent"}, headers=auth_headers)
    assert r3.status_code == 200
    assert r3.json()["status"] == "sent"

    # cannot edit when sent
    r4 = client.put(f"/api/v1/invoices/{iid}", json={"notes": "no"}, headers=auth_headers)
    assert r4.status_code == 400

    # sent -> paid
    r5 = client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "paid"}, headers=auth_headers)
    assert r5.status_code == 200
    assert r5.json()["status"] == "paid"

    # cancel paid -> 400
    r6 = client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "cancelled"}, headers=auth_headers)
    assert r6.status_code == 400

    # delete paid -> 400
    r7 = client.delete(f"/api/v1/invoices/{iid}", headers=auth_headers)
    assert r7.status_code == 400


def test_integration_invoice_delete_draft(client, auth_headers):
    payload = {"issue_date": "2026-01-10", "lines": [{"description": "X", "quantity": "1", "unit_price": "5.00", "tax_rate": "21.00"}]}
    inv = client.post("/api/v1/invoices", json=payload, headers=auth_headers).json()
    iid = inv["id"]
    r = client.delete(f"/api/v1/invoices/{iid}", headers=auth_headers)
    assert r.status_code == 204


def test_integration_dashboard_and_filters(client, auth_headers):
    payload = {"issue_date": "2026-01-10", "lines": [{"description": "X", "quantity": "1", "unit_price": "10.00", "tax_rate": "0"}]}
    inv = client.post("/api/v1/invoices", json=payload, headers=auth_headers).json()
    iid = inv["id"]
    # mark paid
    client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "sent"}, headers=auth_headers)
    client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "paid"}, headers=auth_headers)

    r = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert r.status_code == 200
    d = r.json()
    assert d["count_by_status"]["paid"] == 1
    assert float(d["total_invoiced"]) == 10.0
    assert float(d["total_paid"]) == 10.0
    assert "total_pending" in d

    # filter paid
    rf = client.get("/api/v1/invoices", params={"status": "paid"}, headers=auth_headers)
    assert rf.status_code == 200
    assert any(x["id"] == iid for x in rf.json())


def test_integration_invoice_pdf(client, auth_headers):
    payload = {"issue_date": "2026-01-10", "lines": [{"description": "X", "quantity": "1", "unit_price": "5.00", "tax_rate": "21.00"}]}
    inv = client.post("/api/v1/invoices", json=payload, headers=auth_headers).json()
    iid = inv["id"]
    r = client.get(f"/api/v1/invoices/{iid}/pdf", headers=auth_headers)
    assert r.status_code == 200
    assert "application/pdf" in r.headers.get("content-type", "")
    assert r.content[:4] == b"%PDF"
