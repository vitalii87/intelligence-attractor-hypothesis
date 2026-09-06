# The Intelligence Attractor Hypothesis

## Independent Convergence Under Shared Reality Constraints

**Author:** Vitalii Zhyliaiev

**Initial formulation:** 2026

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

- [Experimental Program](experimental-program.md) — general operational methodology.
- [Origin Dependence and Attenuation](origin-dependence-and-attenuation.md) — origin variables, interventions, and confounds.
- [EXP-001: Independent Self-Improving Lineages](../experiments/001-independent-self-improving-lineages/README.md) — first concrete protocol.
- [IAH Arena](../arena/README.md) — experimental infrastructure.
- [Recursive Architectural Attractor](recursive-architectural-attractor.md) — nested intervention spaces and self-modification.
- [Relational Narrowing and Strong Functional Uniqueness](relational-narrowing-and-strong-functional-uniqueness.md) — uniqueness arguments and counterexamples.
- [Related Work Map](related-work.md) — literature-positioning plan.
- [Speculative Limits](speculative-limits.md) — physical, relativistic, objective-level, and theological limits.
