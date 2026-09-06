# The Intelligence Attractor Hypothesis

## Abstract

The Intelligence Attractor Hypothesis (IAH) proposes that independently formed intelligent systems, as they approach the best attainable performance under the same task, objective, context, and resource constraints, progressively lose functionally consequential differences attributable to their origins.

The proposed mechanism is the elimination of forms of organization that become too costly near the optimum. Early in optimization, many strategies, algorithms, and architectures may remain competitive. Further optimization increases the influence of shared constraints and may direct independent systems toward increasingly similar solutions.

**Weak IAH** predicts decreasing functional diversity and origin sensitivity while allowing several persistent solution families.

**Strong IAH** conjectures that, within a specified domain and at a defined descriptive level, all systems sufficiently close to the frontier approach one common limiting class of functional equivalence.

Architecture is central to the hypothesis. If the organization of memory, computation, communication, and control can be modified and affects performance, optimization may extend to the mechanism that discovers and implements solutions.

The author's maximal conjecture goes further: under fully specified conditions, there may be a unique substantively optimal realization of an intelligent system. A separate extension considers optimization of system boundaries, including cooperation, specialization, and agent integration.

This work formulates these claims, distinguishes their levels, and proposes a program of investigation. This edition reports no empirical results and has not undergone formal peer review.

## 1. Origin of the Idea and Proposed Contribution

The author's initial intuition was that, for a specific task, objective, and world context, extreme optimization might leave only one best solution and one substantive organization of an agent capable of implementing it. Independent agents approaching that boundary would consequently become increasingly alike.

Subsequent development separated this intuition into investigable claims about functional convergence, a strong limiting hypothesis, and a maximal conjecture of architectural uniqueness.

**The proposed contribution of IAH is the joint treatment of:**

- convergence among independently optimized systems;
- attenuation of dependence on historical origin;
- differences between behavioral, representational, algorithmic, and architectural levels;
- optimization of the optimization mechanism itself;
- the geometry of near-optimal solution sets;
- conditions for persistent diversity and possible uniqueness.

IAH is proposed as a unified conceptual hypothesis that can organize research on these phenomena around a shared principle. The novelty of this combination, and whether existing theoretical results can be recovered as its special cases, remain subjects for comparison.

The author developed the initial intuition before becoming acquainted with adjacent literature. AI assistants contributed to formalization, criticism, editing, research-program design, and source discovery. Their involvement was substantive.

The literature map is preliminary. The author does not claim to have personally read every source or independently verified every proof it contains.

References to overlooked work, precise overlaps, counterexamples, and corrections are welcome. Subsequent substantive changes will be released with a version identifier and an explanation of their reasons.

## 2. Foundational Claim

> Under a fixed task, objective, context, and admissible design space, independent optimization near a shared frontier progressively replaces origin-contingent functional variation with structure determined by the task and its binding constraints.

The motivating intuition is:

> There may be far more ways to remain inefficient than ways to remain competitive near the best attainable performance.

The central case is **independent reconstruction of similar solutions**. Systems may converge without copying one another: different developmental histories encounter the same bottlenecks and similar ways of removing them.

In this work, **attractor** denotes a hypothesized convergence or concentration structure in solution space. The term alone does not specify a classical dynamical-systems attractor. A particular model that adopts that interpretation must separately define its dynamics and the relevant properties.

## 3. Domain, Performance, and Frontier

Every IAH claim concerns a specified domain. Define the context as:

$$
\Omega=(e,\mathcal T,\mathcal R,\mathcal I,H),
$$

where:

- \(e\) is the relevant environment state;
- \(\mathcal T\) is its dynamics;
- \(\mathcal R\) specifies resources and physical constraints;
- \(\mathcal I\) specifies available information and interaction interfaces;
- \(H\) is the evaluation horizon.

The objective \(Q\) and admissible design space \(\mathcal X\) are specified separately. System performance is evaluated as:

$$
Q(X\mid\Omega).
$$

For fixed \(\mathcal X,Q,\Omega\), the frontier is:

$$
Q^*=\sup_{X\in\mathcal X}Q(X\mid\Omega).
$$

Regret is the shortfall from that frontier:

$$
r(X)=Q^*-Q(X\mid\Omega).
$$

The frontier may be an attained maximum or a limit that systems can only approach. The following claims concern domains in which this difference is well-defined.

If the true frontier is unknown, an experiment must report its estimate or bounds. The best result found must not automatically be identified with the global optimum.

For dynamic tasks, a candidate may be a policy over a specified horizon. A concrete moment does not require physical time to stop: it defines an initial context relative to which possible subsequent consequences are evaluated.

## 4. Levels of Convergence

IAH distinguishes several descriptive levels:

| Level | Example properties |
| --- | --- |
| Outcome | Accuracy, error, reliability |
| Behavior | Responses to situations and interventions, failure patterns |
| Strategy | Planning, decomposition, allocation of effort |
| Representation | Organization of internal information |
| Algorithm | Search methods, computational procedures, complexity |
| Architecture | Memory, modules, dataflow, topology, control |
| Resources | Time, energy, memory, communication, learning cost |

At level \(\ell\), define a functional distance:

$$
d_\ell(X_i,X_j).
$$

The metric or pseudometric must use properties and invariances chosen before inspecting results.

Equal final scores do not imply equal behavior, algorithms, or architecture. Conversely, different variable names or interchangeable encodings need not indicate substantive differences.

Convergence strength may depend on level: behavioral diversity may decline while differences in other properties persist or increase.

## 5. Weak IAH

Let:

$$
D_\ell(r)=\mathbb E\!\left[d_\ell(X_i,X_j)\mid i\ne j,\;r(X_i)\approx r(X_j)\approx r\right]
$$

describe the mean distance between independently obtained systems at similar regret.

The expectation is taken under a prespecified sampling protocol over independent optimization runs; the regret-bin widths, checkpoint selection, and weighting of origins and optimization procedures must be reported.

Let \(OS_\ell(r)\) be a prespecified measure of the sensitivity of functional properties to controlled origin differences.

Weak IAH predicts:

$$
r\downarrow\quad\Longrightarrow\quad D_\ell(r)\downarrow\quad\text{and}\quad OS_\ell(r)\downarrow.
$$

These are two separate predictions:

1. **Functional Narrowing:** independent systems become less diverse in the specified functional properties.
2. **Origin Attenuation:** changing their origins has progressively less influence on those properties.

The arrows denote statistical tendencies within a prespecified near-frontier regime. They do not require improvement at every optimization step.

Weak IAH allows several persistent solution families, residual path dependence, specialization, and different patterns across descriptive levels.

Support for either prediction must be reported separately from the result for the other.

## 6. Strong IAH

> Within a specified domain and at a defined functional level, all systems sufficiently close to the frontier approach one common limiting class of functional equivalence.

Define the near-optimal set:

$$
\mathcal N_\varepsilon=\{X\in\mathcal X:r(X)\le\varepsilon\}.
$$

Let \([X]_\ell\) be the functional class of a system, and let \(\mathcal F_\ell\) be a specified space of such classes with distance \(\bar d_\ell\). The space must explicitly state which limiting objects it admits.

For these statements, the system-level pseudometric is induced by the metric on functional classes: \(d_\ell(X,Y)=\bar d_\ell([X]_\ell,[Y]_\ell)\). The same functional properties and invariances are used throughout.

The strong claim is the existence of a common class \(z_\ell^*\) such that:

$$
\boxed{\exists z_\ell^*\in\mathcal F_\ell:\quad\lim_{\varepsilon\downarrow0}\sup_{X\in\mathcal N_\varepsilon}\bar d_\ell([X]_\ell,z_\ell^*)=0.}
$$

Thus, whichever admissible near-optimal systems are considered, their functional classes approach the same limit.

This implies vanishing pairwise distance:

$$
D_\ell(r)\rightarrow0
$$

for samples drawn from regions increasingly close to the frontier.

Declining mean distance alone does not establish the converse. A sample may miss other solution families. Moreover, systems may be close to one another at each regret level without having a common stable limit across levels.

The strong formula therefore concerns the entire stated space of near-optimal systems. Experimental samples provide bounded evidence about it.

At the architectural level, Strong IAH predicts convergence in the functionally consequential organization of memory, computation, communication, and control when these properties are among the admissible changes.

The maximal conjecture of a unique substantive realization, presented in Appendix E, preserves the author's still stronger intuition.

## 7. Proposed Mechanism

IAH proposes the following sequence:

1. Different developmental histories produce different initial systems.
2. Optimization eliminates errors and costs.
3. Near the frontier, shared bottlenecks restrict competitive forms of organization.
4. Independent lineages increasingly reconstruct the same functional principles.

For example, independent software systems may develop similar data locality, queue organization, memory allocation, or load control because they face the same communication and latency costs.

This mechanism is an explanatory hypothesis. Constraints may also create new niches and forms of specialization. The research question is when the elimination of costly diversity dominates the emergence of competitive alternatives.

## 8. Architecture and Recursive Optimization

Optimization may act on both an agent's response and the mechanism producing it:

$$
\begin{gathered}
\text{action}\rightarrow\text{policy}\rightarrow\text{representation}\\
\rightarrow\text{algorithm}\rightarrow\text{architecture}\rightarrow\text{optimization mechanism}.
\end{gathered}
$$

If an internal property can be modified and materially affects \(Q\), it may become part of the optimization problem.

Under these conditions, IAH extends the convergence question to the optimizer's own architecture.

Learning, redesign, evaluation, switching, and failed-modification costs must be included when relevant to the objective. Self-modification can improve a system, but it can also introduce regressions and path dependence.

Appendix B develops this extension.

## 9. System Boundaries and Collective Organization

An individual agent's boundary may itself be mutable.

If systems can change the division of functions, share memory, delegate computation, or form joint control loops, the admissible space includes different forms of collective organization.

This introduces an additional question:

> Does approaching the frontier determine not only agents' internal organization, but also how advantageous it is for them to remain separate systems?

Optimization may favor integration when the benefits of joint organization exceed coordination costs. Under other conditions, autonomy, specialization, or cooperation without merger may remain competitive.

**Convergence among independent agents and their integration are different phenomena.** Components of an optimal collective may perform different roles and remain dissimilar. In that case, IAH should be tested by comparing independently formed collectives at the level of their overall organization.

This extension brings mutable system boundaries into the research program.

## 10. Program of Investigation

Initial studies should specify:

1. the task, objective, context, and resources;
2. the admissible design space;
3. origin variables and how they are controlled;
4. functional levels and metrics;
5. how the frontier is estimated;
6. independent optimization lineages;
7. diversity and origin-sensitivity measures;
8. criteria for supporting, weakening, or falsifying claims.

Shared data, libraries, templates, and model ancestry must be considered as possible causes of similarity.

Comparison at achieved regret requires care: origin affects both functional properties and the probability of reaching a given performance level. Selecting only successful systems can manufacture apparent convergence.

Analysis must therefore include complete trajectories, failed lineages, and attrition. Causal conclusions must rest on an explicit design and assumptions.

For the collective extension, the unit of comparison and total resource budget, including coordination costs, must be defined in advance.

## 11. Falsification and Limits of Inference

Weak IAH is weakened in a stated domain if:

- functional diversity remains stable or increases in the predicted near-frontier regime;
- the prespecified origin-effect measure does not show the predicted decline;
- observed similarity is explained by common inheritance;
- convergence is absent at the level for which it was predicted.

Strong IAH is falsified in a specified domain by optimal or arbitrarily near-optimal families that remain functionally separated. The absence of a common stable limit also contradicts its formulation.

Non-attainment of the maximum does not by itself refute convergence near the supremum. It means that the existence of an actual optimal agent requires separate treatment.

A negative result retains its force for the tested domain. Changing the objective, design space, or available physical mechanisms creates a new problem specification.

## 12. Context and Time

An optimal system is defined relative to an objective and conditions.

A change of context may change the optimum; in a dynamic environment, the optimal object may be an adaptive policy.

Whether one system could be optimal across all possible contexts or at all times remains open here. The stated claims are evaluated relative to a specified domain.

Reality determines available consequences and costs. The objective determines how they are ranked. Convergence of objectives themselves is considered separately in Appendix E.
