from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Iterable, Optional
from uuid import UUID

from toshokan_platform.storage.helpers import dt_to_str, str_to_dt, list_to_json, list_from_json

from ..domain.entities import ContactData, Customer, Invitation, PostalAddress, User
from ..ports.accounts import CustomerRepository, InvitationRepository, UserRepository


def _contact_to_json(contact: Optional[ContactData]) -> Optional[str]:
    if contact is None:
        return None
    payload = {
        "email": contact.email,
        "phone": contact.phone,
        "address": None,
    }
    if contact.address is not None:
        payload["address"] = {
            "line1": contact.address.line1,
            "line2": contact.address.line2,
            "city": contact.address.city,
            "region": contact.address.region,
            "postal_code": contact.address.postal_code,
            "country": contact.address.country,
        }
    return json.dumps(payload)


def _contact_from_json(value: Optional[str]) -> Optional[ContactData]:
    if not value:
        return None
    payload = json.loads(value)
    address_payload = payload.get("address")
    address = None
    if address_payload is not None:
        address = PostalAddress(
            line1=address_payload.get("line1"),
            line2=address_payload.get("line2"),
            city=address_payload.get("city"),
            region=address_payload.get("region"),
            postal_code=address_payload.get("postal_code"),
            country=address_payload.get("country"),
        )
    return ContactData(
        email=payload.get("email"),
        phone=payload.get("phone"),
        address=address,
    )


class SqliteCustomerRepository(CustomerRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_customer(self, customer_id: UUID) -> Optional[Customer]:
        row = self._connection.execute(
            "SELECT * FROM customers WHERE id = ?",
            (str(customer_id),),
        ).fetchone()
        return _row_to_customer(row) if row else None

    def list_customers(self) -> Iterable[Customer]:
        rows = self._connection.execute(
            "SELECT * FROM customers ORDER BY created_at ASC"
        ).fetchall()
        return [_row_to_customer(row) for row in rows]

    def create_customer(self, customer: Customer) -> Customer:
        self._connection.execute(
            """
            INSERT INTO customers (
                id,
                stripe_customer_id,
                tokens,
                name,
                contact_json,
                created_at,
                updated_at,
                archived_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(customer.id),
                customer.stripe_customer_id,
                customer.tokens,
                customer.name,
                _contact_to_json(customer.contact),
                dt_to_str(customer.created_at),
                dt_to_str(customer.updated_at),
                dt_to_str(customer.archived_at),
            ),
        )
        self._connection.commit()
        return customer

    def update_customer(self, customer: Customer) -> Customer:
        self._connection.execute(
            """
            UPDATE customers
            SET stripe_customer_id = ?,
                tokens = ?,
                name = ?,
                contact_json = ?,
                created_at = ?,
                updated_at = ?,
                archived_at = ?
            WHERE id = ?
            """,
            (
                customer.stripe_customer_id,
                customer.tokens,
                customer.name,
                _contact_to_json(customer.contact),
                dt_to_str(customer.created_at),
                dt_to_str(customer.updated_at),
                dt_to_str(customer.archived_at),
                str(customer.id),
            ),
        )
        self._connection.commit()
        return customer


class SqliteUserRepository(UserRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_user(self, user_id: UUID) -> Optional[User]:
        row = self._connection.execute(
            "SELECT * FROM users WHERE id = ?",
            (str(user_id),),
        ).fetchone()
        return _row_to_user(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        row = self._connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return _row_to_user(row) if row else None

    def get_user_by_cognito_id(self, cognito_id: str) -> Optional[User]:
        row = self._connection.execute(
            "SELECT * FROM users WHERE cognito_id = ?",
            (cognito_id,),
        ).fetchone()
        return _row_to_user(row) if row else None

    def list_users(self) -> Iterable[User]:
        rows = self._connection.execute(
            "SELECT * FROM users ORDER BY created_at ASC"
        ).fetchall()
        return [_row_to_user(row) for row in rows]

    def list_by_customer(self, customer_id: UUID) -> Iterable[User]:
        users = self.list_users()
        return [user for user in users if customer_id in user.customer_ids]

    def create_user(self, user: User) -> User:
        self._connection.execute(
            """
            INSERT INTO users (
                id,
                customer_ids_json,
                cognito_id,
                email,
                roles_json,
                timezone,
                created_at,
                archived_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(user.id),
                list_to_json([str(customer_id) for customer_id in user.customer_ids]),
                user.cognito_id,
                user.email,
                list_to_json(user.roles),
                user.timezone,
                dt_to_str(user.created_at),
                dt_to_str(user.archived_at),
            ),
        )
        self._connection.commit()
        return user

    def update_user(self, user: User) -> User:
        self._connection.execute(
            """
            UPDATE users
            SET customer_ids_json = ?,
                cognito_id = ?,
                email = ?,
                roles_json = ?,
                timezone = ?,
                created_at = ?,
                archived_at = ?
            WHERE id = ?
            """,
            (
                list_to_json([str(customer_id) for customer_id in user.customer_ids]),
                user.cognito_id,
                user.email,
                list_to_json(user.roles),
                user.timezone,
                dt_to_str(user.created_at),
                dt_to_str(user.archived_at),
                str(user.id),
            ),
        )
        self._connection.commit()
        return user


class SqliteInvitationRepository(InvitationRepository):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create_invitation(self, invitation: Invitation) -> Invitation:
        self._connection.execute(
            """
            INSERT INTO invitations (
                id,
                token,
                customer_id,
                email,
                created_at,
                expires_at,
                accepted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(invitation.id),
                invitation.token,
                str(invitation.customer_id),
                invitation.email,
                dt_to_str(invitation.created_at),
                dt_to_str(invitation.expires_at),
                dt_to_str(invitation.accepted_at),
            ),
        )
        self._connection.commit()
        return invitation

    def verify_token(self, token: str, now: datetime) -> Optional[Invitation]:
        row = self._connection.execute(
            "SELECT * FROM invitations WHERE token = ?",
            (token,),
        ).fetchone()
        if not row:
            return None
        invitation = _row_to_invitation(row)
        if invitation.accepted_at is not None:
            return None
        if invitation.expires_at <= now:
            return None
        return invitation

    def mark_accepted(self, invitation: Invitation, now: datetime) -> Invitation:
        updated = invitation.accept(now=now)
        self._connection.execute(
            "UPDATE invitations SET accepted_at = ? WHERE id = ?",
            (dt_to_str(updated.accepted_at), str(updated.id)),
        )
        self._connection.commit()
        return updated


def _row_to_customer(row: sqlite3.Row) -> Customer:
    return Customer(
        id=UUID(row["id"]),
        stripe_customer_id=row["stripe_customer_id"],
        tokens=row["tokens"],
        name=row["name"],
        contact=_contact_from_json(row["contact_json"]),
        created_at=str_to_dt(row["created_at"]),
        updated_at=str_to_dt(row["updated_at"]),
        archived_at=str_to_dt(row["archived_at"]),
    )


def _row_to_user(row: sqlite3.Row) -> User:
    return User(
        id=UUID(row["id"]),
        customer_ids=[UUID(value) for value in list_from_json(row["customer_ids_json"])],
        cognito_id=row["cognito_id"],
        email=row["email"],
        roles=list_from_json(row["roles_json"]),
        created_at=str_to_dt(row["created_at"]),
        archived_at=str_to_dt(row["archived_at"]),
        timezone=row["timezone"],
    )


def _row_to_invitation(row: sqlite3.Row) -> Invitation:
    return Invitation(
        id=UUID(row["id"]),
        customer_id=UUID(row["customer_id"]),
        email=row["email"],
        token=row["token"],
        created_at=str_to_dt(row["created_at"]),
        expires_at=str_to_dt(row["expires_at"]),
        accepted_at=str_to_dt(row["accepted_at"]),
    )
