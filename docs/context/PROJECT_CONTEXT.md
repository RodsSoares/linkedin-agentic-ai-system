Project Context

Purpose

This file is the operational recovery checkpoint for the My LinkedIn
Agentic AI System.

It exists to answer:

Where is the project now, what has been validated, what is currently
being worked on, and what should happen next?

It is intentionally not a complete architecture specification and
should not duplicate the historical development record.

Use the documentation set as follows:

-   01_system_overview.md --- product model, architectural principles,
    target MVP architecture, responsibility boundaries, and deployed
    architecture at overview level.
-   02_current_architecture.md --- factual view of what is implemented
    now and how the current components are connected.
-   03_data_model.md --- typed contracts, state boundaries, and
    persistence data responsibilities.
-   04_decision_log.md --- architectural rationale and durable
    decisions.
-   05_cloud_deployment.md --- implemented cloud topology, runtime
    configuration, persistence architecture, and deployment constraints.
-   06_opportunity_evaluation.md --- Opportunity Evaluation product
    rationale, scoring contract, deterministic guardrails, and routing.
-   PROJECT_CONTEXT.md --- current recovery checkpoint and immediate
    development context.

When architecture and this checkpoint differ,
02_current_architecture.md is authoritative for implemented topology.

Current Checkpoint

Current development stage:

Human-Centered MVP + Experience Layer + Cloud Deployment

Status:

COMPLETE AND VALIDATED FOR CURRENT PORTFOLIO/MVP SCOPE

Current automated regression baseline:

437 passing tests

Current public runtime:

Render Free Web Service

Current cloud persistence:

Supabase PostgreSQL

Current frontend:

Streamlit

Current orchestration:

LangGraph

Current real web mode:

Brave Search + bounded HTTP reader

Current publication model:

Manual / human-only

Current completed Experience Layer increments:

-   7.1 --- Editable Theme / Intent
-   7.2 --- Content Mode Selection
-   7.3 --- Final Human Refinement
-   7.4 --- Bilingual Presentation
-   7.5 --- Run History / Product Memory

All five Experience Layer increments are implemented and validated.

The previous COMPLETE -\> Run History terminal-state persistence gate is
closed.

Cloud deployment has also been implemented and smoke validated without
reopening the validated reasoning architecture.

Product Goal

Build a controlled, human-centered agentic AI system that helps Rodrigo
identify strategically relevant professional conversations, determine
whether they are worth pursuing, gather defensible evidence, expand that
evidence into multiple intellectual directions, let the human choose the
direction worth owning, and materialize that direction into professional
content.

The system is not an autonomous social-media engagement bot.

Publication remains human-only.

Core product principle:

AI expands → Human converges → AI materializes → Human owns.

A second established principle remains:

Opportunity != Popularity

The system should prioritize opportunities where Rodrigo can make a
relevant, differentiated, professionally valuable, and defensible
contribution rather than simply selecting popular content.

Current Implemented Workflow

The current primary LangGraph flow is:

Human Theme / Intent
\|
v
Discovery / Scout
\|
v
Target Qualification
\|
v
Opportunity Evaluation
\|
+-- LOW ------------------------------\> END
\|
+-- MEDIUM --\> QUEUED ----------------\> END
\|
+-- HIGH
\|
v
Research
\|
v
ResearchBrief
\|
v
Argument Intelligence
\|
v
ArgumentBrief
\|
v
Perspective Generation
\|
v
PerspectiveSet
\|
v
Human Perspective Selection
\|
v
SelectedPerspective
\|
v
Human Content Mode Selection
\|
+-- linkedin_post
+-- linkedin_reply
+-- article
\|
v
Rodrigo Voice / Writer
\|
v
Quality Evaluator
\|
+-- PASS -----------------------------\> Human Final Refinement
\|
+-- REVISE --\> Writer --\> Quality Evaluator
\|
+-- REJECT ---------------------------\> END
\|
v
Human Final Refinement
\|
+-- ACCEPT ---------------------------\> COMPLETE
\|
+-- REFINE --\> Writer ----------------\> COMPLETE
\|
v
Optional Portuguese Translation
\|
v
Run History / Product Memory
\|
v
Manual Publication

Publication remains outside autonomous execution.

The ordinary Writer revision loop is bounded.

Ordinary Writer revision does not rerun Research, Argument Intelligence,
or Perspective Generation.

The final human REFINE path is intentionally different from ordinary
quality revision:

Human Final Refinement
-\> Writer
-\> COMPLETE

It does not automatically trigger another Quality Evaluator loop.

Current Human Decision Boundaries

HITL 1 --- Perspective Selection

The system generates multiple materially distinct and defensible
intellectual perspectives from the same evidence base.

The human chooses the intellectual direction.

Input:

PerspectiveSet

Human decision:

-   perspective_id
-   optional human_guidance

Output:

SelectedPerspective

The selected perspective is authoritative downstream context.

Writer must not silently replace it with another thesis.

HITL 2 --- Content Mode Selection

After the perspective has been selected, the human chooses how that
intellectual direction should be materialized.

Valid MVP modes:

-   linkedin_post
-   linkedin_reply
-   article

Output:

ContentMode

This decision changes expression, depth, contextual independence, and
communication behavior.

It does not change the selected intellectual position.

The same SelectedPerspective can therefore be materialized in another
supported format without rerunning the upstream reasoning pipeline.

HITL 3 --- Final Human Refinement

After Quality Evaluator returns PASS, the human retains final editorial
authority.

The human may:

-   ACCEPT the current draft;
-   REFINE with bounded editorial guidance.

Typical refinement dimensions include:

-   tone;
-   emphasis;
-   length;
-   framing;
-   closing.

The refinement must preserve the selected intellectual direction unless
the human explicitly changes it.

This boundary is separate from publication authority.

Even after ACCEPT or REFINE, publication remains manual.

Experience Layer Status

7.1 --- Editable Theme / Intent

Status: IMPLEMENTED AND VALIDATED

The Streamlit frontend allows the human to define the exploration theme.

The application converts the human input into a bounded Scout objective.

The existing Scout guardrails remain authoritative.

The capability has been exercised through real runs using different
themes.

The system is therefore no longer dependent on a single hard-coded Scout
topic.

7.2 --- Content Mode Selection

Status: IMPLEMENTED AND VALIDATED

A second LangGraph HITL boundary exists after Human Perspective Selection
and before Writer.

Supported modes:

-   LinkedIn Post
-   LinkedIn Reply
-   Article

Writer is content-mode-aware.

Quality Evaluator is content-mode-aware.

Legacy paths default to linkedin_reply for compatibility.

Automated integration coverage confirms that selecting a content mode
does not rerun:

-   Research;
-   Argument Intelligence;
-   Perspective Generation.

Real Streamlit E2E successfully exercised:

Human Perspective Selection
-\> Human Content Mode Selection
-\> Writer
-\> Quality Evaluator
-\> Human Final Refinement

7.3 --- Final Human Refinement

Status: IMPLEMENTED AND E2E VALIDATED

After Quality Evaluator returns PASS, the human can accept the current
draft or provide bounded editorial guidance for a final adjustment.

The real ACCEPT path has been validated through WORKFLOW COMPLETE.

The previous empty interrupt / stale HITL remount failure is no longer
present in the validated ACCEPT path.

The REFINE path returns to Writer for the requested final adjustment and
then completes without creating another automatic quality loop.

7.4 --- Bilingual Presentation

Status: IMPLEMENTED AND E2E VALIDATED

The internal reasoning pipeline remains English-first.

Final generated content can be translated to Portuguese on demand.

Translation is a presentation-layer capability.

It does not rerun the full reasoning pipeline and does not change the
canonical workflow reasoning state.

Portuguese translation of the final draft has been validated in the real
Streamlit experience.

7.5 --- Run History / Product Memory

Status: IMPLEMENTED AND VALIDATED

Run History is navigable from the product UI.

The current product-facing history preserves enough information to
revisit workflow results and relevant metadata.

Important persisted concepts include:

-   run identity;
-   LangGraph thread identity;
-   human theme / intent;
-   selected opportunity metadata;
-   opportunity score / classification;
-   selected perspective;
-   content mode;
-   final refinement action;
-   final draft;
-   serialized workflow state.

Run History list/detail/back navigation has been visually validated.

The earlier defect where a completed HIGH run could be stored as:

No candidate
No content generated

has been corrected.

The persistence implementation prefers authoritative terminal LangGraph
state and protects a richer completed record from later incomplete
overwrite.

The corrected path is now validated.

Run History is distinct from Interaction Memory.

Interaction Memory exists primarily to support agent behavior such as
novelty, URL canonicalization, avoiding repeated content, agentic draft
memory, and human-final interaction memory.

Run History exists so the human can revisit prior intellectual work.

Current Shared State

Important LinkedInAgentState concepts include:

scout_objective
post
opportunity_evaluation
research_result
argument_brief
perspective_set
selected_perspective
content_mode
current_draft
quality_evaluation
final_refinement_action
final_refinement_guidance
iteration
next_step
human_feedback
status

Nodes should map global state into component-specific inputs.

Specialist components should not receive the entire workflow state
unless required.

Current Responsibility Model

LLM

Owns semantic work where interpretation is required, including:

-   search strategy;
-   source selection;
-   semantic opportunity signals;
-   research decisions;
-   evidence interpretation;
-   synthesis;
-   argument construction;
-   perspective generation;
-   drafting;
-   semantic quality assessment;
-   explicit translation requests.

Python

Owns deterministic governance, including:

-   validation;
-   scoring;
-   thresholds;
-   guardrails;
-   action authorization;
-   provenance enforcement;
-   counters;
-   operational limits;
-   context budgets;
-   factual state mutation;
-   validation of explicit human selections;
-   persistence backend selection.

LangGraph

Owns orchestration, including:

-   shared workflow state;
-   node transitions;
-   deterministic routing;
-   bounded revision paths;
-   HITL interruption/resume semantics;
-   termination.

Human

Owns:

-   intellectual convergence;
-   perspective selection;
-   content-mode selection;
-   contextual guidance;
-   final editorial judgment;
-   publication.

Persistence

Owns durable storage of state/artifacts produced under the authority
rules above.

Persistence does not acquire semantic, routing, or publication authority.

Current Core Guardrails

The following architectural behaviors should remain frozen unless a
genuine defect or explicit product decision requires change.

Scout

Bounded action vocabulary:

SEARCH
READ
SELECT
FINISH

Python authorizes requested actions.

The LLM does not control runtime limits.

Opportunity Evaluation

Current weighting:

Contribution Potential 30%
Positioning Fit 25%
Topic Relevance 20%
Engagement Potential 15%
Research Efficiency 10%

Mandatory LOW guardrails:

Contribution Potential \< 30
Positioning Fit \< 30
Topic Relevance \< 25

Otherwise:

HIGH \>= 80
MEDIUM \>= 60 and \< 80
LOW \< 60

The LLM supplies semantic signals.

Python owns final score and classification.

Research

Bounded actions:

SEARCH
READ
EXTRACT
FINISH

Evidence chain:

SEARCH
-\> READ
-\> EXTRACT
-\> EvidenceItem
-\> ResearchBrief

Search snippets and raw reads must not silently become Writer-facing
evidence.

Principal limits:

MAX_RESEARCH_STEPS = 10
MAX_RESEARCH_DECISIONS = 12
MAX_RESEARCH_SEARCHES = 3
MAX_RESEARCH_READS = 5
MAX_RESEARCH_EVIDENCE_ITEMS = 6

Context

Principal budgets:

Scout read context \<= 1800 tokens
Research per-read context \<= 2500 tokens
Research cumulative read context \<= 8000 tokens

Quality

The LLM produces semantic quality signals.

Python owns deterministic PASS / REVISE / REJECT routing.

A PASS does not authorize publication.

Rodrigo Voice and Content Modes

The current architecture separates:

SelectedPerspective = WHAT should be said

Rodrigo Voice = WHO is expressing it / core professional identity and
editorial behavior

ContentMode = HOW the selected direction is materialized

Do not create separate Rodrigo personas for Reply, Post, and Article.

Core Rodrigo Voice remains mode-neutral.

Content-mode rules determine form, depth, contextual independence, and
communication behavior.

The current Golden Set is evidence for calibration, not a mechanical
prompt specification.

Article mode currently has less direct human calibration evidence than
LinkedIn-native content.

Use Core Voice plus article structural rules rather than pretending a
separately calibrated article persona exists.

Current Frontend

Current product surface:

app/frontend/main.py

Implemented UI behavior includes:

-   Editable Theme / Intent;
-   real workflow launch;
-   live workflow progress;
-   Opportunity artifact;
-   Argument Brief;
-   Perspective Selection;
-   Content Mode Selection;
-   Writer / Evaluator continuation;
-   Final Human Refinement;
-   Portuguese translation on demand;
-   Run History list/detail/back navigation;
-   manual-publication boundary.

The frontend uses a background worker so long-running Scout and Research
execution do not freeze the interactive experience.

LangGraph checkpoint/thread state supports interrupt/resume behavior
while the active session retains its thread identity.

Current Persistence Architecture

The system now has three separate persistence responsibilities.

1.  LangGraph Checkpoint / HITL State

Purpose:

Preserve authoritative workflow execution state required by LangGraph
interrupt/resume semantics.

Local backend:

InMemorySaver

Cloud backend:

PostgresSaver

Cloud database:

Supabase PostgreSQL

Primary recovery identity:

thread_id

2.  Interaction Memory

Purpose:

Support agent behavior such as novelty, canonical URL memory,
previously visited content, agentic drafts, human-final content, and
interaction status.

Local backend:

SQLiteInteractionMemoryRepository

Cloud backend:

PostgresInteractionMemoryRepository

3.  Run History / Product Memory

Purpose:

Preserve navigable user-facing workflow history and intellectual
artifacts.

Local backend:

SQLiteRunHistoryRepository

Cloud backend:

PostgresRunHistoryRepository

The three responsibilities share Supabase PostgreSQL infrastructure in
cloud execution but remain separate application concepts.

Do not collapse:

LangGraph execution state
Interaction Memory
Run History / Product Memory

into one state model.

Persistence Backend Selection

Database configuration is explicit.

DATABASE_URL

provides PostgreSQL connection information.

PERSISTENCE_BACKEND

selects persistence behavior.

Current rule:

PERSISTENCE_BACKEND=postgres
+
DATABASE_URL configured
-\>
PostgreSQL persistence enabled

Otherwise:

local persistence remains active.

This prevents cloud credentials from silently changing local/test
behavior.

Current Cloud Deployment

Current topology:

Browser
\|
v
Render Free Web Service
\|
+--\> Streamlit frontend
+--\> LangGraph orchestration
+--\> Python deterministic governance
+--\> OpenAI API
+--\> Brave Search
+--\> bounded HTTP reader
\|
v
Supabase PostgreSQL

Current Render build command:

pip install -r requirements.txt

Current Render start command:

PYTHONPATH=. streamlit run app/frontend/main.py --server.address 0.0.0.0 --server.port \$PORT

The explicit PYTHONPATH keeps the repository root importable when
Streamlit executes app/frontend/main.py.

Current deployed environment configuration includes:

OPENAI_API_KEY
BRAVE_SEARCH_API_KEY
WEB_TOOL_MODE=real
DATABASE_URL
PERSISTENCE_BACKEND=postgres

Secret values remain outside Git and must not be copied into this file.

Supabase Connection

The deployed PostgreSQL connection uses the Supabase Session Pooler.

This was selected after direct connection testing exposed
network/DNS/IPv4 compatibility constraints in the deployment path.

The exact DATABASE_URL and credentials must remain secret.

Current Cloud Validation Snapshot

Validated in the cloud/deployment work:

-   Render build;
-   Streamlit startup;
-   repository-root package imports;
-   public application access;
-   OpenAI-backed workflow execution;
-   Brave Search real mode;
-   Supabase PostgreSQL connectivity;
-   PostgresSaver setup;
-   LangGraph checkpoint table creation;
-   checkpoint recovery from a new workflow instance using the same
    thread_id;
-   Interaction Memory PostgreSQL repository behavior;
-   Run History PostgreSQL repository behavior;
-   deployed Run History navigation;
-   Run History survival across Render process restart.

Current automated suite:

437 passing tests

The current test count is a development checkpoint, not an architectural
invariant.

Render Free Runtime Constraint

Render Free may spin down after inactivity and may introduce cold-start
latency.

The Render local filesystem is therefore not a durable cloud system of
record.

Durable cloud state belongs in Supabase PostgreSQL.

SQLite remains appropriate for local development.

HITL Restart Validation and Current Backlog

A deliberate deployed-runtime test interrupted the workflow at:

Human Perspective Selection

The service was then restarted.

Observed behavior:

PostgresSaver checkpoint
-\> survived restart

Run History
-\> survived restart

Streamlit session_state
-\> did not survive restart

Frontend
-\> returned to SYSTEM READY

Interpretation:

backend checkpoint durability is implemented and validated;

product-history durability is implemented and validated;

automatic frontend reconstruction of an interrupted HITL session is not
implemented.

This is not a PostgresSaver failure.

The missing capability is reconnecting the user-facing session to the
persisted thread_id and reconstructing the interrupt UI.

Backlog item:

Resumable HITL after session/process loss

Target behavior:

History
\|
+--\> terminal run
\| \|
\| +--\> Open / Inspect
\|
+--\> resumable HITL run
\|
+--\> Resume
\|
v
recover thread_id
\|
v
PostgresSaver checkpoint
\|
v
reconstruct interrupt/UI
\|
v
continue human decision

This item is explicitly post-MVP backlog.

It does not reopen the completed cloud-deployment milestone.

Current Validation Snapshot

Automated suite:

437 passing tests

The regression surface includes:

-   Scout;
-   Opportunity Evaluation;
-   deterministic routing;
-   Research;
-   evidence provenance;
-   web tooling;
-   context preparation;
-   Argument Intelligence;
-   Perspective Generation;
-   Human Perspective Selection;
-   SelectedPerspective-aware Writer;
-   Human Content Mode Selection;
-   all three content modes;
-   mode-aware Writer;
-   mode-aware Quality Evaluator;
-   bounded revision;
-   Final Human Refinement;
-   bilingual presentation;
-   Run History;
-   local/cloud persistence selection;
-   HITL interrupt/resume semantics;
-   upstream non-rerun guarantees.

Real Streamlit E2E has demonstrated the Human-Centered path through:

Editable Theme
-\> Scout
-\> Opportunity Evaluation HIGH
-\> Research
-\> Argument Intelligence
-\> Perspective Generation
-\> Human Perspective Selection
-\> Human Content Mode Selection
-\> Writer
-\> Quality Evaluator
-\> Human Final Refinement ACCEPT
-\> WORKFLOW COMPLETE

Portuguese translation of the final draft has been validated.

Run History list/detail/back navigation has been validated.

A separate real run demonstrated correct LOW termination before
Research.

Cloud persistence tests separately demonstrated durable checkpoint,
Interaction Memory, and Run History behavior.

Current Known Gaps

There are no remaining open capabilities inside the frozen local MVP
Experience Layer.

The following remain broader post-MVP or hardening concerns:

-   production LinkedIn-specific discovery;
-   reliable LinkedIn engagement metadata;
-   objective Engagement Potential calculation;
-   multiple-candidate orchestration;
-   production-grade observability;
-   production-grade authentication / authorization;
-   formal data-retention / deletion policy;
-   backup and recovery policy;
-   schema migration discipline;
-   long-term model routing and cost telemetry;
-   real-world Opportunity Score calibration;
-   advanced feedback learning;
-   adaptive policy calibration;
-   automatic Resume Run after Streamlit session/process loss;
-   LinkedIn-native authenticated integration;
-   autonomous publication.

These items should not be used to reopen the validated MVP reasoning
architecture without a demonstrated defect or explicit product decision.

Architecture Freeze

Unless a genuine defect is found, do not redesign:

Scout
Opportunity Evaluation
Research
Argument Intelligence
Perspective Generation
Human Perspective Selection
Human Content Mode Selection
Final Human Refinement
deterministic scoring
evidence provenance
manual publication authority
three-domain persistence separation

The next phase is not another reasoning-architecture redesign.

Immediate Development Sequence

Current immediate sequence:

1.  Complete documentation reconciliation across the architecture/context
    set.

2.  Keep the full regression suite green.

3.  Run:

python -m pytest

Expected baseline:

437 passed

4.  Inspect git status and review the documentation diff.

5.  Commit the reconciled documentation.

6.  Optionally create a recoverable release/tag checkpoint after the
    documentation state is validated.

7.  Select the next post-MVP increment deliberately.

Do not begin Resume HITL after session loss merely because it is the
nearest documented backlog item.

It is backlog, not the current deployment blocker.

Recovery Procedure

When resuming development in a new session:

1.  Read 01_system_overview.md for product principles and system-level
    architecture.

2.  Read 02_current_architecture.md for the factual implemented
    topology.

3.  Read this file for the immediate checkpoint.

4.  If persistence/deployment work is relevant, read
    05_cloud_deployment.md.

5.  If data contracts/persistence boundaries are relevant, read
    03_data_model.md.

6.  Inspect git status.

7.  Inspect the latest relevant commit/tag.

8.  Run:

python -m pytest

Expected baseline at this checkpoint:

437 passed

9.  If the suite differs, determine whether new committed work
    legitimately changed the baseline before assuming regression.

10. Resume from Immediate Development Sequence above.

Documentation Maintenance Rule

Keep this file operational.

It should contain only information required to recover the current
development context.

When an increment is closed:

-   update the current checkpoint;
-   update the test baseline when materially useful;
-   move durable architecture facts to 02_current_architecture.md;
-   move durable rationale to 04_decision_log.md;
-   move detailed deployment behavior to 05_cloud_deployment.md;
-   remove obsolete implementation history from this file.

Do not accumulate a chronological development diary here.

A healthy PROJECT_CONTEXT.md should remain a recovery artifact rather
than a second complete architecture specification.

Current Resume Point

At this checkpoint:

-   7.1 Editable Theme / Intent is complete and validated;
-   7.2 Content Mode Selection is complete and validated;
-   7.3 Final Human Refinement is complete and E2E validated;
-   7.4 Bilingual Presentation is complete and E2E validated;
-   7.5 Run History / Product Memory is complete and validated;
-   437 automated tests pass;
-   the Human-Centered workflow is validated through WORKFLOW COMPLETE;
-   Portuguese translation is validated;
-   Run History is validated;
-   Render deployment is live;
-   Supabase PostgreSQL is the cloud persistence backend;
-   PostgresSaver checkpoint recovery by thread_id is validated;
-   Interaction Memory PostgreSQL persistence is validated;
-   Run History PostgreSQL persistence is validated;
-   Run History survives Render restart;
-   automatic frontend HITL reconstruction after session/process loss is
    explicitly backlog;
-   publication remains manual.

Immediate action:

finish documentation/release hygiene without reopening the validated
reasoning architecture.

Resume here.
