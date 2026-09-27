Current Architecture
Document Purpose
This document is the factual implementation view of the LinkedIn Agentic AI System.
01_system_overview.md explains the architectural model and design philosophy.
This file answers a different question:
What is implemented now, and how are the current components connected?
It should be updated when the implemented workflow, component boundaries, routing, tooling, state, or runtime limits materially change.
Current Development Snapshot
Current automated baseline:
421 passing tests
The Human-Centered Conversation Intelligence architecture is now integrated
through the real LangGraph workflow.
Implemented and validated component / orchestration milestones:
Argument Contracts v0.1 — implemented
Argument Intelligence v0.1 — implemented
Perspective Generation v0.1 — implemented
Human Perspective Selection v0.1 — implemented and integrated as HITL
Writer / Voice Integration v0.1 — implemented
LangGraph Integration — implemented
MVP Experience Layer 7.1 — Editable Theme / Intent — implemented and validated
MVP Experience Layer 7.2 — Content Mode Selection — implemented and validated
The current integrated graph contains two sequential Human-in-the-Loop
boundaries:
PerspectiveSet
|
v
Human Perspective Selection
|
v
SelectedPerspective
|
v
Human Content Mode Selection
|
v
ContentMode
|
v
Writer
Supported content modes are:
linkedin_post
linkedin_reply
article
Writer and Quality Evaluator are content-mode-aware.
Legacy execution paths default to linkedin_reply for backward compatibility.
Real Streamlit E2E has validated the complete path through both HITL
interrupt/resume boundaries and into Human Review.
The next planned product capability is:
MVP Experience Layer 7.3 — Final Human Refinement
Before 7.3, two frontend-only hardening defects observed during real E2E are
being finalized:
visual state / phase can lag the backend worker;
transient Scout / Opportunity text can flicker during Streamlit automatic
reruns.
These are presentation/synchronization defects and do not redefine the
validated graph, component contracts, or reasoning architecture.
Active Workflow
The implemented primary workflow is:
Human Theme / Intent
|
v
Scout
|
v
Opportunity Evaluation
|
+-- LOW ------------------------------> END
|
+-- MEDIUM --> QUEUED ----------------> END
|
+-- HIGH
|
v
ACCEPTED_FOR_RESEARCH
|
v
Research
|
v
ResearchBrief
|
v
Argument Intelligence
|
v
ArgumentBrief
|
v
Perspective Generation
|
v
PerspectiveSet
|
v
Human Perspective Selection
|
v
SelectedPerspective
|
v
Human Content Mode Selection
|
+-- linkedin_post
+-- linkedin_reply
+-- article
|
v
Writer
|
v
Quality Evaluator
|
+-- PASS -----------------> Human Review
|
+-- REVISE --> Writer
|               |
|               +--> Quality Evaluator
|
+-- REJECT ---------------------> END
Publication remains manual and outside autonomous execution.
The Writer revision loop is bounded by the workflow iteration limit.
Research, Argument Intelligence, and Perspective Generation are not
automatically rerun when Writer receives a normal revision request.
Repository-Level Component Map
The implementation is organized around the following responsibilities:
app/
|
+-- agents/
|   +-- scout.py
|   +-- research.py
|
+-- components/
|   +-- opportunity_evaluator.py
|   +-- argument_intelligence.py
|   +-- perspective_generation.py
|   +-- perspective_selection.py
|   +-- writer.py
|   +-- evaluator.py
|
+-- frontend/
|   +-- main.py
|
+-- graph/
|   +-- state.py
|   +-- workflow.py
|   +-- nodes/
|       +-- scout_node.py
|       +-- opportunity_evaluator_node.py
|       +-- opportunity_routing_nodes.py
|       +-- research_node.py
|       +-- argument_intelligence_node.py
|       +-- perspective_generation_node.py
|       +-- human_perspective_selection_node.py
|       +-- human_content_mode_selection_node.py
|       +-- writer_node.py
|       +-- evaluator_node.py
|
+-- schemas/
|   +-- scout.py
|   +-- opportunity.py
|   +-- research.py
|   +-- argument.py
|   +-- writer.py
|   +-- evaluator.py
|   +-- tools.py
|
+-- prompts/
|   +-- perspective_generation.py
|   +-- writer.py
|   +-- evaluator.py
|   +-- rodrigo_voice.py
|
+-- tools/
|   +-- web_search.py
|   +-- web_reader.py
|   +-- brave_search.py
|   +-- http_reader.py
|   +-- web_tools.py
|   +-- errors.py
|
+-- context_preparation.py
Exact filenames can evolve, but the responsibility boundaries should remain
explicit.
Orchestration Layer
Global State
The LangGraph workflow carries shared state across nodes.
The current state includes concepts such as:
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
Specialist components should not automatically receive this entire state.
Nodes are responsible for mapping the relevant global state into
component-specific inputs.
The current human-centered graph is compiled with checkpointing where
interrupt/resume behavior is required.
Human Perspective Selection and Human Content Mode Selection are explicit
graph nodes rather than hidden frontend-only decisions.
Scout Node
The Scout node bridges the global workflow and the bounded Scout agent.
Conceptually:
Workflow
|
v
scout_node
|
+--> obtain configured SearchTool / ReadTool
|
v
run_scout(...)
|
v
ScoutState
|
v
selected PostCandidate
|
v
workflow state
Routing after Scout is deterministic.
Current behavior:
0 candidates
-> END
1 candidate
-> Opportunity Evaluation
1 distinct candidates
-> explicit unsupported-condition failure
Duplicate selection of the same candidate is controlled rather than treated as multiple independent opportunities.
Multiple-candidate orchestration remains intentionally unresolved.
Scout Runtime
Scout is implemented as a bounded Python agent loop rather than as an internal LangGraph subgraph.
Action vocabulary:
SEARCH
READ
SELECT
FINISH
Execution pattern:
ScoutState
|
v
LLM decision
|
v
ScoutAction
|
v
Python validation / authorization
|
v
tool execution
|
v
state mutation
|
+-------> next bounded decision
The LLM owns semantic action selection.
Python owns legal execution.
Opportunity Evaluator Node
The Opportunity Evaluator receives a validated PostCandidate.
The semantic evaluator produces:
topic_relevance
positioning_fit
contribution_potential
research_cost
The application then derives:
research_efficiency = 100 - research_cost
Current score:
Contribution Potential × 0.30
Positioning Fit        × 0.25
Topic Relevance        × 0.20
Engagement Potential   × 0.15
Research Efficiency    × 0.10
Current mandatory LOW guardrails:
Contribution Potential < 30
Positioning Fit        < 30
Topic Relevance        < 25
Otherwise:
HIGH   >= 80
MEDIUM >= 60 and < 80
LOW    < 60
Where reliable engagement data is unavailable, the current implementation uses a neutral placeholder rather than allowing the model to invent engagement metrics.
Opportunity Routing
Routing is deterministic:
LOW
-> END
MEDIUM
-> QUEUED
-> END
HIGH
-> ACCEPTED_FOR_RESEARCH
-> Research
The semantic model therefore does not directly choose whether the graph enters Research.
It provides structured signals; deterministic application logic produces the operational classification.
Research Node
The Research node is integrated into the HIGH opportunity path.
Conceptually:
PostCandidate
+
Opportunity Evaluation
|
v
research_node
|
+--> get_web_tools()
|
v
ResearchState
|
v
run_research_loop(...)
|
v
ResearchBrief
|
v
research_result in workflow state
|
v
Argument Intelligence
The node validates that the required opportunity context exists and that the
opportunity is eligible for Research before invoking the agent.
Research output is not sent directly to Writer in the current primary flow.
It first passes through Argument Intelligence and Perspective Generation,
followed by explicit human convergence.
Research Runtime
Research uses a bounded semantic loop with:
SEARCH
READ
EXTRACT
FINISH
The runtime separates discovery, reading, and evidence extraction:
SEARCH
|
v
SearchResult
|
v
READ
|
v
ReadSource
|
v
EXTRACT
|
v
EvidenceItem
|
v
ResearchBrief
Only extracted evidence is intended to support Writer-facing factual findings.
Current operational limits:
max steps           10
max decisions       12
max searches         3
max reads            5
max evidence items   6
Current completion statuses include:
SUFFICIENT
INSUFFICIENT
LIMIT_REACHED
Differentiated graph routing for all Research completion statuses remains a future hardening decision.
Argument Intelligence
Argument Intelligence is integrated after Research.
Input:
ResearchBrief
Output:
ArgumentBrief
Its responsibility is to organize the evidence into an intellectual decision
artifact rather than write final content.
Representative content includes:
original thesis;
relevant context;
strongest evidence;
counterevidence;
tensions and trade-offs;
uncertainty;
possible contribution areas;
source references.
This boundary separates:
what the evidence supports
from:
what may be worth saying.
Perspective Generation
Perspective Generation is integrated after Argument Intelligence.
Input:
ArgumentBrief
Output:
PerspectiveSet
The component generates a small set of materially distinct and defensible
intellectual directions grounded in the same evidence base.
A perspective represents what could be worth saying.
It is not merely a tone or wording variation.
Artificial disagreement should not be manufactured solely to create options.
Human Perspective Selection
Human Perspective Selection is an explicit LangGraph interrupt.
Input:
PerspectiveSet
Human decision:
perspective_id
optional human_guidance
Output:
SelectedPerspective
The frontend presents the alternatives and resumes the graph with the human
selection.
SelectedPerspective is authoritative downstream context.
Human Content Mode Selection
Human Content Mode Selection is the second sequential LangGraph interrupt.
It occurs after SelectedPerspective and before Writer.
Valid values:
linkedin_post
linkedin_reply
article
The human decision is stored as content_mode in workflow state.
Content mode changes form, depth, contextual independence, and communication
behavior.
It does not change the selected intellectual direction.
Real Streamlit E2E has validated both HITL interrupt/resume boundaries in
sequence.
Writer Node
Writer materializes the human-selected intellectual direction.
The current integration follows the component-specific-input principle:
Global workflow state
|
v
writer_node
|
v
Writer-specific input
|
v
Writer
|
v
current_draft
Current Writer-facing context includes:
PostCandidate
ResearchBrief / evidence context
SelectedPerspective
ContentMode
previous_draft when revising
revision_instruction when revising
Writer does not own source authorization, evidence provenance, perspective
selection, content-mode selection, quality routing, or publication.
SelectedPerspective is authoritative intellectual context.
ContentMode controls the expression contract.
Supported modes:
linkedin_post
linkedin_reply
article
Legacy paths default to linkedin_reply.
Normal Writer revision preserves the selected content mode and does not rerun
the upstream research / argument / perspective pipeline.
Quality Evaluator Node
The Quality Evaluator evaluates the current draft against the quality
contract.
Conceptually:
current_draft
+
ContentMode
|
v
evaluator_node
|
v
Quality Evaluator
|
v
quality_evaluation
|
v
deterministic route
Current outcomes:
PASS
REVISE
REJECT
Routing:
PASS
-> Human Review
REVISE
-> Writer
-> Quality Evaluator
REJECT
-> END
Revision is bounded by MAX_ITERATIONS.
The semantic evaluator is content-mode-aware.
Legacy paths default to linkedin_reply.
Python remains responsible for deterministic consolidated routing.
A quality PASS does not authorize publication.
Web Tool Selection
The current web-tool factory selects execution mode through configuration.
Conceptually:
get_web_tools(mode)
|
+-- fake
|     |
|     +--> deterministic web_search
|     +--> deterministic web_reader
|
+-- real
|
+--> brave_search
+--> http_reader
The returned interface is always:
tuple[SearchTool, ReadTool]
This keeps Scout and Research independent from the concrete provider.
Search Adapter
The current real search implementation uses the Brave Search API.
Important implementation characteristics include:
bounded query size
bounded result count
API-key validation
request timeout
structured SearchResult mapping
controlled HTTP/network errors
injectable HTTP client for tests
The agent does not receive provider-specific response objects.
Provider output is mapped into the internal SearchResult contract.
HTTP Reader
The real reader is a bounded network adapter.
The current safety boundary includes:
HTTP / HTTPS only
localhost rejection
DNS resolution
private/non-global IP rejection
manual redirect handling
redirect revalidation
redirect limit
request timeout
text content-type restriction
response-size limit
controlled WebToolError conversion
This layer is important because READ actions originate from agent decisions.
The reader must therefore treat requested URLs as untrusted input.
Main Content Extraction
For HTML responses, the reader does not simply return the complete rendered page.
Current extraction behavior:
ignore common non-content elements
prefer non-empty <article>
otherwise prefer non-empty <main>
otherwise score section/div candidates
otherwise fall back to cleaned body text
Ignored structures include:
aside
form
footer
head
header
nav
noscript
script
style
Density scoring considers signals such as:
text length
paragraph count
heading count
list-item count
link-text density
positive content hints
negative navigation/promotion hints
Semantic article and main containers are authoritative even when short.
Density thresholds apply to fallback candidates rather than invalidating legitimate short semantic containers.
Context Preparation
app/context_preparation.py creates bounded LLM-facing external context.
The main value object is:
PreparedContext
├── content
├── original_tokens
├── prepared_tokens
└── truncated
Current processing:
external text
|
v
normalize whitespace
|
v
remove exact duplicate lines
|
v
tokenize / count
|
v
truncate if required
|
v
PreparedContext
Current token encoding defaults to:
o200k_base
with a controlled fallback encoding.
Current configured budgets:
SCOUT_READ_CONTEXT_MAX_TOKENS       = 1800
RESEARCH_READ_CONTEXT_MAX_TOKENS    = 2500
RESEARCH_TOTAL_READ_CONTEXT_MAX_TOKENS = 8000
The cumulative Research budget applies to stored read context, not the complete serialized Research prompt.
Scout Context Boundary
Real or fake reader output is prepared before becoming Scout LLM-facing read context.
Conceptually:
ReadTool(url)
|
v
raw content
|
v
prepare_context(...)
|
v
bounded content
|
v
ScoutState / next LLM decision
Raw oversized page content should not bypass this boundary.
Research Context Boundary
Research applies both:
per-read limit
+
cumulative stored-read limit
Conceptually:
Read 1 -> prepare -> store
Read 2 -> prepare -> check cumulative budget -> store
Read N -> bounded by remaining budget
This creates a deterministic context ceiling independent from the model's semantic decision to continue researching.
Error Boundary
External web infrastructure failures use:
WebToolError
Scout and Research catch expected external-tool failures at the agent boundary.
The failure can be recorded in state and the bounded agent may choose a valid recovery action.
The runtime does not intentionally catch arbitrary programming errors and disguise them as external observations.
Fake vs Real Execution
Fake tooling remains a first-class testing capability.
Unit / integration tests
|
v
deterministic fake tools
Real tooling is used for explicit real-infrastructure validation:
Smoke / real workflow validation
|
v
Brave Search + HTTP reader
This separation provides deterministic automated tests without pretending that fake infrastructure represents production web behavior.
Current Real Validation
Scout
A real Scout smoke execution has demonstrated:
real LLM decision-making
real search
real read
main-content extraction
bounded context
candidate creation
normal completion
Research
A real Research smoke execution has demonstrated:
approved opportunity
real search
real source reading
evidence extraction
source provenance
ResearchBrief synthesis
SUFFICIENT completion
The Research run also preserved uncertainty rather than inventing
supply-chain-specific rules that were not present in the source evidence.
Integrated Streamlit E2E
Real Streamlit execution has demonstrated:
Editable Theme / Intent
|
v
Scout
|
v
Opportunity Evaluation
|
v
HIGH
|
v
Research
|
v
Argument Intelligence
|
v
Perspective Generation
|
v
Human Perspective Selection
|
v
Human Content Mode Selection
|
v
Writer
|
v
Quality Evaluator
|
v
Human Review
Both sequential Human-in-the-Loop interrupt/resume boundaries were exercised
in the real application.
A separate real run demonstrated correct LOW termination before Research.
Automated Test Baseline
Current full suite:
421 passing tests
The active regression surface includes:
Scout
Opportunity Evaluation
workflow routing
Research
Argument Intelligence
Perspective Generation
Human Perspective Selection
Human Content Mode Selection
SelectedPerspective-aware Writer
content-mode-aware Writer
content-mode-aware Quality Evaluator
bounded Writer revision
web tool factory
Brave Search adapter
HTTP reader
web-tool recovery
context preparation
Scout context guards
Research context guards
main-content extraction
content-density extraction
LangGraph HITL interrupt/resume behavior
upstream non-rerun guarantees for Content Mode Selection
Automated tests are intentionally isolated from live web/API dependencies
where deterministic test doubles are more appropriate.
The 421-test count is a development snapshot rather than an architectural
invariant.
Streamlit Experience Layer
The current interactive product surface is:
app/frontend/main.py
Implemented behavior includes:
Editable Theme / Intent
real workflow launch
live workflow presentation
Opportunity artifact
Argument / Perspective artifacts
Human Perspective Selection
Human Content Mode Selection
Writer / Quality Evaluator continuation
Human Review
manual-publication boundary
The frontend uses a background worker so real Scout and Research execution do
not block the interactive product experience.
LangGraph checkpoint/thread state preserves interrupt/resume behavior.
Current frontend hardening
Two presentation defects were observed during real E2E:
visual phase/state can lag the backend worker;
Scout / Opportunity text can flicker during Streamlit automatic reruns.
These issues are frontend synchronization concerns.
They must not reopen the validated core graph or reasoning architecture.
Current Known Gaps
The following MVP Experience Layer capabilities remain incomplete:
Final Human Refinement
on-demand Portuguese translation
persistent navigable Run History
The following remain broader hardening or post-MVP concerns:
LinkedIn-specific production discovery
reliable LinkedIn metadata acquisition
objective Engagement Potential calculation
multiple distinct candidate orchestration
production-grade chronological agent telemetry
production cost/latency telemetry
cloud deployment architecture
long-term model routing
real-world score calibration
advanced feedback learning
adaptive policy calibration
autonomous publication
The system must not be described as production-ready while these boundaries
remain unresolved.
Next Increment
The next planned product increment is:
MVP Experience Layer 7.3 — Final Human Refinement
Target behavior:
Quality Evaluator PASS
|
v
Human Final Review
|
+-- accept current draft
|
+-- provide bounded editorial guidance
            |
            v
      final refinement
The refinement must preserve SelectedPerspective unless the human explicitly
changes the intellectual direction.
Before beginning 7.3, the current frontend State Sync / Flicker hardening
should be validated and the complete regression suite should remain green.
Core Freeze During Experience-Layer Closure
The following validated core behavior should remain frozen except where a
genuine defect is discovered:
Scout
Opportunity Evaluation
Research
Argument Intelligence
Perspective Generation
deterministic scoring
evidence provenance
Human Perspective Selection semantics
The remaining Experience Layer work should extend the product interaction
surface rather than redesign the validated reasoning architecture.
Maintenance Rule
Update this document whenever any of the following materially changes:
implemented workflow topology
node responsibilities
component integration
routing behavior
web tooling implementation
context boundaries
runtime limits
failure handling
real validation status
major implemented capability
Do not use this document as a development diary.
Historical rationale belongs in 04_decision_log.md.
Deep capability specifications belong in dedicated architecture documents.
Recovery/checkpoint state belongs in:
docs/context/PROJECT_CONTEXT.md