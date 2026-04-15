"""Export endpoints for QBR drafts."""

from fastapi import APIRouter, HTTPException, Response

from app.models.api import ExportPdfRequest
from app.services.pdf_export import markdown_to_pdf

router = APIRouter(tags=["export"])


def _build_download_name(account_name: str) -> str:
    safe_name = "".join(character if character.isalnum() or character in {" ", "-", "_"} else "_" for character in account_name).strip()
    return safe_name or "QBR"


@router.post("/export-pdf")
def export_pdf(payload: ExportPdfRequest) -> Response:
    """Render a markdown QBR draft as a downloadable PDF."""

    try:
        pdf_bytes = markdown_to_pdf(
            markdown_content=payload.markdown_content,
            account_name=payload.account_name,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to render the QBR PDF.",
        ) from exc

    download_name = f"{_build_download_name(payload.account_name)}_QBR.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
    )
