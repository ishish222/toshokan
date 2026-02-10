from fastapi import APIRouter

from ..schemas import Customer, CustomerUpdate, User
from ..store import STORE

router = APIRouter()


@router.get(
    "/user",
    tags=["User"],
    summary="Get current user",
    response_model=User,
)
def get_user() -> User:
    return STORE.user


@router.delete(
    "/customer",
    tags=["User"],
    summary="Archive current customer",
    response_model=Customer,
)
def archive_customer() -> Customer:
    return STORE.archive_customer()


@router.get(
    "/customer/tokens",
    tags=["User"],
    summary="Get token balance",
)
def get_account_tokens() -> dict[str, int]:
    return {"tokens": STORE.customer.tokens}


@router.get(
    "/customer",
    tags=["User"],
    summary="Get customer metadata (mostly Stripe-linked)",
    response_model=Customer,
)
def get_customer() -> Customer:
    return STORE.customer


@router.patch(
    "/customer",
    tags=["User"],
    summary="Update locally-stored customer fields (optional)",
    response_model=Customer,
)
def update_customer(update: CustomerUpdate) -> Customer:
    return STORE.update_customer(update)
