# Appendix C - Relational Narrowing and Strong Functional Uniqueness

## C.1. Optimality as a Relation

Optimality is defined relative to a context and an objective.

Two systems may achieve the same result under coarse measurement yet have different consequences when latency, energy, memory, reliability, or learning cost is measured more precisely.

Relational Narrowing proposes that incorporating prespecified causally relevant context may distinguish alternatives that previously appeared equivalent.

If a refinement changes what is valued, rather than merely measuring the original criterion more accurately, it defines a new objective and domain.

## C.2. Equivalence

Functional equivalence is defined through properties \(\Psi_\ell\), rather than the final score alone.

For a deterministic description:

$$
A\sim_\ell B\iff\Psi_\ell(A,\Omega)=\Psi_\ell(B,\Omega).
$$

For a stochastic description, the corresponding distributions are compared.

Permitted invariances and thresholds for approximate equivalence are specified in advance.

## C.3. Geometry of Near-Optimal Solutions

For the set:

$$
\mathcal N_\varepsilon=\{X:r(X)\le\varepsilon\},
$$

define its functional diameter:

$$
\Delta_\ell(\varepsilon)=\operatorname{diam}_{d_\ell}(\mathcal N_\varepsilon).
$$

The notation \(\Delta_\ell\) distinguishes this quantity from the sampled mean distance \(D_\ell(r)\).

Because the sets are nested, their diameter cannot increase as \(\varepsilon\) decreases. The substantive limiting claim is:

$$
\Delta_\ell(\varepsilon)\rightarrow0.
$$

To assert one common limiting class as well, the space in which that class exists must be specified. The main text explicitly includes its existence in Strong IAH.

If the maximum is attained, the strong claim implies that all optimal systems belong to one functional class.

The existence of a unique optimal class alone does not guarantee convergence of all near-optimal systems: that is an additional property of the frontier's neighborhood.

## C.4. Multiplicity of Solutions

Different functional classes may remain equally optimal because of symmetries, plateaus, specialization, indifference under the objective, or unresolved trade-offs between criteria.

Specifying a single scalar criterion does not by itself guarantee uniqueness.

A non-attained supremum must be treated separately: it violates an assumption that a maximizer exists, but is compatible with concentration of near-optimal systems.

## C.5. Counterexample

In a finite or exhaustively explored space, two globally optimal systems with nonzero functional distance refute the claim of a unique optimal functional class in that domain.

Such a result cannot be removed by adding an arbitrary preference after discovering the tie.
