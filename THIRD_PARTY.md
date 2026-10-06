# Third-party sources and attribution

## External construct benchmark — not Yan Lab data

**LaCroix AS, Lynch AD, Berginski ME, Hoffman BD.** *Tunable molecular tension sensors reveal extension-based control of vinculin loading.* eLife 2018;7:e33927. [DOI](https://doi.org/10.7554/eLife.33927) · [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6053308/).

Article/source data: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

| File | Use | SHA256 |
| --- | --- | --- |
| [Figure 1 source workbook](https://cdn.elifesciences.org/articles/33927/elife-33927-fig1-data1-v1.xlsx) | Sheets Figure 1G/1H, measured C:D and I:J columns only | `3c79aa488650280e75071aa177ba9aa73704c011c7014d6c514c0932ea5245a4` |
| [Figure 1 supplement 1 workbook](https://cdn.elifesciences.org/articles/33927/elife-33927-fig1-figsupp1-data1-v1.xlsx) | Supplement 1B, fixed/live measured C:D and F:G columns only | `4e4cf81e90edb4536a0cbebafd077d635aa48c5b50e51d6531b19685fa670f7e` |

Changes: selected measured blocks, retained source-row provenance, calculated descriptive summaries and unpaired mean shifts, added a user-defined planning-tolerance screen and numeric exports. Fitted/model columns and digitized/simulated force datasets are excluded. This is independent reanalysis, with no endorsement by the original authors implied.

## Yan-associated membrane-flow code and example data

**De Belly, Yan and coauthors.** *Cell protrusions and contractions generate long-range membrane tension propagation.* Cell (2023). [DOI](https://doi.org/10.1016/j.cell.2023.05.014) · [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10330871/). Shannon Yan is a co-first author.

The paper-linked [weinerlab/Inverse_Photobleach_Flow](https://github.com/weinerlab/Inverse_Photobleach_Flow) repository is pinned at commit `1f469495ada2ca3e7a741637dcc2c95ac973e713`. The author release [Zenodo 7894213](https://doi.org/10.5281/zenodo.7894213) explicitly declares **CC BY 4.0**. Reuse relies on that archived release's license; the GitHub repository itself has no separate license file. The source code and TIFF files used here are byte-identical between the archived release and pinned repository.

The archive credits Henry De Belly, Shannon Yan, Hudson Borja da Rocha, Sacha Ichbiah, Jason P. Town, Patrick J. Zager, Dorothy C. Estrada, Kirstin Meyer, Hervé Turlier, Carlos Bustamante and Orion D. Weiner as creators.

Archive SHA256: `2c35036167001afae6e04906453e3640eb5eee275cfa742d67dbffe3a3b251bf`.

| File | SHA256 |
| --- | --- |
| `seg_funcs.py` | `061139382e8b57289c54fa54b91ababe7b7fe6d0afecd2d6a8a994cbf46a1c34` |
| `data/control_example.tif` | `2fe6d3e9caba8981a0b10789fdbf015b585d2512a532f3f7d7029970b3d8de77` |
| `data/protrusion_example.tif` | `b0890aa89b50d7768c92ce0e311bd3dc797c0a11acbd70c1827681cf35ca659d` |

Changes: preserve and execute the original `outline2map` helper unchanged; adapt the notebook's documented segmentation, binning and Gaussian-fitting steps into a standalone script; add erosion-radius and regression-window sensitivity, explicit fit-failure handling, audit records, exports and scientific trace figures. The original approximate coordinate and center filters are disclosed. Credit remains with the original authors for their code, images and assay. No author endorsement or new force calibration is implied.

Original TIFFs are not distributed in this website. They are fetched on demand by a hash-checked script from the licensed archive. The two example movies do not constitute the full publication dataset.

## Inspected but excluded

The paper-linked [VirtualEmbryo/membrane-cortex-tension](https://github.com/VirtualEmbryo/membrane-cortex-tension) repository and its corresponding Zenodo release were inspected. The deposited Excel files failed ZIP/XLSX integrity in both sources and were not used or repaired. No data from its computational solver is presented as measured force or probe calibration.

## Software dependencies

The reproducibility pipeline uses NumPy, SciPy, scikit-image, tifffile and openpyxl, installed separately under their respective upstream licenses. They are not vendored into the site. Pinned versions appear in [scripts/requirements.txt](scripts/requirements.txt).
