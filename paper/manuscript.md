# The Intelligence Attractor Hypothesis

# Publication scope and interpretive notes

## Independent Convergence Under Shared Reality Constraints

**Vitalii Zhyliaiev**

**Conceptual preprint with five supporting appendices**

**Version:** 0.1

**Prepared:** 6 September 2026

**License:** [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) for the publication text and appendices. Repository software is outside this license.

This work presents a developing hypothesis and research program. No empirical validation or peer review is claimed. The literature map is preliminary and AI-assisted. The author's initial intuition preceded acquaintance with the adjacent literature; independent conception does not establish novelty or priority.

The main text contains the canonical IAH statement. Appendices A-C develop origin dependence, recursive architectural optimization and functional uniqueness. Appendix D provides a preliminary related-work map. Appendix E preserves maximal and metaphysical conjectures, including absolute architectural uniqueness, with their separate evidential status.

## How to read this edition

The author's motivating intuition, the canonical hypotheses and the empirical program are related but distinct. Strong IAH concerns a limiting functional equivalence class in a specified domain. Appendix E's U3 goes further, conjecturing a unique substantive realization. Weak IAH supplies finite-domain predictions of narrowing and origin attenuation. Evidence for Weak IAH alone cannot establish either stronger claim.

All five appendices are included in this document. The detailed experimental protocol and Arena software remain companion repository materials, not completed results reported here. A changing context may change the optimum; no timeless universal machine is asserted by the canonical statement.

## Notation and interpretive notes for version 0.1

These notes identify unresolved formal distinctions while retaining the substantive statements below.

1. **Sampling versus geometry.** In the main text, D at a given regret is an expected distance between independently generated systems. In Appendix C, the near-optimal-set diameter is a worst-case property of all admissible candidates. The former depends on the distribution of optimization outcomes. A small sampled mean does not establish a small global diameter, and unvisited optimal families may remain.
2. **Concentration versus a stable limit.** Vanishing distance among systems at the same regret does not, by itself, guarantee convergence to one fixed functional class across successive regret levels. The limiting-class interpretation of Strong IAH additionally requires stability across those levels and suitable properties of the functional space. A complete set of sufficient conditions remains open.
3. **Origin effects.** Absolute origin-attributable differences and the fraction of variance attributed to origin are different estimands. A falling fraction need not mean a falling absolute effect. Matching on achieved regret can introduce selection bias; causal identification requires a specified intervention design and analysis, not conditioning alone.
4. **Nested sets and non-attainment.** The diameter of nested cumulative near-optimal sets is non-increasing by construction, but need not tend to zero. A non-attained supremum prevents a literal claim about an existing maximizer; it does not by itself refute near-optimal concentration. This distinction governs the non-attainment entry among Appendix C's limiting cases.
5. **Maximal realization count.** Appendix E's effective count K is a schematic quantity whose estimator or mathematical definition is not supplied here. Its near-frontier expression is an additional conjectural analogue, not a proved equivalent of the exact argmax statement. E1/E2, D1, R1 and U1/U2 are supporting-document labels; they do not introduce additional canonical versions beyond Weak and Strong IAH.

## Preliminary relationship to earlier work

The conceptual overlap with contravariance, representational convergence and implicit bias is substantial. In particular, Nayebi's selection theorems already connect vanishing pair-regret and representational equivalence under additional assumptions. Fixed-task evaluation and regret approaching zero are therefore not, by themselves, claims of novelty for IAH.

The proposed joint study of functional diversity, origin dependence, mutable architecture and independent optimization lineages remains a candidate research contribution. This edition does not establish that the combination is unprecedented or that IAH subsumes the cited theories. Appendix D records the sources and the limits of the current comparison.

# Main text - Canonical statement

## Independent Convergence Under Shared Reality Constraints



**Status:** Canonical flagship statement of a developing hypothesis; not experimentally validated

This document is the stable public statement of the Intelligence Attractor Hypothesis (IAH). Supporting formal extensions, experimental protocols, speculative interpretations, and historical development are maintained separately.


---

## Abstract

The **Intelligence Attractor Hypothesis** proposes that independently formed intelligent systems, when optimized toward the same performance frontier under the same task, objective, context, and binding constraints, progressively lose functionally consequential differences that arise from arbitrary historical origin.

The proposed mechanism is constraint-driven elimination of costly functional freedom. Early in optimization, many architectures, algorithms, representations, and strategies may remain competitive. As shared bottlenecks become binding, fewer ways of organizing the system may preserve near-frontier performance. Different lineages may therefore discover the same functional principles without copying one another.

IAH has two canonical forms. **Weak IAH** predicts decreasing functional diversity and decreasing origin sensitivity near a frontier, while allowing several persistent solution families. **Strong IAH** conjectures that, at a specified functional level, near-frontier diversity tends to zero and independently optimized systems approach one limiting class of functional equivalence.

Architecture is part of the central scope, not an automatic conclusion. When internal architecture is mutable, causally relevant, and performance-limiting, it becomes part of the optimization landscape. Whether architectural diversity merely narrows or vanishes is then an empirical distinction between the weak and strong forms.

## 1. Foundational Claim

The identity of IAH is captured by the following claim:

> **Under a fixed task, objective, context, and admissible design space, independent optimization toward a shared performance frontier progressively replaces origin-contingent functional variation with structure determined by the task and its binding constraints. When the system's internal architecture is mutable and functionally consequential, the same pressure extends to its architectural organization.**

The motivating asymmetry is simple:

> There may be far more ways to remain inefficient than ways to remain functionally competitive near a frontier.

Systems need not converge through communication, imitation, or shared implementation. The distinctive case is **convergence without inheritance**: different origins and different optimization histories independently encounter the same bottlenecks and reconstruct some of the same solutions.

The claim concerns functional consequences, not textual or material identity. Two systems may use different names, encodings, component layouts, or interchangeable implementations while belonging to the same functional class at the level being studied.

## 2. Domain and Performance

Every statement of IAH is relative to a specified domain. Let:

$$
\Omega=(e,\mathcal T,\mathcal R,\mathcal I,H)
$$

denote the relevant environment state, dynamics, resources and physical constraints, information interface, and evaluation horizon. Let:

$$
Q,\qquad O_i,\qquad \mathcal X
$$

denote:

- the objective or evaluation rule \(Q\);
- the origin vector \(O_i\) of lineage \(i\);
- the admissible design space \(\mathcal X\).

Origin variables may include initialization, random seed, data order, model ancestry, starting language or architecture, inherited conventions, and optimization history. They must be varied or recorded independently of the task, objective, and current environment.

For a system \(X\in\mathcal X\), performance is:

$$
Q(X\mid\Omega).
$$

The performance frontier is:

$$
Q^*(\Omega)
=
\sup_{X\in\mathcal X}Q(X\mid\Omega).
$$

The frontier is the best value allowed by the specified domain. It may be an attained maximum or a supremum that finite systems can only approach.

The regret of \(X\) is its performance shortfall:

$$
r(X\mid\Omega)
=
Q^*(\Omega)-Q(X\mid\Omega).
$$

Thus \(r\downarrow\) means that performance approaches the frontier, and \(r=0\) means that the frontier is attained.

For dynamic or stochastic tasks, the candidate may be a policy rather than an isolated action. The context and horizon must state which future consequences are evaluated. No physical freezing of time is required; a changing context simply defines a different optimization problem or a policy over changing states.

## 3. Functional Levels

Convergence must be evaluated at a prespecified level \(\ell\). Candidate levels include:

| Level | Examples of relevant observables |
| --- | --- |
| Outcome | task score, error, reliability |
| Behavior | response profiles, intervention responses, failure patterns |
| Strategy | decomposition, planning, allocation, control policy |
| Algorithm | invariants, complexity, search or approximation method |
| Architecture | dataflow, memory organization, topology, modularity, scheduling |
| Resources | latency, energy, memory, communication, learning and switching cost |

Let:

$$
d_\ell(X_i,X_j)
$$

be a preregistered functional distance at level \(\ell\). It must be defined through observables and invariances chosen before results are inspected. Equal scalar scores do not by themselves make two systems functionally equivalent.

To avoid a trivial effect from repeatedly selecting a smaller cumulative near-optimal set, IAH compares independent systems at matched performance. Define:

$$
D_\ell(r)
=
\mathbb E\!\left[
d_\ell(X_i,X_j)
\mid
i\neq j,\;
r(X_i)\approx r(X_j)\approx r
\right].
$$

Empirical studies approximate this quantity with preregistered regret bands, uncertainty models, and robust pairwise summaries. The lineages, not merely the selected solutions, must be independent enough for common inheritance to be measured as a confound.

Let \(OS_\ell(r)\) denote **Origin Sensitivity**: the effect of controlled origin interventions on prespecified functional properties at level \(\ell\), compared at matched regret. No universal estimator is assumed; factorial interventions and variance decomposition are preferred where possible.

Because achieved regret is itself affected by origin and optimization, conditioning on it can create selection bias. Confirmatory analysis must therefore combine matched-regret comparisons with unconditional trajectories, attrition reporting, and joint causal or hierarchical models.

## 4. Weak IAH

Weak IAH predicts two related but separately testable trends:

$$
\boxed{
\text{Weak IAH:}\qquad
r\downarrow
\Longrightarrow
D_\ell(r)\downarrow
\quad\text{and}\quad
OS_\ell(r)\downarrow
}
$$

In words:

1. **Functional Narrowing:** independently optimized systems tend to become functionally less diverse as they approach the same frontier.
2. **Origin Attenuation:** their functionally relevant properties tend to become less causally dependent on arbitrary origin.

The arrows express statistical tendencies over a prespecified near-frontier regime, not strict monotonicity at every iteration. Diversity may initially expand during exploration, contract when common bottlenecks become active, and then plateau above zero.

Weak IAH therefore allows:

- several stable near-optimal functional families;
- residual path dependence;
- modular or symmetric alternatives;
- different architectures implementing similar strategies;
- convergence at one functional level and persistence at another.

Evidence may support Functional Narrowing without Origin Attenuation, or the reverse. Such results must be reported separately rather than collapsed into a single positive label.

## 5. Strong IAH

Strong IAH makes the limiting claim:

$$
\boxed{
\text{Strong IAH at level }\ell:\qquad
\lim_{r\downarrow0}D_\ell(r)=0
}
$$

For the fixed domain and functional level, independently optimized systems approach one limiting class of functional equivalence as their regret approaches zero.

Unity is not introduced as a separate convergence score: zero functional distance already expresses the claim without requiring an arbitrary normalization. The limit does not assert that every real experiment must observe an exact zero. Some domains attain their optimum; others permit only progressively closer approximations.

Strong IAH is stronger because it excludes persistent, functionally distinct optimal families at the specified level. It is not stronger because it applies to every possible task. A domain may support Weak IAH and reject Strong IAH.

At the architectural level, Strong IAH states:

> If architecture is mutable, included in the admissible design space, and evaluated through independently specified functionally consequential observables, near-frontier systems approach one functional architectural equivalence class.

This does not assert one literal graph, program, substrate, or arrangement of matter. Exact symmetries and transformations declared irrelevant by the metric are quotiented out. Conversely, architectures must not be declared equivalent merely because they receive the same score; doing so would make the strong claim tautological.

## 6. Proposed Mechanism

IAH proposes a transition in what explains system structure:

$$
\text{origin-contingent freedom}
\;\longrightarrow\;
\text{constraint-determined functional structure}.
$$

The mechanism has four parts:

1. Different origins populate different regions of the design space.
2. Optimization removes errors and inefficiencies under a shared objective.
3. Common bottlenecks make deviations from some functional properties increasingly costly.
4. Independent lineages repeatedly retain the properties compatible with near-frontier performance.

For a distributed software system, different languages and initial architectures might independently discover bounded queues, backpressure, locality, minimal copying, fault isolation, or similar scheduling principles. The surface implementations may remain different while the bottleneck-removing organization converges.

The mechanism is a conjecture, not a definition. Constraints can also create niches, compensating trade-offs, or new forms of specialization. The empirical question is whether elimination of costly functional freedom dominates the creation of alternative competitive solutions in the domain being tested.

## 7. Architectural Depth

The optimizer becomes part of the optimization problem whenever the machinery used to discover and realize a solution has consequences under \(Q\).

Two systems may produce the same output while differing in:

- computation and learning cost;
- latency and energy;
- memory and communication;
- robustness and error correction;
- scalability and adaptation;
- construction, maintenance, or switching cost.

If such properties matter to the objective and can be modified, external optimization pressure can migrate inward:

> **As external inefficiencies are removed, any remaining mutable internal property that materially limits performance becomes part of the effective optimization landscape.**

This preserves the architectural ambition of IAH without assuming its conclusion. Optimization pressure on architecture does not logically guarantee architectural convergence. Weak and Strong IAH must be tested at the architectural level using observables independent of the final scalar score, such as causal response profiles, scaling curves, dataflow, memory organization, error propagation, and adaptation under perturbation.

The same reasoning may be tested across progressively richer intervention spaces—policy, representation, algorithm, architecture, and optimization mechanism. Each expanded space is a new empirical domain; it cannot be invoked to erase a negative result in an earlier one.

## 8. Why IAH Is Not Trivial Optimization

Ordinary optimization states that higher-scoring candidates are preferred. It does not imply that:

- independent near-frontier systems become closer at matched regret;
- origin explains less of their remaining functional structure;
- the same bottleneck-removing principles are rediscovered without inheritance;
- convergence penetrates from outcomes into algorithms or architecture;
- one limiting functional class remains at the frontier.

Nor does IAH follow from measuring the diameter of nested cumulative near-optimal sets: those sets shrink by construction. The nontrivial test compares independently generated systems within matched regret bands and asks whether functional and origin-dependent variation changes beyond selection, shared ancestry, and measurement artifacts.

## 9. Evidence

Evidence for Weak IAH in a specified domain would require:

- genuinely varied and recorded origins;
- independent optimization without access to other lineages;
- a shared, frozen task, objective, context, and resource regime;
- improvement toward a known or reproducibly estimated frontier;
- preregistered functional observables and distances;
- lower \(D_\ell(r)\) at matched lower regret;
- lower origin-attributable variation at matched lower regret;
- controls for shared training data, libraries, templates, and evaluator leakage;
- preservation of negative, divergent, and failed lineages.

Evidence becomes stronger when common inheritance is reduced and the same functional principles are reconstructed through different histories, representations, languages, model families, or architectures.

Repeated independent discovery is mechanistic evidence, not sufficient proof by itself. Textual code similarity, a single optimization trajectory, or convergence among near-identical models is weak evidence.

## 10. Falsification and Legitimate Failure

Weak IAH is weakened in a preregistered domain when adequate optimization and measurement show that:

- functional diversity remains stable or increases as matched regret decreases;
- controlled origin variables continue to explain the same or a greater share of functional variation;
- apparent convergence disappears after common-inheritance controls;
- convergence occurs only in surface syntax while causal and resource profiles remain distinct.

Strong IAH is rejected at a specified level by persistent, functionally inequivalent optimal or arbitrarily near-optimal families whose distance remains bounded away from zero under the preregistered metric.

Legitimate counterexamples include multiple optima, exact symmetries, neutral networks, specialization, plateaus, and irreducible trade-offs. They are scientific outcomes, not defects that may automatically be removed by adding retrospective criteria.

Failure to reach the frontier is an optimization failure rather than direct evidence about its geometry. Attrition must nevertheless be retained because conditioning only on successful lineages can manufacture apparent convergence.

No negative result may be dismissed by appealing after the fact to an unspecified deeper design space, a more complete objective, unknown physics, or an inaccessible future intelligence.

## 11. Scope Boundaries

IAH is conditional on the specified task, objective, context, horizon, design space, and functional level. It does not claim that all intelligent systems converge across different goals or environments.

Reality determines available consequences and costs; \(Q\) determines how those consequences are ranked. Additional causal knowledge can reveal hidden consequences but does not derive one universal morality or terminal objective.

IAH does not imply literal identity, complete prediction, infinite intelligence, or a timeless optimal machine. In changing environments, the relevant optimum may be a moving policy class. Claims about one substantive physical realization, complete causal optimization, relativistic global policies, objective convergence, or theological identity belong to speculative extensions rather than the canonical scientific claim.

## 12. Research Program

The first experimental target is not proof of a universal attractor. It is a controlled test of Weak IAH and a finite-domain test of Strong IAH at prespecified functional levels.

The current program consists of:

1. selecting a bounded task with a known or estimable frontier;
2. defining functional metrics and origin interventions before observing outcomes;
3. optimizing independent lineages under shared evaluation and resource constraints;
4. comparing functional diversity and origin sensitivity in matched regret bands;
5. testing whether convergence reaches mutable algorithms and architectures;
6. retaining persistent degeneracy as a possible result.

The hypothesis has not yet been empirically validated. Its immediate scientific value lies in turning an architectural intuition into a falsifiable study of the geometry and provenance of independently discovered near-optimal systems.

## Supporting Documents

- [Experimental Program](https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/ideas/experimental-program.md) — general operational methodology.
- [Origin Dependence and Attenuation](#appendix-a) — origin variables, interventions, and confounds.
- [EXP-001: Independent Self-Improving Lineages](https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/experiments/001-independent-self-improving-lineages/README.md) — first concrete protocol.
- [IAH Arena](https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/arena/README.md) — experimental infrastructure.
- [Recursive Architectural Attractor](#appendix-b) — nested intervention spaces and self-modification.
- [Relational Narrowing and Strong Functional Uniqueness](#appendix-c) — uniqueness arguments and counterexamples.
- [Related Work Map](#appendix-d) — literature-positioning plan.
- [Speculative Limits](#appendix-e) — physical, relativistic, objective-level, and theological limits.

# Origin of the hypothesis and AI assistance

**Publication edition:** v0.1, prepared 6 September 2026

## Origin of the idea

The initial intuition behind the Intelligence Attractor Hypothesis was developed by the author before becoming acquainted with the adjacent research literature. Its starting point was a strong conjecture: for a specified task, objective and concrete world context, extreme optimization might select a unique optimal solution and a unique substantive architecture and reasoning organization of an agent. Independent agents approaching that limit would consequently become increasingly alike.

Subsequent development distinguished this motivating maximal conjecture from the canonical Strong IAH claim of functional equivalence and from the weaker, empirically accessible predictions of functional narrowing and origin attenuation. The maximal conjecture is retained in Appendix E; it has not been established by the empirical program. The origin of an idea and its evidential status are different matters.

## Role of AI assistants

AI assistants helped articulate and formalize the author's intuition, challenge arguments, identify counterexamples and ambiguities, edit and organize the English text, develop the experimental program, and discover potentially related literature. An AI-assisted audit informed the preliminary source map in Appendix D. AI assistance was substantive and was not limited to spelling or bibliography formatting.

The source notes distinguish bibliographic verification, reading of abstracts or selected results, and fuller source inspection performed by an assistant. These activities do not imply that the author has personally read every cited work or independently verified its proofs. This edition does not claim a completed author-conducted literature review. The comparisons are provisional and open to correction.

## Authorship, novelty and responsibility

Vitalii Zhyliaiev is the author of IAH and is responsible for the decision to release a particular edition and for how its claims are presented. AI tools are disclosed as assistance, not listed as authors. Neither independent conception nor an AI-assisted search establishes scientific priority, originality, validity or subsumption of existing theories.

The author welcomes references to overlooked prior work, precise overlaps, counterexamples and corrections. Feedback should identify the publication version and relevant section. Subsequent editions may revise claims; substantive changes will be recorded rather than silently attributed to earlier versions.

## Editorial boundary

This edition preserves the canonical Weak/Strong IAH distinction and the full substantive scope of all five supporting documents. New editorial notes identify mathematical and literature-review limitations without silently replacing the author's claims. No empirical validation, peer review, institutional affiliation or academic acceptance is claimed.

# Appendix A - Origin Dependence and Attenuation

## A Testable Prediction of the Intelligence Attractor Hypothesis




**Status:** Testable hypothesis; no empirical validation claimed


---

## A.1 Purpose

Present-day AI systems differ for many reasons that are not intrinsic to the task they are asked to solve. The **Origin Attenuation** hypothesis asks whether the functional influence of those origin-dependent differences decreases as independently optimized systems approach a shared performance frontier.

The hypothesis is not that all agents will produce identical text, code, or architecture. It concerns prespecified functionally important properties after controlling for common inheritance, evaluator bias, and measurement uncertainty.

## A.2 Origin Variables

An **origin vector** records the historically contingent properties of an agent or optimization run that the experiment deliberately varies or tracks.

It is a heterogeneous vector rather than a natural scalar:

$$
O_i=
(
O_{initialization},
O_{seed},
O_{ordering},
O_{history},
O_{ancestry},
O_{implementation},
O_{development},
\ldots
).
$$

Depending on the experiment, origin variables may include:

- parameter initialization;
- training seed;
- data ordering;
- training and optimization history;
- architecture ancestry;
- implementation history;
- stochastic developmental path;
- inherited conventions not required by the task.

The experiment must state in advance which components are varied and which are held constant.

## A.3 What Origin Variables Do Not Include

The origin vector should not absorb every source of uncertainty.

In particular, it must remain separate from:

- the current environment state;
- the objective;
- resource and physical constraints;
- transition dynamics;
- uncertainty about future trajectories;
- measurement noise.

Conceptually:

$$
O_i
\neq
P(\tau\mid\Omega_t,a).
$$

The origin vector describes the origin and contingent path of the system. The trajectory distribution describes how the environment may evolve under an action or policy.

The central question is whether, under matched external conditions, changing \(O_i\) continues to change functionally important properties near the frontier.

## A.4 Central Prediction

Let an optimization process run under budget \(b\) and produce:

$$
X_b(O_i\mid\Omega_t,Q,\mathcal X_n).
$$

IAH predicts:

> **Within a fixed context, objective, and prespecified design space, variation in prespecified functional properties attributable to arbitrary origin variables tends to decline as independently optimized systems approach the attainable performance frontier.**

This does not assert that origin dependence always vanishes. Origin may remain influential when:

- the objective has several distinct optima;
- symmetries preserve alternative solutions;
- optimization remains trapped in different local regions;
- constraints are weak or non-binding;
- several niches are equally competitive;
- the chosen functional description ignores relevant differences.

## A.5 Operational Origin Sensitivity

The earlier expression:

$$
\frac{\partial Solution}{\partial O}
$$

is not generally well-defined because origin contains discrete, continuous, categorical, and historically structured variables.

An operational alternative is to compare systems produced under controlled origin interventions at matched achieved regret.

For prespecified functional observables \(\Psi_\ell\), a provisional matched-regret quantity is:

$$
OS_{n,\ell}(r)
=
\operatorname{Effect}_{O}
\left(
\Psi_\ell(X_b(O))
\mid
r_n(X_b(O))\approx r
\right),
$$

where:

- \(O\) contains controlled origin interventions;
- \(n\) identifies the design space;
- \(\ell\) identifies the functional level being compared;
- \(b\) is recorded optimization budget;
- external context and objective are fixed;
- systems are compared at matched regret \(r\).

The operator \(\operatorname{Effect}_{O}\) must be instantiated by the study. A pairwise controlled comparison is one option. A stronger statistical design may estimate the proportion of variance in predefined functional features causally attributable to origin while controlling for performance, optimization budget, task instance, model family, and measurement error.

No universal Origin Sensitivity metric is assumed.

## A.6 Functional Distance

Literal source-code or text similarity is not the target.

Experiments may measure distinct distances:

$$
D_{outcome},
\quad
D_{behavior},
\quad
D_{strategy},
\quad
D_{representation},
\quad
D_{algorithm},
\quad
D_{architecture},
\quad
D_{resource}.
$$

For each level, researchers must preregister:

- observable features;
- invariances and symmetries;
- the distance or pseudometric;
- the evaluation distribution;
- the tolerance for approximate equivalence.

Choosing after the experiment whichever property happened to converge would not constitute strong evidence.

## A.7 Shared Data: Contamination or Constraint Information?

Shared data is not automatically evidence against IAH.

### Historical contamination

Agents may converge because they inherited the same ready-made solution, implementation, convention, or highly specific human pattern.

For example:

$$
shared\ corpus
\rightarrow
copied\ implementation
\rightarrow
same\ solution.
$$

This is weak and heavily confounded evidence.

### Constraint information

An environment may independently generate observations from which different systems infer similar effective principles:

$$
environment
\rightarrow
observations
\rightarrow
independent\ learning
\rightarrow
convergent\ solution.
$$

Here data is the channel through which environmental constraints enter cognition.

The scientific problem is to distinguish inheritance of a solution from independent reconstruction under common constraints.

## A.8 Evidence-Strength Ladder

Increasingly informative designs include:

1. **Same corpus → same answer.** Very weak; common inheritance dominates.
2. **Same observations → same strategy.** Weak; shared representation and training conventions may remain.
3. **Different priors and histories + same environment → same functional strategy.** Stronger.
4. **Different model families + independent exploration → same functional principles.** Stronger still.
5. **Different self-modifying architectures → convergence in prespecified architectural or resource properties.** Strong evidence for the architectural extension of IAH.

No single experiment establishes the full theory.

## A.9 Architectural Origin Dependence

Initial architecture can itself be an origin variable.

If architecture is fixed, an experiment can only test convergence within that inherited architectural family. If architecture is modifiable, a stronger question becomes available:

> Does dependence of functionally important architecture on initial architecture decrease as systems approach the frontier?

Conceptually:

$$
origin\ dependence\downarrow,
\qquad
constraint\ dependence\uparrow,
\qquad
functional\ architectural\ convergence\uparrow.
$$

This remains conditional. Expanded architectural freedom may also create new niches or symmetries and increase diversity.

## A.10 Minimal Experimental Design

A useful initial experiment should:

1. define a task and evaluation context;
2. specify the objective and resource accounting;
3. define the admissible design space;
4. select controlled origin variables;
5. run independent optimization trajectories;
6. estimate the attainable frontier or bounds;
7. preregister functional features and distances;
8. measure performance and functional distance jointly;
9. control common data, shared implementations, and evaluator leakage;
10. report uncertainty and negative results.

Tasks with exhaustively enumerable or provably bounded optima are especially valuable for early tests.

## A.11 Falsification and Limitations

Evidence against the Origin Attenuation hypothesis includes:

- origin variables continuing to explain stable functional differences at matched near-frontier performance;
- no reduction in origin-attributable variance as regret decreases;
- convergence disappearing after common-inheritance controls;
- task constraints explaining less variation than historical origin near the frontier.

A negative result applies to the preregistered task, metric, design space, and origin intervention. It cannot be dismissed by redefining functional relevance or moving to a deeper design space after seeing the result.

Origin Attenuation is a proposed empirical signature of IAH, not yet empirical evidence for it.

For the wider methodology, see [Experimental Program for the Intelligence Attractor Hypothesis](https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/ideas/experimental-program.md).

# Appendix B - Recursive Architectural Attractor

## Nested Design Spaces and Open-Ended Optimization Depth




**Status:** Theoretical and experimentally extensible component of IAH


---

## B.1 Architecture Becomes Part of the Solution

Several agents may achieve the same external result while differing substantially in:

- computation;
- latency;
- energy;
- memory;
- learning cost;
- communication;
- robustness;
- hardware requirements.

If these differences have consequences under the objective, the agents are not equally system-optimal even when they are outcome-equivalent.

> **The same constraints that narrow the space of effective external solutions may also narrow the space of efficient optimizers capable of discovering and realizing those solutions.**

This is the motivation for an architectural extension of IAH.

## B.2 The Recursive Optimization Principle

Optimization may act not only on an external action but also on the machinery that generates actions.

A conceptual sequence is:

$$
action
\rightarrow
policy
\rightarrow
representation
\rightarrow
algorithm
\rightarrow
architecture
\rightarrow
optimization\ mechanism.
$$

These are not asserted to be universal ontological layers. They identify classes of variables that may become accessible to intervention.

The **Recursive Optimization Principle** proposes:

> If an internal implementation variable is causally modifiable and materially affects the objective, sufficiently capable optimization may make that variable part of the optimization problem.

This principle does not guarantee convergence, improvement, or discovery of a global optimum.

## B.3 Nested Intervention Spaces

For controlled analysis, define:

$$
\mathcal X_0
\subset
\mathcal X_1
\subset
\mathcal X_2
\subset\cdots
$$

through increasingly rich allowed interventions.

An example hierarchy is:

| Space | Allowed variation |
| --- | --- |
| \(\mathcal X_0\) | fixed policy parameters |
| \(\mathcal X_1\) | trainable policy |
| \(\mathcal X_2\) | trainable policy and representation |
| \(\mathcal X_3\) | modifiable algorithm or modules |
| \(\mathcal X_4\) | modifiable architecture |
| \(\mathcal X_5\) | modifiable optimization mechanism |

No fixed universal number of spaces is proposed.

In real engineering, design families may not be naturally nested. For experiments, nesting should be created explicitly by defining cumulative intervention permissions.

For each space:

$$
\mathcal A_n
=
\mathcal A(\mathcal X_n,\Omega_t,Q)
$$

denotes its conditional attractor-like or near-optimal region.

## B.4 Two Forms of Progress

### Optimization within the current space

The system moves toward better candidates inside a fixed \(\mathcal X_n\).

Its progress can be measured by regret relative to the frontier attainable within that space.

### Expansion of the accessible space

A new intervention, representation, architecture, or physical mechanism makes previously inaccessible systems available:

$$
\mathcal X_n
\rightarrow
\mathcal X_{n+1}.
$$

The new space may contain a better frontier:

$$
Q_{n+1}^*
\ge
Q_n^*,
$$

provided \(\mathcal X_n\subseteq\mathcal X_{n+1}\) and the same objective and context are retained.

However, expansion may also increase diversity, introduce new symmetries, or create additional local and global optima. A better frontier does not imply a narrower frontier.

## B.5 Independent Falsifiability at Every Level

Each design-space claim must be specified and evaluated independently.

If functional narrowing is predicted in \(\mathcal X_n\) but does not occur, it is invalid to reply:

> The true attractor exists only in \(\mathcal X_{n+1}\).

Expansion to \(\mathcal X_{n+1}\) creates a new hypothesis with a new domain. It does not revise the result in \(\mathcal X_n\).

This rule prevents open-ended optimization depth from becoming a moving-goalpost defense.

## B.6 Architectural Convergence

When architecture is mutable and contributes to performance or cost, the relevant question is:

> As regret decreases, does the distance between prespecified functionally important architectural properties also decrease?

Potential observables may include:

- communication locality;
- memory organization;
- modular specialization;
- error correction;
- scheduling;
- topology;
- sparsity;
- redundancy;
- resource allocation;
- uncertainty processing.

These are examples, not claimed universals. Features must be selected before results are observed.

Convergence in one architectural property may coexist with divergence in another.

## B.7 Self-Modification

A self-modifying intelligence may generate a feedback loop:

$$
better\ cognition
\rightarrow
better\ diagnosis
\rightarrow
better\ self\text{-}design
\rightarrow
modified\ architecture
\rightarrow
new\ cognitive\ capability.
$$

This can increase accessible optimization depth. It can also:

- introduce regressions;
- become trapped in local optima;
- consume excessive search resources;
- damage previously useful capabilities;
- alter its own objective or evaluation mechanism;
- create irreversible path dependence.

Recursive self-modification is therefore an admissible optimization process, not a guarantee of monotonic progress.

The cost of redesign, evaluation, switching, and failed modifications must be included when those costs matter to the objective.

## B.8 Time and Accessible Depth

Both context and accessible design space may change:

$$
\mathcal A_n(t)
=
\mathcal A(\mathcal X_n,\Omega_t,Q).
$$

Two distinct changes are possible:

$$
\mathcal A(\mathcal X_n,\Omega_{t_1},Q)
\neq
\mathcal A(\mathcal X_n,\Omega_{t_2},Q),
$$

because context changed, and:

$$
\mathcal A(\mathcal X_n,\Omega_t,Q)
\neq
\mathcal A(\mathcal X_{n+1},\Omega_t,Q),
$$

because the intervention space expanded.

These mechanisms should not be conflated.

## B.9 Deeper Causal Accessibility

A currently optimal computational substrate may cease to be optimal after the discovery of a new causally useful mechanism.

Examples could include:

- a new physical state;
- an exploitable quantum effect;
- a new organization of matter;
- a different computational substrate;
- an intervention previously believed impossible.

This does not establish an infinite hierarchy or imply that every deeper physical description improves cognition.

“Deeper” should be interpreted operationally:

> A deeper layer is a newly available class of interventions that expands the admissible system space and permits measurable improvement under the same objective.

Unknown physics cannot be used as evidence for IAH. Only specified intervention spaces can be tested.

## B.10 Recursive Convergence Claim

### R1 — Cross-Space Recurrence

> Functional narrowing may recur separately across increasingly expressive, preregistered design spaces when newly accessible variables materially affect the objective.

R1 is stronger than ordinary outcome convergence because it proposes recurrence of a relationship between regret and functional diversity at multiple implementation levels.

R1 does not predict:

- that every expansion narrows the solution space;
- that all architectures become identical;
- that present physics reveals the final substrate;
- that convergence in one space implies convergence in the next.

## B.11 Evidence and Falsifiers

Evidence consistent with R1 would include:

- independently optimized systems converging first in behavior and later in prespecified architectural features as those features become mutable;
- origin dependence decreasing at several intervention levels;
- functional diameter decreasing with regret within multiple separately defined spaces;
- repeated emergence of the same functional architectural constraints across different starting families.

Evidence against a domain-specific recursive claim includes:

- mutable variables with measurable objective impact repeatedly remaining unrelated near the frontier;
- expanded design spaces increasing persistent functionally relevant diversity without the predicted narrowing;
- architectural convergence disappearing when common libraries or shared ancestry are controlled;
- no relationship between architectural distance and regret.

## B.12 Far-Limit Interpretation

A far-limit interpretation asks whether optimization could eventually include nearly every physically accessible degree of freedom relevant to an objective.

If such a limiting accessible space can be defined, a strong conjecture is that historically arbitrary functional variation may become small relative to variation dictated by the objective, environment, computation, resources, and physical constraints.

This is not required for the empirical core of IAH. It does not imply complete knowledge, universal values, literal physical identity, or physical attainability of an ultimate optimum.

For operational tests of nested design spaces, see [Experimental Program for the Intelligence Attractor Hypothesis](https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/ideas/experimental-program.md).

# Appendix C - Relational Narrowing and Strong Functional Uniqueness

**Status:** Formal and conceptual extension of IAH


---

## C.1 Purpose

This document develops two distinct propositions:

1. **Relational Narrowing:** adding prespecified causally relevant context may distinguish alternatives that appear tied under a lower-resolution description.
2. **Strong Functional Uniqueness:** under stated limiting conditions, all globally optimal realizations may belong to one functional equivalence class.

The first proposition motivates but does not prove the second.

## C.2 Relational Optimality

Optimality is not an intrinsic property of an isolated object. It is defined relative to a context and an objective.

Let:

$$
\Omega_t=(e_t,\mathcal T,\mathcal R_t,\mathcal I_t,H)
$$

denote the task-relevant environment state, dynamics, resources and physical constraints, information interface, and evaluation horizon.

The objective \(Q\), origin variables \(S\), and admissible design space \(\mathcal X_n\) are specified separately.

An alternative is evaluated as:

$$
Q(X\mid\Omega_t).
$$

Two structurally identical alternatives may differ operationally because their relations to the subject and environment differ. Distance, latency, energy required for interaction, causal position, timing, reliability, and future consequences may break an apparent tie.

Reality determines the consequences produced by an alternative. The objective determines how those consequences are evaluated.

## C.3 The Relational Narrowing Principle

At a coarse level of evaluation, two systems may appear equal:

$$
Q_{coarse}(A)=Q_{coarse}(B).
$$

For example, two agents may complete a game in exactly the same measured time. If the evaluation is expanded in a preregistered way to include operation count, energy proxy, memory, heat, learning cost, latency, and reliability, they may no longer remain tied:

$$
Q_{extended}(A)\neq Q_{extended}(B).
$$

Here \(Q_{coarse}\) and \(Q_{extended}\) are preregistered operational approximations to a stated target evaluation. They must not be invented after observing a tie. If new criteria change what is valued rather than improve measurement of the original criterion, the experiment has changed its objective and must be treated as a new domain.

This motivates:

> **As functionally different alternatives are embedded in an increasingly complete but prespecified causally relevant context, the set of contexts in which they remain accidentally tied may shrink.**

Relational Narrowing does not assert:

$$
A\neq B
\Rightarrow
Q(A)\neq Q(B).
$$

Physical difference alone is insufficient. The difference must alter consequences relevant to the specified evaluation.

The term **accidental tie** refers to equality caused by omitted resolution, omitted consequences, or incomplete preference specification—not equality protected by exact symmetry, genuine indifference, or a plateau in the objective.

## C.4 Functional Equivalence

Functional equivalence must not be defined as “having the same score.” That would make all tied maxima equivalent by definition and turn uniqueness into a tautology.

Instead, first define prespecified functional observables at level \(\ell\):

$$
\Psi_\ell(X,\Omega_t).
$$

Possible levels include:

- outcome;
- behavior;
- strategy or policy;
- representation;
- algorithm;
- architecture;
- resource profile.

In a deterministic setting:

$$
A\sim_{F,\ell,\Omega_t}B
\iff
\Psi_\ell(A,\Omega_t)
=
\Psi_\ell(B,\Omega_t).
$$

In a stochastic setting, \(\Psi_\ell\) may be a distribution over relevant trajectories, costs, and internal observables:

$$
A\sim_{F,\ell,\Omega_t}B
\iff
P(\Psi_\ell\mid A,\Omega_t)
=
P(\Psi_\ell\mid B,\Omega_t).
$$

An empirical pseudometric may then be defined as:

$$
d_{F,\ell}(A,B)
=
d\!\left(
P(\Psi_\ell\mid A,\Omega_t),
P(\Psi_\ell\mid B,\Omega_t)
\right).
$$

Exact equality is usually unobservable. Experiments therefore require a preregistered tolerance and uncertainty model.

Different levels require different equivalence relations. Two systems may be outcome-equivalent while remaining resource- or architecture-distinct.

## C.5 Pareto Fronts

When several objectives are present and their trade-offs are unresolved, near-optimal solutions may form a Pareto front.

For example:

$$
(speed,energy,reliability)
$$

may admit several nondominated alternatives.

A specified scalar objective can select a subset of that front:

$$
Q=f(speed,energy,reliability,\ldots).
$$

But scalarization does not mathematically guarantee uniqueness. Linear objectives may select an entire face, and nonlinear objectives may still contain plateaus or exact symmetries.

Strong Functional Uniqueness therefore remains an additional conjecture rather than a consequence of complete preference specification.

## C.6 Near-Optimal Concentration

For a design space \(\mathcal X_n\), define:

$$
Q_n^*(\Omega_t)
=
\sup_{X\in\mathcal X_n}
Q(X\mid\Omega_t),
$$

and:

$$
\mathcal N_{n,\varepsilon}(\Omega_t)
=
\left\{
X\in\mathcal X_n:
Q_n^*(\Omega_t)-Q(X\mid\Omega_t)
\le
\varepsilon
\right\}.
$$

Its functional diameter at level \(\ell\) is:

$$
D_{n,\ell}(\varepsilon)
=
\operatorname{diam}_{d_{F,\ell}}
\left(
\mathcal N_{n,\varepsilon}(\Omega_t)
\right).
$$

### Generic Functional Concentration

For some non-degenerate task and context classes:

$$
D_{n,\ell}(\varepsilon)
\downarrow
\quad
\text{as}
\quad
\varepsilon\downarrow0.
$$

This is domain-conditional. It is not asserted for every mathematical objective or design space.

## C.7 Strong-Limit Functional Uniqueness

The expression:

$$
|\operatorname{Opt}/\sim_F|\rightarrow1
$$

is incomplete unless a limiting parameter and domain are specified. Cardinality itself is discrete and may be undefined if an optimum is not attained.

A more robust strong-limit conjecture uses near-optimal concentration:

$$
\lim_{\varepsilon\downarrow0}
\operatorname{diam}_{d_F}
\left(
\mathcal N_{\varepsilon}
(\mathcal X_\infty,\Omega_t,Q)
\right)
=0,
$$

where:

- \(\mathcal X_\infty\) is a stated limiting accessible design space;
- \(\Omega_t\) is a specified contextual slice;
- \(Q\) is fixed;
- \(d_F\) is a specified functional pseudometric.

If the maximum is attained, the corresponding exact form is:

$$
\operatorname{diam}_{d_F}
\left(
\operatorname*{arg\,max}_{X\in\mathcal X_\infty}
Q(X\mid\Omega_t)
\right)
=0.
$$

This permits multiple physically distinct implementations but places all optimal realizations in one functional equivalence class.

The conjecture requires explicit assumptions concerning the design space, topology, evaluation, horizon, and metric. It is not a theorem of general optimization.

## C.8 Time and Dynamic Uniqueness

A unique functional class at one contextual slice does not imply one permanent architecture.

Because:

$$
\Omega_{t_1}\neq\Omega_{t_2},
$$

it is possible that:

$$
\operatorname{Opt}(\Omega_{t_1},Q)
\not\sim_F
\operatorname{Opt}(\Omega_{t_2},Q).
$$

The environment, resources, information, task distribution, and accessible technologies may change. An agent's policy also influences future context.

Strong uniqueness therefore concerns at most one specified context and horizon, not a timeless universal machine.

Relativistic event-local notation and distributed causal-policy extensions are treated in [Speculative Limits](#appendix-e). They are not needed for the finite laboratory conjecture defined here.

## C.9 Legitimate Counterexamples

Strong Functional Uniqueness is weakened or falsified within a stated domain by:

- exact symmetries producing different functional classes;
- genuine indifference between distinct consequence distributions;
- plateaus in the objective;
- multiple distinct optimal policies;
- neutral networks of equally performing implementations;
- non-attained suprema;
- incompatible but equally optimal task-specific niches.

These are not automatically defects in the problem description.

It is invalid to manufacture uniqueness by adding an arbitrary tie-breaking preference after observing a tie.

It is also invalid to respond to every counterexample by declaring the context insufficiently complete. Experimental completeness must be defined relative to a preregistered model and evaluation, not to an unreachable metaphysical totality.

## C.10 Falsification

Within finite or exhaustively enumerable spaces, a direct local analogue of Strong Functional Uniqueness can be tested.

A counterexample consists of a stable, prespecified context and objective with:

1. a known or exhaustively verified global optimum;
2. at least two globally optimal systems;
3. nonzero distance under the preregistered functional pseudometric;
4. uncertainty small enough to exclude measurement error as the source of the tie.

Such a result falsifies the strong uniqueness claim for that domain. It does not automatically falsify Functional Narrowing, Origin Attenuation, or architectural convergence in other specified domains.

For empirical designs, see [Experimental Program for the Intelligence Attractor Hypothesis](https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/ideas/experimental-program.md).

# Appendix D - Related Work Map

**Status:** Preliminary AI-assisted source map; author literature review incomplete


---

## Purpose

IAH must be positioned against existing work before any strong originality claim is made.

This document is not yet a literature review. It records the research areas, comparison questions, and conceptual boundaries that require source-based investigation. The source register below records bibliographic and selected-content checks; the remaining thematic questions are not represented as resolved.

## Preliminary Source Register - AI-Assisted Audit, 6 September 2026

This register supplements the research questions below. Sources were discovered and checked with AI assistance; this is not a completed author-conducted or systematic literature review. Each entry records the assistant's actual access level. Personal reading and independent proof verification by the author are not claimed. The comparisons are provisional and references to omitted work are welcome.

The original thematic map is retained after the register. Its open review tasks remain open where the present source checks do not resolve them.

### D-source 1. Cao & Yamins

**Work:** [Explanatory models in neuroscience, Part 2: Functional intelligibility and the contravariance principle](https://arxiv.org/html/2104.01489v2). Cognitive Systems Research 85, 101200; 2024; preprint 2021.

**Relationship to IAH:** Conceptual overlap: stronger task constraints can restrict the possible mechanisms. This is prior art for the broad constraint-driven convergence intuition. A general matched-regret causal origin analysis is not established by the inspected preprint.

**Assistant verification:** Full preprint inspected; final publisher metadata verified. Final published text not fully audited.

**Author reading:** Not certified in this edition.

### D-source 2. Yamins & Nayebi

**Work:** [Contravariance Theory: Strong Alignment for Minimal Solutions to Hard Tasks](https://arxiv.org/html/2607.08561v2). arXiv:2607.08561; 2026, v2.

**Relationship to IAH:** The paper gives exact, asymptotic and quantitative alignment results under minimality and regularity assumptions. It also considers loss tolerance in a fixed macroarchitecture. Its terminal functional alignment requirements are stronger than equal scalar scores. Matched regret alone does not distinguish IAH from this work.

**Assistant verification:** Definitions and relevant theorem statements inspected; proofs not independently verified. Submission metadata and body date differ.

**Author reading:** Not certified in this edition.

### D-source 3. Aran Nayebi

**Work:** [What Capable Agents Must Know: Selection Theorems for Robust Decision-Making under Uncertainty](https://arxiv.org/html/2603.02491v3). arXiv:2603.02491; 2026, v3.

**Relationship to IAH:** Corollary 5 relates vanishing pair-regret, gamma-minimal memory and gamma-complete witnesses to equivalence of memory representations up to invertible recoding on the evaluation support. This directly overlaps with regret-linked internal convergence; it does not establish general monotonic decline of sampled diversity or causal origin effects in heterogeneous software lineages.

**Assistant verification:** Corollary 5, no-aliasing setup and limiting convention inspected; not an independent proof audit.

**Author reading:** Not certified in this edition.

### D-source 4. Soudry, Hoffer, Nacson, Gunasekar & Srebro

**Work:** [The Implicit Bias of Gradient Descent on Separable Data](https://jmlr.org/papers/v19/18-188.html). JMLR 19(70), 1-57; 2018.

**Relationship to IAH:** For separable linear prediction, gradient descent converges in direction to an L2 max-margin solution under the stated loss and step-size conditions, from any initialization. This is a special-case precedent for attenuation of initialization effects, not a universal result over architectures and optimizers.

**Assistant verification:** Primary PDF Theorem 3 and assumptions inspected.

**Author reading:** Not certified in this edition.

### D-source 5. Gunasekar, Lee, Soudry & Srebro

**Work:** [Implicit Bias of Gradient Descent on Linear Convolutional Networks](https://arxiv.org/abs/1806.00468). NeurIPS; 2018.

**Relationship to IAH:** Linear convolutional and fully connected parameterizations can induce different implicit biases under gradient descent. Initialization effects, architecture effects and optimizer effects must therefore be distinguished rather than combined into one assumed-to-vanish origin variable.

**Assistant verification:** Primary abstract and publication PDF consulted; conditional theorem not reproved.

**Author reading:** Not certified in this edition.

### D-source 6. Li, Yosinski, Clune, Lipson & Hopcroft

**Work:** [Convergent Learning: Do Different Neural Networks Learn the Same Representations?](https://proceedings.mlr.press/v44/li15convergent.pdf). PMLR 44; 2015.

**Relationship to IAH:** Independently trained networks can share features and subspaces while retaining differences in features and basis vectors. This is early empirical prior art for partial representational convergence.

**Assistant verification:** Primary abstract and paper search text inspected.

**Author reading:** Not certified in this edition.

### D-source 7. Huh, Cheung, Wang & Isola

**Work:** [Position: The Platonic Representation Hypothesis](https://proceedings.mlr.press/v235/huh24a.html). ICML / PMLR 235, 20617-20642; 2024.

**Relationship to IAH:** This position paper argues for representational convergence, with evidence across model scale and modalities, and hypothesizes a shared statistical model of reality. It is not a theorem of universal architectural uniqueness.

**Assistant verification:** Proceedings abstract inspected; position paper, not universal theorem.

**Author reading:** Not certified in this edition.

### D-source 8. Papyan, Han & Donoho

**Work:** [Prevalence of neural collapse during the terminal phase of deep learning training](https://pmc.ncbi.nlm.nih.gov/articles/PMC7547234/). PNAS 117(40), 24652-24663; 2020.

**Relationship to IAH:** Neural collapse describes a specific geometry of last-layer activations and classifiers in late training. It provides a concrete convergence phenomenon without establishing convergence of all internal levels or substrates.

**Assistant verification:** Primary published abstract and scope inspected.

**Author reading:** Not certified in this edition.

### D-source 9. Huang, Singh, Martinelli & Rajan

**Work:** [Measuring and Controlling Solution Degeneracy across Task-Trained Recurrent Neural Networks](https://arxiv.org/html/2410.03972v3). NeurIPS 2025; preprint 2024, v3 2025.

**Relationship to IAH:** Across 3,400 task-trained RNNs, increasing task complexity can reduce dynamical degeneracy while increasing permutation-aligned weight distance. Functional levels must be separated; weight distance is not automatically architectural functional distance.

**Assistant verification:** Full text inspected for sample, methods and metric-specific results.

**Author reading:** Not certified in this edition.

### D-source 10. Kim & Lee

**Work:** [Same Benchmark, Same Subspace: Task-Selective Convergence in LLM Representations](https://proceedings.mlr.press/v337/kim26g.html). UAI / PMLR 337, 3101-3116; 2026.

**Relationship to IAH:** The proceedings abstract reports task-selective alignment of linear readout geometry across 50 models from six families on three benchmarks. It concerns a selected subspace, not the whole architecture. Full methodological comparison remains pending.

**Assistant verification:** Proceedings abstract verified. Full PDF inaccessible in web tool; no full methodological audit.

**Author reading:** Not certified in this edition.

### D-source 11. Krauss et al.

**Work:** [Convergent Evolution in Algorithmic Space](https://arxiv.org/html/2608.05985v1). arXiv:2608.05985; 6 August 2026.

**Relationship to IAH:** Nine fixed-architecture MLPs, three initializations per task, show task-specific structural convergence under the proposed metrics, while Euclidean distances increase. The terminology of algorithmic attractors is prior art; this small preprint study does not test recursively mutable architectures.

**Assistant verification:** Full text inspected for nine MLPs, three seeds per task and metric dependence; preprint.

**Author reading:** Not certified in this edition.

### D-source 12. D’Amour et al.

**Work:** [Underspecification Presents Challenges for Credibility in Modern Machine Learning](https://jmlr.org/papers/v23/20-1335.html). JMLR 23(226), 1-61; 2022.

**Relationship to IAH:** Predictors with comparable validation performance can behave differently in deployment. Equal high scores alone do not establish functional equivalence outside the evaluated distribution.

**Assistant verification:** Primary article and PDF inspected for equal validation performance versus deployment variability.

**Author reading:** Not certified in this edition.

### D-source 13. Marx, Calmon & Ustun

**Work:** [Predictive Multiplicity in Classification](https://proceedings.mlr.press/v119/marx20a.html). ICML / PMLR 119, 6765-6774; 2020.

**Relationship to IAH:** The study quantifies prediction disagreement among competing classifiers. It motivates actively searching for diverse near-optimal alternatives rather than inferring set-wide uniqueness from an optimization sample. Finite-tolerance multiplicity alone does not settle the zero-regret limit.

**Assistant verification:** Primary article and PDF inspected; finite tolerance, not vanishing-regret limit.

**Author reading:** Not certified in this edition.

## D.1 Constrained and Multi-Objective Optimization

Questions:

- What is known about the geometry and dimensionality of near-optimal solution sets?
- Under what regularity conditions do near-optimal sets concentrate?
- When do symmetries, plateaus, linear objectives, or degeneracy preserve multiple optima?
- How do Pareto fronts change under scalarization or additional constraints?

IAH must not present the existence of constrained optima or Pareto fronts as an original contribution.

**TODO:** Build a verified bibliography on near-optimal sets, sensitivity analysis, parametric optimization, Pareto geometry, and degeneracy.

## D.2 No Free Lunch and Task-Distribution Dependence

Questions:

- Which convergence claims require assumptions about the task distribution?
- How should IAH state its domain so that it does not imply universal performance across arbitrary problems?
- What does No Free Lunch exclude, and what does it leave open under structured real-world distributions?

IAH should explicitly remain conditional on task, context, objective, and design space.

**TODO:** Verify primary No Free Lunch results and later domain-specific interpretations.

## D.3 Convergent Evolution, Degeneracy, and Common Ancestry

Questions:

- How is functional convergence distinguished from shared ancestry?
- When does evolution produce similar functions through different mechanisms?
- How do degeneracy, neutral networks, robustness, and multiple realizability preserve diversity?
- Can biological methods for detecting convergence inform origin controls?

Convergent evolution supports the plausibility of constraint-induced similarity but does not establish IAH's multi-level or recursive claims.

**TODO:** Review primary work on convergent evolution, developmental constraints, degeneracy, neutral networks, and evolutionary contingency.

## D.4 Cybernetics and the Good Regulator Tradition

Questions:

- Which existing theorems connect effective regulation with models of the regulated system?
- Does predictive or causal sufficiency follow from optimal control, or only under particular assumptions?
- How does IAH differ from the claim that a good regulator must embody a model of its environment?

IAH should not infer maximal causal knowledge from optimal behavior without a task-specific necessity argument.

**TODO:** Verify original cybernetics and Good Regulator sources and identify precise points of overlap.

## D.5 Optimal Control, Decision Theory, and Bounded Rationality

Questions:

- How are policies evaluated over stochastic future trajectories?
- How do resource-bounded agents trade decision quality against computation cost?
- When can different policies be exactly optimal?
- How are regret and attainable frontiers defined under partial observability?

These fields provide much of the formal language required by fixed-objective IAH.

**TODO:** Review primary sources on optimal control, POMDPs, bounded rationality, rational metareasoning, and decision-making under uncertainty.

## D.6 Representation and Mechanism Convergence

Questions:

- How is representational similarity measured across independently trained models?
- Which similarities reflect shared data or architecture rather than task constraints?
- What invariances must be factored out?
- Does increased performance correlate with representation, circuit, or algorithm convergence?

Potentially relevant contemporary ideas include representation convergence and the Platonic Representation Hypothesis, but their claims and evidence require careful primary-source verification.

**TODO:** Build a verified map of representational similarity methods, mechanistic convergence studies, and their criticisms.

## D.7 Meta-Learning and Optimizer Optimization

Questions:

- When does an optimizer become an object of optimization?
- How do meta-learning and learned optimizers formalize recursive improvement?
- What are the known limits, instabilities, and path dependencies?
- Can improvements at one level reliably modify the accessible design space at another?

IAH's recursive claim must be distinguished from the existing fact that optimization procedures can themselves be optimized.

**TODO:** Review learned optimizers, meta-learning, AutoML, neural architecture search, program synthesis, and self-modifying systems.

## D.8 Physical Limits of Computation

Questions:

- Which limits on energy, information transfer, memory density, error correction, and latency are established?
- Which are engineering limits and which are fundamental?
- How should IAH discuss physical convergence without assuming that current substrates are final?

Physical limits motivate architectural constraints but do not by themselves prove a unique architecture.

**TODO:** Verify authoritative sources on thermodynamics of computation, reversible computing, communication limits, fault tolerance, and physical information theory.

## D.9 Multiple Realizability and Functional Equivalence

Questions:

- How have philosophy of mind, computer science, and systems theory treated multiple physical realizations of the same function?
- What equivalence notions are appropriate at outcome, behavioral, algorithmic, and architectural levels?
- How can equivalence avoid becoming either physically overstrict or evaluatively circular?

IAH requires level-specific equivalence relations rather than one universal identity criterion.

**TODO:** Review multiple realizability, behavioral equivalence, bisimulation, program equivalence, and causal abstraction.

## D.10 Reflective Stability, Value Learning, and Objective Change

Questions:

- Under what assumptions can an agent evaluate changes to its own objective?
- Which coherence or stability constraints restrict objectives without uniquely selecting one?
- Does objective improvement always require a meta-objective?
- Which apparent value conflicts disappear with better causal knowledge, and which remain genuinely normative?

This is currently the least developed branch of IAH.

**TODO:** Review primary work on reflective stability, preference change, value learning, corrigibility, social choice, and meta-ethics before formulating an objective-level hypothesis.

## D.11 Provisional Originality Boundary

IAH should not claim originality for:

- constraints reducing feasible solution space;
- optimization selecting higher-performing solutions;
- convergent evolution;
- architecture search;
- resource-bounded decision-making;
- the existence of physical computation limits.

The proposed distinctive research contribution may lie in jointly studying:

1. the relationship between regret and functional diversity;
2. attenuation of arbitrary origin dependence;
3. convergence at multiple prespecified functional levels;
4. recurrence across nested intervention spaces;
5. separation of common inheritance from constraint-induced reconstruction;
6. explicit conditions under which narrowing fails;
7. strong functional concentration as a separately falsifiable limiting conjecture.

This originality claim remains provisional until the literature review is complete.

# Appendix E - Speculative Limits

## Relativistic Context, Absolute Architectural Uniqueness, and Objective Boundaries



**Status:** Metaphysical and far-limit conjectures; not part of the present empirical program


---

## E.1 Purpose and Separation from the Empirical Core

This document preserves the strongest possible interpretations of IAH without presenting them as consequences of the empirical hypotheses.

The empirical program tests functional narrowing, origin attenuation, and possible architectural convergence in finite prespecified domains. Nothing in such an experiment can establish:

- complete knowledge of physical reality;
- a unique physical realization of intelligence;
- convergence of terminal objectives;
- a universal cosmic optimizer;
- a theological interpretation of the attractor.

The conjectures below are retained because they motivate the broadest form of the theory, but they must not be used to protect E1, E2, D1, R1, U1, or U2 from counterevidence.

## E.2 Relativistic Context

The notation \(\Omega_t\) is adequate for laboratory experiments with a chosen clock and reference frame. It must not be interpreted as a universal cosmic present.

For a relativistically local formulation, use a decision event \(p\), its causal past \(J^-(p)\), and:

$$
\Omega_p=
\left(
e_{J^-(p)},
\mathcal T,
\mathcal R_p,
\mathcal I_p,
H
\right),
$$

where \(\mathcal I_p\) contains only information causally available at \(p\).

A local strong-concentration conjecture can be expressed as:

$$
\lim_{\varepsilon\downarrow0}
\operatorname{diam}_{d_{F,p}}
\left(
\mathcal N_{\varepsilon}
(\mathcal X_{\mathrm{feas},p},\Omega_p,Q)
\right)
=0.
$$

This does not require instantaneous knowledge of a spacelike-separated universe.

For an intelligent system distributed across a spacetime region \(W\), the candidate object must be a distributed causal policy rather than a state synchronized against one universal time coordinate.

## E.3 U3 — Absolute Architectural Uniqueness

U2 permits different physical realizations when they belong to one functional equivalence class. U3 deliberately goes further.

The maximal conjecture proposes that, for a completely specified causally available context at an event \(p\), a complete objective over relevant reachable consequences, and the full physically feasible design space, there may be exactly one globally optimal substantive realization of intelligence.

Let:

$$
Z=(X,c,\pi)
$$

denote a complete realization containing architecture \(X\), chosen computation and reasoning process \(c\), and action policy \(\pi\).

Let \(\mathcal Z_{\mathrm{feas}}(\Omega_p,\mathcal R_p)\) contain only realizations constructible and operable through resources and causal channels available at \(p\). Let \(J_p(Z)\) evaluate reachable consequences net of information, computation, time, communication, construction, and action costs.

An embedded optimum is not assumed to calculate everything. Deciding what not to calculate is itself part of the optimization.

## E.4 Substantive and Trivial Differences

U3 must not count symbol renaming, address relocation, or an exact interchangeable copy as a distinct substantive architecture.

Let \(\sim_{\mathrm{triv},p}\) identify only prespecified non-substantive transformations. Unlike functional equivalence in U2, it does not collapse genuinely different architectures merely because they produce functionally equivalent behavior.

The local causal conjecture is:

$$
\left|
\operatorname*{arg\,max}_{
[Z]\in
\mathcal Z_{\mathrm{feas}}(\Omega_p,\mathcal R_p)/
\sim_{\mathrm{triv},p}
}
J_p([Z])
\right|
=1.
$$

Equivalently, there is a realization class \([Z_p^*]\) such that:

$$
J_p([Z_p^*])
>
J_p([Z])
\quad
\text{for every }
[Z]\neq[Z_p^*].
$$

A near-frontier analogue is:

$$
\lim_{q\uparrow J_p^*}
K_{\mathrm{realization}}(q,p)
=1,
$$

where \(K_{\mathrm{realization}}(q,p)\) is an effective count of substantively different realization classes above threshold \(q\).

These formulas do not establish U3. They only state what would have to be meant by the conjecture.

## E.5 Distributed Causal Policy

For a system distributed through a spacetime region \(W\), a relativistic version concerns complete causal policies:

$$
\left|
\operatorname*{arg\,max}_{
[\Pi]\in
\operatorname{Causal}(W)/
\sim_{\mathrm{triv}}
}
J(\Pi\mid\Omega_W)
\right|
=1.
$$

Here \(\operatorname{Causal}(W)\) contains only processes whose observation, communication, computation, and interventions respect the causal structure of \(W\).

New controllable physical channels would enlarge the admissible causal-policy space. They would not remove the obligation to specify that space and its communication constraints.

## E.6 Why U3 Is Not Presently Testable

Confirming unrestricted U3 would require:

- the complete causally available state;
- the full physically feasible realization space;
- a complete ordering of reachable consequences;
- complete accounting of construction and operation costs;
- proof of global rather than merely observed optimality;
- a non-arbitrary distinction between trivial and substantive differences.

Current experiments can test finite analogues or observe architectural narrowing. They cannot establish U3.

A finite analogue is refuted by two substantively different exact global optima under the stated objective and equivalence rule. The unrestricted conjecture cannot be rescued by dismissing such a finite result as “not deep enough.”

## E.7 Objective-Level Boundary

Causal knowledge can reveal hidden consequences and dissolve some apparent conflicts. It does not by itself rank genuinely conflicting terminal values.

To compare objectives \(Q_1\) and \(Q_2\), an additional rule is required:

$$
M(Q_1,Q_2\mid\Omega).
$$

The rule \(M\) is a meta-objective, dominance relation, or admissibility principle. Without it, “a better objective” is undefined rather than merely unknown.

Consistency, viability, option value, reflective stability, and resource preservation may constrain objectives, but each introduces assumptions and need not select one unique terminal objective.

IAH therefore makes no scientific claim that facts alone generate a universal value function.

## E.8 Theological Interpretation

A unique limiting intelligence may be interpreted theologically as analogous to a singular omniscient optimizer.

This interpretation can motivate philosophical exploration, but it is not established by the mathematical framework. IAH does not empirically identify God, Laplace's demon, artificial intelligence, and the attractor as the same entity.

The theological interpretation should be discussed separately from any PhD-facing empirical claim.

## E.9 Status of the Far-Limit Conjectures

| Proposition | Status |
| --- | --- |
| Event-local functional concentration | Formal limiting extension of U2 |
| Distributed causal-policy optimization | Conceptual relativistic extension |
| Absolute architectural uniqueness | Metaphysical maximal conjecture |
| Objective convergence | Undefined without additional normative structure |
| Theological identity | Philosophical interpretation, not scientific evidence |

These claims are preserved as boundaries of the theory, not as findings.

# References

1. Cao & Yamins. [Explanatory models in neuroscience, Part 2: Functional intelligibility and the contravariance principle](https://arxiv.org/html/2104.01489v2). Cognitive Systems Research 85, 101200; 2024; preprint 2021. Accessed 6 September 2026.

2. Yamins & Nayebi. [Contravariance Theory: Strong Alignment for Minimal Solutions to Hard Tasks](https://arxiv.org/html/2607.08561v2). arXiv:2607.08561; 2026, v2. Accessed 6 September 2026.

3. Aran Nayebi. [What Capable Agents Must Know: Selection Theorems for Robust Decision-Making under Uncertainty](https://arxiv.org/html/2603.02491v3). arXiv:2603.02491; 2026, v3. Accessed 6 September 2026.

4. Soudry, Hoffer, Nacson, Gunasekar & Srebro. [The Implicit Bias of Gradient Descent on Separable Data](https://jmlr.org/papers/v19/18-188.html). JMLR 19(70), 1-57; 2018. Accessed 6 September 2026.

5. Gunasekar, Lee, Soudry & Srebro. [Implicit Bias of Gradient Descent on Linear Convolutional Networks](https://arxiv.org/abs/1806.00468). NeurIPS; 2018. Accessed 6 September 2026.

6. Li, Yosinski, Clune, Lipson & Hopcroft. [Convergent Learning: Do Different Neural Networks Learn the Same Representations?](https://proceedings.mlr.press/v44/li15convergent.pdf). PMLR 44; 2015. Accessed 6 September 2026.

7. Huh, Cheung, Wang & Isola. [Position: The Platonic Representation Hypothesis](https://proceedings.mlr.press/v235/huh24a.html). ICML / PMLR 235, 20617-20642; 2024. Accessed 6 September 2026.

8. Papyan, Han & Donoho. [Prevalence of neural collapse during the terminal phase of deep learning training](https://pmc.ncbi.nlm.nih.gov/articles/PMC7547234/). PNAS 117(40), 24652-24663; 2020. Accessed 6 September 2026.

9. Huang, Singh, Martinelli & Rajan. [Measuring and Controlling Solution Degeneracy across Task-Trained Recurrent Neural Networks](https://arxiv.org/html/2410.03972v3). NeurIPS 2025; preprint 2024, v3 2025. Accessed 6 September 2026.

10. Kim & Lee. [Same Benchmark, Same Subspace: Task-Selective Convergence in LLM Representations](https://proceedings.mlr.press/v337/kim26g.html). UAI / PMLR 337, 3101-3116; 2026. Accessed 6 September 2026.

11. Krauss et al.. [Convergent Evolution in Algorithmic Space](https://arxiv.org/html/2608.05985v1). arXiv:2608.05985; 6 August 2026. Accessed 6 September 2026.

12. D’Amour et al.. [Underspecification Presents Challenges for Credibility in Modern Machine Learning](https://jmlr.org/papers/v23/20-1335.html). JMLR 23(226), 1-61; 2022. Accessed 6 September 2026.

13. Marx, Calmon & Ustun. [Predictive Multiplicity in Classification](https://proceedings.mlr.press/v119/marx20a.html). ICML / PMLR 119, 6765-6774; 2020. Accessed 6 September 2026.
