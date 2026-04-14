# Data Layer

> Parse the sample Excel dataset into typed Pydantic models and expose a data access module for the rest of the backend.

## Meta

| Field         | Value                          |
|---------------|--------------------------------|
| Status        | `DONE`                         |
| Owner         | Agent                          |
| Last Updated  | 2026-04-14                     |

### Dependencies

| Work State File            | Required Status |
|----------------------------|-----------------|
| `00_infrastructure.md`     | `DONE`          |

---

## Objective

Create the canonical data models and a loading module so that every downstream consumer (agent framework, API endpoints) works with validated, typed Python objects rather than raw spreadsheet rows. The source of truth is `docs/sample_customers_q3_2025.xlsx` containing 5 customer accounts with 13 fields each.

---

## Plan

- [x] Define the `CustomerAccount` Pydantic model in `backend/app/models/customer.py` with fields and types:
  ```
  account_name:            str          # Customer name
  plan_type:               str          # Subscription type — "Enterprise" | "Pro" | "Basic"
  active_users:            int          # Number of active users
  usage_growth_qoq:        float        # % change in usage quarter-over-quarter (e.g. 0.16 = +16%)
  automation_adoption_pct: float        # Automation feature adoption rate (0.0–1.0)
  tickets_last_quarter:    int          # Support ticket count
  avg_response_time:       float        # Average support response time (hours)
  nps_score:               float        # Most recent NPS score (note: docx has typo "nps_scorz", Excel uses "nps_score")
  preferred_channel:       str          # Main communication preference (Email / Phone / Chat / In-app chat)
  scat_score:              float        # Success Confidence & Adoption Trend (SCAT) — internal health metric (0–100)
  risk_engine_score:       float        # AI-predicted churn risk (0–1). Higher = greater likelihood of churn
  crm_notes:               str          # Qualitative notes from the CSM
  feedback_summary:        str          # Key feedback or feature requests
  ```
- [x] Create the data loader module at `backend/app/data/loader.py`:
  - Use `openpyxl` to read the Excel file
  - Parse each row into a `CustomerAccount` instance
  - Expose `get_all_accounts() -> list[CustomerAccount]`
  - Expose `get_account_by_name(name: str) -> CustomerAccount | None`
- [x] Copy or symlink the Excel file to `backend/data/sample_customers_q3_2025.xlsx` so the backend has a stable reference path
- [x] Write a quick smoke test (runnable script or pytest) that validates:
  - Exactly 5 accounts are loaded
  - All field types match the Pydantic schema
  - Known values spot-check (e.g., Altura Systems has 420 active users)

---

## Acceptance Criteria

- [x] `from app.models.customer import CustomerAccount` imports without error
- [x] `from app.data.loader import get_all_accounts` returns exactly 5 `CustomerAccount` objects
- [x] `get_account_by_name("Coral Retail")` returns the correct account with `risk_engine_score == 0.73`
- [x] All 13 fields are present and correctly typed on every account object
- [x] The Excel file path is relative to the backend root (no hardcoded absolute paths)

---

## Technical Decisions

- `plan_type` and `preferred_channel` are modeled as `Literal[...]` values for stronger validation while keeping the external interface string-based.
- The backend stores the sample workbook at `backend/data/sample_customers_q3_2025.xlsx` as a local copy for predictable runtime packaging and deployment behavior.
- The loader validates the workbook header row against the expected 13-column schema before parsing any records.
- Workbook reads are cached in-process via `lru_cache(maxsize=1)` so repeated API calls do not re-open the spreadsheet unnecessarily.

---

## Dependencies Detail

### `00_infrastructure.md`

- **What is needed:** A working Python environment managed by `uv` with `openpyxl` and `pydantic` installed.
- **Expected interface/contract:** Running `uv run python -c "import openpyxl; import pydantic; print('ok')"` inside `backend/` succeeds.

---

## Log

- **2026-04-14** — Inspected `docs/sample_customers_q3_2025.xlsx` and confirmed the worksheet schema exactly matches the planned 13 fields.
- **2026-04-14** — Added `CustomerAccount` Pydantic model and data-loader helpers under `backend/app/models/` and `backend/app/data/`.
- **2026-04-14** — Copied the sample workbook to `backend/data/sample_customers_q3_2025.xlsx` for stable backend-relative access.
- **2026-04-14** — Added `backend/tests/test_data_loader.py` smoke tests and verified imports, row count, field coverage, and known value checks.
