"""Pydantic request and response models for the FastAPI layer."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.customer import CustomerAccount


class CustomerAccountResponse(CustomerAccount):
    """Serialized customer record returned by the API."""


class GenerateQBRRequest(BaseModel):
    """Request body for starting a QBR run."""

    model_config = ConfigDict(extra="forbid")

    account_name: str = Field(min_length=1, description="Customer account name")


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
