"""Account data endpoints."""

from fastapi import APIRouter

from app.data.loader import get_all_accounts
from app.data.upload_store import get_all_uploaded_accounts
from app.models.api import CustomerAccountResponse

router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=list[CustomerAccountResponse])
def list_accounts() -> list[CustomerAccountResponse]:
    """Return the sample customer accounts plus any uploaded accounts."""

    merged_by_name: dict[str, CustomerAccountResponse] = {}

    for account in get_all_accounts():
        merged_by_name[account.account_name.casefold()] = CustomerAccountResponse.model_validate(
            account.model_dump() | {"account_source": "sample", "upload_id": None}
        )

    for upload_id, account in get_all_uploaded_accounts():
        merged_by_name[account.account_name.casefold()] = CustomerAccountResponse.model_validate(
            account.model_dump() | {"account_source": "uploaded", "upload_id": upload_id}
        )

    return sorted(merged_by_name.values(), key=lambda account: account.account_name)
