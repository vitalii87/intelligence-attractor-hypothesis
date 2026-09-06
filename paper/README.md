# Publication edition 0.1

**The Intelligence Attractor Hypothesis: Independent Convergence Under Shared Reality Constraints**

**Vitalii Zhyliaiev**

Prepared 6 September 2026. Conceptual preprint; no empirical validation or peer review claimed.

## Read the complete edition

- [Complete PDF, including all five appendices](Intelligence-Attractor-Hypothesis-v0.1.pdf)
- [Assembled manuscript source](manuscript.md)
- [Origin of the hypothesis and AI assistance](../PROVENANCE.md)
- [Publication front matter](front-matter.md)
- [Bibliography](references.md) and [BibTeX records](references.bib)
- [Publication license: CC BY-NC 4.0](LICENSE.md)
- [Zenodo metadata and final deposit decisions](zenodo-metadata.md)

The PDF contains the author-approved English edition, including all five appendices and the maximal U3 conjecture. The final pass adds the metric connection, sampling-protocol clarification and bounded comparison with Nayebi Corollary 5. Transient Coupling is outside v0.1.

## Structure

1. Main text, including origin of the hypothesis and AI assistance.
2. Appendix A: Origin Dependence and Attenuation.
3. Appendix B: Recursive Architectural Attractor.
4. Appendix C: Relational Narrowing and Strong Functional Uniqueness.
5. Appendix D: Preliminary Related Work Map.
6. Appendix E: Maximal and Philosophical Extensions.
7. Authorship, Discussion, and Versioning.
8. Source Register - Recorded Audit Scope.
9. References.

The main text and appendices are assembled from the corresponding repository Markdown files, followed by [authorship and versioning](authorship.md). The [source register](source-register.json) generates the bibliography and its numbering. The manuscript and PDF are generated artifacts; edit the canonical inputs and rebuild. Display equations may wrap for print.

## History and rollback

The baseline commit is `a3410ecf11024b6d204e4a3e0710744136428888`, locally tagged `iah-before-preprint-2026-09-06`. Exact original documents and checksums are stored in [history/before-preprint-2026-09-06](history/before-preprint-2026-09-06/manifest.json). See [CHANGELOG](../CHANGELOG.md).

The preceding canonical publication is preserved in commit `0a084ac`. Its PDF, assembled source, renderer, front matter and build manifest are also saved with checksums in [the pre-finalization archive](history/before-finalization-2026-09-06/manifest.json).

The working branch is `codex/iah-first-preprint`. Publication work is local. Existing unrelated Arena and EXP-001 edits were not included or overwritten. To undo a particular edit, compare with the saved original and restore only the relevant file; avoid a blanket reset that would discard unrelated work.

## Rebuild

Python dependencies: reportlab, Pillow, pypdf. Node dependencies: mathjax-full 3.2.2, sharp and marked. Use the configured bundled runtime for Python and Node. Set `IAH_NODE` to the Node executable, `IAH_NODE_MODULES` to the directory containing sharp and marked, and `IAH_MATHJAX_MODULES` to the directory containing mathjax-full. `IAH_FONT_DIR` may override the default Windows Times/Arial font directory.

Run `python paper/build_pdf.py`. It assembles `manuscript.md` and `references.md`, renders equations and writes `Intelligence-Attractor-Hypothesis-v0.1.pdf` and `build-manifest.json`. Intermediate files go to ignored `paper/.build/`. Check rendered pages after every edition change. Do not overwrite a publicly released edition; increment its version first. A delivery copy in `output/pdf/` must match the canonical PDF's SHA-256.

For the present local setup, MathJax is installed only in `tmp/preprint-runtime/node_modules`; it is a build dependency, not part of the theory or Arena.

## Release boundary

Before uploading, the author must review the PDF and set the actual release date. The publication text and appendices use CC BY-NC 4.0; repository software remains a separate licensing decision. Optional ORCID and any reserved DOI must be genuine. The deposit checklist links the official Zenodo instructions. No upload or publication is performed by the build script.
