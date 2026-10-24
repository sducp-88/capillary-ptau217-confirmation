# Confirmation burden under cutoff uncertainty in capillary p-tau217 testing

Reproducibility code for a secondary analysis of publicly released source data accompanying Huber et al., Nature Medicine, DOI: [10.1038/s41591-025-04080-0](https://doi.org/10.1038/s41591-025-04080-0). This repository contains the analysis and figure scripts aligned with the manuscript revision dated 24 October 2026. It does not imply journal acceptance.

## Reproduce

Use Python 3.12 and the pinned dependencies in `requirements.txt` in a virtual environment:

```sh
python -m venv .venv
# Activate the environment using the command appropriate to your operating system.
python -m pip install -r requirements.txt
python scripts/download_source.py
python scripts/analyze.py
python scripts/calculate_planning.py
python scripts/make_figures.py
```

The download script retrieves the original publisher's workbook and verifies its SHA-256 before writing it. If automated downloading is unavailable, obtain `41591_2025_4080_MOESM3_ESM.xlsx` from the article's supplementary material and save it as `evidence/source/T030_41591_2025_4080_MOESM3_ESM.xlsx`. The analysis independently verifies the checksum. Source data and generated row-level outputs are not tracked in this repository.

Input SHA-256: `4b1f5983b8548d4f4f5edc08f4b541358ade1d624d0d1d8aaaf44535e89f092b`.

The analysis uses the 176 paired observations in the sheet `Extended Data Figure 3`: 99 CSF-reference-positive and 77 CSF-reference-negative observations. It produces aggregate summaries, row decisions, stratified resampling outputs and numerical checks. The plotting script produces Figure 1 and supplementary figures; `--figure1-only` limits plotting to Figure 1. Figure 1 includes the corrected text spacing.

## Interpretation and provenance

The published rounded rule places 53/176 observations in the intermediate zone. Confirming all nonnegative results instead involves 122/176 observations. These are different confirmation policies. The confidence-bound cutoff analysis evaluates uncertainty in estimated thresholds; repeated five-fold resampling is internal evaluation, not independent external validation. These scripts do not establish clinical utility or constitute a clinical testing recommendation.

The files in `protocol/` are preserved unchanged. They describe a plan frozen after earlier exploratory work and a subsequent amendment; they must not be described as prospective preregistration. Existing analysis and figure scripts are copied unchanged from the submission reproducibility package. `scripts/download_source.py` is a distribution convenience added for this repository. `CODE_CHECKSUMS.json` records the distributed files.

The original investigators and publisher remain the source of the underlying observations. Cite the original article when using its data and consult its terms. No additional software licence is granted in this repository. No permanent archive DOI is claimed.

AI-assisted tools were used in preparing code and documentation. Scientific interpretation and responsibility remain with the authors.
