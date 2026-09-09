Opportunity Evaluation

1. Purpose

The Opportunity Evaluation capability determines whether a discovered professional discussion represents a sufficiently valuable opportunity to justify further system effort.

Its purpose is not to answer:

"Is this post good?"
"Is this post popular?"
"Will this post maximize impressions?"

It answers:

Is this a good opportunity for Rodrigo to contribute something relevant, differentiated, professionally valuable, and defensible?

Opportunity Evaluation is the strategic resource-allocation gate between candidate discovery and deeper Research.

The implemented HIGH path is now:

Scout
  ↓
PostCandidate
  ↓
Opportunity Evaluation
  ├── LOW    → END
  ├── MEDIUM → QUEUED → END
  └── HIGH   → ACCEPTED_FOR_RESEARCH
                    ↓
                 Research
                    ↓
              ResearchBrief
                    ↓
                  Writer
                    ↓
            Quality Evaluator
              ├── PASS   → Human / END
              ├── REVISE → Writer
              └── REJECT → END

Human publication authority remains mandatory.

2. Current Capability Status

VERSION: v0.1
DESIGN: IMPLEMENTED
SCHEMAS: IMPLEMENTED
DETERMINISTIC SCORING: IMPLEMENTED
SEMANTIC EVALUATION: IMPLEMENTED
WORKFLOW INTEGRATION: IMPLEMENTED
HIGH → RESEARCH ROUTING: IMPLEMENTED
MEDIUM → QUEUED → END: IMPLEMENTED
LOW → END: IMPLEMENTED
AUTOMATED TEST COVERAGE: IMPLEMENTED

Opportunity Evaluation is no longer a design-only capability.

The project has progressed from the original specification into an integrated workflow where HIGH opportunities lead into the bounded Research capability and then into Writer and Quality Evaluation.

The broader project currently has:

189 passing tests

This document therefore describes the implemented v0.1 contract while preserving the original product rationale and calibration assumptions.

3. Core Product Principle

Opportunity is not popularity

A LinkedIn post or professional discussion with high reach, many reactions, or a well-known author is not automatically a high-value opportunity.

A valuable opportunity should combine:

relevance to Rodrigo's professional domains;

alignment with the intended professional positioning;

potential for a meaningful and differentiated contribution;

reasonable engagement potential;

acceptable research effort.

Conceptually:

High audience
+
low contribution potential
        ↓
limited opportunity

while:

Relevant discussion
+
strong positioning fit
+
strong contribution potential
        ↓
high opportunity

The system must not become an engagement bot that prioritizes content simply because it is popular.

4. Responsibility Model

Opportunity Evaluation uses the same responsibility split as the broader architecture.

LLM

The LLM owns semantic interpretation of:

topic_relevance
positioning_fit
contribution_potential
research_cost

Python

Python owns:

input validation
Research Efficiency
Engagement Potential operational input
weighted Opportunity Score
mandatory guardrails
HIGH / MEDIUM / LOW classification

LangGraph

LangGraph owns the workflow transition after classification.

Human

The human retains final publication authority downstream.

The governing pattern is:

LLM interprets semantically; Python scores and classifies deterministically; LangGraph controls what happens next.

The LLM does not directly own HIGH / MEDIUM / LOW.

5. Evaluation Pipeline

PostCandidate
      │
      ▼
Semantic Opportunity Evaluation
      │
      ▼
OpportunitySignals
      │
      ├── topic_relevance
      ├── positioning_fit
      ├── contribution_potential
      └── research_cost
      │
      ▼
Deterministic Application Logic
      │
      ├── engagement_potential
      ├── research_efficiency
      ├── weighted score
      └── mandatory guardrails
      │
      ▼
OpportunityEvaluation
      │
      ▼
HIGH / MEDIUM / LOW
      │
      ▼
Deterministic Workflow Routing

This separation makes the capability:

predictable;

testable;

explainable;

calibratable;

less dependent on a particular model;

easier to evolve without weakening operational control.

6. Evaluation Dimensions

Opportunity Evaluation v0.1 uses five scoring dimensions:

Contribution Potential

Positioning Fit

Topic Relevance

Engagement Potential

Research Efficiency

The semantic evaluator directly estimates Research Cost, which Python converts into Research Efficiency.

All final positive scoring dimensions use:

0–100
higher = better

Research Cost uses:

0–100
higher = more expensive

and is converted by:

Research Efficiency = 100 - Research Cost

7. Contribution Potential

Definition

Contribution Potential measures whether Rodrigo can add something meaningful, specific, and differentiated to the discussion.

The core question is:

Do we actually have something worth adding?

Useful contributions may include:

professional experience;

practical examples;

technical or business insight;

connections between concepts;

defensible counterpoints;

implementation perspectives;

relevant evidence;

questions that materially advance the discussion;

lessons from building real systems or tools.

The system should penalize opportunities where the likely contribution would merely repeat the source or provide generic agreement.

Examples of low-value contribution:

"Great insight."
"AI is definitely transforming business."
"Very interesting perspective."
"I completely agree."

Rubric

Score

Interpretation

0–20

Little can be added beyond generic agreement or repetition.

21–40

A contribution is possible but likely weakly differentiated.

41–60

Relevant knowledge or experience can add some value.

61–80

A concrete insight, example, connection, or useful perspective is available.

81–100

A strong, specific, differentiated contribution can materially improve the discussion.

Weight

30%

Contribution Potential receives the highest weight.

The rationale remains:

If there is nothing valuable to add, audience size should generally not justify commenting.

8. Positioning Fit

Definition

Positioning Fit measures whether participating reinforces the professional identity the system is intended to build.

The core question is:

Does contributing here reinforce the professional positioning we want to establish?

This is intentionally different from Topic Relevance.

A topic can be technically related to AI while having little relationship to the intended professional positioning.

High-fit discussions tend to connect areas such as:

Business
+
Processes
+
Data
+
Automation
+
AI
+
Architecture

and may also connect those areas with Supply Chain, planning, operations, or decision support.

Rubric

Score

Interpretation

0–20

Little or no value to the intended positioning.

21–40

Weak or indirect positioning connection.

41–60

Partially supports the intended positioning.

61–80

Clearly reinforces the intended professional positioning.

81–100

Excellent opportunity to demonstrate the intended positioning and its differentiating intersections.

Weight

25%

Professional visibility is valuable only when it reinforces a useful and authentic positioning.

9. Topic Relevance

Definition

Topic Relevance measures how closely the subject aligns with the professional areas in which Rodrigo intends to participate and build authority.

The core question is:

Is this a subject Rodrigo wants to be seen discussing professionally?

High-relevance areas currently include:

Artificial Intelligence;

Generative AI;

AI agents and agentic systems;

automation;

data and analytics;

AI solution architecture;

digital transformation;

business applications of technology;

Supply Chain;

planning;

operations;

decision support;

intersections between business, processes, data, automation, and AI.

Topic Relevance alone is insufficient.

A highly relevant topic can still be a poor opportunity when Contribution Potential or Positioning Fit is weak.

Rubric

Score

Interpretation

0–20

Outside the target professional domains.

21–40

Only indirectly related.

41–60

Adjacent and somewhat professionally relevant.

61–80

Directly related to one or more target domains.

81–100

Central to the intended positioning or strongly connects multiple target domains.

Weight

20%

10. Engagement Potential

Definition

Engagement Potential estimates whether a high-quality contribution has a reasonable opportunity to produce useful professional visibility or interaction.

The core question is:

If Rodrigo contributes something valuable here, is there a reasonable opportunity for relevant people to see or interact with it?

Potential future objective signals include:

reaction_count
comment_count
post age
engagement velocity
author reach
author relevance
relationship to author
discussion activity
timing
audience relevance

Whenever reliable objective data is available, deterministic calculation should be preferred over LLM estimation.

The LLM must not invent popularity metrics.

Current v0.1 Limitation

Reliable real-world LinkedIn engagement metadata is not yet established.

Therefore the current implementation does not pretend to have reaction, comment, follower, or velocity data when those values are unavailable.

The current operational approach uses a neutral Engagement Potential placeholder:

50

until a reliable metadata contract and normalization strategy are implemented.

This is intentionally conservative.

Rubric

Score

Interpretation

0–20

Very limited expected professional visibility or interaction.

21–40

Low engagement opportunity.

41–60

Moderate opportunity for relevant visibility or interaction.

61–80

Strong engagement opportunity with a relevant audience.

81–100

Exceptional opportunity for relevant professional visibility or discussion.

Weight

15%

Visibility matters, but it must not dominate strategic contribution value.

11. Research Cost

Definition

Research Cost estimates the effort required before the system can responsibly produce a strong and defensible contribution.

The core question is:

How much additional work is likely to be required before we can contribute responsibly?

Potential factors include:

need for external research;

claims requiring verification;

technical complexity;

unfamiliar context;

requirement for current information;

availability of reliable sources;

expected source volume;

expected LLM/tool usage.

Research Cost is a penalty dimension:

higher = worse

Examples:

Research Cost = 10
→ little additional research expected

Research Cost = 90
→ substantial research expected

Rubric

Score

Interpretation

0–20

Little or no additional research required.

21–40

Limited research or verification required.

41–60

Moderate research necessary.

61–80

Significant research required.

81–100

Extensive research likely, potentially making the opportunity inefficient.

Research Cost is currently a semantic estimate made before the full Research capability executes.

It is not yet a measured token/tool-cost metric.

12. Research Efficiency

Python converts Research Cost into a positive scoring dimension:

Research Efficiency = 100 - Research Cost

Examples:

Research Cost = 10
Research Efficiency = 90

Research Cost = 50
Research Efficiency = 50

Research Cost = 90
Research Efficiency = 10

Weight:

10%

Research effort matters, but strategically valuable opportunities should still be allowed to justify meaningful research.

13. Opportunity Score v0.1

Weights

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

Total

100%

Formula

Opportunity Score =

    Contribution Potential × 0.30
  + Positioning Fit        × 0.25
  + Topic Relevance        × 0.20
  + Engagement Potential   × 0.15
  + Research Efficiency    × 0.10

where:

Research Efficiency = 100 - Research Cost

The resulting score remains in:

0–100

The implementation rounds the final score according to the current application contract.

14. Mandatory Guardrails

Weighted averages alone are insufficient.

A strong score in one dimension must not completely compensate for a critical weakness in strategic contribution value.

Current deterministic guardrails:

Contribution Potential < 30
→ LOW

Positioning Fit < 30
→ LOW

Topic Relevance < 25
→ LOW

If any mandatory guardrail is triggered:

classification = LOW

regardless of the weighted score.

Boundary Behavior

The guardrails use strict < comparisons.

Therefore:

Contribution Potential = 30
→ guardrail not triggered

Positioning Fit = 30
→ guardrail not triggered

Topic Relevance = 25
→ guardrail not triggered

15. Classification

If no mandatory guardrail is triggered:

score >= 80
→ HIGH

score >= 60 and < 80
→ MEDIUM

score < 60
→ LOW

Equivalent conceptual logic:

if guardrail_triggered:
    classification = "LOW"
elif opportunity_score >= 80:
    classification = "HIGH"
elif opportunity_score >= 60:
    classification = "MEDIUM"
else:
    classification = "LOW"

The exact source implementation may differ syntactically, but this behavioral contract must remain stable unless explicitly recalibrated.

16. Classification Semantics and Implemented Routing

HIGH

A HIGH opportunity combines sufficiently strong strategic value to justify Research.

Implemented route:

HIGH
  ↓
ACCEPTED_FOR_RESEARCH
  ↓
Research
  ↓
ResearchBrief
  ↓
Writer
  ↓
Quality Evaluator

ACCEPTED_FOR_RESEARCH records the approval transition before the Research capability executes.

MEDIUM

A MEDIUM opportunity is potentially useful but does not currently justify the HIGH path.

The original design left MEDIUM behavior open.

That decision has now been resolved for v0.1.

Implemented route:

MEDIUM
  ↓
QUEUED
  ↓
END

QUEUED records the semantic lifecycle status, but the current workflow does not yet implement persistent queue storage, later reprioritization, or automatic promotion.

Those remain future capabilities.

LOW

A LOW opportunity either has insufficient score or violates a mandatory strategic guardrail.

Implemented route:

LOW
  ↓
END

LOW opportunities do not consume Research and Writer inference in the normal workflow.

17. Structured Contracts

The original design proposed typed Pydantic contracts.

Those contracts are now implemented.

OpportunitySignals

Conceptually:

OpportunitySignals

topic_relevance
positioning_fit
contribution_potential
research_cost

Each semantic score is constrained to the valid evaluation range.

OpportunitySignals represents LLM semantic interpretation.

It does not own:

authoritative engagement metrics
Research Efficiency
weighted Opportunity Score
mandatory guardrails
final classification
workflow routing

OpportunityEvaluation

The deterministic evaluation artifact carries the operational result required downstream.

Conceptually it includes:

semantic signals
engagement_potential
research_efficiency
opportunity score
classification

The exact source schema remains authoritative if field names evolve.

The architectural distinction is:

OpportunitySignals
    = semantic model output

OpportunityEvaluation
    = validated application decision artifact

18. Engagement Data Separation

Engagement Potential remains outside the LLM-owned OpportunitySignals contract.

This is deliberate.

LLM
    ↓
semantic opportunity signals

Objective / deterministic application data
    ↓
engagement potential

Python
    ↓
final score and classification

This prevents the model from fabricating reaction counts, comment counts, author reach, or other objective metrics.

Until reliable metadata exists:

Engagement Potential = neutral placeholder

rather than:

Engagement Potential = model guess presented as fact

19. Explainability

Opportunity Evaluation must remain interpretable.

A human or developer should be able to inspect:

Contribution Potential
Positioning Fit
Topic Relevance
Engagement Potential
Research Cost
Research Efficiency
Opportunity Score
Classification

Example:

Contribution Potential ...... 90
Positioning Fit .............. 95
Topic Relevance .............. 95
Engagement Potential ......... 80
Research Cost ................ 35
Research Efficiency .......... 65

Opportunity Score ............ 88.25
Classification ............... HIGH

Explainability supports:

human review;

debugging;

prompt calibration;

scoring calibration;

observability;

model comparison;

cost optimization;

later measurement of classification quality.

20. Example A — High-Value Opportunity

Scenario:

A senior executive publishes a discussion about how Generative AI can improve demand planning and Supply Chain decision-making.

Conceptual evaluation:

Contribution Potential ...... 90
Positioning Fit .............. 95
Topic Relevance .............. 95
Engagement Potential ......... 80
Research Cost ................ 35

Therefore:

Research Efficiency = 65

Score:

90 × 0.30 = 27.00
95 × 0.25 = 23.75
95 × 0.20 = 19.00
80 × 0.15 = 12.00
65 × 0.10 =  6.50
              -----
              88.25

No guardrail is triggered.

Result:

Opportunity Score = 88.25
Classification = HIGH

Routing:

HIGH
  ↓
ACCEPTED_FOR_RESEARCH
  ↓
Research

21. Example B — Popular but Low-Value Opportunity

Scenario:

A famous executive publishes a generic announcement celebrating quarterly financial results.

Conceptual evaluation:

Contribution Potential ...... 20
Positioning Fit .............. 25
Topic Relevance .............. 20
Engagement Potential ......... 95
Research Cost ................ 50

Mandatory guardrails trigger:

Contribution Potential < 30
Positioning Fit < 30
Topic Relevance < 25

Result:

Classification = LOW

The opportunity remains LOW regardless of its weighted score.

This demonstrates:

Audience size alone must not dominate opportunity selection.

22. Example C — Relevant but Research-Expensive Opportunity

Scenario:

A technical publication discusses a new AI architecture strongly related to the intended positioning, but understanding and verifying the claims requires substantial external research.

Conceptual evaluation:

Contribution Potential ...... 80
Positioning Fit .............. 90
Topic Relevance .............. 95
Engagement Potential ......... 65
Research Cost ................ 85

Therefore:

Research Efficiency = 15

Score:

80 × 0.30 = 24.00
90 × 0.25 = 22.50
95 × 0.20 = 19.00
65 × 0.15 =  9.75
15 × 0.10 =  1.50
              -----
              76.75

Result:

Opportunity Score = 76.75
Classification = MEDIUM

Current routing:

MEDIUM
  ↓
QUEUED
  ↓
END

The example demonstrates why Research Cost can reduce priority without dominating strategic value.

23. Relationship with Scout

Scout answers:

What candidate opportunities exist?

Opportunity Evaluation answers:

Which candidate is strategically worth pursuing?

The responsibilities remain separate.

Current integration:

Scout
  ↓
validated PostCandidate
  ↓
Opportunity Evaluation

Current Scout cardinality behavior is:

0 candidates
→ END

1 candidate
→ Opportunity Evaluation

>1 distinct candidates
→ explicit unsupported-condition failure

Multiple-candidate orchestration remains a future design problem rather than being hidden inside Opportunity Evaluation.

24. Relationship with Research

Research occurs only after a HIGH opportunity has been accepted.

Research answers:

What evidence and context are required to make a defensible contribution?

Opportunity Evaluation may estimate Research Cost before full research begins.

It does not itself become an unbounded Research agent.

The boundary is:

Opportunity Evaluation
        ↓
HIGH
        ↓
ACCEPTED_FOR_RESEARCH
        ↓
Research

25. Relationship with Writer

Opportunity Evaluation does not generate the contribution.

Writer is responsible for transforming the approved opportunity and structured ResearchBrief into professional communication.

Conceptually:

Opportunity decision
       +
ResearchBrief
       ↓
Writer
       ↓
Draft

This separation prevents strategic prioritization logic from becoming generation logic.

26. Relationship with Quality Evaluator

Opportunity Evaluation and Quality Evaluation solve different problems.

Opportunity Evaluation
        ↓
"Should we spend effort contributing here?"

Quality Evaluator
        ↓
"Is the generated contribution good enough?"

Current downstream quality routing:

PASS
→ Human / END

REVISE
→ Writer
→ Quality Evaluator

REJECT
→ END

A Writer revision does not automatically rerun Research.

27. Current Functional Workflow

The original target workflow has now become an implemented integrated workflow.

Candidate Sources / Web
          │
          ▼
        SCOUT
          │
          ▼
    PostCandidate
          │
          ▼
 OPPORTUNITY EVALUATION
      ┌───┼────────────┐
      │   │            │
     LOW MEDIUM       HIGH
      │   │            │
      ▼   ▼            ▼
     END QUEUED  ACCEPTED_FOR_RESEARCH
          │            │
          ▼            ▼
         END        RESEARCH
                       │
                       ▼
                 ResearchBrief
                       │
                       ▼
                     WRITER
                       │
                       ▼
               QUALITY EVALUATOR
                  ┌────┼─────┐
                  ▼    ▼     ▼
                PASS REVISE REJECT
                  │    │      │
                  ▼    └──► WRITER
             HUMAN / END      END

Publication remains outside autonomous execution.

28. Testing Contract

Opportunity Evaluation must remain independently testable without live OpenAI calls for deterministic behavior.

The test surface should preserve the following contracts.

Schema Validation

Validate:

scores within 0–100
scores below 0 rejected
scores above 100 rejected
required fields enforced
classification values constrained

Research Efficiency

Research Cost = 0
→ Research Efficiency = 100

Research Cost = 50
→ Research Efficiency = 50

Research Cost = 100
→ Research Efficiency = 0

Weighted Scoring

Verify:

correct weights;

correct weighted sum;

valid score range;

expected boundary behavior.

Guardrails

Verify independently:

Contribution Potential < 30 → LOW
Positioning Fit < 30        → LOW
Topic Relevance < 25        → LOW

and exact non-trigger boundaries:

Contribution Potential = 30
Positioning Fit = 30
Topic Relevance = 25

Classification

Verify:

80       → HIGH
79.99    → MEDIUM
60       → MEDIUM
59.99    → LOW

or equivalent numeric precision according to the implementation.

Workflow Routing

Verify:

HIGH   → ACCEPTED_FOR_RESEARCH → Research
MEDIUM → QUEUED → END
LOW    → END

LLM Independence

The deterministic chain must remain independently testable:

OpportunitySignals
      ↓
Research Efficiency
      ↓
Weighted Score
      ↓
Guardrails
      ↓
Classification
      ↓
Routing

Live model calls are not required to validate these deterministic contracts.

29. Calibration Strategy

Opportunity Evaluation v0.1 remains an initial product hypothesis even though it is implemented.

Implementation does not mean the current weights and thresholds are permanently optimal.

Future calibration should use real candidate opportunities and observed outcomes.

Potential signals include:

human agreement with HIGH/MEDIUM/LOW;

whether Rodrigo would actually choose to contribute;

false-positive opportunities;

false-negative opportunities;

actual Research effort;

manual draft correction required;

Writer/Evaluator revision behavior;

resulting professional interaction;

opportunity quality over time.

Calibration must not optimize only for engagement.

The primary objective remains:

Identify opportunities where Rodrigo can make a relevant and professionally valuable contribution.

30. Current Limitations

Opportunity Evaluation v0.1 intentionally retains several limitations.

Engagement Metadata

Reliable LinkedIn-native values are not yet established for:

reaction_count
comment_count
author follower/reach data
engagement velocity
post timing normalization

Therefore objective Engagement Potential remains incomplete.

Neutral Engagement Placeholder

The current neutral value avoids fabrication but reduces discrimination between opportunities where real engagement differs materially.

Research Cost

Research Cost is currently a semantic estimate.

It does not yet incorporate measured:

tokens
tool calls
latency
financial cost
source-access difficulty

Calibration

Weights, guardrails, and thresholds have not yet been calibrated on a sufficiently large real-world labeled opportunity dataset.

Multiple Candidates

The workflow does not yet rank or schedule multiple distinct Scout candidates.

MEDIUM Lifecycle

MEDIUM now has a defined immediate route:

QUEUED → END

but no persistent queue or later promotion lifecycle exists yet.

31. Open Design Decisions

The following remain intentionally unresolved:

how reliable LinkedIn-native candidate content and metadata will be collected;

whether reaction_count is consistently available;

whether comment_count is consistently available;

whether author follower/reach data is consistently available;

exact Engagement Potential normalization;

handling and calibration of partial engagement metadata;

engagement-velocity thresholds;

model selection for semantic Opportunity Evaluation;

whether semantic dimensions should remain in one model call or later be separated;

long-term Opportunity Evaluation calibration methodology;

design of a real-world labeled calibration dataset;

whether measured token/tool/latency cost should influence Research Cost;

whether author relevance should become an independent dimension;

how queued MEDIUM opportunities should later be revisited, prioritized, or promoted;

how multiple candidate opportunities should be ranked and represented in workflow state.

These must be resolved explicitly rather than silently encoded into implementation.

32. Decisions Already Established

Product

Opportunity is not equivalent to popularity.

Contribution value has priority over audience size.

Opportunity Evaluation evaluates the opportunity, not the generated draft.

Human publication authority remains mandatory.

Architecture

Semantic interpretation may use an LLM.

Semantic outputs use typed structured contracts.

Final scoring is deterministic.

Final classification is deterministic.

The LLM does not directly own HIGH/MEDIUM/LOW routing.

Objective data should use deterministic logic whenever practical.

Opportunity Evaluation remains separate from Research, Writer, and Quality Evaluation.

Scoring

Contribution Potential = 30%
Positioning Fit        = 25%
Topic Relevance        = 20%
Engagement Potential   = 15%
Research Efficiency    = 10%

Research Efficiency

Research Efficiency = 100 - Research Cost

Guardrails

Contribution Potential < 30 → LOW
Positioning Fit < 30        → LOW
Topic Relevance < 25        → LOW

Classification

HIGH   >= 80
MEDIUM >= 60 and < 80
LOW    < 60

Routing

HIGH
→ ACCEPTED_FOR_RESEARCH
→ Research

MEDIUM
→ QUEUED
→ END

LOW
→ END

These are the current v0.1 behavioral contracts.

They remain subject to explicit evidence-based future calibration.

33. Implementation Evolution

The original implementation sequence was:

Define dimensions/rubrics
        ↓
Define weights/formula/guardrails
        ↓
Define Pydantic schemas
        ↓
Implement deterministic scoring
        ↓
Test deterministic behavior
        ↓
Implement semantic evaluation
        ↓
Test semantic contracts
        ↓
Integrate into workflow
        ↓
Connect HIGH to Research

That sequence has now been completed.

Opportunity Evaluation is currently integrated with:

Scout upstream
Research downstream
Writer downstream of Research
Quality Evaluator downstream of Writer

The next project increment is not additional basic Opportunity Evaluation implementation.

It is:

End-to-End Real Workflow Validation v0.1

34. Current Status Summary

Opportunity Evaluation v0.1

Purpose ...................... ESTABLISHED
Product principle ............ ESTABLISHED
Dimensions ................... IMPLEMENTED
Rubrics ...................... ESTABLISHED
Pydantic contracts ........... IMPLEMENTED
Semantic evaluator ........... IMPLEMENTED
Research Efficiency .......... IMPLEMENTED
Weighted scoring ............. IMPLEMENTED
Guardrails ................... IMPLEMENTED
Classification ............... IMPLEMENTED
HIGH routing ................. IMPLEMENTED
MEDIUM routing ............... IMPLEMENTED
LOW routing .................. IMPLEMENTED
Research integration ......... IMPLEMENTED
Writer downstream path ....... IMPLEMENTED
Quality downstream path ...... IMPLEMENTED
Human publication boundary ... PRESERVED
Real-world calibration ....... FUTURE
Objective engagement model ... FUTURE

35. Design Summary

Opportunity Evaluation exists to prevent the LinkedIn Agentic AI System from merely finding visible discussions and generating comments.

Its role is to identify conversations where there is a meaningful professional reason to participate.

The implemented decision chain is:

Find candidate
      ↓
Evaluate semantic value
      ↓
Produce structured signals
      ↓
Calculate deterministically
      ↓
Apply mandatory guardrails
      ↓
HIGH / MEDIUM / LOW
      ↓
Allocate workflow resources

The full product logic is:

Scout
"Find a possible opportunity"
        ↓
Opportunity Evaluation
"Is it strategically worth pursuing?"
        ↓
Research
"What evidence do we need?"
        ↓
Writer
"What should we contribute?"
        ↓
Quality Evaluator
"Is the contribution good enough?"
        ↓
Human
"Do I want to publish it?"

The guiding product principle remains:

Select the conversations where Rodrigo can add professional value — not simply the conversations with the largest audience.

And the architectural pattern remains:

LLM
"Interpret what requires semantic understanding"
        ↓
Structured Output
"Represent that interpretation explicitly"
        ↓
Python
"Calculate and decide deterministically"
        ↓
LangGraph
"Control what happens next"
        ↓
Human
"Retain final publication authority"
