from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID

from ..domain.entities import Customer, Invitation, User


@dataclass(frozen=True)
class ProvisionedCustomerUser:
    customer: Customer
    user: User


class CustomerRepository(ABC):
    @abstractmethod
    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        raise NotImplementedError

    @abstractmethod
    def list_customers(self) -> Iterable[Customer]:
        raise NotImplementedError

    @abstractmethod
    def create_customer(self, customer: Customer) -> Customer:
        raise NotImplementedError

    @abstractmethod
    def update_customer(self, customer: Customer) -> Customer:
        raise NotImplementedError


class UserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def get_user_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def list_users(self) -> Iterable[User]:
        raise NotImplementedError

    @abstractmethod
    def list_by_customer(self, customer_id: UUID) -> Iterable[User]:
        raise NotImplementedError

    @abstractmethod
    def create_user(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def update_user(self, user: User) -> User:
        raise NotImplementedError


class InvitationRepository(ABC):
    @abstractmethod
    def create_invitation(self, invitation: Invitation) -> Invitation:
        raise NotImplementedError

    @abstractmethod
    def verify_token(self, token: str, now: datetime) -> Optional[Invitation]:
        raise NotImplementedError

    @abstractmethod
    def mark_accepted(self, invitation: Invitation, now: datetime) -> Invitation:
        raise NotImplementedError


class IdentityProvisioning(ABC):
    @abstractmethod
    def register_user(self, email: str, cognito_id: str) -> ProvisionedCustomerUser:
        raise NotImplementedError

    @abstractmethod
    def register_invited_user(self, invitation: Invitation) -> User:
        raise NotImplementedError
