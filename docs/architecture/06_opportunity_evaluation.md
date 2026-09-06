# Opportunity Evaluation

## 1. Purpose

The Opportunity Evaluation capability determines whether a LinkedIn post represents a valuable opportunity for Rodrigo to comment on.

The objective is **not to evaluate whether a post is good or popular**.

The objective is to answer:

> Is this a good opportunity for Rodrigo to contribute a relevant, differentiated, and professionally valuable comment?

Opportunity Evaluation acts as a strategic prioritization gate between candidate discovery and research/comment generation.

The planned workflow direction is:

```text
Scout
  ↓
Opportunity Evaluation
  ↓
Research
  ↓
Writer
  ↓
Quality Evaluator
  ↓
Human-in-the-loop
```

The capability must prioritize opportunities where Rodrigo can add meaningful professional value rather than simply maximize engagement or visibility.

---

## 2. Core Product Principle

### Opportunity is not the same as popularity

A LinkedIn post with high reach, many reactions, or a well-known author is not automatically a high-value opportunity.

A high-value opportunity should combine:

* relevance to Rodrigo's professional domains;
* alignment with Rodrigo's intended professional positioning;
* potential for a meaningful and differentiated contribution;
* reasonable visibility or engagement potential;
* acceptable research effort.

Therefore:

```text
High audience + low contribution potential
                ↓
        Limited opportunity

Relevant discussion + strong contribution potential
                ↓
          High opportunity
```

The system must avoid becoming an engagement bot that prioritizes posts only because they are popular.

Audience and engagement matter, but they are secondary to professional relevance, positioning, and contribution potential.

---

## 3. Design Principles

### 3.1 Hybrid Evaluation

Opportunity Evaluation follows the architectural principle of using:

* LLM reasoning where semantic understanding adds material value;
* deterministic logic where explicit rules, calculations, or objective signals provide sufficient reliability.

Conceptually:

```text
Post Candidate
      │
      ▼
Semantic Evaluation
      │
      │ LLM where necessary
      ▼
Structured Signals
      │
      │ + objective signals
      ▼
Deterministic Scoring
      │
      ▼
Opportunity Classification
```

The LLM evaluates semantic characteristics.

The application owns the final scoring and classification logic.

---

### 3.2 Structured Outputs

Semantic evaluation must return structured data rather than unrestricted natural-language decisions.

The LLM should produce evaluation signals.

It should **not** have unrestricted authority to decide whether an opportunity proceeds through the workflow.

The expected architectural pattern is:

```text
LLM
 │
 ▼
Structured Output / Pydantic
 │
 ▼
Deterministic Python Logic
 │
 ▼
Opportunity Classification
```

---

### 3.3 Deterministic Decision Ownership

The final opportunity score and classification must be calculated by application logic.

The LLM must not directly decide:

```text
HIGH
MEDIUM
LOW
```

Instead, it provides semantic signals that are consumed by deterministic scoring logic.

This preserves:

* predictability;
* testability;
* explainability;
* calibration;
* model independence;
* cost control.

---

### 3.4 Bounded Autonomy

Opportunity Evaluation is part of a controlled agentic workflow.

The component must not:

* autonomously publish content;
* autonomously interact with LinkedIn;
* initiate unbounded research;
* create unbounded evaluation loops;
* independently redefine evaluation criteria;
* bypass deterministic routing rules.

---

### 3.5 Cost-Aware Orchestration

LLM inference is treated as computational infrastructure.

Opportunity Evaluation should avoid expensive inference when deterministic rules can reliably resolve part of the evaluation.

Future implementations may route different evaluation tasks to different models according to:

* complexity;
* cost;
* latency;
* required quality;
* semantic reasoning requirements.

The goal is not minimum token consumption at any cost.

The goal is:

> Minimum inference cost capable of satisfying the required quality contract.

---

## 4. Evaluation Model

Opportunity Evaluation v0.1 contains five dimensions:

1. Contribution Potential
2. Positioning Fit
3. Topic Relevance
4. Engagement Potential
5. Research Cost

All dimensions use a conceptual range of:

```text
0–100
```

For the first four dimensions:

```text
higher = better
```

For Research Cost:

```text
higher = worse
```

Research Cost is therefore converted into Research Efficiency before final scoring.

---

# 5. Contribution Potential

## 5.1 Definition

Contribution Potential measures whether Rodrigo can add something meaningful, specific, and differentiated to the discussion.

The core question is:

> Do we actually have something worth adding?

Potential contributions may include:

* professional experience;
* practical examples;
* technical or business insight;
* a useful connection between concepts;
* a defensible counterpoint;
* an implementation perspective;
* relevant evidence;
* a question that meaningfully advances the discussion;
* lessons from building real systems or tools.

The system should strongly penalize opportunities where the likely comment would merely repeat the original post or provide generic agreement.

Examples of low-value comments include:

```text
"Great insight."

"AI is definitely transforming business."

"Very interesting perspective."

"I completely agree."
```

The system should favor situations where the resulting comment can contribute additional information or perspective.

---

## 5.2 Contribution Potential Rubric

| Score  | Interpretation                                                                                                  |
| ------ | --------------------------------------------------------------------------------------------------------------- |
| 0–20   | There is little to add beyond generic agreement or repetition.                                                  |
| 21–40  | A comment is possible, but likely to provide limited differentiation.                                           |
| 41–60  | Rodrigo has relevant knowledge or experience that can add some value.                                           |
| 61–80  | Rodrigo can provide a concrete insight, example, connection, or useful perspective.                             |
| 81–100 | Rodrigo has a strong, specific, and differentiated contribution capable of materially improving the discussion. |

---

## 5.3 Strategic Importance

Contribution Potential receives the highest weight in Opportunity Score.

Rationale:

> If Rodrigo has nothing valuable to add, the system should generally not recommend commenting regardless of the size of the audience.

Weight:

```text
30%
```

---

# 6. Positioning Fit

## 6.1 Definition

Positioning Fit measures whether participating in the discussion reinforces the professional identity Rodrigo intends to build.

The core question is:

> Does commenting on this post help reinforce the professional positioning we want to establish?

This dimension is intentionally different from Topic Relevance.

A topic may involve technology while having limited connection to Rodrigo's desired positioning.

For example, a highly technical discussion about low-level software optimization may be technology-related but have limited Positioning Fit.

A discussion about implementing AI agents in corporate processes may have very high Positioning Fit because it connects:

```text
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
```

The evaluation should favor opportunities that strengthen Rodrigo's positioning at the intersection of business expertise and applied technology rather than opportunities requiring him to imitate a professional identity unrelated to his actual experience or development path.

---

## 6.2 Positioning Fit Rubric

| Score  | Interpretation                                                                                                                         |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| 0–20   | Participation provides little or no value to the intended professional positioning.                                                    |
| 21–40  | The connection with the desired positioning is weak or indirect.                                                                       |
| 41–60  | The discussion partially supports the desired positioning.                                                                             |
| 61–80  | Participation clearly reinforces the desired professional positioning.                                                                 |
| 81–100 | The discussion is an excellent opportunity to demonstrate the intended professional positioning and its differentiating intersections. |

---

## 6.3 Weight

Positioning Fit weight:

```text
25%
```

Rationale:

Professional visibility is valuable only when it contributes to the professional identity the system is intended to reinforce.

---

# 7. Topic Relevance

## 7.1 Definition

Topic Relevance measures how closely the subject of the post aligns with the professional areas in which Rodrigo wants to participate and build authority.

The core question is:

> Is this a subject Rodrigo wants to be seen discussing professionally?

High-relevance areas currently include, among others:

* Artificial Intelligence;
* Generative AI;
* AI agents and agentic systems;
* automation;
* data and analytics;
* AI solution architecture;
* digital transformation;
* business applications of technology;
* Supply Chain;
* planning;
* operations;
* decision support;
* intersections between business, processes, data, automation, and AI.

Topic Relevance alone does not determine whether a post should be selected.

A highly relevant topic may still represent a poor opportunity if Rodrigo has little meaningful contribution to add.

---

## 7.2 Topic Relevance Rubric

| Score  | Interpretation                                                                                                   |
| ------ | ---------------------------------------------------------------------------------------------------------------- |
| 0–20   | The topic is outside the target professional domains.                                                            |
| 21–40  | The topic has only an indirect relationship with the target domains.                                             |
| 41–60  | The topic is adjacent to the target positioning and has some professional relevance.                             |
| 61–80  | The topic is directly related to one or more target professional domains.                                        |
| 81–100 | The topic is central to Rodrigo's desired professional positioning or strongly connects multiple target domains. |

---

## 7.3 Weight

Topic Relevance weight:

```text
20%
```

Rationale:

Topic relevance is important for maintaining thematic consistency, but relevance alone is insufficient if positioning or contribution potential is weak.

---

# 8. Engagement Potential

## 8.1 Definition

Engagement Potential estimates whether commenting on the post has a reasonable probability of producing useful professional visibility or interaction.

The core question is:

> If Rodrigo contributes a high-quality comment here, is there a reasonable opportunity for relevant people to see or interact with it?

Possible future signals include:

* number of reactions;
* number of comments;
* post age;
* engagement velocity;
* author reach;
* author relevance;
* relationship to the author;
* activity within the discussion;
* timing of the opportunity;
* audience relevance.

Whenever reliable objective data is available, Engagement Potential should prefer deterministic calculation over LLM estimation.

The LLM should not be asked to guess objective popularity metrics that can be obtained directly from available data.

---

## 8.2 Engagement Potential Rubric

| Score  | Interpretation                                                              |
| ------ | --------------------------------------------------------------------------- |
| 0–20   | Very limited expected professional visibility or interaction.               |
| 21–40  | Low engagement opportunity.                                                 |
| 41–60  | Moderate opportunity for relevant visibility or interaction.                |
| 61–80  | Strong engagement opportunity with a relevant audience.                     |
| 81–100 | Exceptional opportunity for relevant professional visibility or discussion. |

---

## 8.3 Weight

Engagement Potential weight:

```text
15%
```

Rationale:

Visibility matters, but it must not dominate opportunity selection.

A highly popular post should not compensate for very weak contribution potential, positioning fit, or topic relevance.

---

## 8.4 Engagement Signals v0.1

Engagement Potential should be based primarily on objective signals collected
by Scout or another deterministic metadata collection mechanism.

The initial data contract should consider the following signals:

### Primary Signals

```text
reaction_count
comment_count
```

---

# 9. Research Cost

## 9.1 Definition

Research Cost estimates the effort required to produce a factual, defensible, and valuable comment.

The core question is:

> How much additional work is required before the system can responsibly generate a strong comment?

Potential factors include:

* need for external research;
* number of claims requiring verification;
* technical complexity;
* need to understand unfamiliar context;
* need for current information;
* availability of reliable sources;
* amount of source material required;
* expected LLM/tool usage.

Unlike the other dimensions, a higher Research Cost represents a cost or penalty.

For example:

```text
Research Cost = 10
→ little additional research required

Research Cost = 90
→ substantial research required
```

---

## 9.2 Research Cost Rubric

| Score  | Interpretation                                                           |
| ------ | ------------------------------------------------------------------------ |
| 0–20   | Little or no additional research is required.                            |
| 21–40  | Limited research or verification is required.                            |
| 41–60  | Moderate research is necessary.                                          |
| 61–80  | Significant research is required before commenting responsibly.          |
| 81–100 | Extensive research is required and may make the opportunity inefficient. |

---

# 10. Research Efficiency

Research Cost is converted into a positive scoring dimension called Research Efficiency.

Formula:

```text
Research Efficiency = 100 - Research Cost
```

Examples:

```text
Research Cost = 10
Research Efficiency = 90

Research Cost = 50
Research Efficiency = 50

Research Cost = 90
Research Efficiency = 10
```

This transformation ensures that every input used by the weighted Opportunity Score follows the same interpretation:

```text
higher = better
```

Research Efficiency weight:

```text
10%
```

Rationale:

Research effort matters for efficiency and inference cost, but the system should still be willing to research strategically valuable opportunities.

---

# 11. Opportunity Score v0.1

## 11.1 Weights

The initial weights are:

| Dimension              |   Weight |
| ---------------------- | -------: |
| Contribution Potential |      30% |
| Positioning Fit        |      25% |
| Topic Relevance        |      20% |
| Engagement Potential   |      15% |
| Research Efficiency    |      10% |
| **Total**              | **100%** |

---

## 11.2 Formula

The Opportunity Score is calculated as:

```text
Opportunity Score =

    Contribution Potential × 0.30
  + Positioning Fit        × 0.25
  + Topic Relevance        × 0.20
  + Engagement Potential   × 0.15
  + Research Efficiency    × 0.10
```

Where:

```text
Research Efficiency = 100 - Research Cost
```

The resulting Opportunity Score remains in the range:

```text
0–100
```

---

## 11.3 Design Status

This scoring model is:

```text
VERSION: v0.1
STATUS: APPROVED FOR INITIAL IMPLEMENTATION
```

The weights are not considered permanently optimal.

They must be treated as an initial product hypothesis and may later be calibrated using real evaluated opportunities and observed outcomes.

Changes to the weights must be explicit and documented.

---

# 12. Guardrails

Weighted averages alone are not sufficient.

A very strong value in one dimension must not completely compensate for a critical weakness in another.

Opportunity Evaluation v0.1 therefore applies deterministic guardrails.

Initial guardrails:

```text
Contribution Potential < 30
→ LOW

Positioning Fit < 30
→ LOW

Topic Relevance < 25
→ LOW
```

These guardrails are evaluated independently from the weighted Opportunity Score.

If any mandatory guardrail is triggered, the opportunity is classified as:

```text
LOW
```

regardless of the weighted score.

---

## 12.1 Guardrail Rationale

### Contribution Potential

If Rodrigo has almost nothing meaningful to add, large audience size should not justify commenting.

### Positioning Fit

If participating does not meaningfully support the intended professional positioning, visibility alone is insufficient.

### Topic Relevance

If the discussion is substantially outside the intended professional domains, the system should avoid opportunistic engagement merely because the post is popular.

---

# 13. Opportunity Classification v0.1

If no guardrail is triggered, classification follows the Opportunity Score.

Initial thresholds:

```text
80–100
→ HIGH

60–79.99
→ MEDIUM

0–59.99
→ LOW
```

Equivalent conceptual Python logic:

```text
if guardrail_triggered:
    classification = "LOW"

elif opportunity_score >= 80:
    classification = "HIGH"

elif opportunity_score >= 60:
    classification = "MEDIUM"

else:
    classification = "LOW"
```

The exact implementation may differ syntactically but must preserve this behavior.

---

# 14. Interpretation of Classifications

## HIGH

A strong opportunity that combines professional relevance, positioning value, contribution potential, reasonable visibility, and acceptable research effort.

Planned direction:

```text
HIGH
 ↓
Research
```

---

## MEDIUM

A potentially useful opportunity that does not currently meet the HIGH threshold.

MEDIUM exists to prevent premature binary decisions while the system is still being calibrated.

Its final workflow behavior remains an open design decision.

Possible future behaviors include:

* lower priority queue;
* conditional research;
* human review;
* additional deterministic filtering.

---

## LOW

An opportunity with insufficient strategic value or one that triggers a mandatory guardrail.

Planned direction:

```text
LOW
 ↓
END
```

LOW opportunities should not consume Research and Writer inference unless explicitly requested by a human.

---

# 15. Semantic Evaluation vs. Deterministic Logic

The capability explicitly separates semantic interpretation from operational decision-making.

Conceptually:

```text
                    POST CANDIDATE
                          │
                          ▼
               ┌────────────────────┐
               │ SEMANTIC EVALUATION│
               │                    │
               │ LLM where necessary│
               └──────────┬─────────┘
                          │
                          ▼
                Structured Signals
                          │
                          │
                + Objective Signals
                          │
                          ▼
               ┌────────────────────┐
               │ OPPORTUNITY SCORING│
               │                    │
               │ Python             │
               │ deterministic      │
               └──────────┬─────────┘
                          │
                          ▼
                 Guardrails + Score
                          │
                          ▼
                  HIGH / MEDIUM / LOW
```

Potential semantic dimensions include:

```text
Topic Relevance
Positioning Fit
Contribution Potential
Research Cost
```

Potential objective signals include:

```text
Post age
Reactions
Comments
Author information
Engagement velocity
Available evidence
```

The exact boundary between semantic and deterministic evaluation may evolve according to available Scout data.

---

# 16. Structured Output

The semantic evaluator should return typed structured data.

The final Pydantic implementation has not yet been defined, but the conceptual contract is:

```text
OpportunitySignals

topic_relevance: int
positioning_fit: int
contribution_potential: int
research_cost: int
```

Possible supporting fields may include:

```text
reasoning
contribution_angle
research_need
```

Any score field must enforce:

```text
0 <= score <= 100
```

### Engagement Data Separation

Engagement Potential must remain outside `OpportunitySignals`.

`OpportunitySignals` represents only the semantic interpretation produced by
the LLM:

```text
topic_relevance
positioning_fit
contribution_potential
research_cost

The LLM must not return the authoritative final Opportunity Score or classification.

Those remain responsibilities of deterministic application logic.

---

# 17. Explainability

Opportunity Evaluation must remain interpretable.

The system should be able to explain why a post received a particular score and classification.

Example:

```text
Contribution Potential ...... 90
Positioning Fit .............. 95
Topic Relevance .............. 95
Engagement Potential ......... 80
Research Cost ................ 35
Research Efficiency .......... 65

Opportunity Score ............ 88.25
Classification ............... HIGH
```

Explainability supports:

* human review;
* debugging;
* prompt calibration;
* scoring calibration;
* observability;
* model comparison;
* cost optimization;
* future evaluation of prediction quality.

---

# 18. Example A — High-Value Opportunity

Scenario:

> A senior executive publishes a post discussing how Generative AI can improve demand planning and decision-making in Supply Chain.

Conceptual evaluation:

```text
Contribution Potential ...... 90
Positioning Fit .............. 95
Topic Relevance .............. 95
Engagement Potential ......... 80
Research Cost ................ 35
```

Therefore:

```text
Research Efficiency = 65
```

Score:

```text
90 × 0.30 = 27.00
95 × 0.25 = 23.75
95 × 0.20 = 19.00
80 × 0.15 = 12.00
65 × 0.10 =  6.50
              -----
              88.25
```

No guardrail is triggered.

Result:

```text
Opportunity Score = 88.25
Classification = HIGH
```

Interpretation:

* strong overlap with Rodrigo's target positioning;
* strong connection between Supply Chain and applied AI;
* meaningful contribution is possible;
* professional visibility is useful;
* research requirements are manageable.

---

# 19. Example B — Popular but Low-Value Opportunity

Scenario:

> A famous executive publishes a generic announcement celebrating quarterly financial results.

Conceptual evaluation:

```text
Contribution Potential ...... 20
Positioning Fit .............. 25
Topic Relevance .............. 20
Engagement Potential ......... 95
Research Cost ................ 50
```

Multiple guardrails are triggered:

```text
Contribution Potential < 30
Positioning Fit < 30
Topic Relevance < 25
```

Result:

```text
Classification = LOW
```

The opportunity remains LOW regardless of the weighted score.

This demonstrates the core principle:

> Audience size alone must not dominate opportunity selection.

---

# 20. Example C — Relevant but Expensive Opportunity

Scenario:

> A technical publication discusses a new AI architecture strongly related to Rodrigo's positioning, but understanding the claims requires substantial external research.

Conceptual evaluation:

```text
Contribution Potential ...... 80
Positioning Fit .............. 90
Topic Relevance .............. 95
Engagement Potential ......... 65
Research Cost ................ 85
```

Therefore:

```text
Research Efficiency = 15
```

Score:

```text
80 × 0.30 = 24.00
90 × 0.25 = 22.50
95 × 0.20 = 19.00
65 × 0.15 =  9.75
15 × 0.10 =  1.50
              -----
              76.75
```

Result:

```text
Opportunity Score = 76.75
Classification = MEDIUM
```

Interpretation:

The opportunity is strategically relevant, but its high research cost reduces priority.

This demonstrates why Research Cost is part of the model without dominating the score.

---

# 21. Relationship with Other Components

## 21.1 Scout

Scout is responsible for discovering candidate LinkedIn posts.

Scout answers:

> What opportunities exist?

Opportunity Evaluation answers:

> Which of those opportunities are worth pursuing?

The responsibilities must remain separate.

---

## 21.2 Research

Research occurs after an opportunity has been selected.

Research answers:

> What evidence and context do we need to produce a defensible contribution?

Opportunity Evaluation may estimate Research Cost before full research begins.

It should not perform unbounded research itself.

---

## 21.3 Writer

Writer generates the actual LinkedIn comment.

Opportunity Evaluation does not write the comment.

Its output may provide context to Writer, such as a potential contribution angle, but generation remains Writer's responsibility.

---

## 21.4 Quality Evaluator

Opportunity Evaluation and Quality Evaluation solve different problems.

```text
Opportunity Evaluation
        │
        ▼
"Should we comment here?"

              vs.

Quality Evaluator
        │
        ▼
"Is this generated comment good enough?"
```

These responsibilities must remain separate.

The intended architecture is therefore:

```text
Evaluate the opportunity
          ↓
Research the opportunity
          ↓
Generate the comment
          ↓
Evaluate the comment
```

---

# 22. Planned Functional Workflow

The target workflow direction is:

```text
LinkedIn / Candidate Sources
            │
            ▼
          SCOUT
            │
            ▼
     Post Candidates
            │
            ▼
 OPPORTUNITY EVALUATION
            │
       ┌────┴───────────┐
       │                │
      LOW          MEDIUM / HIGH
       │                │
       ▼                ▼
      END            RESEARCH
                        │
                        ▼
                      WRITER
                        │
                        ▼
                QUALITY EVALUATOR
                        │
                 ┌──────┼──────┐
                 ▼      ▼      ▼
               PASS   REVISE  REJECT
                 │      │
                 ▼      └──────► WRITER
               HUMAN
                 │
                 ▼
          Manual Publication
```

The exact behavior of MEDIUM remains to be defined.

Human-in-the-loop remains mandatory before publication.

The system must never autonomously publish a LinkedIn comment.

---

# 23. Implementation Strategy

Opportunity Evaluation must be implemented incrementally.

Approved implementation sequence:

```text
1. Define evaluation dimensions and rubric
        ↓
2. Define weights, formula, guardrails and thresholds
        ↓
3. Define Pydantic schemas
        ↓
4. Implement deterministic scoring
        ↓
5. Add isolated deterministic tests
        ↓
6. Implement semantic evaluation
        ↓
7. Add semantic component contracts/tests
        ↓
8. Validate representative evaluation examples
        ↓
9. Integrate Opportunity Evaluation into workflow
        ↓
10. Run complete test suite
        ↓
11. Run Project Context Snapshot / audit
        ↓
12. Validate audit
        ↓
13. Update PROJECT_CONTEXT.md
        ↓
14. Commit / push
```

Steps 1 and 2 are complete at design level.

The next implementation step is:

```text
Define Pydantic schemas
```

Opportunity Evaluation must be tested independently before being inserted into the active LangGraph workflow.

---

# 24. Testing Strategy

## 24.1 Schema Validation

Tests should cover:

* valid scores;
* score below 0;
* score above 100;
* missing required fields;
* valid classification values;
* invalid classification values.

---

## 24.2 Research Efficiency

Tests should verify:

```text
Research Cost = 0
→ Research Efficiency = 100

Research Cost = 50
→ Research Efficiency = 50

Research Cost = 100
→ Research Efficiency = 0
```

---

## 24.3 Weighted Scoring

Tests should verify:

* correct weights;
* correct weighted sum;
* correct 0–100 range;
* expected behavior at boundary values.

---

## 24.4 Guardrails

Tests must verify independently:

```text
Contribution Potential < 30
→ LOW

Positioning Fit < 30
→ LOW

Topic Relevance < 25
→ LOW
```

They must also verify the exact boundary:

```text
Contribution Potential = 30
→ guardrail not triggered

Positioning Fit = 30
→ guardrail not triggered

Topic Relevance = 25
→ guardrail not triggered
```

---

## 24.5 Classification Thresholds

Tests must verify:

```text
Score >= 80
→ HIGH

Score >= 60 and < 80
→ MEDIUM

Score < 60
→ LOW
```

Boundary tests should explicitly include:

```text
80
79.99
60
59.99
```

or equivalent precision according to the final numeric implementation.

---

## 24.6 Behavioral Scenarios

Tests should eventually include:

* high-quality opportunity;
* popular but strategically irrelevant opportunity;
* high-engagement but low-contribution opportunity;
* high-relevance but low-positioning opportunity;
* high-relevance but high-research-cost opportunity;
* opportunity triggering each individual guardrail;
* opportunity triggering multiple guardrails.

---

## 24.7 LLM Independence

Deterministic scoring tests must not require live OpenAI API calls.

The following logic must be independently testable:

```text
Structured Signals
        ↓
Research Efficiency
        ↓
Weighted Score
        ↓
Guardrails
        ↓
Classification
```

This separation is a formal behavioral contract of the capability.

---

# 25. Calibration Strategy

Opportunity Evaluation v0.1 is an initial product hypothesis.

Weights, guardrails, and thresholds must eventually be calibrated using real candidate posts and observed outcomes.

Potential future calibration signals may include:

* human agreement with HIGH/MEDIUM/LOW classifications;
* whether Rodrigo would actually choose to comment;
* amount of manual correction required;
* research cost actually incurred;
* comment quality after Writer/Evaluator cycles;
* resulting professional interaction;
* false-positive opportunities;
* false-negative opportunities.

Calibration must not optimize only for engagement.

The primary objective remains:

> Identify opportunities where Rodrigo can make a relevant and professionally valuable contribution.

---

# 26. Open Design Decisions

The following decisions remain intentionally unresolved:

1. Whether Scout can reliably collect `reaction_count`.
2. Whether Scout can reliably collect `comment_count`.
3. Whether `author_followers` is technically and consistently available.
4. Exact Engagement Potential normalization and calculation.
5. Handling of missing engagement data.
6. Calibration of engagement and velocity thresholds from observed posts.
7. Model selection for semantic Opportunity Evaluation.
8. Whether all semantic dimensions should be produced by a single LLM call.
9. Final Pydantic schema structure.
10. Exact supporting explanation fields.
11. MEDIUM opportunity routing behavior.
12. Calibration dataset design.
13. Long-term calibration methodology.
14. Whether Research Cost should later incorporate measured token/tool cost.
15. Whether author relevance should become a separate dimension or remain part of Engagement Potential / Positioning Fit.

These items must be resolved incrementally.

They must not be silently encoded into implementation without an explicit design decision.

---

# 27. Decisions Already Established

The following decisions are established for Opportunity Evaluation v0.1:

### Product

* Opportunity is not equivalent to popularity.
* Contribution value has priority over audience size.
* Opportunity Evaluation evaluates the post/opportunity, not the generated comment.

### Architecture

* Semantic interpretation may use an LLM.
* Semantic outputs must be structured.
* Final scoring is deterministic.
* Final classification is deterministic.
* LLMs do not directly own HIGH/MEDIUM/LOW routing.
* Objective data should use deterministic logic whenever practical.
* Human-in-the-loop remains mandatory before publication.

### Scoring

```text
Contribution Potential = 30%
Positioning Fit        = 25%
Topic Relevance        = 20%
Engagement Potential   = 15%
Research Efficiency    = 10%
```

### Research Efficiency

```text
Research Efficiency = 100 - Research Cost
```

### Guardrails

```text
Contribution Potential < 30 → LOW
Positioning Fit < 30        → LOW
Topic Relevance < 25        → LOW
```

### Classification

```text
HIGH   >= 80
MEDIUM >= 60 and < 80
LOW    < 60
```

These decisions are approved for initial implementation but remain subject to future evidence-based calibration.

---

# 28. Current Status

Status:

```text
DESIGN v0.1 COMPLETE
IMPLEMENTATION NOT STARTED
```

Completed at design level:

* capability purpose;
* core product principle;
* evaluation dimensions;
* rubrics;
* dimension weights;
* Research Efficiency transformation;
* Opportunity Score formula;
* deterministic guardrails;
* classification thresholds;
* semantic vs. deterministic separation;
* explainability requirement;
* component responsibilities;
* implementation sequence;
* initial testing strategy;
* calibration principle.

Next planned implementation step:

```text
Pydantic schema design
        ↓
app/schemas/opportunity.py
```

---

# 29. Design Summary

Opportunity Evaluation exists to ensure that the LinkedIn Agentic AI System does not merely find popular posts and generate comments.

It must identify situations where Rodrigo has a meaningful professional reason to participate.

The intended behavior is:

```text
Find opportunities
        ↓
Evaluate strategic value
        ↓
Apply deterministic prioritization
        ↓
Research selectively
        ↓
Generate meaningful contribution
        ↓
Evaluate comment quality
        ↓
Human decides whether to publish
```

The guiding principle is:

> Select the conversations where Rodrigo can add professional value — not simply the conversations with the largest audience.

The architectural pattern is:

```text
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
```
