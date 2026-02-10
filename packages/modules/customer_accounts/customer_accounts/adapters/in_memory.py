from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from typing import Dict, Iterable, Optional
from uuid import UUID, uuid4

from ..config import CustomerAccountsConfig
from ..domain.entities import ContactData, Customer, Invitation, PostalAddress, User
from ..ports.accounts import (
    CustomerRepository,
    IdentityProvisioning,
    InvitationRepository,
    ProvisionedCustomerUser,
    UserRepository,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class InMemoryCustomerAccountsStore:
    customers: Dict[UUID, Customer]
    users: Dict[UUID, User]
    invitations: Dict[str, Invitation]
    current_user_id: UUID


def _load_seed_data(seed_file_path: str, config: CustomerAccountsConfig) -> InMemoryCustomerAccountsStore:
    """Load seed data from a JSON file."""
    with open(seed_file_path, 'r') as f:
        data = json.load(f)

    now = _now()
    customers: Dict[UUID, Customer] = {}
    users: Dict[UUID, User] = {}
    invitations: Dict[str, Invitation] = {}

    for c in data.get("customers", []):
        customer_id = UUID(c["id"])
        contact = None
        if c.get("contact"):
            address = None
            if c["contact"].get("address"):
                addr = c["contact"]["address"]
                address = PostalAddress(
                    line1=addr.get("line1"),
                    line2=addr.get("line2"),
                    city=addr.get("city"),
                    region=addr.get("region"),
                    postal_code=addr.get("postal_code"),
                    country=addr.get("country"),
                )
            contact = ContactData(
                email=c["contact"].get("email"),
                phone=c["contact"].get("phone"),
                address=address,
            )
        customers[customer_id] = Customer(
            id=customer_id,
            stripe_customer_id=c["stripe_customer_id"],
            tokens=c.get("tokens", 0),
            name=c.get("name"),
            contact=contact,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    first_user_id: Optional[UUID] = None
    for u in data.get("users", []):
        user_id = UUID(u["id"])
        if first_user_id is None:
            first_user_id = user_id
        users[user_id] = User(
            id=user_id,
            customer_ids=[UUID(cid) for cid in u["customer_ids"]],
            cognito_id=u["cognito_id"],
            email=u["email"],
            roles=u.get("roles", []),
            created_at=now,
            archived_at=None,
            timezone=u.get("timezone"),
        )

    for inv in data.get("invitations", []):
        invitation_ttl_days = config.invitation_ttl_days if config else 7
        invitation = Invitation(
            id=UUID(inv["id"]),
            customer_id=UUID(inv["customer_id"]),
            email=inv["email"],
            token=inv["token"],
            created_at=now,
            expires_at=now + timedelta(days=invitation_ttl_days),
            accepted_at=None,
        )
        invitations[invitation.token] = invitation

    if first_user_id is None:
        first_user_id = uuid4()  # Fallback

    return InMemoryCustomerAccountsStore(
        customers=customers,
        users=users,
        invitations=invitations,
        current_user_id=first_user_id,
    )


def create_store(config: CustomerAccountsConfig) -> InMemoryCustomerAccountsStore:
    seed_file = os.getenv("SEED_DATA_PATH")
    if seed_file and os.path.exists(seed_file):
        return _load_seed_data(seed_file, config)

    if not config.demo_data_enabled:
        return InMemoryCustomerAccountsStore(
            customers={},
            users={},
            invitations={},
            current_user_id=uuid4(),
        )

    # Default fallback: create demo data
    now = _now()
    customer_id = uuid4()
    user_id = uuid4()
    customer = Customer(
        id=customer_id,
        stripe_customer_id=f"cus_{customer_id.hex[:12]}",
        tokens=1500,
        name="Navigator Demo",
        contact=ContactData(
            email="demo@example.com",
            phone=None,
            address=PostalAddress(
                line1="123 Demo St",
                line2=None,
                city="Navigator City",
                region="CA",
                postal_code="94110",
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
        timezone="Asia/Tokyo",
    )
    invitation = Invitation(
        id=uuid4(),
        customer_id=customer_id,
        email="invitee@example.com",
        token="invite-token-123",
        created_at=now,
        expires_at=now + timedelta(days=config.invitation_ttl_days),
        accepted_at=None,
    )
    return InMemoryCustomerAccountsStore(
        customers={customer.id: customer},
        users={user.id: user},
        invitations={invitation.token: invitation},
        current_user_id=user.id,
    )


class InMemoryCustomerRepository(CustomerRepository):
    def __init__(self, store: InMemoryCustomerAccountsStore) -> None:
        self._store = store

    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        return self._store.customers.get(customer_id)

    def list_customers(self) -> Iterable[Customer]:
        return list(self._store.customers.values())

    def create_customer(self, customer: Customer) -> Customer:
        self._store.customers[customer.id] = customer
        return customer

    def update_customer(self, customer: Customer) -> Customer:
        self._store.customers[customer.id] = customer
        return customer


class InMemoryUserRepository(UserRepository):
    def __init__(self, store: InMemoryCustomerAccountsStore) -> None:
        self._store = store

    def get_user(self, user_id: UUID) -> Optional[User]:
        return self._store.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self._store.users.values() if user.email == email), None)

    def get_user_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        return next((user for user in self._store.users.values() if user.cognito_id == cognito_id), None)

    def list_users(self) -> Iterable[User]:
        return list(self._store.users.values())

    def list_by_customer(self, customer_id: UUID) -> Iterable[User]:
        return [user for user in self._store.users.values() if customer_id in user.customer_ids]

    def create_user(self, user: User) -> User:
        self._store.users[user.id] = user
        return user

    def update_user(self, user: User) -> User:
        self._store.users[user.id] = user
        return user


class InMemoryInvitationRepository(InvitationRepository):
    def __init__(self, store: InMemoryCustomerAccountsStore) -> None:
        self._store = store

    def create_invitation(self, invitation: Invitation) -> Invitation:
        self._store.invitations[invitation.token] = invitation
        return invitation

    def verify_token(self, token: str, now: datetime) -> Optional[Invitation]:
        invitation = self._store.invitations.get(token)
        if invitation is None:
            return None
        if invitation.accepted_at is not None:
            return None
        if invitation.expires_at <= now:
            return None
        return invitation

    def mark_accepted(self, invitation: Invitation, now: datetime) -> Invitation:
        updated = invitation.accept(now=now)
        self._store.invitations[invitation.token] = updated
        return updated


class FakeIdentityProvisioning(IdentityProvisioning):
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
            timezone=None,
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
            timezone=None,
        )
