# From probe design to a defensible cell readout

A small, reproducible research application demo by Cathy Liu for Shannon Yan's laboratory. It asks which construct and analysis assumptions should be checked before trusting a new mammalian-cell force-probe readout.

The two workbenches are deliberately separate:

- **Unloaded-FRET transfer check.** External Hoffman Lab measurements compare 16 nominal linker designs; eight have both lysate and cellular observations. Inspect observed distributions, baseline shifts and a user-chosen planning tolerance. Export a provisional construct/control rationale. This does not choose the best force sensor or calibrate a force range.
- **Membrane-readout robustness.** Execute a real component of the Yan-associated publication's public image-analysis code on its two example movies. Inspect how erosion radius and regression window affect approximate marker-motion readouts. These are two examples, not a biological cohort or a force measurement.

The repository includes source-row provenance, derived data, numeric exports, reviewed analysis scripts, independent arithmetic checks, and small scientific trace figures. No full private application materials or source-movie caches are published.

## Run locally

From the repository root:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. A server is needed for the browser to fetch the data files.

## Reproduce and audit

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for exact source downloads, pinned dependencies, build commands and checks. See [THIRD_PARTY.md](THIRD_PARTY.md) for source identities and reuse licenses.

Detailed methods are in [data/PRIMARY_METHODS.md](data/PRIMARY_METHODS.md) and [data/SECONDARY_METHODS.md](data/SECONDARY_METHODS.md).

## Interpretation boundary

Neither workbench measures force in pN, validates a new Yan Lab probe, or establishes an optimal sensor. The primary dataset is an external benchmark; the secondary uses Yan-associated public example data. They share no probes, cells, units or experimental batches and must not be quantitatively combined. Proposed validation records are plans, not completed experimental work or claims about Cathy's hands-on experience.
