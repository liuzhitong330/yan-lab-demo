#!/usr/bin/env python3
"""Export numeric traces and small scientific SVGs, without changing source images."""
import argparse
import csv
import html
import json
import math
from pathlib import Path

COLORS = ["#263e55", "#607482", "#9f684f"]


def chart(destination, title, subtitle, series, xlabel, ylabel):
    points = [p for s in series for p in s["points"]]
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    margin = max((ymax-ymin)*.08, .01)
    ymin, ymax = ymin-margin, ymax+margin
    left, top, width, height = 80, 96, 570, 235
    sx = lambda x: left+(x-xmin)/(xmax-xmin)*width
    sy = lambda y: top+height-(y-ymin)/(ymax-ymin)*height
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="430" viewBox="0 0 720 430">',
             '<rect width="720" height="430" fill="#faf9f6"/>',
             '<g font-family="Arial, sans-serif" fill="#232a2e">',
             f'<text x="28" y="29" font-size="19">{html.escape(title)}</text>',
             f'<text x="28" y="52" font-size="11">{html.escape(subtitle)}</text>']
    for j in range(5):
        y = ymin+(ymax-ymin)*j/4
        lines.extend([f'<line x1="{left}" y1="{sy(y):.2f}" x2="{left+width}" y2="{sy(y):.2f}" stroke="#deded8"/>',
                      f'<text x="{left-9}" y="{sy(y)+4:.2f}" text-anchor="end" font-size="11">{y:.2f}</text>'])
    for j in range(6):
        x = xmin+(xmax-xmin)*j/5
        lines.append(f'<text x="{sx(x):.2f}" y="{top+height+21}" text-anchor="middle" font-size="11">{x:.1f}</text>')
    for si, s in enumerate(series):
        color = COLORS[si % len(COLORS)]
        if s.get("connect"):
            pointstring = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in s["points"])
            lines.append(f'<polyline points="{pointstring}" fill="none" stroke="{color}" stroke-width="1.5"/>')
        else:
            for x, y in s["points"]:
                lines.append(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="2.4" fill="{color}"/>')
        lx = 80+si*194
        lines.append(f'<circle cx="{lx}" cy="78" r="3" fill="{color}"/><text x="{lx+8}" y="82" font-size="11">{html.escape(s["name"])}</text>')
    lines.extend([f'<text x="365" y="385" text-anchor="middle" font-size="12">{html.escape(xlabel)}</text>',
                  f'<text x="20" y="214" transform="rotate(-90 20 214)" text-anchor="middle" font-size="12">{html.escape(ylabel)}</text>',
                  '<text x="28" y="414" font-size="10">Source: De Belly, Yan et al., Cell 2023 · Example-data analysis; not force calibration.</text>',
                  '</g></svg>'])
    destination.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "package/secondary-data.json")
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    output = args.data.parent
    columns = ["movie", "erosion_radius_px", "source_frame_index", "time_s", "center_um",
               "displacement_from_first_retained_um", "author_center_filter_retained", "fit_failed", "fit_warning",
               "fit_rmse_intensity", "fit_nrmse", "area_px", "boundary_pixels"]
    with (output / "secondary-traces.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for movie in data["movies"]:
            displacement_series = []
            for variant in movie["variants"]:
                frames = variant["frames"]
                retained = [f for f in frames if f["center_valid"]]
                origin = retained[0]["center_um"]
                displacement_series.append({"name": f'radius {variant["erosion_radius_px"]} px',
                    "points": [(f["time_s"], f["center_um"]-origin) for f in frames[:22] if f["center_valid"]]})
                for f in frames:
                    writer.writerow({"movie": movie["id"], "erosion_radius_px": variant["erosion_radius_px"],
                        "source_frame_index": f["frame_index"], "time_s": f["time_s"], "center_um": f["center_um"],
                        "displacement_from_first_retained_um": f["center_um"]-origin if f["center_um"] is not None else None,
                        "author_center_filter_retained": f["center_valid"], "fit_failed": f["fit_failed"],
                        "fit_warning": " | ".join(f["fit_warning"]), "fit_rmse_intensity": f["fit_rmse_intensity"],
                        "fit_nrmse": f["fit_nrmse"], "area_px": f["area_px"], "boundary_pixels": f["boundary_pixels"]})
            chart(output / f'{movie["id"]}-segmentation-sensitivity.svg', movie["label"]+": segmentation sensitivity",
                  "First 22 analyzed frames; points retained by author center filter; each radius has its own baseline.",
                  displacement_series, "Time from analyzed movie start (s)", "Approximate marker displacement (µm)")
            original = next(v for v in movie["variants"] if v["erosion_radius_px"] == movie["original_erosion_radius_px"])
            profiles = []
            for index in [1, 11, 21]:
                frame = original["frames"][index]
                profiles.append({"name": f'{frame["time_s"]:.1f} s, source frame {frame["frame_index"]}',
                                 "points": list(zip(original["x_um"], frame["observed"])), "connect": True})
            chart(output / f'{movie["id"]}-intensity-profiles.svg', movie["label"]+": measured membrane signal",
                  f'Original erosion radius {movie["original_erosion_radius_px"]} px; unnormalized CellMask intensity; no fitted-force scale.',
                  profiles, "Published approximate unrolled coordinate (µm)", "CellMask intensity (arbitrary units)")
    print("Exported 246 per-frame numeric records and four analytical SVG trace figures.")


if __name__ == "__main__":
    main()
