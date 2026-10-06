# Secondary readout benchmark: two public membrane-flow examples

This is a **segmentation and fit-sensitivity benchmark**, not a force-sensor calibration, tension measurement, new cell-line validation, or biological comparison with independent replicates. It supports a future mammalian-cell assay handoff by exposing analysis choices that should be validated before interpreting a marker-motion readout.

## Sources and reuse

De Belly, Yan et al., *Cell* (2023), DOI [10.1016/j.cell.2023.05.014](https://doi.org/10.1016/j.cell.2023.05.014), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10330871/). Shannon Yan is a co-first author. The paper links the public author repository [weinerlab/Inverse_Photobleach_Flow](https://github.com/weinerlab/Inverse_Photobleach_Flow), pinned at `1f469495ada2ca3e7a741637dcc2c95ac973e713`.

The corresponding exact archived release is [Zenodo 7894213](https://doi.org/10.5281/zenodo.7894213), explicitly licensed **Creative Commons Attribution 4.0 International**. The repository itself has no separate license file; reuse here relies on the archived release's stated license. The original `seg_funcs.py` and the two TIFFs in the archive are byte-identical to the pinned GitHub versions. Attribute the paper authors and archived code/data creators. Upstream code is used unchanged; the surrounding reproducibility, parameter-sensitivity analysis, CSV export, and plots are additions by Cathy Liu's application demo.

Archive SHA256: `2c35036167001afae6e04906453e3640eb5eee275cfa742d67dbffe3a3b251bf`.

The two TIFFs each contain 71 time points, two channels, and 256×256 unsigned-16-bit pixels. HT-CAAX defines the membrane segmentation; CellMask is sampled along that outline. The paper's full experimental dataset is available on request; these public examples are **not the complete study**.

## Reproduce in a fresh directory

From the repository root, follow the complete commands in [REPRODUCIBILITY.md](../REPRODUCIBILITY.md). The secondary pipeline alone is:

```sh
python3 -m venv .repro/venv
.repro/venv/bin/python -m pip install -r scripts/requirements.txt
.repro/venv/bin/python scripts/fetch_secondary_source.py --output .repro/membrane-source
.repro/venv/bin/python scripts/build_secondary.py --repo .repro/membrane-source --output .repro/output
.repro/venv/bin/python scripts/test_secondary.py --data .repro/output/secondary-data.json
.repro/venv/bin/python scripts/render_secondary.py --data .repro/output/secondary-data.json
```

The downloader checks the complete archive hash and extracts only six named files, refusing to overwrite a differing local file. The builder verifies the source-code and TIFF hashes before executing the reviewed `outline2map` function. It does not execute an upstream notebook, install Napari, or run unreviewed code. Original helper code imports only NumPy and contains the outline sorting/sampling functions.

Dependencies tested: Python 3.12, NumPy 2.5.3, SciPy 1.18.1, scikit-image 0.26.0, tifffile 2026.9.20. These are the demo's pinned environment, not a claim to reproduce the authors' original package environment. Unbounded Gaussian fitting is sensitive to initialization, optimizer/library behavior, and image processing; nonconvergence and covariance warnings are retained explicitly.

A fresh archive download into a separate source directory followed by a complete rebuild produced a byte-identical `secondary-data.json` (SHA256 `0a286c3897dfaeec7e9da1bf5b8b30f9da6083bbb9314a94825e05c10f5893af`).

## Method and exact conventions

1. Preserve the author ROI: control rows 45:256 and columns 0:128; protrusion full image.
2. Otsu threshold the HT-CAAX channel; remove objects below 100 pixels, fill holes below 10,000 pixels; erode with a disk of radius 1, 2, or 3 pixels. The original radius is 2 for control and 1 for protrusion. The added radii are sensitivity settings, not independently validated optimal segmentations.
3. Find inner boundaries with connectivity 2 and dilate with disk 1. Execute the unchanged upstream `outline2map`, angular shift 180°, to sample the CellMask channel.
4. Skip source frame 0 exactly as the notebooks do. Analyze source frames 1–60 for control and 1–22 for protrusion. Trim each movie/radius profile to its minimum outline length, then average into `minimum_length//3` bins.
5. Preserve the original approximate unrolling coordinate and conversion: `x=linspace(-nx//2,nx//2,nx)`; mean horizontal/diagonal pixel distance `(sqrt(0.1²+0.1²)+0.1)/2` µm. This is **not independently calibrated contour arclength**. Absolute speed requires validation before reuse. A sign denotes direction on the ordered coordinate, not verified movement toward or away from a protrusion.
6. Fit `amplitude*exp(-(x-center)²/(2*width²))+offset` using the original unbounded `curve_fit` defaults. Preserve the author center gates: control `center<=80`; protrusion `0<=center<=50`, in unrolling bins. These gates are not sufficient to establish fit quality; warning, RMSE, and normalized RMSE remain visible. The builder catches rather than crashes on fit nonconvergence, storing null fit parameters and excluding that frame from regression. No new fit-quality gate silently removes data.
7. Compute descriptive OLS slopes from retained centers versus time. Intervals are derived from notebook timestamps: control `(297.8334−105.4653)/69` s; protrusion `(255.8916−63.3731)/69` s. Source frame 1 is displayed at relative time 0; it is **not a verified stimulation-onset timestamp**.
8. The common 22-frame display uses the first 22 analyzed frame positions, because the protrusion notebook fits 22. Control preprocessing still uses its original 60-frame minimum-outline trimming; the common 22-frame control panel is a regression-window sensitivity check, not resegmentation with a new 22-frame crop. The control's full 60-frame window is also retained. The two movies are unpaired examples, not a matched experiment or a cohort.

`center_um` is the fitted approximate coordinate. `gaussian_parameters` are amplitude, width, center, offset in original unrolling-bin units; `x_um` is converted to µm. A plotted displacement subtracts the first retained center within each movie/radius; changing that constant does not alter OLS slope. Exported rows include unsuccessful and center-gate-excluded frames, with flags. Source frame indices are zero-based original TIFF indices, with frame 0 excluded by the author workflow.

## Descriptive findings in this environment

For the first 22 analyzed frame positions, the protrusion example yields approximate fitted slopes of 43.59, 62.38, and −17.70 nm/s at radii 1, 2, and 3, with 22, 20, and 12 retained frames respectively. The radius 3 sign change co-occurs with 10 of 22 center-gate exclusions: it flags **segmentation/fit fragility**, not a reversal of biological membrane flow.

The control's original radius 2 yields −7.68 nm/s over its first 22 observations (21 retained), but 0.42 nm/s over 60 observations (56 retained). This is a window-dependence audit on one movie, not evidence of a biological control effect.

There are two nonconvergent fits in the 246 movie×radius×frame records and three additional covariance-warning records. The QA report independently checks scalar OLS, coordinate conversion, Gaussian residual arithmetic, and record structure. There are no p-values, bootstrap confidence intervals, inferred forces, or cell-level effect claims.

## What this can and cannot inform

**Can inform:** whether the extraction code is reproducible; which radius/window choices materially change the readout; which frame profiles need visual inspection; and which segmentation, calibration, negative-control, and repeated-cell checks to include before transferring a membrane-marker analysis to a new assay.

**Cannot inform:** the performance of a new genetically encoded force probe, optical-tweezers calibration, force/pN values, sensor cloning success, mESC behavior, or biological reproducibility. Construct-specific controls and independently cultured cells must be collected before such decisions.

The companion `VirtualEmbryo/membrane-cortex-tension` repository was also inspected. Its deposited `Actin_data.xlsx` and `Membrane_data.xlsx` fail ZIP/XLSX integrity in both GitHub and the checksum-verified Zenodo release; they are not used here. No numerical missing values were invented or reconstructed.
