System Overview

Purpose

The LinkedIn Agentic AI System is a controlled agentic AI system for discovering strategically relevant professional interaction opportunities, deciding whether they are worth pursuing, researching the evidence required for a defensible contribution, preparing a draft, evaluating its quality, and preserving human authority over publication.

The system is not designed as an autonomous social-media bot.

Its purpose is to reduce the manual effort required to move from:

"Where should I contribute?"

to:

"Here is a researched, evaluated contribution worth reviewing."

while keeping semantic reasoning, deterministic controls, workflow orchestration, and human authority explicitly separated.

Core Product Principle

Opportunity != Popularity

A post is not valuable merely because it has high engagement. A useful opportunity depends on whether the user can make a relevant, differentiated, professionally valuable, and defensible contribution.

High-Level Architecture

External Web / Discussions
          |
          v
        SCOUT
          |
          v
    PostCandidate
          |
          v
 OPPORTUNITY EVALUATION
      /    |     \
    LOW  MEDIUM  HIGH
     |      |      |
    END   QUEUED   v
             |   RESEARCH
            END     |
                    v
              ResearchBrief
                    |
                    v
                  WRITER
                    |
                    v
            QUALITY EVALUATOR
              /     |      \
            PASS  REVISE  REJECT
             |      |       |
             v      +->WRITER
        HUMAN / END          END

Research is only consumed after an opportunity is explicitly accepted. Publication remains outside autonomous execution.

Responsibility Layers

LLM — Semantic Intelligence

The LLM handles tasks where interpretation matters: search strategy, source selection, topic relevance, contribution potential, evidence interpretation, synthesis, writing, and semantic quality assessment.

Python — Deterministic Governance

Python owns validation, scoring, thresholds, guardrails, action authorization, provenance enforcement, counters, operational limits, context budgets, and factual state mutation.

LangGraph — Workflow Orchestration

LangGraph coordinates shared workflow state, node transitions, deterministic routing, bounded revision paths, and termination.

Human — Final Authority

AI discovers
 -> AI evaluates
 -> AI researches
 -> AI drafts
 -> AI evaluates quality
 -> HUMAN DECIDES

Autonomous LinkedIn publication and commenting are explicit non-goals.

LLM interprets and decides semantically; Python governs execution and limits; LangGraph governs workflow; the human retains publication authority.

Scout

Scout is the bounded discovery agent. Its action vocabulary is:

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

The model decides semantically what it wants to do. Python decides whether the action is legal.

Web Tool Layer

Scout and Research use provider-neutral contracts:

SearchTool(query) -> list[SearchResult]
ReadTool(url)     -> str

Two modes are supported:

FAKE MODE -> deterministic tools for isolated tests
REAL MODE -> Brave Search + bounded HTTP reader

The real reader validates network access and includes controls for URL scheme, DNS resolution, localhost/private destinations, redirects, timeouts, content type, response size, and controlled external failures.

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

This prevents arbitrary raw webpages from being treated as clean, unlimited model context.

Current principal budgets:

Scout read context                 <= 1800 tokens
Research per-read context          <= 2500 tokens
Research cumulative read context   <= 8000 tokens

Opportunity Evaluation

Opportunity Evaluation answers:

"Is this opportunity worth pursuing?"

Current weighted dimensions:

Dimension

Weight

Contribution Potential

30%

Positioning Fit

25%

Topic Relevance

20%

Engagement Potential

15%

Research Efficiency

10%

The LLM produces semantic signals. Python calculates the weighted score, applies mandatory guardrails, and produces HIGH, MEDIUM, or LOW.

HIGH   -> ACCEPTED_FOR_RESEARCH -> Research
MEDIUM -> QUEUED -> END
LOW    -> END

Research

Research transforms an accepted opportunity into the minimum evidence package needed for a factual and defensible contribution.

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

A search result is not automatically evidence. A read page is not automatically evidence. Evidence must be explicitly extracted and preserve provenance.

Current principal runtime limits:

max steps           10
max decisions       12
max searches         3
max reads            5
max evidence items   6

Research may terminate as SUFFICIENT, INSUFFICIENT, or LIMIT_REACHED.

Writer

Writer transforms the approved opportunity and ResearchBrief into a professional contribution draft.

Writer does not own discovery, opportunity classification, unrestricted research, quality routing, or publication.

The orchestration layer supplies component-specific input instead of exposing the entire global state indiscriminately.

Quality Evaluator

Opportunity Evaluation and Quality Evaluation solve different problems:

Opportunity Evaluation -> "Should we contribute here?"
Quality Evaluation     -> "Is the generated contribution good enough?"

Quality routing:

PASS   -> Human / END
REVISE -> Writer -> Quality Evaluator
REJECT -> END

Revision is bounded and does not automatically rerun Research.

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
Writer contracts
Quality Evaluation contracts
LinkedInAgentState

Pydantic is preferred at machine-to-machine AI boundaries where practical.

Failure Model

The architecture distinguishes:

semantic failure
operational limit
external infrastructure failure
programming failure

A recoverable web failure can become agent state and permit another bounded decision. A programming failure should not be silently transformed into plausible-looking data.

Implemented Capability Map

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
├── network/SSRF guardrails
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

GENERATION & QUALITY
├── Research-informed Writer
├── Quality Evaluator
└── bounded revision loop

ORCHESTRATION & GOVERNANCE
├── LangGraph workflow
├── explicit shared state
├── deterministic routing
├── structured contracts
└── human publication authority

Validation State

Current automated baseline:

189 passing tests

Real-tool smoke validation has separately demonstrated:

Scout
  OpenAI reasoning
  + real search
  + real reading
  + content extraction
  + bounded context

Research
  OpenAI reasoning
  + real search
  + real reading
  + evidence extraction
  + provenance
  + ResearchBrief

These validate important real infrastructure boundaries but are not equivalent to production readiness.

Current Architectural Boundaries

Still intentionally incomplete or unresolved:

production LinkedIn-specific discovery
reliable LinkedIn engagement metadata
objective Engagement Potential calculation
multiple-candidate orchestration
production-grade observability
production deployment architecture
long-term model routing and cost telemetry
real-world scoring calibration
complete real end-to-end workflow validation

Next Architectural Validation

The next planned increment is:

End-to-End Real Workflow Validation v0.1

Target path:

Real Web
 -> Scout
 -> Opportunity Evaluation
 -> HIGH
 -> Research
 -> Writer
 -> Quality Evaluator
 -> Human / END

The goal is to validate integrated real behavior without weakening existing guardrails merely to produce a successful demonstration.

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
cost/context control
        +
human authority

The architecture is not optimized for maximum autonomy.

It is optimized for useful autonomy under explicit control.
