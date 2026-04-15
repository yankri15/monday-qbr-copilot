"""Graph assembly and execution helpers for the QBR workflow."""

from functools import lru_cache
from uuid import uuid4

from ag_ui_langgraph import LangGraphAgent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.csm_judge import judge_router, run_csm_judge
from app.agents.editor import run_editor
from app.agents.qual_agent import run_qual_agent
from app.agents.quant_agent import run_quant_agent
from app.agents.state import WorkflowState
from app.agents.strategist import run_strategist
from app.models.customer import CustomerAccount


@lru_cache(maxsize=1)
def get_qbr_graph():
    """Compile and cache the LangGraph workflow."""

    builder = StateGraph(WorkflowState)
    builder.add_node("quant_agent", run_quant_agent)
    builder.add_node("qual_agent", run_qual_agent)
    builder.add_node("strategist", run_strategist)
    builder.add_node("csm_judge", run_csm_judge)
    builder.add_node("editor", run_editor)

    builder.add_edge(START, "quant_agent")
    builder.add_edge("quant_agent", "qual_agent")
    builder.add_edge("qual_agent", "strategist")
    builder.add_edge("strategist", "csm_judge")
    builder.add_conditional_edges("csm_judge", judge_router)
    builder.add_edge("editor", END)

    return builder.compile(checkpointer=InMemorySaver(), name="qbr_workflow")


def build_qbr_langgraph_agent() -> LangGraphAgent:
    """Create a fresh AG-UI wrapper around the compiled graph."""

    return LangGraphAgent(
        name="qbr_copilot",
        description="LangGraph workflow for generating customer QBR drafts",
        graph=get_qbr_graph(),
    )


def run_qbr_pipeline(
    account: CustomerAccount,
    *,
    focus_areas: list[str] | None = None,
    tone: str = "executive",
) -> WorkflowState:
    """Run the full QBR workflow for a single account."""

    result = get_qbr_graph().invoke(
        {
            "account": account,
            "focus_areas": list(focus_areas or []),
            "tone": tone,
            "judge_retry_count": 0,
            "judge_critique": "",
        },
        config={"configurable": {"thread_id": f"qbr-{uuid4()}"}},
    )
    result["account"] = account
    return WorkflowState(result)
