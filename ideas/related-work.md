# Related Work Map for the Intelligence Attractor Hypothesis

**Author:** Vitalii Zhyliaiev

**Revision:** Publication preparation, 2026-09-06

**Status:** Preliminary AI-assisted source map; author literature review incomplete

[← Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md)

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
