"""Account data endpoints."""

from fastapi import APIRouter

from app.data.loader import get_all_accounts
from app.models.api import CustomerAccountResponse

router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=list[CustomerAccountResponse])
def list_accounts() -> list[CustomerAccountResponse]:
    """Return the full list of sample customer accounts."""

    return [
        CustomerAccountResponse.model_validate(account.model_dump())
        for account in get_all_accounts()
    ]
