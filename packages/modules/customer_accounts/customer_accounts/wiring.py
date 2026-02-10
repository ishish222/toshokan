from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4

from .adapters.in_memory import (
    InMemoryCustomerAccountsStore,
    InMemoryCustomerRepository,
    InMemoryInvitationRepository,
    InMemoryUserRepository,
    FakeIdentityProvisioning,
    create_store,
)
from .adapters.sqlite import (
    SqliteCustomerRepository,
    SqliteInvitationRepository,
    SqliteUserRepository,
)
from .adapters.sqlite_schema import ensure_schema
from .app import CustomerUsersService
from .config import CustomerAccountsConfig
from .ports import CustomerRepository, UserRepository


@dataclass(frozen=True)
class CustomerAccountsComponents:
    service: CustomerUsersService
    users: UserRepository
    customers: CustomerRepository
    store: Optional[InMemoryCustomerAccountsStore]


def build(
    *,
    storage_backend: str,
    config: CustomerAccountsConfig,
    sqlite_connection: sqlite3.Connection | None = None,
    seed_data_path: str | None = None,
) -> CustomerAccountsComponents:
    store: Optional[InMemoryCustomerAccountsStore] = None
    if storage_backend == "sqlite":
        assert sqlite_connection is not None, "sqlite_connection required for sqlite backend"
        ensure_schema(sqlite_connection)
        customers = SqliteCustomerRepository(sqlite_connection)
        users = SqliteUserRepository(sqlite_connection)
        invitations = SqliteInvitationRepository(sqlite_connection)
        _bootstrap_sqlite_from_seed_if_needed(
            customers=customers,
            users=users,
            invitations=invitations,
            config=config,
            seed_data_path=seed_data_path,
        )
        current_user_id = _first_user_id(users)
    else:
        store = create_store(config)
        customers = InMemoryCustomerRepository(store)
        users = InMemoryUserRepository(store)
        invitations = InMemoryInvitationRepository(store)
        current_user_id = store.current_user_id
    identity = FakeIdentityProvisioning()
    service = CustomerUsersService(
        customers=customers,
        users=users,
        invitations=invitations,
        identity=identity,
        current_user_id=current_user_id,
    )
    return CustomerAccountsComponents(service=service, users=users, customers=customers, store=store)


def _first_user_id(users: UserRepository) -> UUID:
    for user in users.list_users():
        return user.id
    return uuid4()


def _bootstrap_sqlite_from_seed_if_needed(
    *,
    customers: CustomerRepository,
    users: UserRepository,
    invitations: SqliteInvitationRepository,
    config: CustomerAccountsConfig,
    seed_data_path: str | None,
) -> None:
    if not seed_data_path or not os.path.exists(seed_data_path):
        return
    if any(True for _ in users.list_users()):
        return

    seed_store = create_store(config)
    for customer in seed_store.customers.values():
        customers.create_customer(customer)
    for user in seed_store.users.values():
        users.create_user(user)
    for invitation in seed_store.invitations.values():
        invitations.create_invitation(invitation)
