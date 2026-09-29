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
- 01_system_overview.md --- product model, architectural principles,
target MVP architecture, and responsibility boundaries.
- 02_current_architecture.md --- factual view of what is implemented
now and how the current components are connected.
- 04_decision_log.md --- architectural rationale and durable
decisions.
- PROJECT_CONTEXT.md --- current recovery checkpoint and immediate
development context.
When architecture and this checkpoint differ,
02_current_architecture.md is authoritative for implemented topology.
Current Checkpoint
Current development stage:
MVP Experience Layer
Completed Experience Layer increments:
- 7.1 --- Editable Theme / Intent
- 7.2 --- Content Mode Selection
Next planned product increment:
- 7.3 --- Final Human Refinement
Current automated regression baseline:
437 passing tests
Current real E2E status:
Validated through Human Review with both sequential HITL boundaries.
Current frontend hardening status:
Two UX defects were observed during real Streamlit execution and are
being corrected:
1. visual state/phase can lag the backend worker;
2. transient Scout / Opportunity text can flicker during automatic
Streamlit reruns.
These are frontend synchronization/presentation defects. They do not
require a change to the validated graph, agent contracts, or reasoning
architecture.
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
+-- PASS -----------------\> Human Review
\|
+-- REVISE --\> Writer --\> Quality Evaluator
\|
+-- REJECT ---------------------------\> END
Publication remains outside autonomous execution.
The Writer revision loop is bounded.
Ordinary Writer revision does not rerun Research, Argument Intelligence,
or Perspective Generation.
Current Human Decision Boundaries
HITL 1 --- Perspective Selection
The system generates multiple materially distinct and defensible
intellectual perspectives from the same evidence base.
The human chooses the intellectual direction.
Input:
PerspectiveSet
Human decision:
- perspective_id
- optional human_guidance
Output:
SelectedPerspective
The selected perspective is authoritative downstream context.
Writer must not silently replace it with another thesis.
HITL 2 --- Content Mode Selection
After the perspective has been selected, the human chooses how that
intellectual direction should be materialized.
Valid MVP modes:
- linkedin_post
- linkedin_reply
- article
Output:
ContentMode
This decision changes expression, depth, contextual independence, and
communication behavior.
It does not change the selected intellectual position.
The same SelectedPerspective can therefore be materialized in another
supported format without rerunning the upstream reasoning pipeline.
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
A second LangGraph HITL boundary now exists after Human Perspective
Selection and before Writer.
Supported modes:
- LinkedIn Post
- LinkedIn Reply
- Article
Writer is content-mode-aware.
Quality Evaluator is content-mode-aware.
Legacy paths default to linkedin_reply for compatibility.
Automated integration coverage confirms that selecting a content mode
does not rerun:
- Research;
- Argument Intelligence;
- Perspective Generation.
Real Streamlit E2E successfully reached:
Human Perspective Selection
-\> Human Content Mode Selection
-\> Writer
-\> Quality Evaluator
-\> Human Review
7.3 --- Final Human Refinement
Status: NEXT
Target behavior:
After Quality Evaluator returns PASS, the human may either accept the
current draft or provide bounded editorial guidance for a final
adjustment.
Examples of refinement dimensions:
- tone;
- emphasis;
- length;
- framing;
- closing.
The refinement must preserve the selected intellectual direction unless
the human explicitly changes it.
7.4 --- Bilingual Presentation
Status: PLANNED
The internal reasoning pipeline remains English-first.
Final generated content should be translatable to Portuguese on demand.
Translation is a presentation-layer capability and should not rerun the
full reasoning pipeline.
7.5 --- Run History / Product Memory
Status: PLANNED
Completed runs should become navigable from the product UI.
A history record should preserve enough information to reconstruct the
user-facing result, including:
- human theme / intent;
- selected source and link;
- selected perspective;
- content mode;
- final generated response;
- translated response when requested;
- relevant run metadata.
Run History is distinct from Interaction Memory.
Interaction Memory exists primarily to support agent behavior such as
novelty, URL canonicalization, and avoiding repeated content.
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
- search strategy;
- source selection;
- semantic opportunity signals;
- research decisions;
- evidence interpretation;
- synthesis;
- argument construction;
- perspective generation;
- drafting;
- semantic quality assessment.
Python
Owns deterministic governance, including:
- validation;
- scoring;
- thresholds;
- guardrails;
- action authorization;
- provenance enforcement;
- counters;
- operational limits;
- context budgets;
- factual state mutation;
- validation of explicit human selections.
LangGraph
Owns orchestration, including:
- shared workflow state;
- node transitions;
- deterministic routing;
- bounded revision paths;
- HITL interruption/resume;
- termination.
Human
Owns:
- intellectual convergence;
- perspective selection;
- content-mode selection;
- contextual guidance;
- final editorial judgment;
- publication.
Current Core Guardrails
The following architectural behaviors should remain frozen during the
remaining MVP Experience Layer work unless a genuine defect is
discovered.
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
LinkedIn-native content. Use Core Voice plus article structural rules
rather than pretending a separately calibrated article persona exists.
Current Frontend
Current product surface:
app/frontend/main.py
Implemented UI behavior includes:
- Editable Theme / Intent;
- real workflow launch;
- live workflow progress;
- Opportunity artifact;
- Argument Brief;
- Perspective Selection;
- Content Mode Selection;
- Writer / Evaluator continuation;
- Human Review;
- manual-publication boundary.
The frontend uses a background worker so long-running Scout and Research
execution do not freeze the interactive experience.
LangGraph checkpoint/thread state supports interrupt/resume behavior.
Open frontend defects
State synchronization
Observed behavior:
The visual phase/state can remain behind the actual backend node
execution.
Desired behavior:
The latest backend worker phase/event should drive the displayed current
state without corrupting LangGraph state.
Scout / Opportunity flicker
Observed behavior:
Transient Scout / Opportunity text or blocks can appear/disappear during
Streamlit automatic reruns.
Desired behavior:
Keep workspace rendering stable by phase rather than repeatedly mounting
and unmounting transient blocks.
These are presentation defects.
Do not modify the validated core workflow merely to solve them.
Current Validation Snapshot
Automated suite:
437 passing tests
The current regression surface includes:
- Scout;
- Opportunity Evaluation;
- deterministic routing;
- Research;
- evidence provenance;
- web tooling;
- context preparation;
- Argument Intelligence;
- Perspective Generation;
- Human Perspective Selection;
- SelectedPerspective-aware Writer;
- Human Content Mode Selection;
- all three content modes;
- mode-aware Writer;
- mode-aware Quality Evaluator;
- bounded revision;
- HITL interrupt/resume;
- upstream non-rerun guarantees.
Real Streamlit E2E has demonstrated:
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
-\> Human Review
A separate real run demonstrated correct LOW termination before
Research.
The current test count is a development checkpoint, not an architectural
invariant.
Current Known Gaps
The following are not yet complete MVP capabilities:
- Final Human Refinement;
- Portuguese translation;
- persistent Run History.
The following remain broader post-MVP or hardening concerns:
- production LinkedIn-specific discovery;
- reliable LinkedIn engagement metadata;
- objective Engagement Potential calculation;
- multiple-candidate orchestration;
- production-grade observability;
- cloud deployment architecture;
- long-term model routing and cost telemetry;
- real-world score calibration;
- advanced feedback learning;
- adaptive policy calibration;
- autonomous publication.
These items should not distract from closing the frozen MVP Experience
Layer.
Immediate Development Sequence
Current immediate sequence:
1. Validate/finalize frontend State Sync + Flicker hardening
2. Keep full regression suite green
3. Close 7.2 checkpoint
4. Implement 7.3 Final Human Refinement
5. Implement 7.4 Portuguese Translation
6. Implement 7.5 Run History
7. Validate complete MVP Experience Layer E2E
8. Update architecture/checkpoint documentation
9. Create recoverable release checkpoint
Do not reopen validated core capabilities merely because a later
Experience Layer feature is being added.
Recovery Procedure
When resuming development in a new session:
1. Read 01_system_overview.md for product principles and target
architecture.
2. Read 02_current_architecture.md for the factual implemented
topology.
3. Read this file for the immediate checkpoint.
4. Inspect git status.
5. Inspect the latest relevant commit/tag.
6. Run:
python -m pytest
Expected baseline at this checkpoint:
421 passed
7. If the suite differs, determine whether new committed work
legitimately changed the baseline before assuming regression.
8. Resume from Immediate Development Sequence above.
Documentation Maintenance Rule
Keep this file short and operational.
It should contain only information required to recover the current
development context.
When an increment is closed:
- update the current checkpoint;
- update the test baseline when materially useful;
- move durable architecture facts to 02_current_architecture.md;
- move durable rationale to 04_decision_log.md;
- remove obsolete implementation history from this file.
Do not accumulate a chronological development diary here.
A healthy PROJECT_CONTEXT.md should remain a compact recovery artifact
rather than a second architecture specification.
Current Resume Point
At this checkpoint:
- 7.1 Editable Theme / Intent is complete;
- 7.2 Content Mode Selection is functionally complete and validated;
- 421 automated tests pass;
- the two sequential HITL boundaries work in real Streamlit execution;
- frontend State Sync and Scout / Opportunity flicker are the active
hardening items;
- 7.3 Final Human Refinement is the next product capability after
frontend hardening.
Resume here.

Recovery Checkpoint --- 2026-09-29

Automated Regression Baseline

437 passing tests

Current local MVP state

7.1 Editable Theme / Intent:
IMPLEMENTED AND VALIDATED

7.2 Content Mode Selection:
IMPLEMENTED AND VALIDATED

7.3 Final Human Refinement:
IMPLEMENTED AND E2E VALIDATED

7.4 Bilingual Presentation:
IMPLEMENTED AND E2E VALIDATED

7.5 Run History / Product Memory:
IMPLEMENTED
FINAL TERMINAL-STATE PERSISTENCE VALIDATION PENDING

Real E2E status

A real HIGH workflow has been validated through:

Opportunity Evaluation
-\> Research
-\> Argument Intelligence
-\> Perspective Generation
-\> Human Perspective Selection
-\> Human Content Mode Selection
-\> Writer
-\> Quality Evaluator
-\> Human Final Refinement ACCEPT
-\> WORKFLOW COMPLETE

The previous empty interrupt / stale HITL remount failure is no longer present
in the validated ACCEPT path.

Portuguese translation of the final draft has been validated in the real
Streamlit experience.

Run History list/detail/back navigation has been visually validated.

Remaining local validation

A completed HIGH run previously exposed a History persistence defect where the
saved record could appear as:

No candidate
No content generated

The current persistence implementation has been hardened to prefer
authoritative terminal LangGraph state and to prevent a later incomplete save
from degrading a richer completed record.

The full automated regression suite remains green after this change:

437 passing tests

The corrected COMPLETE -\> Run History persistence path still requires one final
runtime validation before 7.5 is described as fully validated.

Deployment status

Production cloud deployment:
NOT IMPLEMENTED

Cloud provider:
NOT SELECTED

Production persistence:
NOT SELECTED

Local Run History persistence:
IMPLEMENTED with SQLite at data/history/run_history.db

Immediate resume sequence

1.  Perform one final low-cost real validation of COMPLETE -\> Run History
    persistence.

2.  If the history record correctly preserves the completed HIGH run and final
    artifacts, close MVP Experience Layer 7.5.

3.  Begin Cloud Deployment design and implementation without reopening the
    validated reasoning architecture.

4.  Validate the deployed application with a cloud smoke / E2E run.

5.  Update 05_cloud_deployment.md, PROJECT_CONTEXT.md, and README.md with the
    actual selected deployment architecture and validated runtime behavior.

6.  Regenerate PROJECT_AUDIT.md from the repository state rather than editing it
    manually.

Architecture freeze

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

The next phase is persistence validation and deployment, not another reasoning
architecture redesign.
