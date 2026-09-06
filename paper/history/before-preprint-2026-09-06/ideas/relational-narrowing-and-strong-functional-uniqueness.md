# Relational Narrowing and Strong Functional Uniqueness

**Author:** Vitalii Zhyliaiev

**Initial formulation:** 2026

**Revision:** v0.5 — 2026-08

**Status:** Formal and conceptual extension of IAH

[← Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md)

---

## 1. Purpose

This document develops two distinct propositions:

1. **Relational Narrowing:** adding prespecified causally relevant context may distinguish alternatives that appear tied under a lower-resolution description.
2. **Strong Functional Uniqueness:** under stated limiting conditions, all globally optimal realizations may belong to one functional equivalence class.

The first proposition motivates but does not prove the second.

## 2. Relational Optimality

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

## 3. The Relational Narrowing Principle

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

## 4. Functional Equivalence

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

## 5. Pareto Fronts

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

## 6. Near-Optimal Concentration

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

## 7. Strong-Limit Functional Uniqueness

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

## 8. Time and Dynamic Uniqueness

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

Relativistic event-local notation and distributed causal-policy extensions are treated in [Speculative Limits](speculative-limits.md). They are not needed for the finite laboratory conjecture defined here.

## 9. Legitimate Counterexamples

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

## 10. Falsification

Within finite or exhaustively enumerable spaces, a direct local analogue of Strong Functional Uniqueness can be tested.

A counterexample consists of a stable, prespecified context and objective with:

1. a known or exhaustively verified global optimum;
2. at least two globally optimal systems;
3. nonzero distance under the preregistered functional pseudometric;
4. uncertainty small enough to exclude measurement error as the source of the tie.

Such a result falsifies the strong uniqueness claim for that domain. It does not automatically falsify Functional Narrowing, Origin Attenuation, or architectural convergence in other specified domains.

For empirical designs, see [Experimental Program for the Intelligence Attractor Hypothesis](experimental-program.md).
