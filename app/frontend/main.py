from __future__ import annotations

import html
import os
import textwrap
import threading
import time
import traceback
import uuid
from datetime import datetime
from typing import Any

# Real web mode must be configured before application imports.
os.environ["WEB_TOOL_MODE"] = "real"

import streamlit as st
from langgraph.types import Command

from app.graph.workflow import build_scout_opportunity_workflow
from app.agents.scout import reset_scout_observer, set_scout_observer


SCOUT_OBJECTIVE = """
Find a current public web article, discussion, or professional publication
where Rodrigo can make a relevant and differentiated contribution about
AI agents, intelligent automation, AI applied to business processes,
supply chain, operations, or AI solution architecture.

Prefer recent, substantive content where a practical business and
engineering perspective would add value.

Select exactly one strong candidate when appropriate. Do not force a
selection if no candidate is good enough.
""".strip()


STAGES = [
    ("discovery", "Discovery"),
    ("opportunity", "Opportunity"),
    ("research", "Research"),
    ("argument", "Argument"),
    ("perspectives", "Perspectives"),
    ("human", "Human"),
    ("writer", "Writer"),
    ("evaluation", "Evaluation"),
]


st.set_page_config(
    page_title="My LinkedIn Agentic AI System",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# Design system
# =========================================================

st.markdown(
    """
<style>
:root {
    --bg-0: #020914;
    --bg-1: #06111f;
    --panel: rgba(8, 24, 42, 0.78);
    --cyan: #20c8ff;
    --blue: #2f7dff;
    --white: #f5f9ff;
    --text: #d8e4f2;
    --muted: #8294aa;
    --green: #26d99a;
    --violet: #9b7cff;
}

html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 82% 4%, rgba(20, 105, 190, 0.18), transparent 27rem),
        radial-gradient(circle at 48% 110%, rgba(0, 178, 255, 0.10), transparent 34rem),
        linear-gradient(145deg, var(--bg-0) 0%, var(--bg-1) 48%, #071423 100%);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(4, 15, 28, 0.98) !important;
    border-bottom: 1px solid rgba(47, 184, 255, 0.10);
}

[data-testid="stDecoration"] { display: none !important; }

.block-container {
    max-width: 1420px;
    padding-top: 1.25rem;
    padding-bottom: 6rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1, h2, h3, h4, h5, h6 { color: var(--white) !important; }
p, li { color: var(--text); }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(47, 184, 255, .20);
    border-radius: 18px;
    padding: 1.15rem 1.45rem;
    background:
        radial-gradient(circle at 90% 15%, rgba(31, 155, 255, .16), transparent 22rem),
        linear-gradient(135deg, rgba(7, 24, 42, .92), rgba(6, 18, 32, .74));
    margin-bottom: .75rem;
}

.eyebrow {
    color: var(--cyan);
    font-size: .67rem;
    font-weight: 800;
    letter-spacing: .18em;
    margin-bottom: .55rem;
}

.hero-title {
    color: var(--white);
    font-size: clamp(1.7rem, 3vw, 2.5rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -.035em;
}

.hero-title .accent {
    background: linear-gradient(90deg, #53d8ff, #278dff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    max-width: 850px;
    margin-top: .65rem;
    color: #a9bbcd;
    font-size: .93rem;
    line-height: 1.55;
}

.tag-row {
    display: flex;
    gap: .45rem;
    flex-wrap: wrap;
    margin-top: .9rem;
}

.tag {
    border: 1px solid rgba(32, 200, 255, .17);
    background: rgba(7, 30, 49, .72);
    color: #91cde9;
    border-radius: 999px;
    padding: .27rem .58rem;
    font-size: .68rem;
}

.architecture {
    border: 1px solid rgba(47, 184, 255, .15);
    border-radius: 15px;
    background: rgba(5, 18, 32, .68);
    padding: .78rem .9rem .82rem;
    margin-bottom: 1rem;
}

.arch-title {
    color: #6fa7c8;
    font-size: .63rem;
    font-weight: 800;
    letter-spacing: .17em;
    margin-bottom: .85rem;
}

.workflow-row {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: .32rem;
}

.stage {
    display: inline-flex;
    align-items: center;
    gap: .38rem;
    border: 1px solid rgba(47, 184, 255, .12);
    background: rgba(8, 25, 43, .60);
    border-radius: 9px;
    padding: .48rem .62rem;
    color: #8294aa;
    font-size: .68rem;
    font-weight: 750;
}

.stage.completed {
    color: #bdf8e4;
    border-color: rgba(38, 217, 154, .30);
    background: rgba(17, 77, 61, .20);
}

.stage.running {
    color: #c8f3ff;
    border-color: rgba(32, 200, 255, .58);
    background: rgba(18, 93, 127, .22);
}

.stage.human {
    color: #e1d7ff;
    border-color: rgba(155, 124, 255, .60);
    background: rgba(84, 61, 139, .22);
}

.arrow {
    color: #34536b;
    font-size: .82rem;
}

.state-panel {
    border: 1px solid rgba(47, 184, 255, .18);
    border-radius: 15px;
    padding: 1.05rem 1.15rem;
    background: linear-gradient(145deg, rgba(8, 27, 47, .88), rgba(7, 20, 35, .78));
    margin-bottom: 1rem;
}

.state-kicker, .card-kicker {
    color: var(--cyan);
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .16em;
}

.state-title {
    color: var(--white);
    font-size: 1.12rem;
    font-weight: 780;
    margin-top: .25rem;
}

.state-copy {
    color: var(--muted);
    font-size: .82rem;
    margin-top: .22rem;
}

.elapsed {
    color: #6f879c;
    font-size: .70rem;
    margin-top: .6rem;
}

.artifact-card {
    border: 1px solid rgba(47, 184, 255, .15);
    border-radius: 13px;
    padding: 1rem;
    background: rgba(8, 25, 43, .58);
    height: 100%;
}

.card-title {
    color: var(--white);
    font-size: 1rem;
    font-weight: 760;
    margin-top: .35rem;
}

.card-copy {
    color: #9cb0c3;
    font-size: .78rem;
    line-height: 1.5;
    margin-top: .45rem;
}

.score {
    color: var(--white);
    font-size: 2rem;
    font-weight: 800;
}

.classification {
    color: var(--green);
    font-weight: 800;
}

.perspective-card {
    min-height: 285px;
    border: 1px solid rgba(47, 184, 255, .17);
    border-radius: 14px;
    padding: 1rem;
    background: linear-gradient(145deg, rgba(8, 27, 47, .88), rgba(7, 20, 35, .78));
}

.perspective-number {
    color: #52748d;
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .14em;
}

.perspective-title {
    color: var(--white);
    font-size: 1rem;
    font-weight: 780;
    margin-top: .45rem;
    margin-bottom: .65rem;
}

.perspective-label {
    color: #6fa7c8;
    font-size: .62rem;
    font-weight: 800;
    letter-spacing: .10em;
    margin-top: .55rem;
}

.perspective-copy {
    color: #b6c6d5;
    font-size: .76rem;
    line-height: 1.5;
    margin-top: .15rem;
}

.final-draft {
    border: 1px solid rgba(47, 184, 255, .17);
    border-radius: 14px;
    padding: 1.15rem;
    background: rgba(7, 22, 39, .80);
    color: #eaf3fb;
    line-height: 1.65;
    min-height: 250px;
    white-space: pre-wrap;
}

.quality-card {
    border: 1px solid rgba(38, 217, 154, .20);
    border-radius: 14px;
    padding: 1.15rem;
    background: rgba(8, 32, 35, .55);
    min-height: 250px;
}

.principle {
    text-align: center;
    margin-top: 1.8rem;
    padding: 1.1rem;
    color: #8ba3b7;
    font-size: .75rem;
    letter-spacing: .08em;
}

.principle strong { color: #dff5ff; }

.stButton > button {
    min-height: 3rem;
    border-radius: 10px;
    border: 1px solid rgba(47, 184, 255, .25);
    background: linear-gradient(145deg, rgba(8, 29, 49, .90), rgba(7, 22, 39, .78));
    color: #dff5ff;
    font-weight: 650;
}

.stButton > button:hover {
    border-color: rgba(32, 200, 255, .70);
    color: white;
}

/* Streamlit expander header can render on a light surface.
   Force readable dark text/icon there without changing the dark content panel. */
[data-testid="stExpander"] summary {
    color: #17324a !important;
    font-weight: 700 !important;
}

[data-testid="stExpander"] summary svg {
    fill: #17324a !important;
    color: #17324a !important;
}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #17324a !important;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .workflow-row {
        justify-content: flex-start;
    }
}

/* =========================================================
   Frozen control plane: Excel-like panes
   ========================================================= */

:root {
    --control-width: 196px;
    --topbar-height: 58px;
}

[data-testid="stHeader"] {
    display: none !important;
}

.block-container {
    max-width: none !important;
    padding: 0 !important;
}

.control-sidebar {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    bottom: 0;
    width: var(--control-width);
    padding: 1.05rem .9rem;
    background:
        radial-gradient(circle at 20% 0%, rgba(32, 200, 255, .09), transparent 18rem),
        linear-gradient(180deg, #061523 0%, #04101c 100%);
    border-right: 1px solid rgba(47, 184, 255, .18);
    box-shadow: 10px 0 28px rgba(0, 0, 0, .14);
}

.control-brand {
    color: #f5f9ff;
    font-size: .83rem;
    line-height: 1.08;
    font-weight: 850;
    letter-spacing: -.015em;
}

.control-brand .accent {
    color: #43cfff;
}

.control-subtitle {
    color: #6f879c;
    font-size: .58rem;
    line-height: 1.35;
    margin-top: .38rem;
}

.control-divider {
    height: 1px;
    background: rgba(47, 184, 255, .12);
    margin: 1rem 0;
}

.control-active {
    display: flex;
    align-items: center;
    gap: .42rem;
    color: #bdf8e4;
    font-size: .64rem;
    font-weight: 800;
    letter-spacing: .08em;
}

.pulse-dot {
    width: .48rem;
    height: .48rem;
    border-radius: 999px;
    background: #26d99a;
    box-shadow: 0 0 0 rgba(38, 217, 154, .42);
    animation: pulse 1.6s infinite;
}

@keyframes pulse {
    0%   { box-shadow: 0 0 0 0 rgba(38, 217, 154, .38); opacity: .72; }
    50%  { box-shadow: 0 0 0 7px rgba(38, 217, 154, 0); opacity: 1; }
    100% { box-shadow: 0 0 0 0 rgba(38, 217, 154, 0); opacity: .72; }
}

.control-phase {
    color: #f5f9ff;
    font-size: 1rem;
    font-weight: 820;
    margin-top: 1rem;
}

.control-copy {
    color: #8ea5b9;
    font-size: .68rem;
    line-height: 1.45;
    margin-top: .38rem;
    min-height: 2.9rem;
}

.heartbeat {
    display: flex;
    align-items: center;
    gap: .28rem;
    margin-top: .9rem;
    height: .8rem;
}

.heartbeat span {
    width: .27rem;
    height: .27rem;
    border-radius: 999px;
    background: #31536b;
    animation: heartbeat-dot 2.4s infinite ease-in-out;
}

.heartbeat span:nth-child(2) { animation-delay: .30s; }
.heartbeat span:nth-child(3) { animation-delay: .60s; }
.heartbeat span:nth-child(4) { animation-delay: .90s; }
.heartbeat span:nth-child(5) { animation-delay: 1.20s; }
.heartbeat span:nth-child(6) { animation-delay: 1.50s; }
.heartbeat span:nth-child(7) { animation-delay: 1.80s; }\n\n.heartbeat-idle {
    opacity: .28;
}

.heartbeat-idle span {
    animation: none !important;
    transform: scale(.82);
    background: #31536b;
    box-shadow: none;
}


@keyframes heartbeat-dot {
    0%, 20%, 100% {
        background: #31536b;
        transform: scale(.82);
        opacity: .45;
    }
    8% {
        background: #20c8ff;
        transform: scale(1.35);
        opacity: 1;
        box-shadow: 0 0 8px rgba(32, 200, 255, .55);
    }
}

.control-time-label {
    color: #526f86;
    font-size: .55rem;
    font-weight: 800;
    letter-spacing: .13em;
    margin-top: 1rem;
}

.control-time {
    color: #dff5ff;
    font-size: 1.45rem;
    font-weight: 800;
    font-variant-numeric: tabular-nums;
    margin-top: .08rem;
}

.control-last-event {
    color: #68849a;
    font-size: .60rem;
    line-height: 1.4;
    margin-top: .9rem;
}

.workflow-topbar {
    position: fixed;
    z-index: 999;
    top: 0;
    left: var(--control-width);
    right: 0;
    height: var(--topbar-height);
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(3, 14, 25, .97);
    border-bottom: 1px solid rgba(47, 184, 255, .17);
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 22px rgba(0, 0, 0, .12);
}

.workflow-topbar .workflow-row {
    flex-wrap: nowrap;
    gap: .25rem;
}

.workflow-topbar .stage {
    padding: .36rem .48rem;
    font-size: .61rem;
    border-radius: 8px;
}

.workflow-topbar .arrow {
    font-size: .66rem;
}

.workspace-shell {
    margin-left: var(--control-width);
    padding: calc(var(--topbar-height) + 1.15rem) 1.6rem 4rem;
    min-height: 100vh;
}

.workspace-intro {
    margin-bottom: .8rem;
}

.workspace-kicker {
    color: #5d91b0;
    font-size: .59rem;
    font-weight: 800;
    letter-spacing: .14em;
}

.workspace-title {
    color: #f5f9ff;
    font-size: 1.12rem;
    font-weight: 800;
    margin-top: .22rem;
}

.workspace-copy {
    color: #7890a5;
    font-size: .72rem;
    margin-top: .18rem;
}

/* Expander header contrast when Streamlit renders a light summary bar. */
[data-testid="stExpander"] summary {
    color: #17324a !important;
    font-weight: 700 !important;
}

[data-testid="stExpander"] summary svg,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #17324a !important;
    fill: #17324a !important;
}

@media (max-width: 900px) {
    :root {
        --control-width: 156px;
    }

    .control-sidebar {
        padding: .85rem .7rem;
    }

    .workflow-topbar {
        overflow-x: auto;
        justify-content: flex-start;
        padding: 0 .55rem;
    }

    .workspace-shell {
        padding-left: .9rem;
        padding-right: .9rem;
    }
}


[data-testid="stTextArea"] textarea {
    background: rgba(7, 22, 39, .92) !important;
    color: #eaf3fb !important;
    border: 1px solid rgba(47, 184, 255, .22) !important;
}

[data-testid="stTextArea"] textarea::placeholder {
    color: #637d92 !important;
}


/* Native Streamlit document is the scrollable workspace. */
[data-testid="stAppViewContainer"] .block-container {
    padding-top: calc(var(--topbar-height) + 1rem) !important;
    padding-right: 1.35rem !important;
    padding-bottom: 3rem !important;
    padding-left: calc(var(--control-width) + 1.35rem) !important;
    max-width: none !important;
}

/* Fixed overlays must not consume document height. */
.element-container:has(.control-sidebar),
.element-container:has(.workflow-topbar),
.element-container:has(.workspace-anchor) {
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: visible !important;
}

.workspace-anchor { display: none; }


.control-copy {
    transition: opacity .18s ease;
}

.control-time {
    min-width: 5.5rem;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Helpers
# =========================================================


def render_html(markup: str) -> None:
    st.markdown(
        textwrap.dedent(markup).strip(),
        unsafe_allow_html=True,
    )


def safe_text(value: Any, default: str = "—") -> str:
    if value is None:
        return default
    return html.escape(str(value))


def serialize(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "value"):
        return value.value
    return value


def get_field(value: Any, field: str, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)


def reset_run() -> None:
    st.session_state.workflow = build_scout_opportunity_workflow()
    st.session_state.thread_id = f"frontend-{uuid.uuid4()}"
    st.session_state.result = None
    st.session_state.interrupt_payload = None
    st.session_state.selected_perspective_id = None
    st.session_state.started_at = None
    st.session_state.finished_at = None
    st.session_state.phase = "ready"
    st.session_state.error = None
    st.session_state.human_guidance = ""
    st.session_state.worker = None
    st.session_state.worker_shared = None
    st.session_state.worker_done = False
    st.session_state.worker_interrupt = None
    st.session_state.worker_error = None
    st.session_state.worker_traceback = None
    st.session_state.worker_last_node = None
    st.session_state.worker_events = []
    st.session_state.agent_state = {}
    st.session_state.operational_events = []
    st.session_state.current_action = None


def elapsed_seconds() -> float | None:
    started_at = st.session_state.started_at
    if started_at is None:
        return None
    end = st.session_state.finished_at or time.perf_counter()
    return max(end - started_at, 0.0)


def format_elapsed(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    minutes = int(seconds // 60)
    remaining = int(seconds % 60)
    return f"{minutes:02d}:{remaining:02d}"


def stage_status(stage: str) -> str:
    phase = st.session_state.phase
    order = [item[0] for item in STAGES]

    if phase == "ready":
        return "waiting"

    if phase == "human":
        human_index = order.index("human")
        stage_index = order.index(stage)
        if stage_index < human_index:
            return "completed"
        if stage == "human":
            return "human"
        return "waiting"

    if phase == "complete":
        return "completed"

    if phase == "error":
        return "waiting"

    if phase in order:
        current_index = order.index(phase)
        stage_index = order.index(stage)
        if stage_index < current_index:
            return "completed"
        if stage_index == current_index:
            return "running"

    return "waiting"


# =========================================================
# Presentation
# =========================================================


def render_architecture(container=None) -> None:
    pieces: list[str] = []

    for index, (key, label) in enumerate(STAGES):
        status = stage_status(key)
        symbol = {
            "completed": "✓",
            "running": "●",
            "human": "◉",
            "waiting": "○",
        }[status]

        pieces.append(
            f'<div class="stage {status}">'
            f'<span>{symbol}</span>'
            f'<span>{safe_text(label)}</span>'
            f'</div>'
        )

        if index < len(STAGES) - 1:
            pieces.append('<span class="arrow">→</span>')

    markup = (
        '<div class="workflow-topbar">'
        f'<div class="workflow-row">{"".join(pieces)}</div>'
        '</div>'
    )

    target = container if container is not None else st
    target.markdown(markup, unsafe_allow_html=True)


def contextual_activity_text(phase: str) -> str:
    messages = {
        "discovery": [
            "Scanning current discussions...",
            "Exploring contribution opportunities...",
            "Checking candidate signals...",
            "Continuing discovery...",
        ],
        "opportunity": [
            "Evaluating relevance...",
            "Checking positioning fit...",
            "Assessing contribution potential...",
            "Consolidating opportunity signals...",
        ],
        "research": [
            "Gathering evidence...",
            "Reviewing sources...",
            "Connecting evidence and counterpoints...",
            "Checking unresolved questions...",
        ],
        "argument": [
            "Structuring the central thesis...",
            "Mapping tensions and uncertainties...",
            "Connecting evidence to contribution areas...",
            "Building the argument brief...",
        ],
        "perspectives": [
            "Expanding intellectual directions...",
            "Testing distinct angles...",
            "Separating materially different perspectives...",
            "Preparing human choices...",
        ],
        "writer": [
            "Materializing the selected direction...",
            "Applying Rodrigo Voice...",
            "Shaping the final contribution...",
            "Preparing the draft...",
        ],
        "evaluation": [
            "Checking factual accuracy...",
            "Checking relevance...",
            "Checking voice alignment...",
            "Preparing the quality decision...",
        ],
    }

    options = messages.get(phase)
    if not options:
        return ""

    # Rotate every 4 seconds using elapsed workflow time.
    index = int(elapsed_seconds() // 4) % len(options)
    return options[index]


def render_state_panel(container=None) -> None:
    states = {
        "ready": ("READY", "Start a discovery run when you are ready."),
        "discovery": ("DISCOVERY", "Scanning for a strong contribution opportunity."),
        "opportunity": ("OPPORTUNITY", "Evaluating relevance, positioning and contribution potential."),
        "research": ("RESEARCH", "Gathering evidence, counterpoints and unresolved questions."),
        "argument": ("ARGUMENT", "Turning evidence into a defensible argument structure."),
        "perspectives": ("PERSPECTIVES", "Expanding the argument into distinct intellectual directions."),
        "human": ("HUMAN DECISION", "Choose the intellectual direction the system should materialize."),
        "writer": ("WRITER", "Materializing the selected perspective in Rodrigo Voice."),
        "evaluation": ("EVALUATION", "Checking factual accuracy, relevance and voice alignment."),
        "complete": ("HUMAN REVIEW", "Workflow complete. Final publication remains your decision."),
        "no_candidate": ("NO CANDIDATE", "Discovery completed without a suitable opportunity."),
        "error": ("INTERRUPTED", "The workflow ended with an unexpected error."),
    }

    phase = st.session_state.phase
    title, copy = states.get(phase, states["ready"])
    running = phase in {
        "discovery", "opportunity", "research", "argument",
        "perspectives", "writer", "evaluation",
    }

    if running:
        current_action = st.session_state.get("current_action")
        agent_state = st.session_state.get("agent_state") or {}
        live_status = agent_state.get("status")
        if current_action:
            copy = f"Current action · {current_action}"
        elif live_status:
            copy = f"Agent state · {live_status}"

    last_node = st.session_state.get("worker_last_node")
    operational_events = st.session_state.get("operational_events") or []
    if operational_events:
        event_name = operational_events[-1].get("event", "").replace("_", " ").title()
        last_event = f"Last event · {event_name}"
    else:
        last_event = (
            f"Last completed · {last_node.replace('_', ' ').title()}"
            if last_node else "Waiting for the first runtime event."
        )
    active_label = (
        "SYSTEM ACTIVE" if running else
        "HUMAN REQUIRED" if phase == "human" else
        "READY FOR REVIEW" if phase == "complete" else
        "RUN COMPLETE" if phase == "no_candidate" else
        "SYSTEM READY" if phase == "ready" else
        "SYSTEM INTERRUPTED"
    )
    heartbeat_class = "heartbeat" if running else "heartbeat heartbeat-idle"

    markup = (
        '<div class="control-sidebar">'
        '<div class="control-brand">MY LINKEDIN<br><span class="accent">AGENTIC AI SYSTEM</span></div>'
        '<div class="control-subtitle">Human-Centered<br>Conversation Intelligence</div>'
        '<div class="control-divider"></div>'
        '<div class="control-active"><span class="pulse-dot"></span>'
        f'<span>{safe_text(active_label)}</span></div>'
        f'<div class="control-phase">{safe_text(title)}</div>'
        f'<div class="control-copy">{safe_text(copy)}</div>'
        f'<div class="{heartbeat_class}">'
        '<span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>'
        '<div class="control-time-label">ELAPSED</div>'
        f'<div class="control-time">{format_elapsed(elapsed_seconds())}</div>'
        '<div class="control-divider"></div>'
        f'<div class="control-last-event">{safe_text(last_event)}</div>'
        '</div>'
    )
    target = container if container is not None else st
    target.markdown(markup, unsafe_allow_html=True)


def render_live_agent_state() -> None:
    if st.session_state.phase != "discovery":
        return

    state = st.session_state.get("agent_state") or {}
    if not state:
        return

    status = state.get("status", "—")
    searches = state.get("searches", 0)
    max_searches = state.get("max_searches", 8)
    read_attempts = state.get("read_attempts", 0)
    max_reads = state.get("max_reads", 8)
    successful_reads = state.get("successful_reads", 0)
    blocked_reads = state.get("blocked_reads", 0)
    sources_discovered = state.get("sources_discovered", 0)
    already_seen = state.get("already_seen", 0)
    candidates = state.get("candidates", 0)
    search_strategy = state.get("search_strategy", "default")
    current_action = st.session_state.get("current_action") or "—"

    st.markdown("### Scout State")
    render_html(
        f"""
        <div class="artifact-card">
            <div class="card-kicker">LIVE DOMAIN STATE</div>
            <div class="card-title">{safe_text(status)}</div>
            <div class="card-copy">
                Current action · <strong>{safe_text(current_action)}</strong><br>
                Searches · <strong>{safe_text(searches)} / {safe_text(max_searches)}</strong><br>
                Reads · <strong>{safe_text(read_attempts)} / {safe_text(max_reads)}</strong><br>
                Successful reads · <strong>{safe_text(successful_reads)}</strong><br>
                Blocked reads · <strong>{safe_text(blocked_reads)}</strong><br>
                Sources discovered · <strong>{safe_text(sources_discovered)}</strong><br>
                Already seen · <strong>{safe_text(already_seen)}</strong><br>
                Candidates · <strong>{safe_text(candidates)}</strong><br>
                Strategy · <strong>{safe_text(search_strategy)}</strong>
            </div>
        </div>
        """
    )

    events = st.session_state.get("operational_events") or []
    if events:
        st.markdown("#### Recent Runtime Events")
        for item in events[-5:]:
            event = item.get("event", "").replace("_", " ").title()
            timestamp = item.get("timestamp") or ""
            details = item.get("details") or {}
            detail = ""
            if "results" in details:
                detail = f" · {details['results']} results"
            elif "novel" in details and "total" in details:
                detail = f" · {details['novel']}/{details['total']} novel"
            elif "error" in details:
                detail = f" · {details['error']}"
            elif "action" in details:
                detail = f" · {details['action']}"
            st.caption(f"{timestamp} · {event}{detail}")

def render_opportunity() -> None:
    result = st.session_state.result
    if not result:
        return

    post = result.get("post")
    opportunity = result.get("opportunity_evaluation")
    if post is None or opportunity is None:
        return

    title = (
        get_field(post, "title", None)
        or get_field(post, "content", "Selected opportunity")
    )
    source_url = get_field(post, "url", None)

    score = get_field(opportunity, "opportunity_score", "—")
    classification = get_field(opportunity, "classification", "—")
    topic = get_field(opportunity, "topic_relevance", "—")
    positioning = get_field(opportunity, "positioning_fit", "—")
    contribution = get_field(opportunity, "contribution_potential", "—")
    research_efficiency = get_field(opportunity, "research_efficiency", "—")

    st.markdown("#### Opportunity")
    left, right = st.columns([2.4, 1])

    with left:
        render_html(
            f"""
            <div class="artifact-card">
                <div class="card-kicker">SELECTED CONTENT</div>
                <div class="card-title">{safe_text(title)}</div>
                <div class="card-copy">
                    The Scout selected this candidate for opportunity evaluation.
                </div>
            </div>
            """
        )
        if source_url:
            st.link_button("View source", str(source_url))

    with right:
        render_html(
            f"""
            <div class="artifact-card">
                <div class="card-kicker">OPPORTUNITY SCORE</div>
                <div class="score">{safe_text(score)}</div>
                <div class="classification">{safe_text(classification)}</div>
                <div class="card-copy">
                    Topic relevance · {safe_text(topic)}<br>
                    Positioning fit · {safe_text(positioning)}<br>
                    Contribution · {safe_text(contribution)}<br>
                    Research efficiency · {safe_text(research_efficiency)}
                </div>
            </div>
            """
        )


def render_argument_brief() -> None:
    result = st.session_state.result
    if not result:
        return

    argument = result.get("argument_brief")
    if argument is None:
        return

    thesis = (
        get_field(argument, "thesis", None)
        or get_field(argument, "core_thesis", None)
    )

    st.markdown("#### Argument Intelligence")

    if thesis:
        render_html(
            f"""
            <div class="artifact-card">
                <div class="card-kicker">ARGUMENT BRIEF</div>
                <div class="card-title">Core thesis</div>
                <div class="card-copy">{safe_text(thesis)}</div>
            </div>
            """
        )

    with st.expander("View complete Argument Brief"):
        st.json(serialize(argument))


def render_perspective_selection() -> None:
    payload = st.session_state.interrupt_payload or {}
    perspectives = payload.get("perspectives", [])

    if not perspectives:
        st.warning("No perspectives were returned by the workflow.")
        return

    render_html(
        """
        <div style="text-align:center; margin:1.4rem 0 1.1rem 0;">
            <div class="eyebrow">AI EXPANDS</div>
            <div style="color:#f5f9ff;font-size:1.35rem;font-weight:800;">
                Choose the intellectual direction
            </div>
            <div style="color:#8294aa;font-size:.82rem;margin-top:.35rem;">
                The system generated materially different, defensible perspectives.
            </div>
        </div>
        """
    )

    cols = st.columns(2)

    for index, perspective in enumerate(perspectives):
        perspective_id = str(perspective.get("perspective_id", ""))
        label = perspective.get("label", perspective_id)
        core = perspective.get("core_argument", "")
        why = perspective.get("why_it_matters", "")
        contribution = perspective.get("contribution", "")
        counterargument = perspective.get("counterargument")
        uncertainty = perspective.get("uncertainty")

        with cols[index % 2]:
            render_html(
                f"""
                <div class="perspective-card">
                    <div class="perspective-number">PERSPECTIVE {index + 1:02d}</div>
                    <div class="perspective-title">{safe_text(label)}</div>
                    <div class="perspective-label">CORE ARGUMENT</div>
                    <div class="perspective-copy">{safe_text(core)}</div>
                    <div class="perspective-label">WHY IT MATTERS</div>
                    <div class="perspective-copy">{safe_text(why)}</div>
                    <div class="perspective-label">CONTRIBUTION</div>
                    <div class="perspective-copy">{safe_text(contribution)}</div>
                </div>
                """
            )

            with st.expander("Counterargument & uncertainty"):
                if counterargument:
                    st.markdown(f"**Counterargument**  \n{counterargument}")
                if uncertainty:
                    st.markdown(f"**Uncertainty**  \n{uncertainty}")
                if not counterargument and not uncertainty:
                    st.caption("No additional caveat was provided.")

            selected = (
                st.session_state.selected_perspective_id == perspective_id
            )

            if st.button(
                "✓ Selected" if selected else f"Select perspective {index + 1}",
                key=f"select_{perspective_id}_{index}",
                use_container_width=True,
            ):
                st.session_state.selected_perspective_id = perspective_id
                st.rerun()

    selected_id = st.session_state.selected_perspective_id
    if not selected_id:
        return

    selected = next(
        (
            item
            for item in perspectives
            if str(item.get("perspective_id", "")) == selected_id
        ),
        None,
    )
    if selected is None:
        return

    st.markdown("---")
    st.markdown("### Human converges")
    st.success(
        f"Selected perspective: {selected.get('label', selected_id)}"
    )

    guidance = st.text_area(
        "Optional human guidance",
        placeholder="Add emphasis or direction...",
        key="human_guidance",
    )

    if st.button(
        "Continue with perspective",
        type="primary",
        use_container_width=True,
    ):
        resume_workflow(
            perspective_id=selected_id,
            human_guidance=guidance.strip() or None,
        )
        st.rerun()


def render_final_result() -> None:
    result = st.session_state.result
    if not result:
        return

    draft = result.get("current_draft")
    quality = result.get("quality_evaluation")
    selected = result.get("selected_perspective")
    if not draft:
        return

    st.markdown("## Human Review")

    selected_perspective = get_field(selected, "perspective", None)
    selected_label = (
        get_field(selected_perspective, "label", None)
        or get_field(selected, "label", None)
    )

    if selected_label:
        st.caption(f"Selected direction · {selected_label}")

    left, right = st.columns([1.65, 1])

    with left:
        st.markdown("#### Final Draft")
        render_html(
            f'<div class="final-draft">{safe_text(draft)}</div>'
        )

    with right:
        st.markdown("#### Quality Evaluation")
        factual = get_field(quality, "factual_accuracy", "—")
        relevance = get_field(quality, "relevance", "—")
        voice = get_field(quality, "voice_match", "—")
        decision = get_field(quality, "decision", "—")
        iteration = result.get("iteration", "—")

        render_html(
            f"""
            <div class="quality-card">
                <div class="card-kicker">QUALITY GATE</div>
                <div class="card-copy">
                    Factual accuracy · <strong>{safe_text(factual)}</strong><br><br>
                    Relevance · <strong>{safe_text(relevance)}</strong><br><br>
                    Voice match · <strong>{safe_text(voice)}</strong><br><br>
                    Decision · <strong>{safe_text(decision)}</strong><br><br>
                    Iterations · <strong>{safe_text(iteration)}</strong>
                </div>
            </div>
            """
        )

    render_html(
        """
        <div class="principle">
            <strong>AI EXPANDS</strong>
            &nbsp;→&nbsp;
            <strong>HUMAN CONVERGES</strong>
            &nbsp;→&nbsp;
            <strong>AI MATERIALIZES</strong>
            &nbsp;→&nbsp;
            <strong>HUMAN OWNS</strong>
            <br><br>
            Final publication remains a human decision.
        </div>
        """
    )

    if st.button("New run", use_container_width=True):
        reset_run()
        st.rerun()


def render_system_activity() -> None:
    # Superseded by real-time agent state in the workspace.
    return


# =========================================================
# Background execution
# =========================================================


NODE_TO_NEXT_PHASE = {
    "scout": "opportunity",
    "opportunity_evaluator": "research",
    "accepted_for_research": "research",
    "research": "argument",
    "argument_intelligence": "perspectives",
    "perspective_generation": "human",
    "human_perspective_selection": "writer",
    "writer": "evaluation",
    "evaluator": "complete",
}


def _make_scout_observer(shared: dict[str, Any], lock: threading.Lock):
    def observer(event: str, payload: dict[str, Any]) -> None:
        details = payload.get("details") or {}
        state = payload.get("state") or {}

        action_map = {
            "llm_decision_started": "LLM DECISION",
            "search_started": "SEARCH",
            "read_started": "READ",
            "candidate_selected": "SELECT",
            "finish": "FINISH",
        }

        with lock:
            shared["agent_state"] = dict(state)
            if event in action_map:
                shared["current_action"] = action_map[event]

            shared["operational_events"].append({
                "event": event,
                "timestamp": payload.get("timestamp"),
                "details": dict(details),
            })
            shared["operational_events"] = shared["operational_events"][-20:]

    return observer


def _background_graph_run(
    workflow,
    graph_input: Any,
    config: dict[str, Any],
    shared: dict[str, Any],
    lock: threading.Lock,
) -> None:
    accumulated = dict(shared.get("result") or {})
    started = time.perf_counter()
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")
    _workflow_log(f"START | thread_id={thread_id} | input={type(graph_input).__name__}")

    observer_token = set_scout_observer(_make_scout_observer(shared, lock))
    try:
        stream = workflow.stream(graph_input, config=config, stream_mode="updates")
        _workflow_log("STREAM OPEN")
        chunk_index = 0

        for chunk in stream:
            chunk_index += 1
            _workflow_log(
                f"CHUNK {chunk_index} | keys="
                f"{list(chunk.keys()) if isinstance(chunk, dict) else type(chunk).__name__}"
            )

            if not isinstance(chunk, dict):
                continue

            if "__interrupt__" in chunk:
                interrupts = chunk.get("__interrupt__") or ()
                payload = interrupts[0].value if interrupts else None
                _workflow_log(
                    "INTERRUPT | type="
                    + (str(payload.get("type")) if isinstance(payload, dict) else type(payload).__name__)
                )
                with lock:
                    shared["interrupt"] = payload
                    shared["done"] = True
                    shared["last_node"] = "human_perspective_selection"
                    shared["events"].append("human_perspective_selection")
                return

            for node_name, update in chunk.items():
                if isinstance(update, dict):
                    accumulated.update(update)
                with lock:
                    shared["result"] = dict(accumulated)
                    shared["last_node"] = node_name
                    shared["events"].append(node_name)
                _workflow_log(
                    f"NODE COMPLETE | {node_name} | elapsed={time.perf_counter()-started:.1f}s"
                )

        _workflow_log("STREAM EXHAUSTED")

        try:
            snapshot = workflow.get_state(config)
            values = getattr(snapshot, "values", None)
            if isinstance(values, dict):
                accumulated.update(values)
            _workflow_log(
                "STATE SNAPSHOT | keys="
                + (str(list(values.keys())) if isinstance(values, dict) else "unavailable")
            )
        except Exception as snapshot_exc:
            _workflow_log(
                f"STATE SNAPSHOT ERROR | {type(snapshot_exc).__name__}: {snapshot_exc}"
            )

        with lock:
            shared["result"] = dict(accumulated)
            shared["done"] = True

        _workflow_log(
            f"COMPLETE | chunks={chunk_index} | elapsed={time.perf_counter()-started:.1f}s"
        )

    except BaseException as exc:
        error_text = f"{type(exc).__name__}: {exc}"
        trace = traceback.format_exc()
        with lock:
            shared["error"] = error_text
            shared["traceback"] = trace
            shared["done"] = True
        _workflow_log(f"ERROR | {error_text}")
        print(trace, flush=True)

    finally:
        reset_scout_observer(observer_token)


def _new_shared_state() -> dict[str, Any]:
    return {
        "lock": threading.Lock(),
        "result": dict(st.session_state.result or {}),
        "interrupt": None,
        "error": None,
        "traceback": None,
        "done": False,
        "last_node": None,
        "events": [],
        "agent_state": {},
        "operational_events": [],
        "current_action": None,
        "started_monotonic": time.perf_counter(),
    }


def launch_background_run(graph_input: Any) -> None:
    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
        }
    }

    shared = _new_shared_state()
    workflow = st.session_state.workflow
    lock = shared["lock"]

    worker = threading.Thread(
        target=_background_graph_run,
        args=(workflow, graph_input, config, shared, lock),
        daemon=True,
        name=f"linkedin-agentic-{st.session_state.thread_id}",
    )

    st.session_state.worker_shared = shared
    st.session_state.worker = worker
    _workflow_log(f"THREAD LAUNCH | name={worker.name} | thread_id={st.session_state.thread_id}")
    worker.start()


def sync_background_state() -> None:
    shared = st.session_state.get("worker_shared")
    if not shared:
        return

    lock = shared["lock"]
    with lock:
        result = dict(shared.get("result") or {})
        interrupt_payload = shared.get("interrupt")
        error = shared.get("error")
        worker_traceback = shared.get("traceback")
        done = bool(shared.get("done"))
        last_node = shared.get("last_node")
        events = list(shared.get("events") or [])
        agent_state = dict(shared.get("agent_state") or {})
        operational_events = list(shared.get("operational_events") or [])
        current_action = shared.get("current_action")

    st.session_state.result = result
    st.session_state.worker_interrupt = interrupt_payload
    st.session_state.worker_error = error
    st.session_state.worker_done = done
    st.session_state.worker_last_node = last_node
    st.session_state.worker_events = events
    st.session_state.agent_state = agent_state
    st.session_state.operational_events = operational_events
    st.session_state.current_action = current_action

    worker = st.session_state.get("worker")
    worker_stopped_unexpectedly = (
        worker is not None
        and not worker.is_alive()
        and not done
        and interrupt_payload is None
        and error is None
    )

    if worker_stopped_unexpectedly:
        error = (
            "Background workflow worker stopped unexpectedly before reaching "
            "a terminal state or human interrupt."
        )
        st.session_state.worker_error = error

    if error:
        st.session_state.error = error
        st.session_state.worker_traceback = worker_traceback
        st.session_state.finished_at = time.perf_counter()
        st.session_state.phase = "error"
        return

    if interrupt_payload is not None:
        if interrupt_payload.get("type") != "perspective_selection":
            st.session_state.error = (
                f"Unexpected workflow interrupt: {interrupt_payload}"
            )
            st.session_state.finished_at = time.perf_counter()
            st.session_state.phase = "error"
            return

        st.session_state.interrupt_payload = interrupt_payload
        st.session_state.phase = "human"
        return

    if last_node:
        next_phase = NODE_TO_NEXT_PHASE.get(last_node)
        if next_phase:
            st.session_state.phase = next_phase

    if done:
        st.session_state.finished_at = time.perf_counter()

        status = result.get("status")
        post = result.get("post")
        draft = result.get("current_draft")

        if status == "NO_CANDIDATE_FOUND" or (
            post is None and last_node == "scout"
        ):
            st.session_state.phase = "no_candidate"
        elif draft:
            st.session_state.phase = "complete"
        elif st.session_state.phase not in {"human", "error"}:
            # A terminal graph state that is neither HITL nor a final draft
            # should not masquerade as an active workflow.
            st.session_state.phase = "complete"

def _workflow_log(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [WORKFLOW] {message}", flush=True)


def start_workflow() -> None:
    _workflow_log("UI START requested")
    st.session_state.started_at = time.perf_counter()
    st.session_state.finished_at = None
    st.session_state.phase = "discovery"
    st.session_state.error = None
    st.session_state.result = {}
    st.session_state.interrupt_payload = None
    st.session_state.selected_perspective_id = None
    launch_background_run({"scout_objective": SCOUT_OBJECTIVE})


def resume_workflow(
    *,
    perspective_id: str,
    human_guidance: str | None,
) -> None:
    _workflow_log(f"UI RESUME requested | perspective_id={perspective_id}")
    st.session_state.phase = "writer"
    st.session_state.worker = None
    st.session_state.worker_done = False
    st.session_state.worker_interrupt = None
    st.session_state.worker_error = None
    st.session_state.worker_traceback = None
    st.session_state.worker_last_node = None
    st.session_state.worker_events = []

    decision = {
        "perspective_id": perspective_id,
        "human_guidance": human_guidance,
    }
    launch_background_run(Command(resume=decision))


def render_live_activity() -> None:
    # Activity is permanently visible in the frozen control sidebar.
    return


def schedule_ui_refresh() -> None:
    """
    Refresh the UI while the logical workflow is active.

    Important: refresh is intentionally NOT gated by Thread.is_alive().
    The browser must keep receiving fresh elapsed time and worker state
    until the workflow reaches a terminal, human-interrupt, or error state.
    """
    active_phases = {
        "discovery",
        "opportunity",
        "research",
        "argument",
        "perspectives",
        "writer",
        "evaluation",
    }

    if st.session_state.phase not in active_phases:
        return

    time.sleep(1.0)
    st.rerun()


# =========================================================
# Session
# =========================================================

if "workflow" not in st.session_state:
    reset_run()


# =========================================================
# Page
# =========================================================

# Pull background-thread state into Streamlit session state before
# any UI element is rendered. This is the authoritative UI sync point.
sync_background_state()

render_html(
    """
    <div class="workspace-anchor"></div>
    """
)


render_architecture()
render_state_panel()
render_live_activity()

phase = st.session_state.phase

if phase == "ready":
    render_html(
        """
        <div class="artifact-card">
            <div class="card-kicker">HUMAN-CENTERED WORKFLOW</div>
            <div class="card-title">AI expands. Human converges.</div>
            <div class="card-copy">
                Start a real discovery run. The system will search for an
                opportunity, evaluate it, research the topic, build an argument
                and generate multiple perspectives before asking for human direction.
            </div>
        </div>
        """
    )

    if st.button(
        "Start workflow",
        type="primary",
        use_container_width=True,
    ):
        start_workflow()
        st.rerun()

elif phase == "human":
    render_opportunity()
    render_argument_brief()
    render_perspective_selection()

elif phase == "complete":
    render_opportunity()
    render_argument_brief()
    render_final_result()

elif phase == "no_candidate":
    render_html(
        """
        <div class="artifact-card">
            <div class="card-kicker">DISCOVERY COMPLETE</div>
            <div class="card-title">No candidate found</div>
            <div class="card-copy">
                The Scout completed its bounded discovery run without selecting
                a suitable opportunity. No downstream research or writing was executed.
            </div>
        </div>
        """
    )

    if st.button(
        "New discovery run",
        type="primary",
        use_container_width=True,
    ):
        reset_run()
        st.rerun()

elif phase == "error":
    st.error(st.session_state.error or "Unexpected workflow error.")

    worker_traceback = st.session_state.get("worker_traceback")
    if worker_traceback:
        with st.expander("Technical traceback", expanded=False):
            st.code(worker_traceback, language="text")

    if st.button("Reset workflow", use_container_width=True):
        reset_run()
        st.rerun()

else:
    render_live_agent_state()
    render_opportunity()

schedule_ui_refresh()
