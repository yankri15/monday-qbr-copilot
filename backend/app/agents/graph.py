"""Graph assembly and execution helpers for the QBR workflow."""

from functools import lru_cache
from uuid import uuid4

from ag_ui_langgraph import LangGraphAgent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

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
    builder.add_node("editor", run_editor)

    builder.add_edge(START, "quant_agent")
    builder.add_edge("quant_agent", "qual_agent")
    builder.add_edge("qual_agent", "strategist")
    builder.add_edge("strategist", "editor")
    builder.add_edge("editor", END)

    return builder.compile(checkpointer=InMemorySaver(), name="qbr_workflow")


def build_qbr_langgraph_agent() -> LangGraphAgent:
    """Create a fresh AG-UI wrapper around the compiled graph."""

    return LangGraphAgent(
        name="qbr_copilot",
        description="LangGraph workflow for generating customer QBR drafts",
        graph=get_qbr_graph(),
    )


def run_qbr_pipeline(account: CustomerAccount) -> WorkflowState:
    """Run the full QBR workflow for a single account."""

    result = get_qbr_graph().invoke(
        {"account": account},
        config={"configurable": {"thread_id": f"qbr-{uuid4()}"}},
    )
    return WorkflowState(
        account=account,
        quantitative_insights=result["quantitative_insights"],
        qualitative_insights=result["qualitative_insights"],
        strategic_synthesis=result["strategic_synthesis"],
        final_draft=result["final_draft"],
    )
