# Related Work Map for the Intelligence Attractor Hypothesis

**Author:** Vitalii Zhyliaiev

**Revision:** 2026-08

**Status:** Research map; verified bibliography still required

[← Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md)

---

## Purpose

IAH must be positioned against existing work before any strong originality claim is made.

This document is not yet a literature review. It records the research areas, comparison questions, and conceptual boundaries that require source-based investigation. Bibliographic details should be added only after verification from primary or authoritative sources.

## 1. Constrained and Multi-Objective Optimization

Questions:

- What is known about the geometry and dimensionality of near-optimal solution sets?
- Under what regularity conditions do near-optimal sets concentrate?
- When do symmetries, plateaus, linear objectives, or degeneracy preserve multiple optima?
- How do Pareto fronts change under scalarization or additional constraints?

IAH must not present the existence of constrained optima or Pareto fronts as an original contribution.

**TODO:** Build a verified bibliography on near-optimal sets, sensitivity analysis, parametric optimization, Pareto geometry, and degeneracy.

## 2. No Free Lunch and Task-Distribution Dependence

Questions:

- Which convergence claims require assumptions about the task distribution?
- How should IAH state its domain so that it does not imply universal performance across arbitrary problems?
- What does No Free Lunch exclude, and what does it leave open under structured real-world distributions?

IAH should explicitly remain conditional on task, context, objective, and design space.

**TODO:** Verify primary No Free Lunch results and later domain-specific interpretations.

## 3. Convergent Evolution, Degeneracy, and Common Ancestry

Questions:

- How is functional convergence distinguished from shared ancestry?
- When does evolution produce similar functions through different mechanisms?
- How do degeneracy, neutral networks, robustness, and multiple realizability preserve diversity?
- Can biological methods for detecting convergence inform origin controls?

Convergent evolution supports the plausibility of constraint-induced similarity but does not establish IAH's multi-level or recursive claims.

**TODO:** Review primary work on convergent evolution, developmental constraints, degeneracy, neutral networks, and evolutionary contingency.

## 4. Cybernetics and the Good Regulator Tradition

Questions:

- Which existing theorems connect effective regulation with models of the regulated system?
- Does predictive or causal sufficiency follow from optimal control, or only under particular assumptions?
- How does IAH differ from the claim that a good regulator must embody a model of its environment?

IAH should not infer maximal causal knowledge from optimal behavior without a task-specific necessity argument.

**TODO:** Verify original cybernetics and Good Regulator sources and identify precise points of overlap.

## 5. Optimal Control, Decision Theory, and Bounded Rationality

Questions:

- How are policies evaluated over stochastic future trajectories?
- How do resource-bounded agents trade decision quality against computation cost?
- When can different policies be exactly optimal?
- How are regret and attainable frontiers defined under partial observability?

These fields provide much of the formal language required by fixed-objective IAH.

**TODO:** Review primary sources on optimal control, POMDPs, bounded rationality, rational metareasoning, and decision-making under uncertainty.

## 6. Representation and Mechanism Convergence

Questions:

- How is representational similarity measured across independently trained models?
- Which similarities reflect shared data or architecture rather than task constraints?
- What invariances must be factored out?
- Does increased performance correlate with representation, circuit, or algorithm convergence?

Potentially relevant contemporary ideas include representation convergence and the Platonic Representation Hypothesis, but their claims and evidence require careful primary-source verification.

**TODO:** Build a verified map of representational similarity methods, mechanistic convergence studies, and their criticisms.

## 7. Meta-Learning and Optimizer Optimization

Questions:

- When does an optimizer become an object of optimization?
- How do meta-learning and learned optimizers formalize recursive improvement?
- What are the known limits, instabilities, and path dependencies?
- Can improvements at one level reliably modify the accessible design space at another?

IAH's recursive claim must be distinguished from the existing fact that optimization procedures can themselves be optimized.

**TODO:** Review learned optimizers, meta-learning, AutoML, neural architecture search, program synthesis, and self-modifying systems.

## 8. Physical Limits of Computation

Questions:

- Which limits on energy, information transfer, memory density, error correction, and latency are established?
- Which are engineering limits and which are fundamental?
- How should IAH discuss physical convergence without assuming that current substrates are final?

Physical limits motivate architectural constraints but do not by themselves prove a unique architecture.

**TODO:** Verify authoritative sources on thermodynamics of computation, reversible computing, communication limits, fault tolerance, and physical information theory.

## 9. Multiple Realizability and Functional Equivalence

Questions:

- How have philosophy of mind, computer science, and systems theory treated multiple physical realizations of the same function?
- What equivalence notions are appropriate at outcome, behavioral, algorithmic, and architectural levels?
- How can equivalence avoid becoming either physically overstrict or evaluatively circular?

IAH requires level-specific equivalence relations rather than one universal identity criterion.

**TODO:** Review multiple realizability, behavioral equivalence, bisimulation, program equivalence, and causal abstraction.

## 10. Reflective Stability, Value Learning, and Objective Change

Questions:

- Under what assumptions can an agent evaluate changes to its own objective?
- Which coherence or stability constraints restrict objectives without uniquely selecting one?
- Does objective improvement always require a meta-objective?
- Which apparent value conflicts disappear with better causal knowledge, and which remain genuinely normative?

This is currently the least developed branch of IAH.

**TODO:** Review primary work on reflective stability, preference change, value learning, corrigibility, social choice, and meta-ethics before formulating an objective-level hypothesis.

## 11. Provisional Originality Boundary

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
