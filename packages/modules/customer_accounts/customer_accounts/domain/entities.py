from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class PostalAddress:
    line1: Optional[str]
    line2: Optional[str]
    city: Optional[str]
    region: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]


@dataclass(frozen=True)
class ContactData:
    email: Optional[str]
    phone: Optional[str]
    address: Optional[PostalAddress]


@dataclass(frozen=True)
class Customer:
    id: UUID
    stripe_customer_id: str
    tokens: int
    name: Optional[str]
    contact: Optional[ContactData]
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]

    def update(self, name: Optional[str], contact: Optional[ContactData], now: datetime) -> "Customer":
        return replace(
            self,
            name=name if name is not None else self.name,
            contact=contact if contact is not None else self.contact,
            updated_at=now,
        )

    def archive(self, now: datetime) -> "Customer":
        return replace(self, archived_at=now, updated_at=now)


@dataclass(frozen=True)
class User:
    id: UUID
    customer_ids: list[UUID]
    cognito_id: str
    email: str
    roles: list[str]
    created_at: datetime
    archived_at: Optional[datetime]
    timezone: Optional[str] = None

    def archive(self, now: datetime) -> "User":
        return replace(self, archived_at=now)


@dataclass(frozen=True)
class Invitation:
    id: UUID
    customer_id: UUID
    email: str
    token: str
    created_at: datetime
    expires_at: datetime
    accepted_at: Optional[datetime]

    def accept(self, now: datetime) -> "Invitation":
        return replace(self, accepted_at=now)
