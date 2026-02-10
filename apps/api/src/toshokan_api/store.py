from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from .schemas import Customer, CustomerUpdate, User


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class InMemoryStore:
    user: User
    customer: Customer

    def update_customer(self, update: CustomerUpdate) -> Customer:
        if update.name is not None:
            self.customer.name = update.name
        if update.contact is not None:
            self.customer.contact = update.contact
        self.customer.updated_at = _now()
        return self.customer

    def archive_customer(self) -> Customer:
        now = _now()
        self.customer.archived_at = now
        self.customer.updated_at = now
        return self.customer


def _seed_ids() -> tuple[UUID, UUID]:
    customer_id = uuid4()
    user_id = uuid4()
    return customer_id, user_id


def create_store() -> InMemoryStore:
    customer_id, user_id = _seed_ids()
    now = _now()
    customer = Customer(
        id=customer_id,
        stripe_customer_id=f"cus_{customer_id.hex[:12]}",
        tokens=1500,
        name="Navigator Demo",
        contact=None,
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
    return InMemoryStore(user=user, customer=customer)


STORE = create_store()
