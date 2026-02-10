from __future__ import annotations


def test_get_current_user(client_user) -> None:
    response = client_user.get("/v1/me")
    assert response.status_code == 200
    assert response.json()["email"] == "demo@example.com"


def test_register_user(client_backoffice) -> None:
    response = client_backoffice.post(
        "/v1/user/register",
        json={"email": "new@example.com", "cognito_id": "cognito-test-123"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["user"]["email"] == "new@example.com"
    assert payload["user"]["cognito_id"] == "cognito-test-123"


def test_accept_invitation(client_user) -> None:
    invite = client_user.post(
        "/v1/invitations",
        json={"customer_id": client_user.get("/v1/customer").json()["id"], "email": "invitee@example.com"},
    )
    assert invite.status_code == 201
    token = invite.json()["token"]
    response = client_user.post("/v1/invitations/accept", json={"token": token})
    assert response.status_code == 201
    assert response.json()["email"] == "invitee@example.com"


def test_update_customer(client_user) -> None:
    response = client_user.patch("/v1/customer", json={"name": "Updated Co"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Co"


def test_get_customer_by_id(client_backoffice) -> None:
    current = client_backoffice.get("/v1/customer")
    assert current.status_code == 200
    customer_id = current.json()["id"]
    response = client_backoffice.get(f"/v1/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == customer_id


def test_list_customers(client_backoffice) -> None:
    response = client_backoffice.get("/v1/customers")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1


def test_list_users(client_backoffice) -> None:
    response = client_backoffice.get("/v1/users")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1


def test_get_user_by_id(client_backoffice) -> None:
    current = client_backoffice.get("/v1/user")
    assert current.status_code == 200
    user_id = current.json()["id"]
    response = client_backoffice.get(f"/v1/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_patch_user_by_id(client_backoffice) -> None:
    current = client_backoffice.get("/v1/user")
    assert current.status_code == 200
    user_id = current.json()["id"]
    response = client_backoffice.patch(
        f"/v1/users/{user_id}",
        json={"email": "updated@example.com", "roles": ["admin"]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "updated@example.com"
    assert payload["roles"] == ["admin"]


def test_patch_customer_by_id(client_backoffice) -> None:
    current = client_backoffice.get("/v1/customer")
    assert current.status_code == 200
    customer_id = current.json()["id"]
    response = client_backoffice.patch(f"/v1/customers/{customer_id}", json={"name": "Backoffice Co"})
    assert response.status_code == 200
    assert response.json()["name"] == "Backoffice Co"


def test_credit_and_debit_tokens(client_backoffice) -> None:
    current = client_backoffice.get("/v1/customer")
    assert current.status_code == 200
    customer_id = current.json()["id"]
    credit = client_backoffice.post(f"/v1/customers/{customer_id}/tokens/credit", json={"amount": 10})
    assert credit.status_code == 200
    debit = client_backoffice.post(f"/v1/customers/{customer_id}/tokens/debit", json={"amount": 5})
    assert debit.status_code == 200


def test_debit_tokens_insufficient(client_backoffice) -> None:
    current = client_backoffice.get("/v1/customer")
    assert current.status_code == 200
    customer_id = current.json()["id"]
    response = client_backoffice.post(f"/v1/customers/{customer_id}/tokens/debit", json={"amount": 999999})
    assert response.status_code == 409


def test_get_customer_tokens_by_id(client_backoffice) -> None:
    current = client_backoffice.get("/v1/customer")
    assert current.status_code == 200
    customer_id = current.json()["id"]
    response = client_backoffice.get(f"/v1/customers/{customer_id}/tokens")
    assert response.status_code == 200
    assert "tokens" in response.json()


def test_user_cannot_list_customers(client_user) -> None:
    response = client_user.get("/v1/customers")
    assert response.status_code == 403
