from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from ..config import get_config
from ..domain.entities import ContactData, Customer, Invitation, User
from ..ports import (
    CustomerRepository,
    IdentityProvisioning,
    InvitationRepository,
    ProvisionedCustomerUser,
    UserRepository,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CustomerUsersService:
    customers: CustomerRepository
    users: UserRepository
    invitations: InvitationRepository
    identity: IdentityProvisioning
    current_user_id: UUID

    def get_current_user(self, current_user_id: Optional[UUID] = None) -> Optional[User]:
        user_id = current_user_id or self.current_user_id
        return self.users.get_user(user_id)

    def get_current_customer(self, current_user_id: Optional[UUID] = None) -> Optional[Customer]:
        current = self.get_current_user(current_user_id=current_user_id)
        if current is None:
            return None
        if not current.customer_ids:
            return None
        return self.customers.get_customer(current.customer_ids[0])

    def get_customer_by_id(self, customer_id: UUID) -> Optional[Customer]:
        return self.customers.get_customer(customer_id)

    def list_customers(self) -> list[Customer]:
        return list(self.customers.list_customers())

    def list_users(self) -> list[User]:
        return list(self.users.list_users())

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self.users.get_user(user_id)

    def update_user_by_id(
        self,
        user_id: UUID,
        email: Optional[str],
        timezone: Optional[str] = None,
        roles: Optional[list[str]] = None,
    ) -> Optional[User]:
        user = self.users.get_user(user_id)
        if user is None:
            return None
        updated = replace(
            user,
            email=email if email is not None else user.email,
            timezone=timezone if timezone is not None else user.timezone,
            roles=roles if roles is not None else user.roles,
        )
        return self.users.update_user(updated)

    def update_customer_by_id(
        self,
        customer_id: UUID,
        name: Optional[str],
        contact: Optional[ContactData],
    ) -> Optional[Customer]:
        customer = self.customers.get_customer(customer_id)
        if customer is None:
            return None
        updated = customer.update(name=name, contact=contact, now=_now())
        return self.customers.update_customer(updated)

    def credit_customer_tokens(self, customer_id: UUID, amount: int) -> Optional[Customer]:
        customer = self.customers.get_customer(customer_id)
        if customer is None:
            return None
        updated = replace(customer, tokens=customer.tokens + amount, updated_at=_now())
        return self.customers.update_customer(updated)

    def debit_customer_tokens(self, customer_id: UUID, amount: int) -> Optional[Customer]:
        customer = self.customers.get_customer(customer_id)
        if customer is None:
            return None
        if customer.tokens < amount:
            raise ValueError("Insufficient tokens")
        updated = replace(customer, tokens=customer.tokens - amount, updated_at=_now())
        return self.customers.update_customer(updated)

    def register_user(self, email: str, cognito_id: str) -> ProvisionedCustomerUser:
        provisioned = self.identity.register_user(email=email, cognito_id=cognito_id)
        self.customers.create_customer(provisioned.customer)
        self.users.create_user(provisioned.user)
        return provisioned

    def delete_current_user(self, current_user_id: Optional[UUID] = None) -> Optional[User]:
        current = self.get_current_user(current_user_id=current_user_id)
        if current is None:
            return None
        updated = current.archive(now=_now())
        return self.users.update_user(updated)

    def delete_current_customer(self, current_user_id: Optional[UUID] = None) -> Optional[Customer]:
        customer = self.get_current_customer(current_user_id=current_user_id)
        if customer is None:
            return None
        active_users = [
            user for user in self.users.list_by_customer(customer.id) if user.archived_at is None
        ]
        if len(active_users) > 1:
            raise ValueError("Customer still has active users")
        updated = customer.archive(now=_now())
        return self.customers.update_customer(updated)

    def invite_user(self, customer_id: UUID, email: str) -> Invitation:
        config = get_config()
        invitation = Invitation(
            id=uuid4(),
            customer_id=customer_id,
            email=email,
            token=f"invite-{uuid4().hex[:12]}",
            created_at=_now(),
            expires_at=_now() + timedelta(days=config.invitation_ttl_days),
            accepted_at=None,
        )
        return self.invitations.create_invitation(invitation)

    def accept_invitation(self, token: str) -> Optional[User]:
        invitation = self.invitations.verify_token(token=token, now=_now())
        if invitation is None:
            return None
        existing = self.users.get_user_by_email(invitation.email)
        if existing is not None:
            if invitation.customer_id in existing.customer_ids:
                return existing
            updated = replace(existing, customer_ids=[*existing.customer_ids, invitation.customer_id])
            self.users.update_user(updated)
            self.invitations.mark_accepted(invitation, now=_now())
            return updated
        user = self.identity.register_invited_user(invitation)
        self.users.create_user(user)
        self.invitations.mark_accepted(invitation, now=_now())
        return user

    def update_customer(
        self,
        name: Optional[str],
        contact: Optional[ContactData],
        current_user_id: Optional[UUID] = None,
    ) -> Optional[Customer]:
        customer = self.get_current_customer(current_user_id=current_user_id)
        if customer is None:
            return None
        updated = customer.update(name=name, contact=contact, now=_now())
        return self.customers.update_customer(updated)
