"""Pydantic request and response models for the FastAPI layer."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.customer import CustomerAccount


class CustomerAccountResponse(CustomerAccount):
    """Serialized customer record returned by the API."""

    account_source: Literal["sample", "uploaded"] = Field(
        default="sample",
        description="Whether this account came from the bundled sample dataset or an upload.",
    )
    upload_id: str | None = Field(
        default=None,
        description="Upload identifier when the account came from an uploaded file.",
    )


class GenerateQBRRequest(BaseModel):
    """Request body for starting a QBR run."""

    model_config = ConfigDict(extra="forbid")

    account_name: str = Field(min_length=1, description="Customer account name")
    account: CustomerAccountResponse | None = Field(
        default=None,
        description=(
            "Optional full account payload from the client. Used to keep uploaded-account "
            "generation stable in stateless deployment environments."
        ),
    )
    focus_areas: list[str] = Field(
        default_factory=list,
        description=(
            "Optional focus areas: 'upsell_opportunity', "
            "'churn_risk', 'automation_adoption'"
        ),
    )
    tone: str = Field(
        default="executive",
        description="Audience tone: 'executive', 'team_lead', or 'technical'",
    )


class RefineQBRRequest(BaseModel):
    """Request body for refining an existing QBR draft."""

    model_config = ConfigDict(extra="forbid")

    current_draft: str = Field(min_length=1, description="Existing markdown draft")
    instructions: str = Field(
        min_length=1,
        description="Natural-language instructions for revising the draft",
    )


class RefineQBRResponse(BaseModel):
    """Response body for a refined QBR draft."""

    refined_draft: str


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str


class UploadDataResponse(BaseModel):
    """Response body returned after a successful customer data upload."""

    model_config = ConfigDict(extra="forbid")

    upload_id: str
    accounts: list[CustomerAccountResponse]


class ExportPdfRequest(BaseModel):
    """Request body for converting a markdown draft into a PDF."""

    model_config = ConfigDict(extra="forbid")

    markdown_content: str = Field(
        min_length=1,
        description="Markdown QBR draft to convert to PDF",
    )
    account_name: str = Field(
        min_length=1,
        description="Account name for the PDF filename",
    )
