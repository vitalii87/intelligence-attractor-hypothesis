# Recursive Architectural Attractor

## Nested Design Spaces and Open-Ended Optimization Depth

**Author:** Vitalii Zhyliaiev

**Initial formulation:** 2026

**Revision:** v0.5 — 2026-08

**Status:** Theoretical and experimentally extensible component of IAH

[← Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md)

---

## 1. Architecture Becomes Part of the Solution

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

## 2. The Recursive Optimization Principle

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

## 3. Nested Intervention Spaces

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

## 4. Two Forms of Progress

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

## 5. Independent Falsifiability at Every Level

Each design-space claim must be specified and evaluated independently.

If functional narrowing is predicted in \(\mathcal X_n\) but does not occur, it is invalid to reply:

> The true attractor exists only in \(\mathcal X_{n+1}\).

Expansion to \(\mathcal X_{n+1}\) creates a new hypothesis with a new domain. It does not revise the result in \(\mathcal X_n\).

This rule prevents open-ended optimization depth from becoming a moving-goalpost defense.

## 6. Architectural Convergence

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

## 7. Self-Modification

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

## 8. Time and Accessible Depth

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

## 9. Deeper Causal Accessibility

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

## 10. Recursive Convergence Claim

### R1 — Cross-Space Recurrence

> Functional narrowing may recur separately across increasingly expressive, preregistered design spaces when newly accessible variables materially affect the objective.

R1 is stronger than ordinary outcome convergence because it proposes recurrence of a relationship between regret and functional diversity at multiple implementation levels.

R1 does not predict:

- that every expansion narrows the solution space;
- that all architectures become identical;
- that present physics reveals the final substrate;
- that convergence in one space implies convergence in the next.

## 11. Evidence and Falsifiers

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

## 12. Far-Limit Interpretation

A far-limit interpretation asks whether optimization could eventually include nearly every physically accessible degree of freedom relevant to an objective.

If such a limiting accessible space can be defined, a strong conjecture is that historically arbitrary functional variation may become small relative to variation dictated by the objective, environment, computation, resources, and physical constraints.

This is not required for the empirical core of IAH. It does not imply complete knowledge, universal values, literal physical identity, or physical attainability of an ultimate optimum.

For operational tests of nested design spaces, see [Experimental Program for the Intelligence Attractor Hypothesis](experimental-program.md).
