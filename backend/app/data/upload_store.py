"""In-memory storage for uploaded customer datasets."""

from uuid import uuid4

from app.models.customer import CustomerAccount

_UPLOADS: dict[str, tuple[CustomerAccount, ...]] = {}


def add_uploaded_accounts(accounts: list[CustomerAccount]) -> str:
    upload_id = str(uuid4())
    _UPLOADS[upload_id] = tuple(account.model_copy(deep=True) for account in accounts)
    return upload_id


def get_uploaded_accounts_by_upload_id(upload_id: str) -> list[CustomerAccount]:
    return [account.model_copy(deep=True) for account in _UPLOADS.get(upload_id, ())]


def get_uploaded_account_by_name(name: str) -> CustomerAccount | None:
    normalized_name = name.strip().casefold()
    for accounts in reversed(list(_UPLOADS.values())):
        for account in accounts:
            if account.account_name.casefold() == normalized_name:
                return account.model_copy(deep=True)
    return None


def get_all_uploaded_accounts() -> list[tuple[str, CustomerAccount]]:
    uploaded: list[tuple[str, CustomerAccount]] = []
    for upload_id, accounts in _UPLOADS.items():
        for account in accounts:
            uploaded.append((upload_id, account.model_copy(deep=True)))
    return uploaded


def clear_uploads() -> None:
    _UPLOADS.clear()
