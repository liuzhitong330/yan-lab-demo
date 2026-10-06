#!/usr/bin/env python3
"""Reproduce and stress-test the publication's two example membrane-readout movies.

This is not a force-sensor calibration, a tension measurement, or a cohort test.
The reviewed upstream outline2map is executed at an exact content hash.
"""
import argparse
import hashlib
import importlib.util
import json
import warnings
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import curve_fit, OptimizeWarning
from scipy.stats import linregress
import skimage
from skimage import filters, morphology, segmentation
import tifffile

HASHES = {
    "seg_funcs.py": "061139382e8b57289c54fa54b91ababe7b7fe6d0afecd2d6a8a994cbf46a1c34",
    "data/control_example.tif": "2fe6d3e9caba8981a0b10789fdbf015b585d2512a532f3f7d7029970b3d8de77",
    "data/protrusion_example.tif": "b0890aa89b50d7768c92ce0e311bd3dc797c0a11acbd70c1827681cf35ca659d",
}


def finite(value):
    return round(float(value), 8) if np.isfinite(value) else None


def gaussian(x, amplitude, width, center, offset):
    return amplitude * np.exp(-((x-center)**2) / (2*width**2)) + offset


def regress(frames, n):
    valid = [f for f in frames[:n] if f["center_valid"]]
    if len(valid) < 3:
        return {"n_frames": len(valid), "slope_nm_s": None, "r_squared": None}
    fit = linregress([f["time_s"] for f in valid], [f["center_um"] for f in valid])
    return {"n_frames": len(valid), "slope_nm_s": finite(fit.slope*1000),
            "intercept_um": finite(fit.intercept), "r_squared": finite(fit.rvalue**2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path(__file__).parent / "Inverse_Photobleach_Flow")
    ap.add_argument("--output", type=Path, default=Path(__file__).parent / "package")
    args = ap.parse_args()
    # Keep the authors' strict-size thresholds rather than silently switching to
    # the new <= threshold semantics in scikit-image 0.26.
    warnings.filterwarnings("ignore", category=FutureWarning, message="Parameter `(min_size|area_threshold)` is deprecated.*")
    args.output.mkdir(exist_ok=True, parents=True)
    for name, digest in HASHES.items():
        assert hashlib.sha256((args.repo/name).read_bytes()).hexdigest() == digest, name
    spec = importlib.util.spec_from_file_location("reviewed_upstream_seg_funcs", args.repo / "seg_funcs.py")
    upstream = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(upstream)
    payload = {"metadata": {
        "dataset": "Two public example HL-60 membrane-flow movies, De Belly, Yan et al., Cell 2023",
        "source_repo": "https://github.com/weinerlab/Inverse_Photobleach_Flow",
        "commit": "1f469495ada2ca3e7a741637dcc2c95ac973e713",
        "archive_doi": "10.5281/zenodo.7894213", "license": "CC BY 4.0",
        "source_sha256": HASHES,
        "analysis_unit": "one example movie per condition; frames are repeated observations, not independent cells",
        "quantity": "fluorescent membrane-marker peak motion using the published approximate spatial coordinate, NOT force",
        "pixel_size_um": .1,
        "coordinate_note": "Author unrolling coordinate: averaged boundary samples mapped with mean horizontal/diagonal pixel distance. Not an independently calibrated contour arclength; absolute speed should be validated before reuse.",
        "common_window_note": "First 22 analyzed frames chosen because the protrusion author notebook fits 22. The control notebook fits 60; those extra frames remain available separately. Movie starts are not aligned to verified stimulation onset.",
        "no_force_inference": "No force, FRET, sensor construct, calibration, or mESC data in these two movies.",
        "dependencies": {"numpy": np.__version__, "scipy": scipy.__version__, "scikit-image": skimage.__version__, "tifffile": tifffile.__version__}
    }, "movies": []}
    # Approximate coordinate conversion copied from the author notebooks.
    dist = ((.1**2+.1**2)**.5 + .1)/2
    for kind in ["control", "protrusion"]:
        image = tifffile.imread(args.repo / "data" / f"{kind}_example.tif")
        assert image.shape == (71,2,256,256), image.shape
        ht, cm = image[:,0], image[:,1]
        if kind == "control":
            ht, cm = ht[:,45:,0:128], cm[:,45:,0:128]
            dt, n, original_radius = (297.8334-105.4653)/69, 60, 2
        else:
            dt, n, original_radius = (255.8916-63.3731)/69, 22, 1
        movie = {"id": kind, "label": "Unstimulated example" if kind == "control" else "Protruding example",
                 "source_frames": 71, "frame_interval_s": dt, "analyzed_frame_origin": 1,
                 "author_fit_frames": n, "original_erosion_radius_px": original_radius,
                 "roi": "rows 45:256, columns 0:128" if kind == "control" else "full 256x256 image",
                 "variants": []}
        for radius in [1,2,3]:
            outlines, areas, centroids = [], [], []
            for frame in ht:
                binary = frame > filters.threshold_otsu(frame)
                clean = morphology.remove_small_objects(binary, min_size=100)
                fill = morphology.remove_small_holes(clean, area_threshold=10000)
                eroded = morphology.erosion(fill, morphology.disk(radius))
                edge = segmentation.find_boundaries(eroded, mode="inner", connectivity=2)
                outline = morphology.dilation(edge, morphology.disk(1))
                outlines.append(outline)
                areas.append(int(eroded.sum()))
                coords = np.argwhere(eroded)
                centroids.append(coords.mean(axis=0))
            outlines = np.stack(outlines)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                profiles, _, _ = upstream.outline2map(outlines[1:], cm[1:], n_images=n, ang_shift=180)
            edge_lengths = [int(o.sum()) for o in outlines[1:n+1]]
            min_len = min(edge_lengths)
            trimmed = [np.asarray(vals)[len(vals)//2-min_len//2:len(vals)//2+min_len//2] for vals in profiles]
            binned = np.stack([[np.mean(chunk) for chunk in np.array_split(v, min_len//3)] for v in trimmed])
            nx = binned.shape[1]
            x = np.linspace(-nx//2, nx//2, nx)
            frames = []
            for i, values in enumerate(binned):
                failed, warning_messages = False, []
                try:
                    with warnings.catch_warnings(record=True) as captured:
                        warnings.simplefilter("always", OptimizeWarning)
                        fit, cov = curve_fit(gaussian, x, values)
                    warning_messages = [str(w.message) for w in captured]
                    predicted = gaussian(x,*fit)
                    center = fit[2]
                    valid = (center <= 80) if kind == "control" else (0 <= center <= 50)
                    residual = np.sqrt(np.mean((values-predicted)**2))
                    span = np.ptp(values)
                    rmse_normalized = residual/span if span > 0 else np.nan
                except (RuntimeError, ValueError, FloatingPointError) as err:
                    fit = np.full(4,np.nan); cov = np.full((4,4),np.nan)
                    predicted = np.full(nx,np.nan); center, residual, rmse_normalized = np.nan,np.nan,np.nan
                    failed, valid = True, False
                    warning_messages = [str(err)]
                frame = {"frame_index": i+1, "time_s": finite(i*dt), "area_px": areas[i+1],
                         "centroid_px": [finite(v) for v in centroids[i+1]],
                         "boundary_pixels": edge_lengths[i], "observed": [finite(v) for v in values],
                         "gaussian_parameters": [finite(v) for v in fit],
                         "center_um": finite(center*dist), "center_valid": bool(valid),
                         "fit_failed": failed, "fit_warning": warning_messages,
                         "fit_rmse_intensity": finite(residual), "fit_nrmse": finite(rmse_normalized)}
                frames.append(frame)
            variant = {"erosion_radius_px": radius, "x_um": [finite(v*dist) for v in x], "frames": frames,
                       "common22": regress(frames,22), "author_window": regress(frames,n),
                       "author_center_filter": "center <= 80 unrolling bins" if kind == "control" else "0 <= center <= 50 unrolling bins"}
            movie["variants"].append(variant)
            print(kind, radius, variant["common22"], variant["author_window"], flush=True)
        payload["movies"].append(movie)
    (args.output / "secondary-data.json").write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False))
    summary = [{"movie": m["id"], "original_radius": m["original_erosion_radius_px"],
                "variants": [{"radius": v["erosion_radius_px"], "common22": v["common22"], "author_window": v["author_window"]} for v in m["variants"]]} for m in payload["movies"]]
    (args.output / "secondary-findings.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
