#!/usr/bin/env python3
"""Align a photographed page and compare it with its final slide render.

Usage: python review_photo_overlay.py PHOTO RENDER OUTPUT --corners X,Y X,Y X,Y X,Y
Corners are top-left, top-right, bottom-right, bottom-left after EXIF rotation.
Dependencies: Pillow, already used by the dense PPTX checker.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


def parse_corner(value: str) -> tuple[float, float]:
    try:
        x, y = map(float, value.split(","))
        if math.isfinite(x) and math.isfinite(y):
            return x, y
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("Enter each corner as a finite X,Y pair")


def align_photo(photo: Image.Image, size: tuple[int, int], corners: list[tuple[float, float]]) -> Image.Image:
    for x, y in corners:
        if not (0 <= x <= photo.width and 0 <= y <= photo.height):
            raise ValueError("A corner is outside the oriented photo")
    edges = [(b[0] - a[0], b[1] - a[1]) for a, b in zip(corners, corners[1:] + corners[:1])]
    if any(ax * by - ay * bx <= 0 for (ax, ay), (bx, by) in zip(edges, edges[1:] + edges[:1])):
        raise ValueError("Use a convex page in clockwise order, starting at top-left")

    # Map the unit square to the source quadrilateral. Pillow samples the source
    # with this inverse map, scaled from unit coordinates to output pixels.
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = corners
    dx1, dy1 = x1 - x2, y1 - y2
    dx2, dy2 = x3 - x2, y3 - y2
    sx, sy = x0 - x1 + x2 - x3, y0 - y1 + y2 - y3
    det = dx1 * dy2 - dx2 * dy1
    if math.isclose(det, 0, abs_tol=1e-8):
        raise ValueError("Photo corners are too close to a straight line")
    g = (sx * dy2 - dx2 * sy) / det
    h = (dx1 * sy - sx * dy1) / det
    width, height = size
    transform = (
        (x1 - x0 + g * x1) / width, (x3 - x0 + h * x3) / height, x0,
        (y1 - y0 + g * y1) / width, (y3 - y0 + h * y3) / height, y0,
        g / width, h / height,
    )
    return photo.transform(size, Image.Transform.PERSPECTIVE, transform, Image.Resampling.BICUBIC)


def edge_ink(image: Image.Image) -> Image.Image:
    edges = image.convert("L").filter(ImageFilter.GaussianBlur(0.7)).filter(ImageFilter.FIND_EDGES)
    ink = edges.point(lambda value: 255 - min(255, max(0, value - 14) * 5))
    ImageDraw.Draw(ink).rectangle((0, 0, ink.width - 1, ink.height - 1), outline=255)
    return ink


def review_images(aligned: Image.Image, render: Image.Image) -> dict[str, Image.Image]:
    source_ink, render_ink = edge_ink(aligned), edge_ink(render)
    shared = ImageChops.lighter(source_ink, render_ink)
    boundaries = Image.merge("RGB", (
        ImageChops.multiply(render_ink, shared),
        ImageChops.multiply(source_ink, shared),
        ImageChops.multiply(source_ink, shared),
    ))
    return {
        "aligned-photo.png": aligned,
        "overlay.png": Image.blend(aligned, render, 0.5),
        "boundaries.png": boundaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photo", type=Path)
    parser.add_argument("render", type=Path, help="PNG from the exact final PPTX")
    parser.add_argument("output", type=Path, help="new review directory")
    parser.add_argument("--corners", nargs=4, type=parse_corner, required=True)
    args = parser.parse_args()
    try:
        source_bytes, render_bytes = args.photo.read_bytes(), args.render.read_bytes()
        with Image.open(BytesIO(source_bytes)) as source, Image.open(BytesIO(render_bytes)) as raster:
            photo = ImageOps.exif_transpose(source).convert("RGB")
            if raster.format != "PNG" or min(raster.size) < 3:
                raise ValueError("Use a complete slide render in PNG format")
            rgba = raster.convert("RGBA")
            render = Image.alpha_composite(Image.new("RGBA", rgba.size, "white"), rgba).convert("RGB")
        aligned = align_photo(photo, render.size, args.corners)
        images = review_images(aligned, render)
        args.output.mkdir(parents=True, exist_ok=False)
        hashes = {}
        for name, image in images.items():
            path = args.output / name
            image.save(path)
            hashes[name] = sha256(path.read_bytes()).hexdigest()
        receipt = {
            "photo_sha256": sha256(source_bytes).hexdigest(),
            "render_sha256": sha256(render_bytes).hexdigest(),
            "oriented_photo_size_px": photo.size,
            "render_size_px": render.size,
            "photo_corners_px": args.corners,
            "images_sha256": hashes,
            "boundary_legend": {"red": "source photo", "cyan": "slide render", "dark": "shared edges"},
            "scope": "visual review aid; lighting and photographic detail can produce differences",
        }
        (args.output / "review.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        parser.exit(1, f"Photo overlay failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
