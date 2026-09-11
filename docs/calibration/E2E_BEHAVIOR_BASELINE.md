E2E BEHAVIOR BASELINE — LinkedIn Agentic AI System

1. Purpose

This document preserves the first consolidated real-web behavioral baseline for the
LinkedIn Agentic AI System.

The objective is to record what the system actually did across repeated unchanged E2E
runs before changing thresholds, Scout budgets, Research behavior, or routing policy.

This file is experimental evidence.

It is not a production specification and individual observations must not be converted
directly into permanent rules.

2. Experimental Conditions

The runs used the same production Scout objective and the same current workflow logic.

During this battery:

no HIGH threshold was lowered;

no Scout objective was changed to force different outcomes;

Interaction Memory remained active;

real web tooling remained active;

the SQLite memory database was not intentionally cleared between runs;

no production prompt was altered between individual runs merely to obtain a HIGH;

downstream Research, Writer, and Evaluator only ran when routing allowed them.

The intent was behavioral observation rather than benchmark optimization.

3. Consolidated Run Table

Run

Outcome

Opportunity Score

Research

Total Tokens

1

HIGH

83.45

Yes -> PASS

104,783

2

NO_CANDIDATE_FOUND

—

No

8,452

3

MEDIUM

79.45

No

15,297

4

NO_CANDIDATE_FOUND

—

No

5,160

5

MEDIUM

79.75

No

16,889

6

MEDIUM

79.60

No

16,350

7

NO_CANDIDATE_FOUND

—

No

5,937

8

NO_CANDIDATE_FOUND

—

No

4,514

4. Outcome Distribution

Across eight runs:

HIGH: 1/8

MEDIUM: 3/8

NO_CANDIDATE_FOUND: 4/8

LOW routed outcome: 0/8

runs that reached downstream Research: 1/8

The system did not manufacture content merely because an E2E execution was started.

Half of the runs correctly terminated without a candidate.

Three more found relevant candidates but classified them as MEDIUM, preventing expensive
downstream Research and writing.

5. HIGH Baseline Run

Run 1 selected:

https://www.scmr.com/article/how-agentic-ai-changes-supply-chain-operations

Opportunity classification:

HIGH

score: 83.45

This run represents the original expensive Research baseline that motivated the current
Token Governance work.

Observed total E2E usage:

total tokens: 104,783

input tokens: 100,904

output tokens: 3,879

captured reasoning tokens: 721

LLM calls: 22

Research alone consumed approximately:

75,474 total tokens

14 LLM calls

47.85 seconds of captured LLM latency

Research ended with:

LIMIT_REACHED

despite having already produced useful evidence and a final draft that passed the Quality
Evaluator.

This mismatch is the main empirical motivation for Gap-Driven Research.

Important limitation:

This HIGH run occurred before the current Gap-Driven Research behavior was validated in a
new real E2E execution.

Therefore no token-saving claim should yet be made for the new Research contract.

6. MEDIUM Cluster

Three independent runs produced MEDIUM classifications:

Run

Score

3

79.45

5

79.75

6

79.60

Range:

79.45 -> 79.75

All three remained below the current HIGH threshold of 80.

The cluster is notable because it is narrow and repeated, but it is not yet evidence that
the threshold is wrong.

Across these cases, topic relevance and positioning fit were high while contribution
potential was the main limiting dimension.

Current interpretation:

The evaluator may be successfully distinguishing between:

highly relevant material; and

material that creates a sufficiently differentiated contribution.

No threshold change should be made solely from these three observations.

7. NO_CANDIDATE_FOUND Behavior

Runs 2, 4, 7, and 8 ended with:

NO_CANDIDATE_FOUND

Observed total token usage:

Run

Tokens

2

8,452

4

5,160

7

5,937

8

4,514

These outcomes are valid E2E results.

They indicate that the system can stop without forcing a candidate when the Scout does
not find a sufficiently useful opportunity within the current bounded process.

However, repeated no-candidate outcomes create an evidence-backed calibration question:

Is the Scout search budget too restrictive for a persistent-memory system that must
increasingly search beyond previously visited URLs?

This question remains open.

8. Interaction Memory Observation

Across repeated runs, Scout behavior was consistent with persistent URL-level novelty
filtering.

Previously selected or visited material was not observed being repeatedly recycled as
the next candidate.

This supports the current Interaction Memory design operationally.

Important limitation:

The current memory model is URL-level identity.

It does not yet provide semantic deduplication across different URLs that may discuss the
same article, thesis, event, or idea.

Therefore this experiment should not be described as proof of semantic novelty.

9. Token Governance Observation

The eight-run battery reinforces that downstream Research is the dominant token-risk area.

The original HIGH run consumed approximately 104.8k E2E tokens, while NO_CANDIDATE runs
were roughly 4.5k-8.5k tokens and MEDIUM runs roughly 15.3k-16.9k tokens.

This supports the current governance principle:

cheap discovery -> selective reading -> opportunity gating -> expensive research only when justified

The Gap-Driven Research contract was introduced to reduce unnecessary continuation after
useful evidence already exists.

It has passed automated tests but still requires a controlled real validation.

10. Context Preparation Observation

In the original HIGH baseline, context preparation materially reduced stored web context.

Observed examples included:

Scout READ: 2,939 -> 1,800 tokens

Research READ: 5,391 -> 2,500 tokens

Research READ: 6,761 -> 2,500 tokens

Across those observed reads:

15,091 original tokens -> 6,800 prepared tokens

This is approximately a 55% reduction.

Current interpretation:

The existing context-preparation layer is already useful and should not be treated as the
primary optimization target before the Research loop itself is validated.

11. Latency Observation

Latency showed large variance between runs.

Examples:

Run 4:

workflow: 26.05 s

captured LLM: 24.50 s

remainder: 1.55 s

Run 6:

workflow: 166.11 s

captured LLM: 62.63 s

remainder: 103.47 s

Run 8:

workflow: 138.20 s

captured LLM: 56.41 s

remainder: 81.79 s

The remainder must not be described as pure web latency.

Current telemetry does not isolate:

SEARCH latency;

READ latency;

network delay;

provider delay;

tool runtime;

orchestration overhead.

Future Web / Tool Latency Observability is justified, but it is not part of the current
calibration closure.

12. Scout Search-Budget Hypothesis

The repeated no-candidate outcomes suggest that the Scout search budget should be
reviewed.

The correct question is not simply whether to increase a single hard step limit.

The system should distinguish the costs of:

raw SEARCH;

READ;

Scout LLM decisions;

novelty retries;

context growth;

downstream Research.

Because raw web search is comparatively cheap and Interaction Memory increases the effort
required to find novel material over time, a future Adaptive Scout Search Budget may be
preferable to a single fixed low ceiling.

Possible future policy:

start with normal bounded search
-> if results are known / non-novel, allow targeted reformulation
-> preserve selective READ
-> stop on strong candidate, repeated lack of novelty, or hard ceiling

This remains a design hypothesis.

No Scout budget change has yet been justified by direct per-operation search telemetry.

13. Controlled Research Validation Required

The natural repeated-run battery should stop at eight runs.

Continuing to rerun Scout until a random HIGH appears would consume resources without
improving experimental control.

The next scientifically useful validation is controlled:

reuse a known HIGH opportunity;

invoke the current Gap-Driven Research under current production logic;

capture telemetry;

compare with the original Research baseline.

Compare:

Research LLM calls;

total/input/output tokens;

decision-prompt growth;

terminal status;

EvidenceItem count and quality;

ResearchBrief size;

latency;

Writer/Evaluator quality if downstream execution is included.

Do not lower the production HIGH threshold merely to manufacture a Research run.

14. Product-Direction Observation

The experiment also exposed a product-design opportunity.

A candidate that is only MEDIUM for COMMENT may still be valuable as raw material for an
AUTHORIAL_POST.

Future opportunity evaluation should therefore consider separate content intents instead
of assuming every discovery has only one possible use.

Candidate future outcomes:

IGNORE
COMMENT
AUTHORIAL_POST
COMMENT + AUTHORIAL_POST
SAVE_FOR_LATER

This product expansion is intentionally recorded here as a future architectural direction.

It should not alter the interpretation of this eight-run behavioral baseline.

15. Baseline Conclusions

Current evidence supports the following conclusions:

The system is capable of terminating without forcing content.

Opportunity gating is preventing unnecessary downstream Research in MEDIUM cases.

Interaction Memory behavior is consistent with persistent URL diversification.

Three MEDIUM opportunities formed a narrow 79.x calibration cluster.

The original Research loop was the dominant token consumer in the HIGH baseline.

Gap-Driven Research still requires a controlled real E2E validation.

Existing context preparation is already materially reducing external-text payload.

Scout search-budget calibration is now an evidence-backed question.

Web/tool latency deserves separate future instrumentation.

No current evidence justifies lowering the HIGH threshold.

16. Experimental Status

Natural repeated-run battery:

COMPLETE — 8 runs

Next experiment:

CONTROLLED GAP-DRIVEN RESEARCH VALIDATION

Production behavior should remain unchanged until that validation is designed and run.
