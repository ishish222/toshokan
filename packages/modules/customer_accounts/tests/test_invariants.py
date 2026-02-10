from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional
from uuid import UUID, uuid4

import pytest

from customer_accounts.app.service import CustomerUsersService
from customer_accounts.domain.entities import ContactData, Customer, Invitation, PostalAddress, User
from customer_accounts.ports.accounts import (
    CustomerRepository,
    IdentityProvisioning,
    InvitationRepository,
    ProvisionedCustomerUser,
    UserRepository,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class _Customers(CustomerRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Customer] = {}

    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        return self.items.get(customer_id)

    def list_customers(self) -> Iterable[Customer]:
        return list(self.items.values())

    def create_customer(self, customer: Customer) -> Customer:
        self.items[customer.id] = customer
        return customer

    def update_customer(self, customer: Customer) -> Customer:
        self.items[customer.id] = customer
        return customer


class _Users(UserRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, User] = {}

    def get_user(self, user_id: UUID) -> Optional[User]:
        return self.items.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self.items.values() if user.email == email), None)

    def get_user_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        return next((user for user in self.items.values() if user.cognito_id == cognito_id), None)

    def list_users(self) -> Iterable[User]:
        return list(self.items.values())

    def list_by_customer(self, customer_id: UUID) -> Iterable[User]:
        return [user for user in self.items.values() if customer_id in user.customer_ids]

    def create_user(self, user: User) -> User:
        self.items[user.id] = user
        return user

    def update_user(self, user: User) -> User:
        self.items[user.id] = user
        return user


class _Invitations(InvitationRepository):
    def __init__(self) -> None:
        self.items: dict[str, Invitation] = {}

    def create_invitation(self, invitation: Invitation) -> Invitation:
        self.items[invitation.token] = invitation
        return invitation

    def verify_token(self, token: str, now: datetime) -> Optional[Invitation]:
        invitation = self.items.get(token)
        if invitation is None:
            return None
        if invitation.expires_at <= now:
            return None
        return invitation

    def mark_accepted(self, invitation: Invitation, now: datetime) -> Invitation:
        updated = invitation.accept(now)
        self.items[invitation.token] = updated
        return updated


class _Identity(IdentityProvisioning):
    def register_user(self, email: str, cognito_id: str) -> ProvisionedCustomerUser:
        now = _now()
        customer_id = uuid4()
        user_id = uuid4()
        customer = Customer(
            id=customer_id,
            stripe_customer_id=f"cus_{customer_id.hex[:12]}",
            tokens=0,
            name="Created",
            contact=None,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )
        user = User(
            id=user_id,
            customer_ids=[customer_id],
            cognito_id=cognito_id,
            email=email,
            roles=["owner"],
            created_at=now,
            archived_at=None,
        )
        return ProvisionedCustomerUser(customer=customer, user=user)

    def register_invited_user(self, invitation: Invitation) -> User:
        now = _now()
        user_id = uuid4()
        return User(
            id=user_id,
            customer_ids=[invitation.customer_id],
            cognito_id=f"cognito-{user_id.hex[:8]}",
            email=invitation.email,
            roles=["member"],
            created_at=now,
            archived_at=None,
        )


def _service(current_user_id: UUID) -> CustomerUsersService:
    return CustomerUsersService(
        customers=_Customers(),
        users=_Users(),
        invitations=_Invitations(),
        identity=_Identity(),
        current_user_id=current_user_id,
    )


def test_customer_update_refreshes_timestamp() -> None:
    now = _now()
    customer = Customer(
        id=uuid4(),
        stripe_customer_id="cus_123",
        tokens=10,
        name="Old",
        contact=None,
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    later = now + timedelta(hours=1)
    updated = customer.update(name=None, contact=None, now=later)
    assert updated.name == "Old"
    assert updated.updated_at == later


def test_customer_archive_sets_archived_and_updated() -> None:
    now = _now()
    customer = Customer(
        id=uuid4(),
        stripe_customer_id="cus_123",
        tokens=10,
        name="Old",
        contact=None,
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    later = now + timedelta(hours=1)
    archived = customer.archive(now=later)
    assert archived.archived_at == later
    assert archived.updated_at == later


def test_user_archive_sets_archived_at() -> None:
    now = _now()
    user = User(
        id=uuid4(),
        customer_ids=[uuid4()],
        cognito_id="cognito-x",
        email="user@example.com",
        roles=["owner"],
        created_at=now,
        archived_at=None,
    )
    later = now + timedelta(minutes=10)
    archived = user.archive(now=later)
    assert archived.archived_at == later


def test_invitation_accept_sets_accepted_at() -> None:
    now = _now()
    invitation = Invitation(
        id=uuid4(),
        customer_id=uuid4(),
        email="invitee@example.com",
        token="invite-123",
        created_at=now,
        expires_at=now + timedelta(days=7),
        accepted_at=None,
    )
    later = now + timedelta(minutes=5)
    accepted = invitation.accept(now=later)
    assert accepted.accepted_at == later


def test_register_user_creates_customer_and_user() -> None:
    current_user_id = uuid4()
    service = _service(current_user_id)
    provisioned = service.register_user("new@example.com", cognito_id="cognito-new-user")
    assert service.customers.get_customer(provisioned.customer.id) is not None
    assert service.users.get_user(provisioned.user.id) is not None


def test_debit_tokens_insufficient_raises() -> None:
    current_user_id = uuid4()
    service = _service(current_user_id)
    now = _now()
    customer = Customer(
        id=uuid4(),
        stripe_customer_id="cus_123",
        tokens=3,
        name="Low",
        contact=None,
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    service.customers.create_customer(customer)
    with pytest.raises(ValueError, match="Insufficient tokens"):
        service.debit_customer_tokens(customer.id, amount=10)


def test_delete_current_customer_rejects_multiple_active_users() -> None:
    now = _now()
    customer_id = uuid4()
    user_id = uuid4()
    service = _service(user_id)
    service.customers.create_customer(
        Customer(
            id=customer_id,
            stripe_customer_id="cus_123",
            tokens=0,
            name="Customer",
            contact=None,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )
    )
    user = User(
        id=user_id,
        customer_ids=[customer_id],
        cognito_id="cognito-1",
        email="owner@example.com",
        roles=["owner"],
        created_at=now,
        archived_at=None,
    )
    other_user = replace(
        user,
        id=uuid4(),
        email="other@example.com",
    )
    service.users.create_user(user)
    service.users.create_user(other_user)
    with pytest.raises(ValueError, match="Customer still has active users"):
        service.delete_current_customer()


def test_accept_invitation_existing_user_adds_customer() -> None:
    now = _now()
    customer_id = uuid4()
    user_id = uuid4()
    service = _service(user_id)
    user = User(
        id=user_id,
        customer_ids=[],
        cognito_id="cognito-1",
        email="invitee@example.com",
        roles=["member"],
        created_at=now,
        archived_at=None,
    )
    service.users.create_user(user)
    invitation = Invitation(
        id=uuid4(),
        customer_id=customer_id,
        email="invitee@example.com",
        token="invite-xyz",
        created_at=now,
        expires_at=now + timedelta(days=7),
        accepted_at=None,
    )
    service.invitations.create_invitation(invitation)
    accepted = service.accept_invitation(token="invite-xyz")
    assert accepted is not None
    assert customer_id in accepted.customer_ids


def test_update_customer_by_id_missing_returns_none() -> None:
    service = _service(uuid4())
    update = service.update_customer_by_id(customer_id=uuid4(), name="Missing", contact=None)
    assert update is None


def test_customer_update_preserves_contact_when_none() -> None:
    now = _now()
    contact = ContactData(
        email="contact@example.com",
        phone=None,
        address=PostalAddress(
            line1="1 Main",
            line2=None,
            city="Town",
            region="CA",
            postal_code="12345",
            country="US",
        ),
    )
    customer = Customer(
        id=uuid4(),
        stripe_customer_id="cus_123",
        tokens=10,
        name="Name",
        contact=contact,
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    updated = customer.update(name="New", contact=None, now=now + timedelta(minutes=5))
    assert updated.contact == contact
