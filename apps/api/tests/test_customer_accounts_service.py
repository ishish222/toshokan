from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Optional
from uuid import UUID, uuid4

import pytest

from customer_accounts.app import CustomerUsersService
from customer_accounts.domain import ContactData, Customer, Invitation, PostalAddress, User
from customer_accounts.ports import (
    CustomerRepository,
    IdentityProvisioning,
    InvitationRepository,
    ProvisionedCustomerUser,
    UserRepository,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class InMemoryCustomerRepository(CustomerRepository):
    customers: Dict[UUID, Customer]

    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        return self.customers.get(customer_id)

    def list_customers(self) -> Iterable[Customer]:
        return list(self.customers.values())

    def create_customer(self, customer: Customer) -> Customer:
        self.customers[customer.id] = customer
        return customer

    def update_customer(self, customer: Customer) -> Customer:
        self.customers[customer.id] = customer
        return customer


@dataclass
class InMemoryUserRepository(UserRepository):
    users: Dict[UUID, User]

    def get_user(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self.users.values() if user.email == email), None)

    def get_user_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        return next((user for user in self.users.values() if user.cognito_id == cognito_id), None)

    def list_users(self) -> Iterable[User]:
        return list(self.users.values())

    def list_by_customer(self, customer_id: UUID) -> Iterable[User]:
        return [user for user in self.users.values() if customer_id in user.customer_ids]

    def create_user(self, user: User) -> User:
        self.users[user.id] = user
        return user

    def update_user(self, user: User) -> User:
        self.users[user.id] = user
        return user


@dataclass
class InMemoryInvitationRepository(InvitationRepository):
    invitations: Dict[str, Invitation]

    def create_invitation(self, invitation: Invitation) -> Invitation:
        self.invitations[invitation.token] = invitation
        return invitation

    def verify_token(self, token: str, now: datetime) -> Optional[Invitation]:
        invitation = self.invitations.get(token)
        if invitation is None or invitation.accepted_at is not None or invitation.expires_at <= now:
            return None
        return invitation

    def mark_accepted(self, invitation: Invitation, now: datetime) -> Invitation:
        updated = invitation.accept(now=now)
        self.invitations[invitation.token] = updated
        return updated


class FakeIdentity(IdentityProvisioning):
    def register_user(self, email: str, cognito_id: str) -> ProvisionedCustomerUser:
        now = _now()
        customer_id = uuid4()
        user_id = uuid4()
        customer = Customer(
            id=customer_id,
            stripe_customer_id=f"cus_{customer_id.hex[:12]}",
            tokens=0,
            name=None,
            contact=ContactData(email=email, phone=None, address=None),
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


def _seed_service() -> CustomerUsersService:
    now = _now()
    customer_id = uuid4()
    user_id = uuid4()
    customer = Customer(
        id=customer_id,
        stripe_customer_id=f"cus_{customer_id.hex[:12]}",
        tokens=100,
        name="Demo",
        contact=ContactData(
            email="demo@example.com",
            phone=None,
            address=PostalAddress(
                line1="123 Demo St",
                line2=None,
                city="Demo",
                region="CA",
                postal_code="12345",
                country="US",
            ),
        ),
        created_at=now,
        updated_at=now,
        archived_at=None,
    )
    user = User(
        id=user_id,
        customer_ids=[customer_id],
        cognito_id=f"cognito-{user_id.hex[:8]}",
        email="demo@example.com",
        roles=["owner"],
        created_at=now,
        archived_at=None,
    )
    invitation = Invitation(
        id=uuid4(),
        customer_id=customer_id,
        email="invitee@example.com",
        token="invite-token",
        created_at=now,
        expires_at=now + timedelta(days=7),
        accepted_at=None,
    )
    customers = InMemoryCustomerRepository({customer.id: customer})
    users = InMemoryUserRepository({user.id: user})
    invitations = InMemoryInvitationRepository({invitation.token: invitation})
    return CustomerUsersService(
        customers=customers,
        users=users,
        invitations=invitations,
        identity=FakeIdentity(),
        current_user_id=user_id,
    )


def test_register_user_persists_entities() -> None:
    service = _seed_service()
    provisioned = service.register_user(email="new@example.com", cognito_id="cognito-new-user")
    assert service.customers.get_customer(provisioned.customer.id) is not None
    assert service.users.get_user(provisioned.user.id) is not None
    assert provisioned.user.cognito_id == "cognito-new-user"


def test_delete_customer_requires_single_active_user() -> None:
    service = _seed_service()
    customer = service.get_current_customer()
    assert customer is not None
    extra_user = User(
        id=uuid4(),
        customer_ids=[customer.id],
        cognito_id="cognito-extra",
        email="extra@example.com",
        roles=["member"],
        created_at=_now(),
        archived_at=None,
    )
    service.users.create_user(extra_user)
    with pytest.raises(ValueError):
        service.delete_current_customer()


def test_invite_and_accept_user() -> None:
    service = _seed_service()
    customer = service.get_current_customer()
    assert customer is not None
    invitation = service.invite_user(customer_id=customer.id, email="invitee@example.com")
    invited = service.accept_invitation(token=invitation.token)
    assert invited is not None
    assert invited.email == "invitee@example.com"
    stored = service.users.get_user(invited.id)
    assert stored is not None


def test_accept_invitation_adds_customer_to_existing_user() -> None:
    service = _seed_service()
    customer = service.get_current_customer()
    assert customer is not None
    existing_user = service.get_current_user()
    assert existing_user is not None
    new_customer = Customer(
        id=uuid4(),
        stripe_customer_id="cus_new",
        tokens=0,
        name="Extra",
        contact=None,
        created_at=_now(),
        updated_at=_now(),
        archived_at=None,
    )
    service.customers.create_customer(new_customer)
    invitation = service.invite_user(customer_id=new_customer.id, email=existing_user.email)
    updated = service.accept_invitation(token=invitation.token)
    assert updated is not None
    assert new_customer.id in updated.customer_ids


def test_update_customer_changes_name() -> None:
    service = _seed_service()
    updated = service.update_customer(name="Updated", contact=None)
    assert updated is not None
    assert updated.name == "Updated"
