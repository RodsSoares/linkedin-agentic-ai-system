Editorial Preference Contract v0.1

1. Purpose

Define the conceptual and machine-facing contract required to distinguish between:

a professionally strong draft that Rodrigo could plausibly have written; and

a draft that Rodrigo would probably choose to publish after Human Review.

This capability exists to improve the final-mile calibration of the LinkedIn Agentic AI System.

The problem being addressed is not factual quality alone.

The current system can already produce drafts that are:

relevant;

factually grounded;

semantically differentiated;

professionally written;

highly rated by the existing Quality Evaluator.

However, repeated Golden Set cases show that Rodrigo still removes explanatory completeness, secondary detail, excessive enumeration, and overly polished LLM-like rhetorical structure before publication.

The target is therefore not generic style imitation.

The target is editorial preference.

2. Governing Question

Given:

the source opportunity;

the available ResearchBrief;

the Agentic draft;

the accumulated Rodrigo Voice calibration evidence;

evaluate whether the draft contains information, structure, rhetoric, or explanatory density that Rodrigo would likely remove, simplify, reframe, or stop before publishing.

The central question is:

Would Rodrigo probably choose to publish this formulation?

This is distinct from:

Could Rodrigo plausibly have written this?

3. Architectural Principle

The capability must preserve the established ownership model:

LLM
→ semantic interpretation and bounded semantic judgment

Python
→ deterministic execution, validation, thresholds, routing, limits, and factual state

LangGraph
→ workflow orchestration

Human
→ final publication authority

The capability must also preserve:

Context ≠ Policy

ResearchBrief is context.

Golden Set evidence is calibration context.

Critical editorial requirements must eventually be promoted into explicit policy rather than relying on the model to infer them implicitly from large context.

4. Scope

Editorial Preference v0.1 evaluates a completed draft.

It does not:

rewrite the draft;

publish content;

change Opportunity Evaluation;

rerun Research;

alter Research evidence;

invent new factual claims;

infer hidden personal traits;

replace Human Review;

automatically mutate the Golden Set;

establish permanent Rodrigo Voice rules from one example.

The first implementation should remain diagnostic.

5. Inputs

Conceptual input contract:

EditorialPreferenceInput

source_post: PostCandidate
research_result: ResearchBrief | None
draft: str
content_intent: COMMENT
calibration_context: bounded Rodrigo Voice evidence

content_intent is explicitly included because editorial preference is context-dependent.

v0.1 should support only:

COMMENT

AUTHORIAL_POST should not silently reuse the same contract.

6. Output

Proposed structured output:

EditorialPreferenceEvaluation

central_thesis_focus: int
contribution_density: int
conversational_naturalness: int
selective_evidence_use: int
stopping_discipline: int
synthetic_completeness_risk: int
publication_likelihood: int

unnecessary_elements: list[str]
preserve_elements: list[str]
editorial_reason: str

decision: PASS | ADJUST

All numeric dimensions use:

0–100

Important:

No production threshold is frozen in v0.1.

The initial implementation should gather calibration evidence before deterministic PASS / ADJUST thresholds become authoritative.

7. Semantic Dimensions

7.1 Central Thesis Focus

Question:

Does the draft communicate one primary contribution clearly, or does it attempt to deliver several parallel insights?

High score:

one dominant thesis;

supporting detail serves that thesis;

no unnecessary second or third argument.

Low score:

multiple competing insights;

side arguments dilute the contribution;

research findings are surfaced merely because they are available.

This dimension does not reward oversimplification.

A complex point may remain complex if complexity is necessary.

7.2 Contribution Density

Question:

How much professionally useful contribution is delivered per unit of explanation?

High score:

each sentence materially advances the contribution;

supporting detail earns its presence;

little semantic redundancy.

Low score:

technically correct but low-value elaboration;

repeated conclusions;

evidence enumeration that does not change the social contribution;

explanatory continuation after the thesis is already defensible.

Contribution Density is not equivalent to short length.

A longer comment may still have high contribution density.

7.3 Conversational Naturalness

Question:

Does the text read as a professional entering an existing discussion, or as an LLM answering a prompt?

High score:

socially contextual opening;

natural professional phrasing;

human conversational rhythm;

proportionate explanation;

language appropriate to a LinkedIn comment.

Low score:

essay-like framing;

report-like tone;

generic explanatory opening;

excessive rhetorical symmetry;

detached "correct answer" posture.

This dimension must not encourage slang, intentional errors, or artificial informality.

7.4 Selective Evidence Use

Question:

Does the draft use only the Research evidence needed to strengthen the contribution?

High score:

evidence improves thinking;

only necessary findings surface;

factual grounding remains intact;

omitted evidence does not weaken the central argument.

Low score:

the Writer tries to display the entire ResearchBrief;

multiple facts appear only because they were discovered;

caveats, metrics, controls, or examples exceed the needs of the social artifact.

Governing principle:

Research informs the Writer.

Research does not mandate exhaustive disclosure.

7.5 Stopping Discipline

Question:

Does the draft stop when the strongest useful contribution is complete?

High score:

strong natural ending;

no redundant final explanation;

no extra metric/framework paragraph after the conclusion is already clear.

Low score:

continues proving completeness;

restates the thesis;

adds a final explanatory layer with little marginal value;

feels unable to leave relevant information unused.

7.6 Synthetic Completeness Risk

Question:

How strongly does the draft exhibit rhetorical patterns that may make it feel generically LLM-produced even when technically excellent?

Unlike the other dimensions:

higher score = higher risk

Possible signals:

overly symmetrical structure;

polished thesis → enumeration → synthesis → closed conclusion pattern;

excessive parallelism;

exhaustive coverage;

multiple neatly balanced clauses;

unnecessary rhetorical perfection;

generic consultant / white-paper cadence;

every available nuance explicitly resolved.

This must be treated carefully.

The goal is not to detect whether AI wrote the text.

The goal is to detect whether the output has social-writing characteristics that reduce distinctiveness.

No authorship attribution should ever be made from this score.

7.7 Publication Likelihood

Question:

Given the draft and the accumulated Rodrigo Voice evidence, how likely is Rodrigo to publish this formulation without substantive editorial revision?

This is the closest semantic representation of:

Rodrigo would probably choose to publish this.

The score must be based on editorial fit, not only stylistic resemblance.

High Publication Likelihood requires more than a high-quality draft.

8. Diagnostic Lists

unnecessary_elements

The evaluator may identify specific draft elements that appear correct but editorially unnecessary.

Examples:

secondary metric list;

duplicated conclusion;

excessive governance dimensions;

extra example;

caveat not needed for the current social context;

formal phrase that adds little value.

This list must reference actual draft content.

It must not invent edits.

preserve_elements

The evaluator should identify the content that carries the distinctive contribution and should survive any future rewrite.

Examples:

central thesis;

useful operational mechanism;

one concrete example;

key causal consequence;

explicit Human-in-the-Loop boundary.

This protects against compression that destroys substance.

9. Decision Semantics

v0.1 decisions:

PASS
ADJUST

PASS means:

The draft is not only factually/professionally acceptable, but is also sufficiently aligned with Rodrigo's current editorial preference evidence to proceed to Human Review without an editorial rewrite request.

ADJUST means:

The draft is professionally viable but likely contains avoidable editorial mismatch.

Important:

ADJUST is not equivalent to factual failure.

It must not trigger Research again.

It must not automatically reject the opportunity.

It must not imply that the thesis is wrong.

10. Relationship with the Existing Quality Evaluator

The existing Quality Evaluator and Editorial Preference Evaluator solve different problems.

Quality Evaluator

Primary concerns:

factual accuracy;

relevance;

voice plausibility;

overall quality;

revision correctness.

Editorial Preference Evaluator

Primary concerns:

what Rodrigo would keep;

what Rodrigo would remove;

how much explanation is necessary;

whether the comment feels conversational rather than generated;

whether the draft stops at the right point;

whether the formulation is likely to be published.

The two evaluators should not be collapsed prematurely.

Conceptual sequence:

Writer
↓
Quality Evaluator
↓
Editorial Preference Evaluator
↓
Human Review

Alternative ordering may later be tested empirically.

No final graph change is approved by this document alone.

11. Golden Set Usage

The Golden Set is calibration evidence.

It should provide bounded examples of:

agentic_draft
→ human_final
→ published / not published

The evaluator should learn from the delta.

Useful comparison features include:

preserved concepts;

removed concepts;

Human-added concepts;

removed metrics;

removed examples;

softened or strengthened certainty;

changed opening;

changed closing;

sentence reduction;

change in number of parallel ideas;

stopping-point shift;

publication outcome.

The system should increasingly model editorial transformation rather than superficial lexical similarity.

12. Calibration Evidence Established So Far

The current Golden Set supports the following provisional hypotheses:

Rodrigo often preserves the core thesis while removing secondary explanatory detail.

Rodrigo tends to prefer one central contribution per LinkedIn comment.

Rodrigo values operational and architectural mechanisms.

Human-in-the-Loop is often expressed as a concrete workflow boundary.

Conversational professional positioning is preferred over white-paper exposition.

Supporting evidence is selectively surfaced rather than exhaustively exposed.

Strong endings should not be followed by another explanatory paragraph.

High existing voice_match scores do not yet reliably predict publication without revision.

Human revision often behaves as semantic compression rather than simple shortening.

Rodrigo may add a better synthesis during compression rather than merely deleting text.

Generic semantic correctness is insufficient differentiation because multiple users and LLMs can converge on the same obvious professional thesis.

These remain hypotheses.

They are not yet frozen production rules.

13. External Semantic-Convergence Observation

A real LinkedIn interaction exposed an important calibration risk.

Another public commenter independently expressed essentially the same semantic nucleus reached by the Agentic system:

understand the process
→ determine whether it should continue
→ redesign / simplify / eliminate
→ automate afterward.

The external text appeared to Rodrigo to have stylistic characteristics commonly associated with LLM-assisted professional writing.

No claim is made about whether the external author actually used AI.

The useful observation is:

semantic convergence is cheap.

A screenshot plus a general-purpose LLM can often produce a competent and polished answer to a public post.

Therefore, the final artifact must not rely on semantic correctness alone as differentiation.

The system should aim for:

correct intelligence
+
relevant contribution
+
Rodrigo-specific editorial selection
+
natural conversational formulation
+
Human publication authority

14. Anti-Goals

Editorial Preference must not become:

an "AI detector";

a detector of whether another person used AI;

a forced brevity mechanism;

a style-transfer gimmick;

a list of banned phrases;

a hardcoded imitation engine;

a mechanism that intentionally introduces mistakes;

a substitute for factual grounding;

a substitute for Human Review.

The system should not optimize for appearing "less AI" through artificial imperfections.

It should optimize for authentic editorial fit.

15. Deterministic vs Semantic Ownership

LLM owns

identifying the central thesis;

judging whether supporting material materially strengthens it;

detecting semantic redundancy;

identifying conversational-vs-expository mismatch;

estimating editorial relevance of details;

judging synthetic-completeness risk;

estimating publication likelihood;

explaining why a draft may need adjustment.

Python owns

validating score ranges;

validating allowed decisions;

enforcing bounded input size;

enforcing required fields;

deterministic routing once thresholds are eventually calibrated;

preventing Editorial Preference from rerunning Research;

preserving source and draft provenance;

preserving Human publication authority.

16. v0.1 Implementation Strategy

Phase 1 — Observation

Implement the structured evaluation contract without changing production routing.

Run it against existing Golden Set cases.

Compare predicted editorial issues with actual Human edits.

Goal:
measure whether the dimensions are meaningful.

Phase 2 — Calibration

Collect additional LinkedIn-native examples.

Prefer:

real public opportunities;

exact Agentic draft preservation;

exact Human Final preservation;

publication outcome;

blind Human comparison where practical.

Goal:
determine which dimensions reliably predict Human revision.

Phase 3 — Shadow Evaluation

Run Editorial Preference evaluation in the real workflow but do not allow it to alter Writer routing.

Record:

scores;

diagnostics;

Human action;

final publication choice.

Goal:
validate correlation without changing behavior.

Phase 4 — Controlled Rewrite Integration

Only after sufficient evidence:

Writer
↓
Quality Evaluator
↓
Editorial Preference
├── PASS → Human
└── ADJUST → Writer

If ADJUST later routes to Writer:

Research must not rerun;

the same ResearchBrief must be reused;

the rewrite instruction must concern formulation/editorial selection only;

revision count must remain bounded;

Human publication authority remains mandatory.

17. Proposed Initial Schema

Illustrative Pydantic direction:

class EditorialPreferenceEvaluation(BaseModel):
    central_thesis_focus: int = Field(ge=0, le=100)
    contribution_density: int = Field(ge=0, le=100)
    conversational_naturalness: int = Field(ge=0, le=100)
    selective_evidence_use: int = Field(ge=0, le=100)
    stopping_discipline: int = Field(ge=0, le=100)
    synthetic_completeness_risk: int = Field(ge=0, le=100)
    publication_likelihood: int = Field(ge=0, le=100)

    unnecessary_elements: list[str]
    preserve_elements: list[str]
    editorial_reason: str

    decision: Literal["PASS", "ADJUST"]

This schema is a design proposal.

Do not implement final deterministic thresholds before calibration evidence supports them.

18. Test Contract

Initial isolated tests should eventually validate:

all scores remain inside 0–100;

decision is restricted to PASS / ADJUST;

evaluator receives the actual draft;

evaluator may receive ResearchBrief without mutating it;

source context is available;

empty draft is rejected;

unnecessary_elements and preserve_elements are bounded;

Editorial Preference cannot trigger Research;

Human publication authority remains unchanged;

a future ADJUST loop, if implemented, reuses the existing ResearchBrief;

maximum editorial revision iterations are bounded;

deterministic tests use mocked semantic evaluation.

Golden Set regression tests should not require live LLM calls.

19. Success Criteria for v0.1

Editorial Preference v0.1 is successful if it provides a useful structured explanation of why a technically strong draft would or would not likely survive Rodrigo's Human Review.

It is not necessary for v0.1 to perfectly predict publication.

It is necessary for it to create measurable calibration data.

Minimum success evidence:

existing Golden Set cases can be scored;

diagnostics correspond meaningfully to actual Human edits;

the evaluator does not confuse factual quality with editorial preference;

high-quality-but-overcomplete drafts can be distinguished from publication-ready drafts;

no Research rerun or autonomous publication behavior is introduced.

20. Current Decision

Approved conceptual direction:

Editorial Preference should become an explicit capability.

Not yet approved:

final production thresholds;

automatic Writer revision routing;

merging with Quality Evaluator;

model selection;

permanent Social Writing Contract;

AUTHORIAL_POST reuse;

autonomous publication.

Next development step:

Define the actual Pydantic input/output schemas and isolated semantic evaluator interface while keeping the capability out of production routing.

EDITORIAL PREFERENCE CHECKPOINT — v0.2.2 EXPERIMENTAL BASELINE

This section supersedes earlier schema and next-step declarations in this document where they conflict with the implemented experimental state.

Status

Editorial Preference and Editorial Rewrite have progressed beyond the original v0.1 design proposal.

Current experimental baseline:

v0.2.2

Focused regression status:

43 passed

Current implementation remains outside authoritative production routing.

No production threshold is frozen.

Human publication authority remains mandatory.

Current Evaluation Schema

The current Editorial Preference Evaluation includes:

central_thesis_focus
contribution_density
conversational_naturalness
selective_evidence_use
stopping_discipline
front_loaded_value
synthetic_completeness_risk
publication_likelihood

core_thesis
must_preserve_elements
optional_support_elements
remove_or_compress_elements

editorial_reason
decision = PASS | ADJUST

The original preserve_elements / unnecessary_elements distinction was replaced because it overloaded correctness, usefulness, and editorial necessity.

Core Thesis Scarcity

core_thesis must contain exactly one dominant professional contribution.

Governing question:

If the reader remembers only one professional idea from this comment,
what should it be?

Do not combine multiple independent useful insights simply because they are all correct.

Must-Preserve Semantic Minimum

must_preserve_elements means:

minimum semantic content required for core_thesis to survive

It does not mean:

everything correct
everything useful
everything technical
everything supported by Research
everything well written

Apply the counterfactual test:

If this meaning is removed, does core_thesis still survive intact?

If yes, it is not mandatory.

Optional Support

optional_support_elements contains correct and potentially useful material that may strengthen the thesis but is not required for it to survive.

Examples may include:

metrics;

compliance / risk caveats;

examples;

secondary mechanisms;

evidence;

additional operational criteria;

consequences.

Optional means genuinely optional.

Front-Loaded Value

front_loaded_value evaluates whether the reader receives the main professional contribution early.

It does not merely evaluate whether the opening is relevant or interesting.

Governing question:

If the reader consumes only the opening block,
do they already know the main point being contributed?

This dimension is inspired by answer-first executive communication and the practical possibility of LinkedIn visual truncation.

It remains contextual.

It must not become a deterministic rule that every comment uses the same sentence order.

Real Case Result

The v0.2.2 experiment improved semantic decomposition.

The system correctly isolated a single core thesis around questioning whether a process step should exist before automation.

It also correctly moved previously over-preserved supporting material into optional support.

The decision changed to:

ADJUST

which better matched the actual Human behavior.

However, the subsequent AI Rewrite still selected a formulation Rodrigo would likely discard.

The Rewrite preserved technically reasonable caveats while removing a compact operational mechanism that Rodrigo actually chose to preserve in his Human Final.

This is strong evidence that:

correct semantic decomposition
!=
perfect contextual editorial preference

Architectural Decision — Freeze Manual Prompt Tuning

Do not continue indefinitely tuning this prompt against one example.

Reason:

Editorial preference may change according to:

content context;

interaction goal;

source author;

topic;

audience;

desired professional positioning;

available Research;

conversation tone.

Repeatedly encoding post-specific discoveries into static prompt policy risks overfitting.

The current v0.2.2 prompt should therefore remain an experimental baseline while the project collects additional real-world cases.

Learned-Preference Direction

The preferred long-term architecture is based on real Human decisions:

Agentic Draft
↓
Human Final / Human Rejection
↓
Feedback Capture
↓
Preference Memory
↓
Contextual Retrieval
↓
Future Writer / Rewrite

Important Human outcomes:

PUBLISHED AS-IS
EDITED + PUBLISHED
DISCARDED

All three should become calibration evidence.

Future Feedback Capture Contract

Future direction:

HumanEditLearningRecord

case_id
content_intent
source_context
objective

agentic_draft
human_final
publication_outcome

preserved_meanings
removed_meanings
added_meanings
reordered_meanings

tone_shift
density_shift
opening_shift
closing_shift

likely_editorial_preference
confidence

This record should describe the observed transformation.

It must not silently convert a single observed edit into permanent global policy.

Global vs Contextual Preference

Future calibration should distinguish:

GLOBAL PREFERENCE
patterns recurring across many examples

CONTEXTUAL PREFERENCE
patterns relevant only under particular circumstances

The system should eventually retrieve bounded relevant prior cases rather than injecting the entire calibration history into every generation.

Current Calibration Principle

The strongest current formulation is:

Rodrigo Voice is not a static prompt.
It is an editorial decision function inferred from real choices.

Golden Set evidence remains useful.

It should increasingly be treated as training / calibration evidence for contextual preference rather than as a growing list of manually hardcoded universal rules.

Next Calibration Step

Do not continue refining against the same real post.

Collect additional genuine interaction cases through real opportunity discovery.

For each case preserve:

source opportunity
research evidence
agentic draft
Human action
Human final when applicable
publication outcome

Future Human Feedback Learning / Preference Memory implementation should be driven by that larger evidence base.

Real opportunity discovery currently has priority over further prompt refinement.