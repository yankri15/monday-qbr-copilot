"""QBR generation and refinement endpoints."""

from typing import Any, AsyncGenerator
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from ag_ui.core import (
    BaseEvent,
    EventType,
    RunAgentInput,
    RunErrorEvent,
    RunFinishedEvent,
    StateDeltaEvent,
    StateSnapshotEvent,
    StepStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
)

from app.agents.graph import build_qbr_langgraph_agent
from app.agents.refiner import refine_draft
from app.data.upload_store import get_uploaded_account_by_name
from app.models.customer import CustomerAccount
from app.models.api import GenerateQBRRequest, HealthResponse, RefineQBRRequest, RefineQBRResponse
from app.data.loader import get_account_by_name

router = APIRouter(tags=["qbr"])

STREAMED_STATE_KEYS = (
    "quantitative_insights",
    "qualitative_insights",
    "strategic_synthesis",
    "judge_verdict",
)

STEP_MESSAGES = {
    "quant_agent": "Analyzing usage metrics...",
    "qual_agent": "Extracting sentiment from CRM notes...",
    "strategist": "Synthesizing strategic recommendations...",
    "csm_judge": "Evaluating QBR quality against CSM acceptance criteria...",
    "editor": "Formatting the final QBR draft...",
}

PASSTHROUGH_EVENT_TYPES = {
    EventType.RUN_STARTED,
    EventType.STEP_STARTED,
    EventType.STEP_FINISHED,
    EventType.RUN_FINISHED,
    EventType.RUN_ERROR,
}


def _encode_sse(event: BaseEvent) -> str:
    payload = event.model_dump_json(by_alias=True, exclude_none=True)
    event_name = event.type.value if hasattr(event.type, "value") else str(event.type)
    return f"event: {event_name}\ndata: {payload}\n\n"


def _build_state_delta(
    previous_snapshot: dict[str, Any],
    current_snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    delta: list[dict[str, Any]] = []
    for key in STREAMED_STATE_KEYS:
        if key not in current_snapshot:
            continue
        if previous_snapshot.get(key) == current_snapshot.get(key):
            continue
        op = "add" if key not in previous_snapshot else "replace"
        delta.append({"op": op, "path": f"/{key}", "value": current_snapshot[key]})
    return delta


async def _generate_qbr_stream(
    *,
    request: Request,
    account: CustomerAccount,
    focus_areas: list[str],
    tone: str,
) -> AsyncGenerator[str, None]:
    """Stream AG-UI events from the LangGraphAgent."""

    agent = build_qbr_langgraph_agent()
    run_input = RunAgentInput(
        threadId=str(uuid4()),
        runId=str(uuid4()),
        state={
            "account": account.model_dump(),
            "focus_areas": focus_areas,
            "tone": tone,
            "judge_retry_count": 0,
            "judge_critique": "",
        },
        messages=[],
        tools=[],
        context=[],
        forwardedProps={},
    )

    previous_snapshot: dict[str, Any] = {}
    emitted_final_draft = False
    final_message_id = f"draft-{uuid4()}"

    try:
        async for event in agent.run(run_input):
            if await request.is_disconnected():
                break

            if isinstance(event, StepStartedEvent):
                step_message = STEP_MESSAGES.get(event.step_name)
                yield _encode_sse(
                    StepStartedEvent(stepName=event.step_name, message=step_message)
                )
                continue

            if isinstance(event, StateSnapshotEvent):
                current_snapshot = dict(event.snapshot)
                delta = _build_state_delta(previous_snapshot, current_snapshot)
                if delta:
                    yield _encode_sse(StateDeltaEvent(delta=delta))

                final_draft = current_snapshot.get("final_draft")
                if final_draft and not emitted_final_draft:
                    yield _encode_sse(TextMessageStartEvent(message_id=final_message_id))
                    yield _encode_sse(
                        TextMessageContentEvent(
                            messageId=final_message_id,
                            delta=final_draft,
                        )
                    )
                    yield _encode_sse(TextMessageEndEvent(messageId=final_message_id))
                    emitted_final_draft = True

                previous_snapshot = current_snapshot
                continue

            if event.type not in PASSTHROUGH_EVENT_TYPES:
                continue

            if isinstance(event, RunFinishedEvent) and not emitted_final_draft:
                final_draft = previous_snapshot.get("final_draft")
                if final_draft:
                    yield _encode_sse(TextMessageStartEvent(messageId=final_message_id))
                    yield _encode_sse(
                        TextMessageContentEvent(
                            messageId=final_message_id,
                            delta=final_draft,
                        )
                    )
                    yield _encode_sse(TextMessageEndEvent(messageId=final_message_id))
                    emitted_final_draft = True

            yield _encode_sse(event)

    except HTTPException:
        raise
    except Exception:
        yield _encode_sse(
            RunErrorEvent(message="Failed to generate QBR. Please try again.")
        )


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Backend health endpoint."""

    return HealthResponse(status="ok")


def _resolve_requested_account(payload: GenerateQBRRequest) -> CustomerAccount | None:
    account_name = payload.account_name.strip()
    if not account_name:
        return None

    if payload.account is not None:
        if payload.account.account_name.casefold() != account_name.casefold():
            raise HTTPException(
                status_code=422,
                detail="account payload must match account_name",
            )
        return CustomerAccount.model_validate(
            payload.account.model_dump(exclude={"account_source", "upload_id"})
        )

    return get_uploaded_account_by_name(account_name) or get_account_by_name(account_name)


@router.post("/generate-qbr")
async def generate_qbr(
    payload: GenerateQBRRequest,
    request: Request,
) -> StreamingResponse:
    """Stream AG-UI events for a generated QBR run."""

    account_name = payload.account_name.strip()
    if not account_name:
        raise HTTPException(status_code=422, detail="account_name must not be empty")
    account = _resolve_requested_account(payload)
    if account is None:
        raise HTTPException(status_code=404, detail=f"Unknown account: {account_name}")

    stream = _generate_qbr_stream(
        request=request,
        account=account,
        focus_areas=payload.focus_areas,
        tone=payload.tone,
    )

    return StreamingResponse(
        stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/refine-qbr", response_model=RefineQBRResponse)
def refine_qbr(payload: RefineQBRRequest) -> RefineQBRResponse:
    """Refine an existing markdown draft with natural-language instructions."""

    refined = refine_draft(
        current_draft=payload.current_draft,
        instructions=payload.instructions,
    )
    return RefineQBRResponse(refined_draft=refined)
