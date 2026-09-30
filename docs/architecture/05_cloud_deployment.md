Cloud Deployment

Purpose

This document records the current deployment status, deployment requirements, and architectural constraints for the LinkedIn Agentic AI System.

It documents both the deployment constraints established before hosting and the cloud architecture that has now been implemented and validated for the current MVP.

The initial provider/runtime and persistence decisions are now established:

Render Free Web Service for the Python/Streamlit application runtime;

Supabase PostgreSQL for durable cloud persistence;

PostgresSaver for LangGraph checkpoint/HITL state;

PostgreSQL repositories for Interaction Memory and Run History / Product Memory.

A message broker, distributed autoscaling architecture, production-grade observability stack, and multi-user authentication model remain intentionally unselected because the current validated MVP does not require them.

The purpose of this file is therefore twofold:

preserve the original deployment constraints that prevented premature infrastructure coupling;

record the actual deployed topology and the remaining post-MVP hardening boundaries.

Current Status

Public cloud deployment
IMPLEMENTED AND SMOKE VALIDATED

Application hosting
RENDER FREE WEB SERVICE

Cloud persistence
SUPABASE POSTGRESQL

LangGraph cloud checkpoint backend
POSTGRESSAVER

Interaction Memory cloud backend
POSTGRESQL

Run History / Product Memory cloud backend
POSTGRESQL

Production-grade observability stack
NOT YET SELECTED

Production-grade multi-user authentication
NOT IMPLEMENTED

Secret handling for current deployment
RENDER ENVIRONMENT VARIABLES / SECRETS

Production LinkedIn-native integration
NOT IMPLEMENTED

The project has now been validated as both an application/runtime architecture and a deployed portfolio/MVP application.

The active priority remains correctness of:

agent behavior
workflow routing
tool boundaries
evidence provenance
context limits
argument intelligence
human perspective selection
quality evaluation
human intellectual authority
human publication authority

before production infrastructure is introduced.

Why Deployment Was Intentionally Deferred

The deployment architecture was intentionally deferred until it could serve the validated product architecture rather than force premature infrastructure decisions into the application.

That sequencing is now complete for the current MVP: the product architecture was validated first, then deployed without reopening its core reasoning boundaries.

Post-MVP product/runtime questions still include:

LinkedIn-native access
multiple-candidate orchestration
production-grade observability
model routing
long-term cost telemetry
human approval UX
queue persistence
engagement metadata acquisition

These can materially influence the right deployment design.

The selected Render/Supabase topology was introduced only after the core workflow and experience layer were sufficiently stable, reducing unnecessary coupling and rework.

Deployment Principle

Cloud deployment preserves the same architectural boundaries established in local execution.

Cloud deployment must not collapse:

semantic reasoning
deterministic governance
workflow orchestration
tool execution
human authority

into an opaque runtime.

A deployment platform is an execution environment, not a replacement for application architecture.

Minimum Runtime Components

The deployed system contains the following logical runtime roles.

Application / Orchestration Runtime

Responsible for:

LangGraph workflow execution
Python deterministic logic
component invocation
routing
state transitions
configuration loading

This currently runs as a single Render Web Service.

The architecture does not require distributed microservices for the current validated scope.

LLM Provider Access

The runtime requires outbound access to configured LLM APIs.

Current LLM-dependent capabilities include:

Scout semantic decisions
Opportunity semantic evaluation
Research semantic decisions
Research synthesis
Writer generation
Quality evaluation

Model selection may evolve independently by component.

The deployment architecture must therefore avoid hardcoding one model assumption across the entire system.

Web Search Provider Access

Current real search uses Brave Search through the provider-neutral SearchTool interface.

The deployed Render environment provides outbound HTTPS access to the configured search provider.

The application-facing contract must remain provider-neutral.

Web Reading Access

Research and Scout can invoke the bounded HTTP reader.

The deployed environment must allow controlled outbound network access while preserving:

URL validation
DNS resolution
private/non-global IP rejection
redirect revalidation
timeouts
content-type restrictions
response-size limits

Cloud networking must not weaken these application-level protections.

Configuration

Runtime configuration should remain environment-driven.

Representative configuration categories include:

LLM credentials
search-provider credentials
WEB_TOOL_MODE
model configuration
token/context budgets
timeouts
runtime limits
environment identity
logging level

Environment-specific configuration should remain separate from source code.

Secrets

Secrets must never be committed to Git.

Examples include:

OPENAI_API_KEY
BRAVE_SEARCH_API_KEY
future provider credentials
future database credentials
future OAuth secrets

Local development can use ignored environment files.

The current Render deployment stores environment-specific secrets outside Git through the platform environment configuration.

A separate enterprise secret-management product is not required by the current portfolio/MVP scope.

Network Security

Any deployment must treat agent-accessible outbound networking as a security boundary.

The system must not rely solely on cloud-level firewalling.

Application-level protections remain mandatory because URLs can originate from agent decisions.

Required properties include:

HTTP/HTTPS-only policy where applicable
localhost blocking
private-address blocking
DNS validation
redirect-target validation
request timeout
response-size cap
content-type checks
controlled failure handling

Additional cloud egress restrictions may complement these controls.

They should not replace them.

Inbound Surface

The current deployed product surface is the Streamlit web UI.

It exposes:

editable human theme / intent;
workflow progress;
opportunity artifacts;
research / argument / perspective artifacts;
Human Perspective Selection;
Human Content Mode Selection;
Final Human Refinement;
on-demand Portuguese translation;
Run History / Product Memory.

A separate public HTTP API is not required by the current MVP and should not be invented solely to make the project appear more production-like.

Human Approval Boundary

Cloud deployment must preserve the rule:

AI expands
Human converges
AI materializes
AI evaluates
Human owns

A hosted version must not turn a quality PASS into automatic publication.

Any future approval interface should distinguish:

ready for review
approved by human
published externally

as separate states.

Persistence

Persistent storage is now implemented for the current MVP, while longer-term retention, migration, backup, and multi-user governance remain future hardening concerns.

Potential future persistence needs may include:

candidate opportunities
ResearchBrief artifacts
ArgumentBrief artifacts
PerspectiveSet artifacts
SelectedPerspective / human guidance
generated drafts
quality evaluations
human feedback
approval status
execution traces
token/cost metrics
tool-call metadata
outcome history

The application remains repository/checkpointer-driven rather than coupling semantic components directly to database-specific behavior.

For cloud execution, Supabase PostgreSQL is the selected durable store. Local execution retains InMemorySaver/SQLite implementations.

State Durability

Current LangGraph workflow state should not automatically be treated as the long-term system-of-record schema.

There is an important distinction between:

execution state
and
business/history persistence

The current implementation resolves the principal MVP durability questions:

LangGraph workflow/HITL checkpoint state survives through PostgresSaver;

Interaction Memory persists through its PostgreSQL repository;

Run History / Product Memory persists through its PostgreSQL repository;

Streamlit session_state remains ephemeral.

Automatic frontend reconstruction of an interrupted HITL run after process/session loss remains open as a product-resilience backlog item.

Queueing and Asynchronous Execution

A queue/broker is not currently an architectural requirement.

The present workflow can remain synchronous while product behavior is validated.

A future queue may become justified if the system introduces:

long-running research
multiple concurrent opportunities
scheduled discovery
background monitoring
human approval waiting states
retry orchestration
rate-limit smoothing

If this happens, the queue should support an actual product/runtime requirement rather than being added for architectural fashion.

Observability

Production deployment will require stronger observability than the current development environment.

Future observability should distinguish at least:

workflow execution
node transitions
LLM calls
tool calls
tool failures
agent decisions
token usage
latency
cost
context truncation
Research evidence counts
quality outcomes
revision counts
human decisions

Sensitive prompts, evidence, credentials, and personal data must not be logged indiscriminately.

The exact telemetry stack is not yet selected.

Cost Telemetry

The project already treats LLM consumption as computational infrastructure.

A future deployment should make cost measurable at useful boundaries, potentially including:

per workflow
per component
per model
per tool
per opportunity
per successful contribution

The target optimization principle is:

Use the lowest inference cost capable of satisfying the required Quality Contract.

A provider/platform choice should eventually support this observability rather than obscure it.

Reliability

Future deployment should define explicit handling for:

LLM timeout
search timeout
reader timeout
provider rate limit
provider outage
invalid structured output
external page rejection
workflow interruption
human approval delay
process restart

Existing bounded agent recovery should remain intact.

Infrastructure retries must not accidentally multiply agent-level retries without a defined policy.

Retry Layers

Deployment design must distinguish:

provider/client retry
tool-level retry
agent-level recovery
workflow-level retry

These are different mechanisms.

Uncoordinated retries can cause:

duplicate requests
higher inference cost
unexpected loops
rate-limit amplification
duplicate external actions

Future production hardening should define ownership for each retry layer.

Scalability

No current evidence requires distributed scaling.

The system should initially favor operational simplicity.

Scale-out decisions should follow observed bottlenecks such as:

concurrent workflows
LLM latency
web-tool throughput
background discovery volume
human-review queues
database load

Premature microservice decomposition is not an architectural goal.

Deployment Unit

The current deployment shape is a single application unit containing:

Python application
LangGraph orchestration
agent runtimes
deterministic components
web-tool adapters
context preparation
configuration

This is now the implemented provider-specific deployment shape for the current MVP.

Specialist components should remain modular in code even if they share one process.

Containerization

Containerization may be useful for reproducible deployment.

However:

Docker/Kubernetes

are not currently architectural requirements.

A container should be introduced when it improves:

environment reproducibility
deployment portability
dependency isolation
CI/CD

Kubernetes should only be introduced if scale or operational requirements justify its complexity.

CI/CD

A future deployment pipeline should preserve the existing development quality gates.

At minimum, deployment should not proceed from a revision that fails:

automated tests
project audit consistency
configuration validation
security-sensitive checks

The current project checkpoint discipline should inform later CI/CD rather than be discarded.

Environment Separation

Future hosted environments should distinguish at least:

development
test/staging
production

Real external tools should not automatically be enabled in every environment.

For example:

tests
fake/mocked tools

staging
optional controlled real tools

production
configured production tools

This maintains deterministic automated validation while allowing real integration testing.

Real vs Fake Tool Configuration

WEB_TOOL_MODE is currently an explicit runtime selector.

A deployed environment should make the selected mode visible and auditable.

A production environment must not silently fall back to fake data if real infrastructure is unavailable.

Likewise, automated tests should not accidentally consume production API credentials or live quotas.

External Provider Abstraction

The current application contracts intentionally separate agents from external providers.

Deployment architecture should preserve:

SearchTool
ReadTool
LLM client boundary

rather than wiring provider-specific structures throughout the application.

This keeps provider migration and multi-provider routing possible later.

Data Protection

A production deployment may process:

public web content
professional-profile information
generated text
human feedback
possibly authenticated platform data in the future

Before production use, retention, access control, logging, deletion, and regional/privacy requirements must be explicitly assessed.

The current project has not yet established a production data-governance policy.

Authentication and Authorization

The current system does not define production user authentication.

A future product deployment will need to distinguish at minimum:

who can start a workflow
who can inspect research
who can edit a draft
who can approve publication
who can configure credentials/tools

Publication approval authority should receive stronger protection than read-only access.

Human Approval UX

The future deployment should make agent progress observable rather than presenting a long opaque request.

A useful future interaction model may expose states such as:

discovering
evaluating opportunity
researching
preparing evidence
building argument space
generating perspectives
waiting for human perspective selection
writing selected direction
evaluating quality
revision required
ready for final human review

This UI concern should remain decoupled from the orchestration engine.

The workflow should emit meaningful state/events; the frontend should decide how to represent them.

Cloud Provider Selection Criteria

The initial provider decision was evaluated against the application rather than chosen as a target architecture in advance.

Important criteria include:

simple Python hosting
secure secrets
controlled outbound networking
logging/metrics
background execution support
persistent storage options
cost transparency
region availability
CI/CD integration
ease of operations
ability to preserve human approval state

Provider lock-in should be justified by material product value.

Earlier Illustrative Topology and Current Realization

A potential future topology could look like:

User / Review UI
\|
v
Application API
\|
v
Workflow Runtime
\| \| \|
v v v
LLM Search Reader
Provider Provider Web
\|
v
Optional Persistence
\|
v
Telemetry / Audit

This diagram was originally illustrative. The implemented MVP is simpler: Streamlit, LangGraph, and the Python application share one Render service, while Supabase PostgreSQL provides durable cloud persistence.

Infrastructure That Must Not Be Assumed

Do not describe the project as currently using infrastructure that has not been implemented.

Current explicit infrastructure includes PostgreSQL through Supabase.

The project should not be described as using:

AWS
Azure
Google Cloud
Kubernetes
serverless architecture
Redis
Kafka
Celery
Docker
Terraform
a production vector database
a production API gateway

unless one of these is explicitly implemented and accepted later.

The absence of a choice is intentional.

Deployment Readiness Gates

Before calling the system production-deployable, at minimum the project should establish:

complete Human-Centered real end-to-end workflow validation
production configuration model
secret-management approach
persistent state requirements
human approval persistence
production observability
retry ownership
provider failure behavior
authentication/authorization
data-retention policy
deployment rollback strategy
security review of outbound tool access

Not all of these must require complex infrastructure, but each must be consciously addressed.

Current Next Step

The frozen Human-Centered MVP, Experience Layer, and current cloud-deployment milestone are complete.

The immediate work is documentation reconciliation and release hygiene while preserving the 437-test regression baseline.

Post-MVP work should be selected from explicit backlog items rather than reopening validated core reasoning architecture.

One concrete resilience backlog item is automatic Resume Run after Streamlit session/process loss.

Implemented Cloud Topology

The current deployed topology is:

Browser
\|
v
Render Free Web Service
\|
+--\> Streamlit frontend
+--\> LangGraph orchestration
+--\> Python deterministic governance
+--\> Scout / Research bounded agents
+--\> Argument Intelligence / Perspective Generation
+--\> Writer / Quality Evaluator
\|
+--\> OpenAI API
+--\> Brave Search API
+--\> bounded HTTP reader
\|
v
Supabase PostgreSQL
\|
+--\> LangGraph checkpoint / HITL state
+--\> Interaction Memory
+--\> Run History / Product Memory

Render Configuration

Repository branch:

main

Build command:

pip install -r requirements.txt

Start command:

PYTHONPATH=. streamlit run app/frontend/main.py --server.address 0.0.0.0 --server.port \$PORT

The explicit repository-root PYTHONPATH is required because Streamlit executes
app/frontend/main.py and the application imports modules through the app package.

The initial deployment attempt exposed this boundary directly: the application
built successfully but could not resolve the app package until the runtime
PYTHONPATH was made explicit.

Declared Runtime Dependencies

The deployed requirements include the application dependencies plus cloud
persistence/runtime dependencies required by the selected topology.

Relevant additions include:

psycopg\[binary\]
langgraph-checkpoint-postgres
streamlit

The Streamlit package must be declared explicitly in requirements because Render
installs only the repository dependency set.

Environment Configuration

The deployed Render service uses environment configuration including:

OPENAI_API_KEY
BRAVE_SEARCH_API_KEY
WEB_TOOL_MODE=real
DATABASE_URL
PERSISTENCE_BACKEND=postgres

Secret values are never part of this document and must remain outside Git.

Supabase Connection Mode

The cloud database connection uses the Supabase Session Pooler rather than
assuming a direct IPv6-capable PostgreSQL route.

This was selected after direct connection testing exposed network/DNS
compatibility constraints in the deployment path.

The application treats DATABASE_URL as connection information, not as an
implicit persistence selector.

Persistence Backend Selection

app/config/database.py separates:

credentials
from
runtime behavior

Current semantics:

get_database_url()
-\> reads DATABASE_URL

get_persistence_backend()
-\> reads PERSISTENCE_BACKEND
-\> defaults to local

is_postgres_enabled()
-\> true only when backend == postgres and DATABASE_URL exists

This design was introduced after a full-suite test demonstrated that persistent
PostgresSaver state can contaminate a deterministic test when a fixed thread_id
is reused.

The resulting rule is:

local / tests
PERSISTENCE_BACKEND absent
-\> local persistence

Render
PERSISTENCE_BACKEND=postgres
-\> PostgreSQL persistence

LangGraph Cloud Checkpointing

The workflow checkpointer is environment-aware.

Local:
InMemorySaver

Cloud:
PostgresSaver

The cloud PostgresSaver path uses a psycopg connection appropriate for the
LangGraph checkpoint implementation.

Validation created the LangGraph checkpoint tables in Supabase and then proved
cross-instance recovery:

workflow instance 1
-\> execute state with known thread_id
-\> PostgresSaver
-\> Supabase

workflow instance 2
-\> same thread_id
-\> recover persisted state

This establishes that the checkpoint is not tied to one Python process.

Interaction Memory Cloud Persistence

Interaction Memory retains separate local and cloud repository
implementations.

Local:
SQLiteInteractionMemoryRepository

Cloud:
PostgresInteractionMemoryRepository

The cloud implementation was validated for:

repository selection;
initialization;
record creation;
has_seen;
agentic draft persistence;
status transition;
human-final persistence;
recent-history retrieval.

Run History Cloud Persistence

Run History / Product Memory also retains separate local and cloud repository
implementations.

Local:
SQLiteRunHistoryRepository

Cloud:
PostgresRunHistoryRepository

The frontend consumes the repository abstraction rather than owning
database-specific SQLite logic.

Cloud validation covered:

repository selection;
initialization;
create;
get by run_id;
recent-list retrieval;
UPSERT;
updated field recovery.

The deployed Streamlit History also remained available after a Render restart.

Render Restart / HITL Recovery Experiment

A real deployed workflow was intentionally left at the Human Perspective
Selection interrupt.

The Render service was then restarted.

Before restart:

workflow state
-\> HUMAN REQUIRED
-\> HUMAN DECISION

After restart:

PostgresSaver checkpoint
-\> still persisted

Run History
-\> still persisted

Streamlit session_state
-\> lost

frontend
-\> SYSTEM READY

Interpretation:

backend checkpoint durability is validated;

product-history durability is validated;

automatic frontend session reconstruction is not implemented.

The missing capability is not additional database durability.

The missing capability is reconnecting a user-facing run to its persisted
thread_id and rebuilding the correct interrupt UI.

Resume Run Backlog

Future target:

History
\|
+--\> terminal run
\| \|
\| +--\> Open / inspect
\|
+--\> resumable HITL run
\|
+--\> Resume
\|
v
recover thread_id
\|
v
PostgresSaver
\|
v
authoritative checkpoint
\|
v
reconstruct interrupt/UI
\|
v
continue human decision

This capability is explicitly backlog.

It does not block the current deployment milestone.

Free-Tier Runtime Constraint

Render Free may spin down after inactivity and may introduce cold-start latency.

That behavior is acceptable for the current portfolio/MVP target.

It reinforces one architectural rule:

the Render local filesystem is ephemeral infrastructure, not the durable cloud
system of record.

Durable state belongs in Supabase PostgreSQL.

Current Deployment Assessment

The current deployment is appropriately described as:

public;
cloud hosted;
real-tool enabled;
durably persisted;
smoke validated;
suitable for the current portfolio/MVP scope.

It should not be described as:

fully hardened multi-user production SaaS;
production-authenticated;
production-observable at enterprise depth;
horizontally scaled;
autonomously publishing to LinkedIn.

Current automated regression baseline:

437 passing tests.

Maintenance Rule

Update this document when any of the following becomes established:

cloud/provider selection
deployment topology
container strategy
persistence architecture
queue/background execution
public API
human-review frontend
authentication
secret-management mechanism
observability stack
CI/CD deployment pipeline
runtime scaling model
production networking policy

When a major choice becomes durable, also record the rationale in 04_decision_log.md.

Summary

The current MVP deployment architecture is now:

IMPLEMENTED AND VALIDATED FOR CURRENT SCOPE

while the original deployment constraints remain authoritative.

Any future hosting solution must preserve:

bounded autonomy
deterministic governance
safe external tools
explicit context budgets
evidence provenance
observable workflow execution
cost awareness
human publication authority

The selected Render/Supabase architecture emerged from the validated product and runtime requirements rather than preceding them.

MVP-Derived Deployment Requirements

The local MVP now establishes additional runtime requirements that the eventual
cloud architecture must preserve.

These requirements informed the selected Render/Supabase deployment and remain constraints on future evolution.

Human-in-the-Loop Durability

The implemented workflow contains three explicit Human-in-the-Loop boundaries:

Human Perspective Selection
Human Content Mode Selection
Human Final Refinement

The deployed runtime must preserve the ability to interrupt and resume a
workflow using the same thread identity without losing the authoritative graph
state.

Local development currently uses LangGraph checkpoint/thread state to support
this behavior.

Cloud deployment now uses PostgresSaver so checkpoint state can survive
process restart, instance replacement, and application redeploy.

A direct persistence test recovered state from a newly constructed workflow
instance using the same thread_id.

The deployment therefore does not rely on in-memory checkpoint state for cloud
HITL durability.

Multiple concurrent user sessions and automatic frontend reconstruction after
session loss remain separate hardening concerns.

Run History / Product Memory Durability

The local MVP implements product-facing Run History using:

data/history/run_history.db

Local technology:

SQLite

Cloud technology:

PostgreSQL through Supabase

SQLite remains appropriate for local development. PostgreSQL is the durable
cloud system of record for the deployed MVP.

The cloud deployment preserves the conceptual separation between:

LangGraph execution/checkpoint state;
Interaction Memory;
Run History / Product Memory.

All three use Supabase PostgreSQL infrastructure in cloud execution, but through
separate persistence abstractions and responsibilities.

A production history store must preserve stable run identity and prevent a
later incomplete state from degrading a richer completed run.

The production design must also consider:

persistent storage across application redeploys;
concurrent access;
backup and recovery;
schema migration;
retention;
operational observability.

Streamlit Runtime Behavior

The frontend uses Streamlit while workflow execution may continue through
background work and multiple automatic reruns.

The selected hosting model must therefore be validated against:

background workflow execution;
session continuity;
HITL interrupt/resume;
application reruns;
runtime sleep or restart behavior;
persistent storage availability.

A platform that can host Streamlit is not automatically sufficient if its
runtime lifecycle breaks these workflow guarantees.

Bilingual Presentation

Portuguese translation is implemented as an on-demand presentation-layer
operation.

Deployment therefore does not require a duplicated Portuguese reasoning
pipeline.

The deployed application only needs controlled model access for explicit
translation requests in addition to the existing reasoning/model calls.

Secrets and Controlled Egress

The deployed environment must provide secure configuration for external
services used by the application.

At minimum, deployment design must preserve secret isolation for model and
search-provider credentials and controlled outbound access required by:

OpenAI-compatible model calls;
Brave Search;
bounded HTTP reading.

Secrets must not be committed to the repository or embedded in frontend
artifacts.

Current Deployment Gate

The local MVP and current cloud-deployment milestone are closed for the agreed
portfolio/MVP scope.

The former validation gate:

authoritative COMPLETE -\> Run History persistence

has been completed.

The current deployment has also validated:

Render build and Streamlit startup;
public application access;
OpenAI-backed workflow execution;
Brave Search real mode;
Supabase connectivity;
PostgresSaver checkpoint recovery by thread_id;
Interaction Memory PostgreSQL behavior;
Run History PostgreSQL create/read/list/upsert behavior;
Run History survival across Render restart.

Production-grade observability, multi-user authentication, formal data
retention/backup policy, and automatic frontend Resume Run remain post-MVP
hardening concerns.
