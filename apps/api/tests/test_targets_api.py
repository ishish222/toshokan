from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from navigator_api.auth import AuthContext, get_auth_context


def _client_for(app, auth: AuthContext) -> TestClient:
    app.dependency_overrides[get_auth_context] = lambda: auth
    return TestClient(app)


def test_backoffice_targets_crud(client_backoffice) -> None:
    customer = client_backoffice.get("/v1/customer")
    assert customer.status_code == 200
    customer_id = customer.json()["id"]

    create = client_backoffice.post(
        f"/v1/customers/{customer_id}/targets",
        json={"name": "Example Target", "seed_uris": ["https://example.com"]},
    )
    assert create.status_code == 201
    target = create.json()
    target_id = target["id"]
    assert target["customer_account_id"] == customer_id

    listing = client_backoffice.get(f"/v1/customers/{customer_id}/targets")
    assert listing.status_code == 200
    payload = listing.json()
    assert any(item["id"] == target_id for item in payload["items"])

    get_target = client_backoffice.get(f"/v1/customers/{customer_id}/targets/{target_id}")
    assert get_target.status_code == 200
    assert get_target.json()["id"] == target_id

    patch = client_backoffice.patch(
        f"/v1/customers/{customer_id}/targets/{target_id}",
        json={"name": "Updated Target", "seed_uris": ["https://example.org"]},
    )
    assert patch.status_code == 200
    assert patch.json()["seed_uris"] == ["https://example.org"]


def test_user_cannot_access_other_customer_targets(app_base) -> None:
    store = app_base.state.customer_accounts_store
    customer_id = next(iter(store.customers.keys()))
    backoffice_auth = AuthContext(
        user_id=store.current_user_id,
        groups=["backoffice"],
        customer_ids=[customer_id],
    )
    backoffice_client = _client_for(app_base, backoffice_auth)
    create = backoffice_client.post(
        f"/v1/customers/{customer_id}/targets",
        json={"name": "Example Target", "seed_uris": ["https://example.com"]},
    )
    assert create.status_code == 201
    target_id = create.json()["id"]

    user_auth = AuthContext(
        user_id=store.current_user_id,
        groups=["user"],
        customer_ids=[uuid4()],
    )
    user_client = _client_for(app_base, user_auth)
    response = user_client.get(f"/v1/customers/{customer_id}/targets/{target_id}")
    assert response.status_code == 403
