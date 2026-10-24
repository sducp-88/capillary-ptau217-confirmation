# Analysis plan v1: confirmation burden under bounded classification error

Frozen locally on 2026-10-08 before any extension calculations. This is not a registry preregistration. The analyst has already seen the prior feasibility results on these same data. All extension analyses are secondary/exploratory, including the primary estimand selected below.

## Question and evidence unit

For the public capillary DPS p-tau217 paired source rows, how much reference testing is required when rule-out/rule-in thresholds are selected to meet specified class-conditional error tolerances, and how does this change when sampling uncertainty in the cutoffs is explicitly allowed for?

Input: Huber et al., DOI 10.1038/s41591-025-04080-0, source workbook 41591_2025_4080_MOESM3_ESM.xlsx, Extended Data Figure 3. Expected SHA-256 4b1f5983b8548d4f4f5edc08f4b541358ade1d624d0d1d8aaaf44535e89f092b. Use all 176 complete rows, with 99 CSF-positive and 77 CSF-negative author-supplied binary labels. One public paired row is the analysis unit, described as a participant by the article. No public IDs allow independent verification of unique identities. No cross-sheet linkage, center reconstruction, or new data imputation. No source file is modified.

Measurements: capillary DPS p-tau217 (ALZpath Simoa, pg/mL of eluate); paired venous plasma p-tau217 (pg/mL, with center-specific assay heterogeneity reported in the original study); abnormal CSF Aβ42/p-tau181 status. The ratio's continuous values, center-specific thresholds, collection/batch metadata and clinical eligibility are unavailable. No use as a patient-care protocol.

## Estimands and locked rules

Primary estimand: fraction requiring reference confirmation under a two-cutoff rule, jointly reported with FN/CSF-positive and FP/CSF-negative rates. A gray-zone row is a deferred decision, not an error. FN and FP denote disagreement with the supplied CSF reference, not proven clinical misdiagnosis. Report NPV/PPV only with their correct denominators and observed prevalence. Do not interpret conditional errors as population risk or harms.

1. Published rounded capillary rule: negative x<0.01, positive x>=0.02, gray otherwise. Reproduce without attributing a 0.02 boundary discrepancy to author error.
2. Empirical 90/90 rule: candidate cutoffs are midpoints of adjacent distinct values, plus extreme boundaries. Lower threshold is the largest with training sensitivity>=0.90; upper is smallest with training specificity>=0.90. Keep ties intact. Use negative x<L, positive x>=U. If L>=U, use midpoint single cutoff and record overlap (never prioritize one overlapping label silently).
3. Confidence-constrained 90/90 rule: use nonparametric order-statistic tolerance bounds with each conditional error<=0.10 and failure probability 0.025 for each tail, giving at least 0.95 joint coverage by Bonferroni under independent, exchangeable source-population sampling. For class sample size n, choose largest r>=1 with BinomialCDF(r-1;n,0.10)<=0.025. Lower threshold is positive-class order statistic X_(r), with x<L negative; upper threshold is nextafter of negative-class order statistic X_(n-r+1) towards +infinity, with x>=U positive. These strict comparisons preserve conservative behavior with rounded ties. If no r exists, use -infinity for rule-out or +infinity for rule-in (no unqualified tail decisions). If thresholds overlap, choose a common cutoff inside the admissible interval. This is a statistical sensitivity scenario, not a guideline-mandated confidence standard or proven transport guarantee.
4. Prespecified sensitivity targets: empirical 95/95 and confidence-constrained 95/95 using the same method; one-sided 95% confidence for each tail separately as a less stringent sensitivity scenario; fixed rounded-boundary > versus >= analysis. Retain all outcomes.

No optimizing of targets, models, or titles on result significance. Confidence limits for evaluation do not reuse naive binomial intervals to certify an adaptively selected cutoff. Order-statistic derivation is stated explicitly.

## Decision pathways

A. Two-cutoff direct decisions, confirm gray zone with the supplied CSF reference; unresolved error comprises capillary FN+FP outside gray zone. Reference confirmation is idealized as exactly reproducing the reference label; it is not a model of actual CSF/PET measurement error or a clinical impact trial.
B. Rule-out triage: only x<L avoids reference testing; all other rows undergo reference testing. Remaining errors are FN only. Report binary sensitivity and specificity at L; this distinguishes a high-sensitivity cutoff from meeting the guideline's separate specificity criterion for triage.
C. Comparative baseline: reference test everyone (100% burden, 0 discordance by definition, not an observed care pathway).
D. Supplementary descriptive paired decisions against plasma >0.42. Tabulate CSF-stratified 3x2 decisions, definite opposites, whose result matches CSF, and errors shared by both tests. Do not identify plasma as gold standard. The source study reports different plasma platforms at one center and lacks center labels in this table; therefore 0.42 cannot be certified platform-appropriate for every row. Supersede the feasibility phase's primary comparator designation; keep the old result for transparency, not as the main new inference. An adaptive plasma 90/90 rule is retained as a sensitivity result from the prior analysis.

## Internal evaluation

Repeated stratified fivefold cross-fitting, 200 repeats, seed 20261008. Fit thresholds exclusively in each training fold, then classify untouched test rows. Every repeat covers all 176 rows exactly once. No fold-specific tuning based on held-out performance. Report average FN/99, FP/77, gray/176, triage-confirmation/176, paired definite opposition/176, and cutoff distributions. Per-repeat 2.5th-97.5th percentiles describe split variability; they are not independent population CIs and repetitions are not new participants. Show empirical and confidence-constrained rules at 90% and 95% targets. The confidence-constrained method has its analytic bound under assumptions; cross-fitting assesses within-sample behavior only.

Full-sample paired differences and exact binomial (Clopper-Pearson) intervals for the published fixed rule are descriptive/conditional because the original cutoffs were developed in this sample. Fixed-rule paired comparison can include exact McNemar discordant-error counts but is not the principal hypothesis; no multiplicity-dependent positive claims.

## Additional sensitivity and validation gate

Prevalence-standardized policy projections at 10%, 30%, 50% and observed 56.25%, holding class-conditional performance fixed; label this as arithmetic transport under constant sensitivity/specificity, not external validation. Evaluate reference error tolerances 10% and 5% only; derive sample sizes for zero observed errors at one-sided 97.5% confidence (n>=ceil(log(0.025)/log(1-alpha))). No monetary cost or clinical utility is estimated without cost/harm weights.

Search independent public datasets for matched capillary DPS assay/unit, paired venous result, independent CSF/PET label, unique participant/linkage and recruitment independence. Log exclusions (PROTECT cognition-only, liquid capillary Tasso, venous-only cohorts, DBS other platforms, study designs without released outcomes). Do not pool or substitute them. If eligible data are found, freeze a separate transport amendment before applying frozen source thresholds.

Claims limited to this public paired subset and explicit mathematical assumptions. The paper will acknowledge that the original article already withheld clinical-use recommendations, and will quantify a validation/confirmation requirement rather than claim to refute the original feasibility conclusion. If no external cohort is available, do not claim validated implementation. Report scientific and editorial limitations even if a complete manuscript package is prepared.

## Outputs and QA

Save source hashes, plan hash, exact thresholds/ranks, all alternative-rule results, fold assignments/predictions, source-row decisions, figures and their source data, software/seed metadata and numerical assertions. Primary figure: confirmation-versus-residual-error tradeoff and CSF-stratified decision accounting. Supplement: cutoff/split distributions, full definitions and prevalence sensitivity. Verify source invariance and perform an independent implementation check of tolerance-rank coverage and full-sample counts. Submission files and bilingual internal review remain separate.
