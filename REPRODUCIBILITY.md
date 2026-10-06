# Reproduce the two bounded analyses

The browser demo uses precomputed public-data derivatives. It does not send data to an API, require an account, or execute downloaded notebooks. Both source pipelines verify pinned file hashes and fail if the remote sources change.

## Environment

Tested with Python 3.12 and the versions in [scripts/requirements.txt](scripts/requirements.txt). Run these commands from the repository root. `.repro` is a new local scratch folder and is not part of the published site.

```sh
python3 -m venv .repro/venv
.repro/venv/bin/python -m pip install -r scripts/requirements.txt
```

The code and sources are explained below so that the pipeline can be reviewed before execution. Only the explicitly reviewed, content-hashed `seg_funcs.py` is imported from a third-party download. No whole upstream notebook or model solver is executed.

## 1. Unloaded-FRET transfer benchmark

```sh
.repro/venv/bin/python scripts/build_primary.py --cache .repro/primary-sources --output .repro/output
.repro/venv/bin/python scripts/audit_primary_independent.py --sources .repro/primary-sources --data .repro/output --report .repro/output/primary-qa.json
```

The builder downloads two hash-pinned eLife source workbooks. It reads **measured columns only** and preserves the exact source file, sheet, row and cell addresses in its CSVs. It does not execute spreadsheet formulas or use model-fit columns.

Outputs:

- `primary-data.json`: 16 nominal linkers, eight matched between contexts, observed values and descriptive summaries.
- `primary-observations.csv`: 850 source measurements, comprising 111 in-vitro experiment observations and 739 pooled cellular observations.
- `primary-live-fixed-observations.csv`: 425 separate observations from fixed 23°C versus live 37°C controls.
- `primary-qa.json`: independent checks of every source-cell value, coverage, arithmetic mean, sample SD, shifts and tolerance membership. The auditor does not import the builder.

No batch identities are available for the pooled cell data, so no cell-bootstrap significance, p-values or replicate-level confidence intervals are computed. Assay modality and cellular context differ together. The user-adjusted tolerance is a planning criterion, not measured instrument noise. Unloaded FRET does not define a force-response curve or an optimal sensor.

The JSON schema's example default is 3 percentage points; the website intentionally initializes its slider at 5 percentage points. Both flag seven of eight matched linkers, and all browser readouts/exports follow the live slider value. This presentation choice does not change source measurements or derived shifts. Every tolerance is descriptive, not a validated acceptance threshold.

Source details and assumptions: [PRIMARY_METHODS.md](data/PRIMARY_METHODS.md).

## 2. Yan-associated membrane-marker benchmark

```sh
.repro/venv/bin/python scripts/fetch_secondary_source.py --output .repro/membrane-source
.repro/venv/bin/python scripts/build_secondary.py --repo .repro/membrane-source --output .repro/output
.repro/venv/bin/python scripts/test_secondary.py --data .repro/output/secondary-data.json
.repro/venv/bin/python scripts/render_secondary.py --data .repro/output/secondary-data.json
```

The downloader retrieves the pinned CC-BY archive, checks its complete SHA256, extracts six explicit allowlisted files and refuses to overwrite different local contents. The builder checks the hashes of the two TIFFs and `seg_funcs.py` again, then executes the original `outline2map` function as part of the reviewed analysis.

Outputs:

- `secondary-data.json`: measured membrane profiles, source-frame indices, approximate fitted centers and fit-quality records for two movies and three erosion radii.
- `secondary-traces.csv`: all 246 analyzed movie×radius×frame records, including rejected or unsuccessful fits with their flags.
- `secondary-findings.json`: descriptive common-window and author-window regressions.
- `secondary-qa.json`: independent scalar OLS, coordinate and Gaussian-residual arithmetic checks.
- Four `*-segmentation-sensitivity.svg` / `*-intensity-profiles.svg` scientific trace figures, generated from numeric outputs without modifying source images.

The control notebook analyzes 60 frames; the protrusion notebook analyzes 22. A first-22-frame regression comparison is exposed without claiming aligned stimulation onsets or matched biological replicates. The author's approximate spatial coordinate is preserved, not independently calibrated. Radius-sensitive sign changes flag analysis fragility, not reversed biological motion. Two fit failures and three covariance warnings remain explicit in this pinned environment.

A fresh source download followed by a full rebuild produced a byte-identical `secondary-data.json`, SHA256 `0a286c3897dfaeec7e9da1bf5b8b30f9da6083bbb9314a94825e05c10f5893af`. Numerical fitting can vary across dependency versions; use the pinned environment.

Source details and assumptions: [SECONDARY_METHODS.md](data/SECONDARY_METHODS.md).

## Compare against the released data

After rebuilding, compare each corresponding JSON/CSV in `.repro/output` against `data/`. For example:

```sh
cmp data/primary-data.json .repro/output/primary-data.json
cmp data/primary-observations.csv .repro/output/primary-observations.csv
cmp data/primary-live-fixed-observations.csv .repro/output/primary-live-fixed-observations.csv
cmp data/secondary-data.json .repro/output/secondary-data.json
cmp data/secondary-traces.csv .repro/output/secondary-traces.csv
```

No output from a failed check should be substituted silently. Revisit the source identity, hash and environment if a comparison changes.

## Publication boundaries

Only reviewed scripts, public-data derivatives, method notes and scientific trace figures are distributed here. Original movies and downloaded workbooks are obtained by the reproducibility commands, not copied into the website. Do not publish `.repro`, a virtual environment, downloaded caches, private applicant documents, credentials, or application records.
