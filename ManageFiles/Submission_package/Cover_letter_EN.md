# Cover Letter（致 Computers and Electronics in Agriculture 编辑）

Dear Editors of Computers and Electronics in Agriculture,

We are pleased to submit our manuscript "The Trap of Model-Derived Yield Targets: A Controlled Diagnostic of Target Construction, Validation Design, and Co-Construction Bias in County-Scale Yield Mapping" for consideration as a research article. The work sits at the journal's core intersection of machine learning, digital agriculture, and evaluation methodology.

Regional yield mapping increasingly trains machine-learning models against model-derived targets (process-model baselines, satellite retrievals, interpolations) because grid-scale field measurements are rare. Our manuscript asks what such targets do to reported skill, and answers with a controlled diagnostic built entirely on public data: (i) a circular-validation upper bound (interpolated target R2 = 0.98 versus a leave-one-out interpolation bound of 0.20-0.27); (ii) the mechanism by which checkerboard cross-validation becomes structurally inert in small domains (between-block distance pinned at 2.3-2.4 km across all block sizes), with gradient-cutting schemes as the honest alternative; (iii) a detectability framework reconciling county-scale nulls with genuine regional signal (R2 = 0.69 across 7,784 grids) via window sweeps and planted-signal power analysis; and (iv) directional proof of co-construction bias: two national yield products correlate at r = 0.017 while one environmental model "explains" both at R2 near 0.65, with official provincial statistics arbitrating which product carries real signal (rho = 0.893 versus -0.04).

The contribution is directly aligned with the journal's scope in computational methods for agriculture: a six-step pre-mapping audit protocol in which every step is computational, costs minutes, and requires no new data - target provenance disclosure, variogram- and domain-aware validation design, PC1 screening, decision-relevant uncertainty, sampling-geometry power ceilings, and inter-target agreement with statistical arbitration. All code, fold assignments, seeds, and statistical ledgers are released; every number in the manuscript regenerates from a scripted ledger (27/27 claims verified programmatically), matching the journal's standards for reproducible computational research.

The manuscript is original, not under consideration elsewhere, and all authors have approved the submission and declare no conflicts of interest. We will publish under the subscription route (no open-access charge).

Suggested reviewers (no collaborations or conflicts in the past five years): Edzer Pebesma (University of Muenster; spatial validation), Pierre Ploton (IRD; spatial model assessment), Alexandre Wadoux (University of Sydney; map accuracy evaluation), and a senior author of the ChinaWheatYield30m dataset for the remote-sensing perspective.

Thank you for your consideration.

Yucheng Peng, on behalf of all authors
College of Agronomy / National Maize Improvement Center, China Agricultural University
