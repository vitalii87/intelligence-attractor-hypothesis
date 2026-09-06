# Intelligence Attractor Hypothesis — Research Program Overview

**Author:** Vitalii Zhyliaiev

**Role:** Status and research-planning companion to the [canonical IAH statement](ideas/intelligence-attractor-hypothesis.md)

**Status:** Developing research program; no empirical result claimed

## One-Sentence Thesis

Under a fixed task, objective, context, and admissible design space, IAH proposes that independent optimization toward a shared performance frontier progressively replaces origin-contingent functional variation with structure determined by the task and its binding constraints.

## Primary Research Question

> Under what task, objective, constraint, and design-space conditions does functional diversity among independently optimized systems decrease as normalized regret approaches zero relative to the performance frontier?

A second, independently testable question is:

> Does initialization and optimization history explain a decreasing share of functionally relevant variation near that frontier?

These are the empirical claims the current project is designed to defend or reject.

## Why This Is Not a Trivial Optimization Claim

Ordinary optimization implies that low-performing candidates are rejected. It does not by itself imply:

- that independently discovered near-optimal systems become functionally similar;
- that dependence on initial architecture or training history decreases;
- that convergence penetrates from behavior into strategy, algorithms, or architecture;
- that the same relationship recurs when deeper system variables become mutable.

IAH therefore studies the geometry and provenance of the near-optimal set, not merely whether optimization improves performance.

## Canonical Forms

The [flagship theory](ideas/intelligence-attractor-hypothesis.md) distinguishes:

- **Weak IAH:** functional diversity and Origin Sensitivity tend to decrease among independent systems compared at matched lower regret, while several persistent solution families may remain.
- **Strong IAH:** at a specified functional level, diversity tends to zero as regret approaches zero, leaving one limiting functional equivalence class.

Functional Narrowing and Origin Attenuation remain separately measurable. Architecture is a central level of application whenever it is mutable, performance-relevant, and evaluated through prespecified functional observables.

## Current Experiment

[EXP-001 — Independent Self-Improving Lineages](experiments/001-independent-self-improving-lineages/README.md) proposes a controlled test in which different software lineages optimize the same synthetic task under shared evaluation and resource constraints.

The experiment is designed to measure:

- performance and regret;
- behavioral and strategic distance;
- algorithmic and architectural features;
- resource profiles;
- variance attributable to origin;
- persistent degeneracy and multiple near-optimal families.

The task and evaluator are not yet frozen. EXP-001 remains a design draft rather than a completed or preregistered experiment.

## Experimental Infrastructure

[IAH Arena](arena/README.md) is the provider-neutral laboratory being built to run isolated lineages, enforce budgets, preserve provenance, and prevent candidate systems from accessing the evaluator or one another.

The orchestration, transactional workspace, container boundary, frozen run lifecycle, telemetry export, and sequential lineage coordination are implemented. A task-specific evaluator and real model providers are not yet connected.

## Claim Boundary

The project currently distinguishes:

| Claim | Status |
| --- | --- |
| Weak IAH: functional narrowing and origin attenuation | Empirical hypothesis |
| Strong IAH: one limiting functional equivalence class | Strong limiting conjecture |
| Convergence in mutable internal or architectural properties | Application of Weak or Strong IAH at an internal level |
| Recurrence across richer intervention spaces | Recursive supplement |
| Exactly one substantive physical realization | Metaphysical conjecture; outside the present empirical program |
| Convergence of terminal objectives | Undefined without a meta-objective or normative criterion |

Failure of a stronger claim does not automatically falsify a weaker claim. Conversely, inaccessible stronger levels cannot be invoked to dismiss a negative result in a preregistered finite domain.

## What the Project Does Not Currently Claim

The repository does not claim that:

- all optimization problems have unique solutions;
- all intelligent systems converge;
- high-performing systems become textually or physically identical;
- constraints always reduce diversity;
- complete causal knowledge determines values;
- the theory has been experimentally validated;
- the work has been peer reviewed or academically accepted.

## Immediate Research Milestones

1. Complete a verified related-work review and establish the novelty boundary.
2. Select a bounded synthetic task with a known or estimable frontier.
3. Freeze functional metrics, origin interventions, constraint regimes, and statistical hypotheses.
4. Implement and preregister EXP-001.
5. Connect independent optimizer families to the arena.
6. Run a pilot before any broader architectural or physical-limit claims are evaluated.

## Recommended Reading

1. [Canonical IAH theory](ideas/intelligence-attractor-hypothesis.md).
2. This research-program overview.
3. [Experimental methodology](ideas/experimental-program.md).
4. [EXP-001 protocol](experiments/001-independent-self-improving-lineages/README.md).
5. [IAH Arena](arena/README.md).

The complete theory map, including strong extensions and speculative limits, is available in [the ideas index](ideas/README.md).
