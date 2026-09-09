Cloud Deployment

Purpose

This document records the current deployment status, deployment requirements, and architectural constraints for the LinkedIn Agentic AI System.

It does not define a final cloud architecture.

No cloud provider, hosting topology, persistence technology, message broker, observability stack, or autoscaling strategy has been formally selected yet.

The purpose of this file is therefore to prevent premature infrastructure assumptions while establishing the constraints that any future deployment must preserve.

Current Status

Production cloud deployment
    NOT IMPLEMENTED

Cloud provider
    NOT SELECTED

Production persistence
    NOT SELECTED

Production observability stack
    NOT SELECTED

Production secret-management solution
    NOT SELECTED

Production LinkedIn-native integration
    NOT IMPLEMENTED

The project is currently being validated primarily as an application/runtime architecture.

The active priority remains correctness of:

agent behavior
workflow routing
tool boundaries
evidence provenance
context limits
quality evaluation
human publication authority

before production infrastructure is introduced.

Why Deployment Is Intentionally Deferred

A deployment architecture should serve the validated product architecture.

It should not force premature decisions into the application.

Current unresolved product/runtime questions include:

LinkedIn-native access
multiple-candidate orchestration
production-grade observability
model routing
long-term cost telemetry
human approval UX
queue persistence
engagement metadata acquisition

These can materially influence the right deployment design.

Selecting infrastructure too early could create unnecessary coupling or rework.

Deployment Principle

Future deployment must preserve the same architectural boundaries established in local execution.

Cloud deployment must not collapse:

semantic reasoning
deterministic governance
workflow orchestration
tool execution
human authority

into an opaque runtime.

A deployment platform is an execution environment, not a replacement for application architecture.

Minimum Runtime Components

A future deployed system will likely require at least the following logical runtime roles.

Application / Orchestration Runtime

Responsible for:

LangGraph workflow execution
Python deterministic logic
component invocation
routing
state transitions
configuration loading

This may initially run as a single service.

The architecture does not currently require distributed microservices.

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

A deployed environment must provide outbound HTTPS access to the configured search provider.

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

A production deployment should use the selected platform's secret-management mechanism once a provider is chosen.

No specific secret-management product is mandated yet.

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

The current project does not yet define a production public API or frontend contract.

A future deployment may expose:

HTTP API
web UI
human approval interface
agent-execution status
results/review interface

but those interfaces should be designed as separate product capabilities.

They should not be invented solely to make the project deployable.

Human Approval Boundary

Cloud deployment must preserve the rule:

AI prepares
AI evaluates
Human decides

A hosted version must not turn a quality PASS into automatic publication.

Any future approval interface should distinguish:

ready for review
approved by human
published externally

as separate states.

Persistence

Persistent storage is not yet formally designed.

Potential future persistence needs may include:

candidate opportunities
ResearchBrief artifacts
generated drafts
quality evaluations
human feedback
approval status
execution traces
token/cost metrics
tool-call metadata
outcome history

The current application should not be prematurely coupled to a specific database.

A persistence architecture should be designed when the lifecycle and retention requirements are clear.

State Durability

Current LangGraph workflow state should not automatically be treated as the long-term system-of-record schema.

There is an important distinction between:

execution state
        and
business/history persistence

Future deployment must decide:

which workflow state must survive process failure;

which artifacts should be retained historically;

which data should be ephemeral;

whether human approval requires durable checkpoints;

how retries and resumed executions should behave.

These decisions remain open.

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

The likely initial deployment shape is a single application unit containing:

Python application
LangGraph orchestration
agent runtimes
deterministic components
web-tool adapters
context preparation
configuration

This is a logical direction, not a frozen provider-specific deployment decision.

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
writing
evaluating quality
revision required
ready for human review

This UI concern should remain decoupled from the orchestration engine.

The workflow should emit meaningful state/events; the frontend should decide how to represent them.

Cloud Provider Selection Criteria

When a provider decision becomes necessary, evaluate candidates against the application rather than choosing by habit.

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

Possible Future Topology

A potential future topology could look like:

User / Review UI
        |
        v
Application API
        |
        v
Workflow Runtime
   |       |       |
   v       v       v
 LLM     Search   Reader
Provider Provider  Web
        |
        v
Optional Persistence
        |
        v
Telemetry / Audit

This is illustrative only.

It is not a committed deployment architecture.

What Must Not Be Assumed Yet

Do not describe the project as currently using:

AWS
Azure
Google Cloud
Kubernetes
serverless
PostgreSQL
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

complete real end-to-end workflow validation
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

The current next development increment remains:

End-to-End Real Workflow Validation v0.1

Deployment work should not displace that validation.

A successful real integrated run will provide stronger evidence for what the eventual runtime and observability architecture actually need.

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

The current deployment architecture is intentionally:

UNDECIDED

but the deployment constraints are not.

Any future hosting solution must preserve:

bounded autonomy
deterministic governance
safe external tools
explicit context budgets
evidence provenance
observable workflow execution
cost awareness
human publication authority

The correct cloud architecture should emerge from the validated product and runtime requirements, not precede them.
