"""Uploaded customer data endpoints."""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.data.loader import parse_customer_file
from app.data.upload_store import add_uploaded_accounts, get_uploaded_accounts_by_upload_id
from app.models.api import CustomerAccountResponse, UploadDataResponse

router = APIRouter(tags=["uploads"])

ALLOWED_SUFFIXES = {".xlsx", ".csv"}


@router.post(
    "/upload-data",
    response_model=UploadDataResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_data(file: UploadFile = File(...)) -> UploadDataResponse:
    """Validate and store uploaded customer account data."""

    file_name = file.filename or "uploaded-data"
    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=422,
            detail="Unsupported file type. Please upload an .xlsx or .csv file.",
        )

    try:
        contents = await file.read()
        accounts = parse_customer_file(file_name, contents)
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail="CSV files must be UTF-8 encoded.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not accounts:
        raise HTTPException(
            status_code=422,
            detail="The uploaded file did not contain any customer rows.",
        )

    upload_id = add_uploaded_accounts(accounts)
    stored_accounts = get_uploaded_accounts_by_upload_id(upload_id)

    return UploadDataResponse(
        upload_id=upload_id,
        accounts=[
            CustomerAccountResponse.model_validate(
                account.model_dump()
                | {"account_source": "uploaded", "upload_id": upload_id}
            )
            for account in stored_accounts
        ],
    )
