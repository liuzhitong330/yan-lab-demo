# Unloaded-FRET transfer check

This is an independent reanalysis of external Hoffman Lab source data, not Yan Lab experimental data or a new force calibration. Its intended use is to choose a small provisional construct/control panel and expose what must be revalidated when a probe moves between assay contexts.

## Reproduce

Use the pinned Python environment and commands in [REPRODUCIBILITY.md](../REPRODUCIBILITY.md). From the repository root, the primary builder is `scripts/build_primary.py --output .repro/output --cache .repro/primary-sources`. It downloads two public eLife workbooks and refuses changed SHA-256 hashes or invalid workbook files. It does not write or modify a workbook. Generated JSON and CSV files are deterministic and contain no private applicant data.

- LaCroix AS, Lynch AD, Berginski ME, Hoffman BD (2018). *Tunable molecular tension sensors reveal extension-based control of vinculin loading*. [eLife 7:e33927](https://doi.org/10.7554/eLife.33927). [Full text and methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6053308/).
- [Figure 1 source workbook](https://cdn.elifesciences.org/articles/33927/elife-33927-fig1-data1-v1.xlsx), DOI 10.7554/eLife.33927.010. The builder uses measured columns C:D and I:J from sheets Figure 1G and Figure 1H, never fitted columns F:G/L:M or Model Parameters.
- [Figure 1 supplement 1 source workbook](https://cdn.elifesciences.org/articles/33927/elife-33927-fig1-figsupp1-data1-v1.xlsx), DOI 10.7554/eLife.33927.005. The builder uses sheet Figure 1-Figure supplement 1B measured columns C:D and F:G. The full-length-FP comparison in supplement1A is outside this bounded analysis, and brightness raw rows for supplement1C are not present in this workbook.
- Source article/data are reused with attribution under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Publication XML verified the CC-BY-4.0 license and listed only a commentary as a related article, with no retraction/correction notice found in that record on 2026-10-06. This is not a guarantee that no later notice exists.

## Data and calculations

The main dataset contains 111 in-vitro experiment measurements and 739 in-cell measurements across 16 nominal linker designs. Eight linkers have both contexts. The control dataset separately contains 425 cells across three fixed/live comparisons. Neither total is a count of independent biological replicates.

In vitro means HEK293-cell hypotonic lysates measured by spectrofluorometry. In cellulo means vinculin-null mouse embryonic fibroblasts measured by FRET imaging. The manuscript reports at least five independent experiments per in-vitro condition and three experiments underlying the pooled in-cell measurements. Source tables do not identify which experiment each cell belongs to.

For each measured linker, retain every source row, source cell address, observed FRET efficiency (%) and nominal linker length (amino acids). Derive repeat count from measured length divided by the explicitly named motif length. The repeat-segment string is not a verified complete plasmid insert: fluorophore truncations, junctions and full sequence are not reconstructed.

For matched linkers, compute the unpaired mean difference as in-cell mean minus in-vitro mean, in percentage points. Display arithmetic mean, sample SD (n−1) and number of observations. SD is dispersion, not measurement accuracy or a confidence interval. No missing measurement is imputed; no p-values or bootstrap inference is produced. Different measurement modalities and cellular contexts confound a causal environmental interpretation.

The adjustable tolerance is a user-set planning criterion on absolute mean shift, not a calibrated instrument-noise threshold. A linker outside the tolerance is prioritized for matched-context baseline checks. A linker inside the tolerance is not proven equivalent or mechanically calibrated. Sensitivity tables show how this provisional triage changes at 1, 2, 3, 5, 7, 8 and 10 percentage points.

The reproducible data schema retains a 3-percentage-point example in `defaults.tolerance_pp`; the interactive website intentionally starts at 5 percentage points. Both descriptive settings flag seven of the eight matched linkers. Browser tables and exports use the currently selected slider value, not the schema example. Neither setting is a calibrated or statistically validated cutoff.

Supplement1B compares fixed cells at 23°C with live cells at 37°C. Report live-minus-fixed means without pairing or assigning the difference to fixation alone. These controls are not added to the primary environment dataset or used as independent replications of it.

## Proposed next validation record

For a new probe, preserve separate fields for construct ID/version, nominal repeat segment, verified full insert/plasmid sequence, host/targeting context, donor-only and acceptor-only correction controls, unloaded/force-insensitive control, localization and expression assessment, cell identity/health, biological batch, acquisition settings and response calibration. This demo fills only the public-data-informed candidate/control rationale. It does not mark the remaining checks completed.

The resulting small panel is a *proposal*: a candidate linker selected for the intended application and a contrasting linker with a different observed baseline-transfer pattern, tested in the same planned cellular context. Only direct mechanical calibration and functional validation can establish the appropriate force range. Unloaded FRET alone cannot select the best force sensor or convert signal to pN.

## Scope relative to the Yan role

The external construct comparison supports probe-design and validation planning. A separate reuse of Yan-associated public membrane-flow code/movies supports image-readout robustness and cell-assay documentation. The two datasets do not share cells, probes, units or experimental batches and must not be quantitatively merged. Neither dataset demonstrates Cathy has performed molecular cloning, built a mammalian cell line or operated optical tweezers.
