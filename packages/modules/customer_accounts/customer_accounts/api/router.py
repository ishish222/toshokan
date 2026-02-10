from __future__ import annotations

from typing import Callable, Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..app import CustomerUsersService
from ..domain.entities import ContactData as DomainContactData
from ..domain.entities import Customer as DomainCustomer
from ..domain.entities import Invitation as DomainInvitation
from ..domain.entities import PostalAddress as DomainPostalAddress
from ..domain.entities import User as DomainUser
from .schemas import (
    ContactData,
    Customer,
    CustomerUpdate,
    Invitation,
    InvitationAcceptRequest,
    InvitationCreateRequest,
    PostalAddress,
    RegisterRequest,
    RegisterResponse,
    TokenBalanceUpdate,
    User,
    UserUpdate,
)


class AuthContext(Protocol):
    user_id: UUID
    customer_ids: list[UUID]
    groups: list[str]

    @property
    def is_backoffice(self) -> bool:
        raise NotImplementedError


def create_router(service: CustomerUsersService, get_auth_context: Callable[..., AuthContext]) -> APIRouter:
    router = APIRouter()

    @router.get("/me", tags=["User"], summary="Get current user", response_model=User)
    def get_current_user(auth: AuthContext = Depends(get_auth_context)) -> User:
        current = service.get_current_user(current_user_id=auth.user_id)
        if current is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return _to_user(current)

    @router.post(
        "/user/register",
        tags=["User"],
        summary="Register user and create customer",
        status_code=status.HTTP_201_CREATED,
        response_model=RegisterResponse,
    )
    def register_user(payload: RegisterRequest, auth: AuthContext = Depends(get_auth_context)) -> RegisterResponse:
        _require_backoffice(auth)
        provisioned = service.register_user(email=payload.email, cognito_id=payload.cognito_id)
        return RegisterResponse(
            customer=_to_customer(provisioned.customer),
            user=_to_user(provisioned.user),
        )

    @router.delete(
        "/user",
        tags=["User"],
        summary="Archive current user",
        response_model=User,
    )
    def delete_user(auth: AuthContext = Depends(get_auth_context)) -> User:
        updated = service.delete_current_user(current_user_id=auth.user_id)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return _to_user(updated)

    @router.delete(
        "/customer",
        tags=["Customer"],
        summary="Archive current customer",
        response_model=Customer,
    )
    def delete_customer(auth: AuthContext = Depends(get_auth_context)) -> Customer:
        try:
            updated = service.delete_current_customer(current_user_id=auth.user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(updated)

    @router.post(
        "/invitations",
        tags=["Invitations"],
        summary="Invite user to customer",
        status_code=status.HTTP_201_CREATED,
        response_model=Invitation,
    )
    def create_invitation(payload: InvitationCreateRequest, auth: AuthContext = Depends(get_auth_context)) -> Invitation:
        _require_customer_access(auth, payload.customer_id)
        invitation = service.invite_user(customer_id=payload.customer_id, email=payload.email)
        return _to_invitation(invitation)

    @router.post(
        "/invitations/accept",
        tags=["Invitations"],
        summary="Accept invitation token and register user",
        status_code=status.HTTP_201_CREATED,
        response_model=User,
    )
    def accept_invitation(payload: InvitationAcceptRequest, auth: AuthContext = Depends(get_auth_context)) -> User:
        user = service.accept_invitation(token=payload.token)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
        return _to_user(user)

    @router.get(
        "/user",
        tags=["User"],
        summary="Get current user",
        response_model=User,
    )
    def get_user(auth: AuthContext = Depends(get_auth_context)) -> User:
        current = service.get_current_user(current_user_id=auth.user_id)
        if current is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return _to_user(current)

    @router.get(
        "/customer",
        tags=["Customer"],
        summary="Get customer metadata (mostly Stripe-linked)",
        response_model=Customer,
    )
    def get_customer(auth: AuthContext = Depends(get_auth_context)) -> Customer:
        customer = service.get_current_customer(current_user_id=auth.user_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(customer)

    @router.get(
        "/customers/{customer_id}",
        tags=["Customer"],
        summary="Get customer by id",
        response_model=Customer,
    )
    def get_customer_by_id(customer_id: UUID, auth: AuthContext = Depends(get_auth_context)) -> Customer:
        _require_backoffice(auth)
        customer = service.get_customer_by_id(customer_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(customer)

    @router.get(
        "/customers",
        tags=["Customer"],
        summary="List customers",
        response_model=list[Customer],
    )
    def list_customers(auth: AuthContext = Depends(get_auth_context)) -> list[Customer]:
        _require_backoffice(auth)
        customers = service.list_customers()
        return [_to_customer(customer) for customer in customers]

    @router.get(
        "/users",
        tags=["User"],
        summary="List users",
        response_model=list[User],
    )
    def list_users(auth: AuthContext = Depends(get_auth_context)) -> list[User]:
        _require_backoffice(auth)
        users = service.list_users()
        return [_to_user(user) for user in users]

    @router.get(
        "/users/{user_id}",
        tags=["User"],
        summary="Get user by id",
        response_model=User,
    )
    def get_user_by_id(user_id: UUID, auth: AuthContext = Depends(get_auth_context)) -> User:
        _require_backoffice(auth)
        user = service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return _to_user(user)

    @router.patch(
        "/users/{user_id}",
        tags=["User"],
        summary="Update user by id",
        response_model=User,
    )
    def update_user_by_id(user_id: UUID, payload: UserUpdate, auth: AuthContext = Depends(get_auth_context)) -> User:
        _require_backoffice(auth)
        updated = service.update_user_by_id(user_id=user_id, email=payload.email, timezone=payload.timezone, roles=payload.roles)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return _to_user(updated)

    @router.patch(
        "/customer",
        tags=["Customer"],
        summary="Update locally-stored customer fields (optional)",
        response_model=Customer,
    )
    def update_customer(payload: CustomerUpdate, auth: AuthContext = Depends(get_auth_context)) -> Customer:
        updated = service.update_customer(
            name=payload.name,
            contact=_to_domain_contact(payload.contact),
            current_user_id=auth.user_id,
        )
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(updated)

    @router.patch(
        "/customers/{customer_id}",
        tags=["Customer"],
        summary="Update customer by id",
        response_model=Customer,
    )
    def update_customer_by_id(
        customer_id: UUID,
        payload: CustomerUpdate,
        auth: AuthContext = Depends(get_auth_context),
    ) -> Customer:
        _require_backoffice(auth)
        updated = service.update_customer_by_id(
            customer_id=customer_id,
            name=payload.name,
            contact=_to_domain_contact(payload.contact),
        )
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(updated)

    @router.get(
        "/customer/tokens",
        tags=["Customer"],
        summary="Get token balance",
    )
    def get_account_tokens(auth: AuthContext = Depends(get_auth_context)) -> dict[str, int]:
        customer = service.get_current_customer(current_user_id=auth.user_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return {"tokens": customer.tokens}

    @router.get(
        "/customers/{customer_id}/tokens",
        tags=["Customer"],
        summary="Get customer token balance",
    )
    def get_customer_tokens(customer_id: UUID, auth: AuthContext = Depends(get_auth_context)) -> dict[str, int]:
        _require_backoffice(auth)
        customer = service.get_customer_by_id(customer_id)
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return {"tokens": customer.tokens}

    @router.post(
        "/customers/{customer_id}/tokens/credit",
        tags=["Customer"],
        summary="Credit customer token balance",
        response_model=Customer,
    )
    def credit_tokens(customer_id: UUID, payload: TokenBalanceUpdate, auth: AuthContext = Depends(get_auth_context)) -> Customer:
        _require_backoffice(auth)
        updated = service.credit_customer_tokens(customer_id=customer_id, amount=payload.amount)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(updated)

    @router.post(
        "/customers/{customer_id}/tokens/debit",
        tags=["Customer"],
        summary="Debit customer token balance",
        response_model=Customer,
    )
    def debit_tokens(customer_id: UUID, payload: TokenBalanceUpdate, auth: AuthContext = Depends(get_auth_context)) -> Customer:
        _require_backoffice(auth)
        try:
            updated = service.debit_customer_tokens(customer_id=customer_id, amount=payload.amount)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        return _to_customer(updated)

    return router


def _require_backoffice(auth: AuthContext) -> None:
    if not auth.is_backoffice:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Backoffice access required")


def _require_customer_access(auth: AuthContext, customer_id: UUID) -> None:
    if auth.is_backoffice:
        return
    if customer_id not in auth.customer_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access denied")


def _to_user(user: DomainUser) -> User:
    return User(
        id=user.id,
        customer_ids=user.customer_ids,
        cognito_id=user.cognito_id,
        email=user.email,
        roles=user.roles or None,
        timezone=user.timezone,
        created_at=user.created_at,
        archived_at=user.archived_at,
    )


def _to_customer(customer: DomainCustomer) -> Customer:
    return Customer(
        id=customer.id,
        stripe_customer_id=customer.stripe_customer_id,
        tokens=customer.tokens,
        name=customer.name,
        contact=_to_api_contact(customer.contact),
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        archived_at=customer.archived_at,
    )


def _to_api_contact(contact: DomainContactData | None) -> ContactData | None:
    if contact is None:
        return None
    address = None
    if contact.address is not None:
        address = PostalAddress(
            line1=contact.address.line1,
            line2=contact.address.line2,
            city=contact.address.city,
            region=contact.address.region,
            postal_code=contact.address.postal_code,
            country=contact.address.country,
        )
    return ContactData(email=contact.email, phone=contact.phone, address=address)


def _to_domain_contact(contact: ContactData | None) -> DomainContactData | None:
    if contact is None:
        return None
    address = None
    if contact.address is not None:
        address = DomainPostalAddress(
            line1=contact.address.line1,
            line2=contact.address.line2,
            city=contact.address.city,
            region=contact.address.region,
            postal_code=contact.address.postal_code,
            country=contact.address.country,
        )
    return DomainContactData(email=contact.email, phone=contact.phone, address=address)


def _to_invitation(invitation: DomainInvitation) -> Invitation:
    return Invitation(
        id=invitation.id,
        customer_id=invitation.customer_id,
        email=invitation.email,
        token=invitation.token,
        created_at=invitation.created_at,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
    )

