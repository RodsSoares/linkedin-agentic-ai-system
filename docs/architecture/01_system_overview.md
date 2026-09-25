System Overview
Purpose
The LinkedIn Agentic AI System is a controlled, human-centered
agentic AI system for discovering strategically relevant professional
conversations, deciding whether they are worth pursuing, researching the
evidence required for a defensible contribution, expanding that evidence
into multiple intellectual directions, helping the human choose what is
worth saying, materializing the selected direction into a draft,
evaluating its quality, and preserving human authority over publication.
The system is not designed as an autonomous social-media bot.
The final MVP experience layer is intended to make the same architecture
usable as an interactive product: the human can define the exploration
theme, choose the intellectual direction, choose how that direction should
be materialized, refine the final expression, request a Portuguese
translation, and revisit prior runs through navigable run history.
Its purpose is to reduce the manual effort required to move from:
"Where should I contribute?"
to:
"What are the defensible directions here, which one do I want to own,
and how should it be expressed?"
The system therefore separates semantic reasoning, deterministic
governance, workflow orchestration, and human judgment.
Core Product Principle
AI expands. Human converges. AI materializes. Human owns.
AI is used where machine intelligence provides leverage:
discovery;
filtering;
research;
evidence retrieval;
synthesis;
tension mapping;
perspective generation;
drafting;
evaluation.
Human judgment remains authoritative for:
intellectual direction;
perspective selection, rejection, or combination;
personal context;
contextual nuance;
final editorial judgment;
publication.
Human-in-the-Loop is therefore not merely a safety gate. It is part of
the cognitive architecture of the product.
A second established principle remains:
Opportunity != Popularity
A post is not valuable merely because it has high engagement. A useful
opportunity depends on whether Rodrigo can make a relevant,
differentiated, professionally valuable, and defensible contribution.
Frozen MVP Target
MVP Human-Centered Conversation Intelligence = a system capable of
finding or receiving an opportunity, qualifying it, researching it,
transforming evidence into an ArgumentBrief, generating multiple
defensible perspectives, asking the human for the desired intellectual
direction, and only then producing and evaluating the final content. The
final experience-layer increment extends this target with editable theme
input, explicit content-mode selection, final human refinement, optional
Portuguese translation, and navigable run history without changing the
core human-centered reasoning principle.
The MVP is intentionally narrower than the broader long-term product
vision.
Performance Analytics, Feedback Learning, adaptive policy calibration,
advanced UX, autonomous publication, and other post-MVP capabilities are
not required to close this MVP.
Target MVP Architecture
Human Intent / Editable Theme
        |
        v
Discovery / Scout
        |
        v
Target Qualification
        |
        v
Opportunity Evaluation
        |
        +-- LOW -----------------------------> END
        |
        +-- MEDIUM --> QUEUED --------------> END
        |
        +-- HIGH
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
(LinkedIn Post / LinkedIn Reply / Article)
        |
        v
Rodrigo Voice / Writer
        |
        v
Quality Evaluator
        |
        +-- PASS ----------------------------> Human Final Review
        |
        +-- REVISE --> Writer --> Evaluator
        |
        +-- REJECT --------------------------> END
                                                  |
                                                  v
                                          Manual Publication
Publication remains outside autonomous execution.
The core Human-Centered Conversation Intelligence flow is integrated in
the LangGraph workflow. The current development focus is the MVP Experience
Layer described below. Capabilities described as planned experience-layer
features should not be interpreted as already implemented until validated
in the current architecture and release documentation.
Responsibility Layers
LLM --- Semantic Intelligence
The LLM handles tasks where interpretation matters, including:
search strategy;
source selection;
topic relevance;
contribution potential;
evidence interpretation;
synthesis;
tension identification;
perspective generation;
writing;
semantic quality assessment.
The LLM may expand the intellectual decision space, but it must not
silently replace the human-selected intellectual direction.
Python --- Deterministic Governance
Python owns:
validation;
scoring;
thresholds;
guardrails;
action authorization;
provenance enforcement;
counters;
operational limits;
context budgets;
factual state mutation;
validation of explicit human selections.
Semantic proposals do not automatically become authoritative operational
state.
LangGraph --- Workflow Orchestration
LangGraph coordinates:
shared workflow state;
node transitions;
deterministic routing;
bounded revision paths;
Human-in-the-Loop transitions;
termination.
LangGraph orchestrates specialist components; it should not absorb their
business logic.
Human --- Intellectual and Publication Authority
The human owns two distinct decision boundaries.
Intellectual convergence
AI researches
 -> AI builds argument space
 -> AI generates defensible perspectives
 -> HUMAN SELECTS / REJECTS / COMBINES / GUIDES
Final ownership
AI materializes selected direction
 -> AI evaluates quality
 -> HUMAN REVIEWS
 -> HUMAN DECIDES WHETHER TO PUBLISH
Autonomous LinkedIn publication and commenting remain explicit
non-goals.
Discovery / Scout
Scout is the bounded discovery agent.
Its action vocabulary is:
SEARCH
READ
SELECT
FINISH
Its loop is:
ScoutState
   |
   v
LLM chooses allowed action
   |
   v
Structured ScoutAction
   |
   v
Python authorization
   |
   v
Tool execution
   |
   v
Observation -> State -> next bounded decision
The model decides semantically what it wants to do. Python decides
whether the action is legal.
Web Tool Layer
Scout and Research use provider-neutral contracts:
SearchTool(query) -> list[SearchResult]
ReadTool(url)     -> str
Two execution modes are supported:
FAKE MODE -> deterministic tools for isolated tests
REAL MODE -> Brave Search + bounded HTTP reader
The real reader validates network access and includes controls for URL
scheme, DNS resolution, localhost/private destinations, redirects,
timeouts, content type, response size, and controlled external failures.
Content Preparation
External pages pass through explicit preparation boundaries:
HTTP response
    |
    v
Main Content Extraction
    |
    +-> prefer article/main
    +-> density fallback for section/div
    |
    v
Editorial text
    |
    v
Context Preparation
    |
    +-> normalize
    +-> remove exact duplicate lines
    +-> count tokens
    +-> enforce component budget
    |
    v
PreparedContext
    |
    v
LLM-facing input
This prevents arbitrary raw webpages from being treated as clean,
unlimited model context.
Current principal budgets:
Scout read context                 <= 1800 tokens
Research per-read context          <= 2500 tokens
Research cumulative read context   <= 8000 tokens
Opportunity Evaluation
Opportunity Evaluation answers:
"Is this opportunity worth pursuing?"
Current weighted dimensions:
Dimension                  Weight
Contribution Potential        30%
Positioning Fit               25%
Topic Relevance               20%
Engagement Potential          15%
Research Efficiency           10%
The LLM produces semantic signals. Python calculates the weighted score,
applies mandatory guardrails, and produces the operational
classification.
HIGH   -> ACCEPTED_FOR_RESEARCH -> Research
MEDIUM -> QUEUED -> END
LOW    -> END
Opportunity Evaluation is a strategic resource-allocation gate. It does
not determine Rodrigo's final intellectual position.
Research
Research transforms an accepted opportunity into the minimum evidence
package needed for a factual and defensible contribution.
Actions:
SEARCH
READ
EXTRACT
FINISH
Provenance chain:
SearchResult
    |
    v
Authorized URL
    |
    v
ReadSource
    |
    v
EvidenceItem
    |
    v
ResearchBrief
A search result is not automatically evidence. A read page is not
automatically evidence. Evidence must be explicitly extracted and
preserve provenance.
Current principal runtime limits:
max steps           10
max decisions       12
max searches         3
max reads            5
max evidence items   6
Research may terminate as SUFFICIENT, INSUFFICIENT, or
LIMIT_REACHED.
Research should remain independent from the final editorial direction
whenever practical so that multiple perspectives can reuse the same
evidence base.
Argument Intelligence
Argument Intelligence sits between Research and final content
generation.
Its responsibility is not to write the final LinkedIn contribution.
It transforms a ResearchBrief into an ArgumentBrief: a compact
intellectual decision artifact that can expose, where supported by the
evidence:
the original thesis;
relevant context;
strongest evidence;
counterevidence;
tensions and trade-offs;
uncertainty;
possible contribution areas;
source references.
Conceptually:
ResearchBrief
      |
      v
Argument Intelligence
      |
      v
ArgumentBrief
This boundary separates researching what is supported from
deciding what is worth saying.
Perspective Generation
Perspective Generation deliberately preserves divergence before human
convergence.
Instead of immediately producing one supposedly "best" answer, the
system generates a small set of materially distinct and defensible
intellectual directions grounded in the same ArgumentBrief and
evidence base.
Conceptually:
ArgumentBrief
      |
      v
Perspective Generation
      |
      v
PerspectiveSet
A perspective represents what could be worth saying.
It is not merely a change in tone, style, or wording.
Artificial disagreement should not be created solely to produce multiple
options.
Human Perspective Selection
Human Perspective Selection is the central convergence boundary of the
MVP.
The human may:
select a perspective;
reject a proposed direction;
combine ideas where the contract supports it;
add guidance or personal context;
modify the intended direction;
request another direction through the interaction layer.
The selected intellectual direction is represented explicitly through
SelectedPerspective.
Conceptually:
PerspectiveSet
      |
      v
Human decision
      |
      v
SelectedPerspective
Only after this convergence should the system materialize the complete
final contribution.
The human selection is authoritative context. Downstream generation must
not silently substitute another argument.
Perspective Is Not Expression
The architecture explicitly separates:
Perspective
What should be said.
from:
Expression
How the selected idea should be communicated.
A technical perspective can be expressed conversationally. An
organizational perspective can be expressed humorously. These dimensions
must not be collapsed into one variable.
MVP Experience Layer
The final MVP increment adds a product experience layer without reopening
the validated core reasoning architecture. Its purpose is to expose the
existing agentic capabilities through a more flexible and navigable human
workflow.
The planned capabilities are:
Editable Theme / Intent
The human can define the topic to explore instead of relying on a fixed
Scout objective. The application converts the human theme into the bounded
Scout objective while preserving the existing discovery guardrails.
This is intended to demonstrate that the architecture is not hard-coded to
a single professional domain.
Content Mode Selection
After selecting the intellectual perspective, the human chooses how the
idea should be materialized. Initial MVP modes are:
LinkedIn Post;
LinkedIn Reply / Comment;
Article.
Content mode is an expression decision, not an intellectual-position
decision. The same SelectedPerspective may therefore be materialized in
different formats without rerunning Research or Perspective Generation.
Final Human Refinement
After a generated draft passes quality evaluation, the human can provide
additional editorial guidance for final adjustment, such as tone, emphasis,
length, framing, or closing. This refinement must preserve the selected
intellectual direction unless the human explicitly changes it.
Bilingual Presentation
The MVP remains English-first internally. Final generated content can be
presented in English and translated to Portuguese on demand through a
Translate interaction. Translation is treated as a presentation layer so
that it does not duplicate the complete reasoning pipeline or increase cost
unnecessarily.
Run History / Product Memory
The application should expose navigable history for completed runs so that
the intellectual work produced by the system does not disappear when a new
workflow starts. A history entry should preserve, at minimum:
human theme / intent;
selected supporting source and link;
selected perspective;
content mode;
final generated response;
translated response when requested;
relevant run metadata required to reconstruct the user-facing result.
This product-facing run history is distinct from Interaction Memory.
Interaction Memory primarily supports agent behavior such as URL
canonicalization, novelty, and avoiding repeated content. Run History
exists so the human can revisit prior intellectual work and generated
artifacts. Both may use persistent storage, but they have different
responsibilities.
The intended experience is therefore:
Editable Theme
  -> Discovery / Qualification / Research
  -> Argument Intelligence
  -> Perspective Generation
  -> Human Perspective Selection
  -> Human Content Mode Selection
  -> Writer / Quality Evaluation
  -> Human Final Refinement
  -> Optional Translation
  -> Persistent Run History
  -> Manual Publication
The core Scout, Opportunity Evaluation, Research, Argument Intelligence,
Perspective Generation, and scoring behavior should remain frozen during
this experience-layer increment except where a genuine defect requires a
change.
Rodrigo Voice
Rodrigo Voice is a personalization layer, not a simulator of Rodrigo's
beliefs.
Its responsibility is narrower:
"Given this specific human-selected perspective, how might Rodrigo
naturally express it?"
Rodrigo Voice must not independently infer which intellectual position
Rodrigo should adopt.
This keeps personalization downstream from human intellectual
convergence.
Writer
The Writer materializes the human-selected direction into a professional
contribution draft using the available evidence and personalization
context.
Its role is therefore:
SelectedPerspective
        +
ContentMode
        +
ResearchBrief / evidence context
        +
Rodrigo Voice
        |
        v
Writer
        |
        v
Draft
Writer does not own:
discovery;
opportunity classification;
unrestricted research;
perspective selection;
human belief inference;
quality routing;
publication.
The orchestration layer supplies component-specific input instead of
exposing the entire global state indiscriminately.
Quality Evaluator
Opportunity Evaluation and Quality Evaluation solve different problems:
Opportunity Evaluation -> "Should we invest effort in this conversation?"
Quality Evaluation     -> "Is the generated contribution good enough?"
Quality routing:
PASS   -> Human Final Review
REVISE -> Writer -> Quality Evaluator
REJECT -> END
Revision is bounded and does not automatically rerun Research.
A quality PASS does not authorize publication.
Structured Contracts
Representative typed contracts include:
PostCandidate
OpportunitySignals
OpportunityEvaluation
ScoutAction
ScoutSelection
ScoutState
SearchResult
SearchTool
ReadTool
ResearchObjective
ResearchAction
ReadSource
EvidenceItem
ResearchState
ResearchBriefSynthesis
ResearchBrief
ArgumentBrief
Perspective
PerspectiveSet
SelectedPerspective
Writer contracts
Quality Evaluation contracts
LinkedInAgentState
Pydantic is preferred at machine-to-machine AI boundaries where
practical.
The new argument contracts create an explicit data boundary between
evidence, intellectual alternatives, human convergence, and final
expression.
Failure Model
The architecture distinguishes:
semantic failure
operational limit
external infrastructure failure
programming failure
A recoverable web failure can become agent state and permit another
bounded decision.
A programming failure should not be silently transformed into
plausible-looking data.
A human rejection or request for another intellectual direction is not
necessarily a system failure; it is a legitimate product outcome.
Capability Map
DISCOVERY
├── bounded Scout loop
├── structured actions
├── deterministic authorization
├── fake and real web tools
└── bounded failure recovery
WEB INFRASTRUCTURE
├── provider-neutral contracts
├── Brave Search adapter
├── bounded HTTP reader
├── network / SSRF guardrails
├── main-content extraction
└── content-density fallback
CONTEXT
├── normalization
├── duplicate-line removal
├── token counting
├── per-component truncation
└── cumulative Research read budget
OPPORTUNITY
├── semantic signal evaluation
├── deterministic weighted scoring
├── mandatory guardrails
├── HIGH / MEDIUM / LOW
└── deterministic routing
RESEARCH
├── bounded semantic loop
├── SEARCH / READ / EXTRACT / FINISH
├── source authorization
├── evidence provenance
└── ResearchBrief
CONVERSATION INTELLIGENCE
├── ArgumentBrief contracts
├── Argument Intelligence
├── Perspective / PerspectiveSet contracts
├── Perspective Generation
├── SelectedPerspective contract
└── Human Perspective Selection boundary
GENERATION & QUALITY
├── selected-perspective-aware Writer
├── content-mode-aware materialization
├── Rodrigo Voice personalization
├── Quality Evaluator
├── bounded revision loop
└── final human refinement
EXPERIENCE & MEMORY
├── editable human theme / intent
├── LinkedIn Post / Reply / Article modes
├── on-demand Portuguese translation
├── navigable run history
└── separation of product history from Interaction Memory
ORCHESTRATION & GOVERNANCE
├── LangGraph workflow
├── explicit shared state
├── deterministic routing
├── structured contracts
├── Human-in-the-Loop boundaries
└── human publication authority
The core Conversation Intelligence flow is integrated. Experience-layer
capabilities may be described here as the approved MVP target before all of
them are implemented. This capability map must therefore be read together
with 02_current_architecture.md for the exact implemented topology.
Validation State
The project has extensive automated unit and integration coverage,
deterministic fake-tool validation, and real-tool smoke validation.
Real-tool smoke validation has demonstrated important infrastructure
boundaries including:
Scout
OpenAI reasoning
- real search
- real reading
- content extraction
- bounded context
Research
OpenAI reasoning
- real search
- real reading
- evidence extraction
- provenance
- ResearchBrief
Automated test counts are development snapshots rather than
architectural invariants and should be recorded in the current
implementation/audit context rather than treated as a permanent design
property of this document.
Roadmap to MVP
Increment         Delivery                                           Architectural
Impact
1                 Argument          ArgumentBrief, Perspective, PerspectiveSet,  Creates the
Contracts v0.1    SelectedPerspective                              formal language
of the new
architecture
2                 Argument          ResearchBrief -> ArgumentBrief                   Separates
Intelligence v0.1                                                    research from
positioning
3                 Perspective       ArgumentBrief -> 2–4 defensible perspectives     Implements AI
Generation v0.1                                                      expands
4                 Human Perspective Human selects / rejects / combines / guides        Implements
Selection v0.1    perspective                                        Human
converges
5                 Writer / Voice    SelectedPerspective -> Rodrigo Voice -> Writer   Implements AI
Integration v0.1                                                     materializes
6                 LangGraph         Complete new flow + HITL + routing                 Transforms
Integration                                                          components into
an integrated
system
7                 MVP Experience    Editable theme, content mode, final human            Converts the
                  Layer v1.0       refinement, on-demand translation, run history       validated agentic
                                                                                          workflow into a
                                                                                          navigable product
                                                                                          experience
The roadmap is sequential at the architectural level, even when
implementation work overlaps between adjacent increments.
Current Architectural Boundaries
Still intentionally incomplete or unresolved outside the MVP closure
path:
production LinkedIn-specific discovery;
reliable LinkedIn engagement metadata;
objective Engagement Potential calculation;
multiple-candidate orchestration;
production-grade observability;
production deployment architecture;
long-term model routing and cost telemetry;
real-world scoring calibration;
advanced Human-in-the-Loop UX beyond the MVP Experience Layer;
Performance Analytics and Feedback Learning;
adaptive policy calibration;
autonomous publication.
These items must not distract from closing the frozen MVP.
Architectural Direction
The system is evolving toward:
semantic intelligence
        +
deterministic governance
        +
bounded tools
        +
explicit state
        +
evidence provenance
        +
argument intelligence
        +
human intellectual convergence
        +
personalized materialization
        +
quality evaluation
        +
human ownership
The architecture is not optimized for maximum autonomy.
It is optimized for useful autonomy under explicit human control,
with AI expanding the decision space and the human retaining authority
over both intellectual direction and publication.