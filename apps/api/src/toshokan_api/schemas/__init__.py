from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PostalAddress(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = Field(default=None, min_length=2, max_length=2)

    model_config = ConfigDict(extra="forbid")


class ContactData(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[PostalAddress] = None

    model_config = ConfigDict(extra="forbid")


class Customer(BaseModel):
    id: UUID
    stripe_customer_id: str
    tokens: int = Field(ge=0)
    name: Optional[str] = None
    contact: Optional[ContactData] = None
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[ContactData] = None

    model_config = ConfigDict(extra="forbid")


class User(BaseModel):
    id: UUID
    customer_ids: List[UUID]
    cognito_id: str
    email: str
    roles: Optional[List[str]] = None
    created_at: datetime
    archived_at: Optional[datetime] = None
