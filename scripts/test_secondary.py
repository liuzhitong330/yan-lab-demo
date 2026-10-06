#!/usr/bin/env python3
"""Independent arithmetic and structural checks of secondary-data.json."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def close(a, b, tolerance=1e-5):
    assert abs(a-b) <= tolerance, (a, b, tolerance)


def scalar_ols(frames):
    xs = [f["time_s"] for f in frames]
    ys = [f["center_um"] for f in frames]
    xbar, ybar = sum(xs)/len(xs), sum(ys)/len(ys)
    numerator = sum((x-xbar)*(y-ybar) for x, y in zip(xs, ys))
    xvariance = sum((x-xbar)**2 for x in xs)
    yvariance = sum((y-ybar)**2 for y in ys)
    slope = numerator/xvariance
    return slope*1000, ybar-slope*xbar, numerator**2/(xvariance*yvariance)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "package/secondary-data.json")
    args = parser.parse_args()
    raw = args.data.read_bytes()
    data = json.loads(raw)
    assert len(data["movies"]) == 2
    factor = (math.sqrt(.02)+.1)/2
    frame_checks = regression_checks = profile_checks = 0
    warnings = []
    failures = []
    for movie in data["movies"]:
        assert movie["id"] in ("control", "protrusion")
        n = 60 if movie["id"] == "control" else 22
        assert movie["source_frames"] == 71 and movie["author_fit_frames"] == n
        assert [v["erosion_radius_px"] for v in movie["variants"]] == [1, 2, 3]
        for variant in movie["variants"]:
            assert len(variant["frames"]) == n
            nx = len(variant["x_um"])
            # Match the exact author coordinate expression, including floor(-nx/2).
            start, end = (-nx)//2, nx//2
            x = [start+(end-start)*j/(nx-1) for j in range(nx)]
            for i, frame in enumerate(variant["frames"]):
                assert frame["frame_index"] == i+1
                close(frame["time_s"], i*movie["frame_interval_s"], 1e-7)
                assert frame["area_px"] > 0 and frame["boundary_pixels"] > 0
                assert len(frame["observed"]) == nx
                frame_checks += 1
                profile_checks += nx
                if frame["fit_failed"]:
                    assert not frame["center_valid"] and frame["center_um"] is None
                    assert all(p is None for p in frame["gaussian_parameters"])
                    failures.append([movie["id"], variant["erosion_radius_px"], frame["frame_index"], frame["fit_warning"]])
                    continue
                amplitude, width, center, offset = frame["gaussian_parameters"]
                close(frame["center_um"], center*factor, 1e-7)
                expected_valid = center <= 80 if movie["id"] == "control" else 0 <= center <= 50
                assert frame["center_valid"] == expected_valid
                for stored, original in zip(variant["x_um"], x):
                    close(stored, original*factor, 1e-7)
                predicted = [amplitude*math.exp(-(value-center)**2/(2*width**2))+offset for value in x]
                errors = [(o-p)**2 for o, p in zip(frame["observed"], predicted)]
                residual = math.sqrt(sum(errors)/len(errors))
                close(residual, frame["fit_rmse_intensity"], 1e-4)
                close(residual/(max(frame["observed"])-min(frame["observed"])), frame["fit_nrmse"], 1e-7)
                if frame["fit_warning"]:
                    warnings.append([movie["id"], variant["erosion_radius_px"], frame["frame_index"], frame["fit_warning"]])
            for label, limit in [("common22", 22), ("author_window", n)]:
                valid = [f for f in variant["frames"][:limit] if f["center_valid"]]
                summary = variant[label]
                assert summary["n_frames"] == len(valid)
                slope, intercept, r_squared = scalar_ols(valid)
                close(slope, summary["slope_nm_s"])
                close(intercept, summary["intercept_um"])
                close(r_squared, summary["r_squared"])
                regression_checks += 1
    report = {"status": "passed", "data_sha256": hashlib.sha256(raw).hexdigest(),
              "movies_checked": 2, "radius_variants_checked": 6,
              "per_frame_checks": frame_checks, "intensity_profile_values_checked": profile_checks,
              "independent_OLS_checks": regression_checks,
              "fit_warning_records": warnings, "nonconvergent_fit_records": failures,
              "scope": "Independent scalar OLS, coordinate and Gaussian-residual arithmetic; structure and source metadata checks. This does not establish biological validity or independence."}
    output = args.data.parent / "secondary-qa.json"
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
