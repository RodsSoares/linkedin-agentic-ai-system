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
from app.schemas.opportunity import OpportunityEvaluation
from app.schemas.post import PostCandidate
from app.schemas.research import ResearchState
from app.schemas.tools import SearchResult
from app.tools.web_reader import web_reader
from app.tools.web_search import web_search


client = OpenAI(api_key=OPENAI_API_KEY)


def research_search(query: str) -> list[SearchResult]:
    return web_search(query)


def research_read(url: str) -> str:
    results = web_search("research-reader-adapter")

    result = next(
        (
            candidate
            for candidate in results
            if candidate.url == url
        ),
        None,
    )

    if result is None:
        raise ValueError(
            f"Research reader could not resolve discovered URL: {url}"
        )

    return web_reader(result)


def main() -> None:
    post = PostCandidate(
        post_id="smoke-research-001",
        author_name="Test Author",
        post_text=(
            "AI agents are changing supply chain planning by coordinating "
            "specialized capabilities and supporting human decision-making."
        ),
        post_url="https://example.com/posts/ai-agents-supply-chain",
    )

    opportunity_evaluation = OpportunityEvaluation(
        topic_relevance=90,
        positioning_fit=90,
        contribution_potential=90,
        research_cost=30,
        engagement_potential=50,
        research_efficiency=70,
        opportunity_score=84.5,
        classification="HIGH",
    )

    state = ResearchState(
        post=post,
        opportunity_evaluation=opportunity_evaluation,
    )

    final_state = run_research_loop(
        state=state,
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
        search_tool=research_search,
        read_tool=research_read,
    )

    brief = build_research_brief(
        state=final_state,
        brief_builder=lambda current_state: (
            build_research_brief_with_llm(
                state=current_state,
                llm=client,
            )
        ),
    )

    print("\n=== RESEARCH OBJECTIVE ===")
    print(final_state.research_objective.model_dump_json(indent=2))

    print("\n=== TERMINAL STATE ===")
    print(
        {
            "status": (
                final_state.status.value
                if final_state.status is not None
                else None
            ),
            "steps": final_state.steps,
            "decision_attempts": final_state.decision_attempts,
            "search_count": final_state.search_count,
            "read_count": final_state.read_count,
            "evidence_count": len(final_state.evidence),
            "last_error": final_state.last_error,
        }
    )

    print("\n=== RESEARCH BRIEF ===")
    print(brief.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
