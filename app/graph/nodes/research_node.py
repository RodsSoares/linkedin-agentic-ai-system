from openai import OpenAI

from app.agents.research import (
    build_research_brief,
    run_research_loop,
)
from app.agents.research_llm import (
    build_research_brief_with_llm,
    build_research_objective_with_llm,
    decide_research_action_with_llm,
)
from app.config.settings import OPENAI_API_KEY
from app.graph.state import LinkedInAgentState
from app.schemas.research import ResearchState
from app.tools.web_tools import get_web_tools


client = OpenAI(api_key=OPENAI_API_KEY)


def research_node(
    state: LinkedInAgentState,
) -> dict:
    post = state.get("post")
    opportunity_evaluation = state.get("opportunity_evaluation")

    if post is None:
        raise ValueError(
            "Research workflow requires a PostCandidate."
        )

    if opportunity_evaluation is None:
        raise ValueError(
            "Research workflow requires an OpportunityEvaluation."
        )

    if opportunity_evaluation.classification != "HIGH":
        raise ValueError(
            "Research may only execute for HIGH opportunities."
        )

    search_tool, read_tool = get_web_tools()

    research_state = ResearchState(
        post=post,
        opportunity_evaluation=opportunity_evaluation,
    )

    final_state = run_research_loop(
        state=research_state,
        objective_builder=lambda current_state: (
            build_research_objective_with_llm(
                state=current_state,
                llm=client,
            )
        ),
        action_decider=lambda current_state: (
            decide_research_action_with_llm(
                state=current_state,
                llm=client,
            )
        ),
        search_tool=search_tool,
        read_tool=read_tool,
    )

    research_brief = build_research_brief(
        state=final_state,
        brief_builder=lambda current_state: (
            build_research_brief_with_llm(
                state=current_state,
                llm=client,
            )
        ),
    )

    return {
        "research_result": research_brief,
        "next_step": "end",
        "status": "RESEARCH_COMPLETED",
    }