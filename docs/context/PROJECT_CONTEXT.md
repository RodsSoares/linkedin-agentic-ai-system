# Project Context

## Product Goal

Build an agentic AI system that identifies relevant LinkedIn
interaction opportunities, gathers supporting evidence, writes
comments aligned with Rodrigo's professional voice, evaluates
quality, and keeps a human in control of publication.

## Current Stable Baseline

Commit:

`5d0865e`

Last completed capability:

Deterministic quality evaluation for LinkedIn comments.

## Current Workflow

Current active workflow:

START → Writer → Evaluator

Evaluator routing:

- PASS → Human / END
- REVISE → Writer
- REJECT → END

Revision loops are bounded by a maximum iteration limit.

## Implemented Capabilities

- PostCandidate schema
- Writer component
- Rodrigo Voice prompt
- Quality Evaluator
- Structured quality evaluation
- Deterministic PASS / REVISE / REJECT decision
- Controlled revision loop
- LangGraph workflow
- Automated tests

## Current Development Objective

Harden the Project Context Snapshot so development can resume
with reliable context recovery across sessions and AI agents.

After this isolated audit increment is validated and committed,
development returns to Opportunity Evaluation.

## Current WIP

Project Context Snapshot v1.6.

This isolated WIP improves development continuity without changing
the LinkedIn agent workflow itself.

Changes in this WIP:

- real SHA-256 project-content fingerprint for snapshot integrity;
- explicit consistency checks between repository facts and
  human-maintained context;
- formal separation between stable baseline, current WIP, and
  next planned capability;
- preservation of recent commits, detailed working tree,
  test execution, test discovery, dependencies, and human context.

The LinkedIn workflow remains unchanged during this WIP.

## Planned Workflow Direction

Scout
→ Opportunity Evaluation
→ Research
→ Writer
→ Quality Evaluator
→ Human-in-the-loop

The exact implementation remains incremental and must preserve
controlled routing.

## Architectural Principles

- Human-in-the-loop is mandatory before publication.
- The system must never publish autonomously.
- Prefer deterministic decisions where deterministic logic
  provides sufficient reliability.
- Use LLM reasoning where semantic understanding adds material
  value.
- Use structured outputs between AI components.
- Keep agent autonomy bounded.
- Preserve explicit workflow state.
- Bound retries and revision loops.
- Treat LLM consumption as computational infrastructure.
- Apply cost-aware orchestration and token governance.
- Reserve expensive/frontier models for high-value reasoning.
- Prefer cheaper models or deterministic logic where quality
  requirements can still be satisfied.

## Explicit Non-Goals

- Autonomous LinkedIn publication.
- Unbounded autonomous browsing.
- Unbounded agent-to-agent loops.
- Using an LLM for decisions that can be reliably deterministic.
- Building unrelated platform capabilities before the current
  workflow is operational.
- Expanding Project Context Snapshot v1.6 into AST analysis,
  LangGraph introspection, JSON output, schema extraction,
  capability inference, or architecture linting.

## Current Development Status

Stable baseline:

`5d0865e`

Current test baseline:

8 passing tests.

Repository state during Project Context Snapshot v1.6 is expected
to be dirty until this isolated audit increment is validated and
committed.

## Next Planned Capability

Opportunity Evaluation / Opportunity Scoring.

After Project Context Snapshot v1.6 is validated and committed,
implementation must resume from the new clean baseline.

Opportunity Evaluation should be introduced incrementally with
tests before integration into the main workflow.

## Context Maintenance Rule

Update this file whenever any of the following changes:

- current development objective;
- stable baseline;
- current WIP;
- completed capability;
- workflow architecture;
- architectural principle;
- frozen decision;
- explicit non-goal;
- test baseline;
- next planned capability.

The Project Context Snapshot incorporates this file so that a new
human or AI development session can reconstruct project intent
without relying on previous conversation history.
