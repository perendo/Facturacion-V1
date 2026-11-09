from decimal import Decimal


def _setup(client, headers):
    c = client.post("/api/v1/clients", json={"name": "Acme"}, headers=headers).json()
    p = client.post("/api/v1/products", json={"name": "Widget", "unit_price": "10.00", "tax_rate": "21.00"}, headers=headers).json()
    return c, p


def test_invoice_create_totals(client, auth_headers):
    c, p = _setup(client, auth_headers)
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


def test_invoice_status_transitions(client, auth_headers):
    c, p = _setup(client, auth_headers)
    payload = {"client_id": c["id"], "issue_date": "2026-01-10", "lines": [{"description": "X", "quantity": "1", "unit_price": "5.00", "tax_rate": "21.00"}]}
    inv = client.post("/api/v1/invoices", json=payload, headers=auth_headers).json()
    iid = inv["id"]

    # draft -> sent
    r = client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "sent"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "sent"

    # cannot edit when sent
    r2 = client.put(f"/api/v1/invoices/{iid}", json={"notes": "no"}, headers=auth_headers)
    assert r2.status_code == 400

    # sent -> paid
    r3 = client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "paid"}, headers=auth_headers)
    assert r3.status_code == 200

    # paid terminal
    r4 = client.patch(f"/api/v1/invoices/{iid}/status", json={"status": "cancelled"}, headers=auth_headers)
    assert r4.status_code == 400

    # delete non-draft forbidden
    r5 = client.delete(f"/api/v1/invoices/{iid}", headers=auth_headers)
    assert r5.status_code == 400


def test_invoice_delete_draft(client, auth_headers):
    payload = {"issue_date": "2026-01-10", "lines": [{"description": "X", "quantity": "1", "unit_price": "5.00", "tax_rate": "21.00"}]}
    inv = client.post("/api/v1/invoices", json=payload, headers=auth_headers).json()
    iid = inv["id"]
    r = client.delete(f"/api/v1/invoices/{iid}", headers=auth_headers)
    assert r.status_code == 204


def test_dashboard_summary(client, auth_headers):
    payload = {"issue_date": "2026-01-10", "lines": [{"description": "X", "quantity": "1", "unit_price": "10.00", "tax_rate": "0"}]}
    client.post("/api/v1/invoices", json=payload, headers=auth_headers)
    r = client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert r.status_code == 200
    d = r.json()
    assert d["count_by_status"]["draft"] == 1
    assert float(d["total_invoiced"]) == 10.0