# Architecture Decision Log

## ADR-001 — Component-specific inputs instead of full orchestration state

**Status:** Accepted  
**Date:** 2026-09-04

### Context

The orchestration layer maintains a shared `LinkedInAgentState` containing
information required across the complete agentic workflow.

Passing the entire state directly to specialized components such as the Writer
would unnecessarily expose data that may not be relevant to their responsibility.
This coupling would increase as the global state grows.

### Decision

The orchestration layer will maintain the global `LinkedInAgentState`, while
specialized components will receive dedicated input contracts containing only
the information required for their responsibility.

Example:

`LinkedInAgentState → writer_node → WriterInput → Writer`

### Rationale

This approach:

- reduces coupling between components and the global state;
- makes component dependencies explicit;
- limits unnecessary data exposure;
- improves testability;
- allows the global state to evolve without forcing changes to unrelated components.

### Consequences

The orchestration layer becomes responsible for mapping the global state into
component-specific inputs.

This introduces a small amount of additional code in exchange for clearer
component boundaries and better maintainability.