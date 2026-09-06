# Publication edition 0.1

**The Intelligence Attractor Hypothesis: Independent Convergence Under Shared Reality Constraints**

**Vitalii Zhyliaiev**

Prepared 6 September 2026. Conceptual preprint; no empirical validation or peer review claimed.

## Read the complete edition

- [Complete PDF, including all five appendices](IAH-v0.1.pdf)
- [Assembled manuscript source](manuscript.md)
- [Origin of the hypothesis and AI assistance](../PROVENANCE.md)
- [Publication scope and interpretive notes](front-matter.md)
- [Bibliography](references.md) and [BibTeX records](references.bib)
- [Publication license: CC BY-NC-ND 4.0](LICENSE.md)
- [Zenodo metadata and final deposit decisions](zenodo-metadata.md)

The PDF is prepared for author review, not yet deposited. No DOI or public release date is claimed. The title and substantive claims of the flagship are preserved. All five appendices are included, including U3 and the full speculative scope of Appendix E.

## Structure

1. Publication scope and interpretive notes.
2. Canonical IAH statement.
3. Origin of the hypothesis and AI assistance.
4. Appendix A: Origin Dependence and Attenuation.
5. Appendix B: Recursive Architectural Attractor.
6. Appendix C: Relational Narrowing and Strong Functional Uniqueness.
7. Appendix D: Related Work Map, including AI-assisted source register.
8. Appendix E: Speculative Limits.
9. References.

The main text and appendices are assembled from the corresponding repository Markdown files. Repository-only back links and repeated author/revision lines are removed; appendix section numbers are prefixed A-E. Display equations may wrap for print. Interpretive caveats are explicit in the edition preface rather than silent rewrites of the underlying theory.

## History and rollback

The baseline commit is `a3410ecf11024b6d204e4a3e0710744136428888`, locally tagged `iah-before-preprint-2026-09-06`. Exact original documents and checksums are stored in [history/before-preprint-2026-09-06](history/before-preprint-2026-09-06/manifest.json). See [CHANGELOG](../CHANGELOG.md).

The working branch is `codex/iah-first-preprint`. Publication work is local. Existing unrelated Arena and EXP-001 edits were not included or overwritten. To undo a particular edit, compare with the saved original and restore only the relevant file; avoid a blanket reset that would discard unrelated work.

## Rebuild

Python dependencies: reportlab, Pillow, pypdf. Node dependencies: mathjax-full 3.2.2, sharp and marked. Use the configured bundled runtime for Python and Node. Set `IAH_NODE` to the Node executable, `IAH_NODE_MODULES` to the directory containing sharp and marked, and `IAH_MATHJAX_MODULES` to the directory containing mathjax-full. `IAH_FONT_DIR` may override the default Windows Times/Arial font directory.

Run `python paper/build_pdf.py`. It assembles `manuscript.md`, renders equations and writes `IAH-v0.1.pdf` and `build-manifest.json`. Intermediate files go to ignored `paper/.build/`. Check rendered pages after every edition change. Do not overwrite a publicly released edition; increment its version first.

For the present local setup, MathJax is installed only in `tmp/preprint-runtime/node_modules`; it is a build dependency, not part of the theory or Arena.

## Release boundary

Before uploading, the author must review the PDF and set the actual release date. The publication text and appendices use CC BY-NC-ND 4.0; repository software remains a separate licensing decision. Optional ORCID and any reserved DOI must be genuine. The deposit checklist links the official Zenodo instructions. No upload or publication is performed by the build script.
