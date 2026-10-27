# PRISM implementation sequence

1. **Contract scaffold (present):** records, statuses, compatibility helper,
   adapter/metric protocols, JSON serialization and requirements.
2. **Evidence ingestion (partial in 0.2.0):** Arena ArtifactStore adapter, dataset
   manifest, digest verification and parsing limits are present. Full run import
   and case/replicate alignment remain unfinished.
3. **First measurements:** behavioral disagreement, quality/resource summaries,
   explicit file-change measurements; tests for missing and incompatible data.
4. **Offline comparison report:** pairwise and within-agent comparisons, coverage,
   trajectories and failure counts. Add a CLI before a GUI.
5. **Structural extensions:** language-specific dependency extraction and execution
   traces, declared invariances, separately labeled model-assisted interpretation.
6. **Experiment analysis:** origin interventions, repeated-run uncertainty,
   performance/budget matching, alternative metrics and degeneracy controls.
7. **Recursive-system evaluation:** analyze matched trials of old/new improvement
   mechanisms. Execution remains in Arena or an external runner.

Version 0.2.0 adds artifact import, not completion of stages 2–7. Prioritize evidence
integrity and transparent measurements before an architectural similarity score.
