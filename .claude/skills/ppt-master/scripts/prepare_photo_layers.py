#!/usr/bin/env python3
"""PPT Master - Prepare editable photo reconstruction layers.

Apply a reviewed polygon to a crop, or prepare a photo crop and the matching
native PowerPoint caption geometry from a reviewed diagonal.

Usage:
    python prepare_photo_layers.py ALIGNED.png PLAN.json NEW_OUTPUT

Example:
    python prepare_photo_layers.py page.png photo-layers.json prepared

Dependencies:
    Pillow (already used by the photo overlay tool).
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from console_encoding import configure_utf8_stdio


def _integers(value: object, length: int, label: str) -> list[int]:
    if not isinstance(value, list) or len(value) != length or any(
        type(item) is not int for item in value
    ):
        raise ValueError(f"{label} must contain {length} integers")
    return value


def _check_box(box: list[int], size: tuple[int, int]) -> None:
    left, top, right, bottom = box
    if not (0 <= left < right <= size[0] and 0 <= top < bottom <= size[1]):
        raise ValueError("Crop is outside the aligned page")


def _mask(crop: Image.Image, points: list[tuple[int, int]], scale: int) -> Image.Image:
    mask = Image.new("L", (crop.width * scale, crop.height * scale))
    ImageDraw.Draw(mask).polygon([(x * scale, y * scale) for x, y in points], fill=255)
    if scale > 1:
        mask = mask.resize(crop.size, Image.Resampling.LANCZOS)
    result = crop.convert("RGBA")
    result.putalpha(ImageChops.multiply(result.getchannel("A"), mask))
    if result.getchannel("A").getextrema() in ((0, 0), (255, 255)):
        raise ValueError("Mask must preserve visible content and remove background")
    return result


def _caption(
    crop: Image.Image, box: list[int], spec: dict, page_size: tuple[int, int]
) -> tuple[Image.Image, dict]:
    left, top, right, bottom = box
    start_y, end_x = _integers(spec.get("diagonal"), 2, "diagonal")
    if not (top < start_y < bottom and right <= end_x <= page_size[0]):
        raise ValueError("Caption must run down from the crop's left side to its bottom")
    width, height = end_x - left, bottom - start_y
    # One pixel under the editable panel prevents a seam at the shared edge.
    crop_edge = min(crop.height, start_y - top + round(height * crop.width / width) + 1)
    points = [(0, 0), (crop.width, 0), (crop.width, crop_edge), (0, start_y - top + 1)]
    geometry = {
        "position_px": [left, start_y, width, height],
        "points_px": [[0, 0], [width, height], [0, height]],
        "closed": True,
    }
    return _mask(crop, points, 1), geometry


def prepare_layers(source: Image.Image, spec: dict) -> tuple[Image.Image, dict]:
    """Return one transparent picture layer and page-space placement metadata."""
    box = _integers(spec.get("crop"), 4, "crop")
    _check_box(box, source.size)
    if (box[2] - box[0]) * (box[3] - box[1]) > 4_000_000:
        raise ValueError("Crop exceeds four million pixels; use a tighter region")
    crop = source.crop(tuple(box))
    kind = spec.get("kind")
    metadata = {"kind": kind, "crop_px": box, "page_size_px": list(source.size)}
    if kind == "illustration":
        polygon = spec.get("keep")
        if not isinstance(polygon, list) or not 3 <= len(polygon) <= 512:
            raise ValueError("keep must contain 3 to 512 reviewed polygon points")
        points = [tuple(_integers(point, 2, "point")) for point in polygon]
        if any(not (0 <= x <= crop.width and 0 <= y <= crop.height) for x, y in points):
            raise ValueError("A polygon point is outside the crop")
        area = sum(x * v - y * u for (x, y), (u, v) in zip(points, points[1:] + points[:1]))
        if not area:
            raise ValueError("Polygon has no signed area")
        return _mask(crop, points, 2), metadata
    if kind == "caption":
        picture, geometry = _caption(crop, box, spec, source.size)
        metadata["native_caption"] = geometry
        return picture, metadata
    raise ValueError("kind must be illustration or caption")


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("aligned", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path, help="new private output directory")
    args = parser.parse_args(argv)
    try:
        source_bytes = args.aligned.read_bytes()
        plan_bytes = args.plan.read_bytes()
        spec = json.loads(plan_bytes)
        if not isinstance(spec, dict):
            raise ValueError("Plan must be a JSON object")
        with Image.open(BytesIO(source_bytes)) as source:
            if source.format != "PNG":
                raise ValueError("Use an aligned PNG in the reviewed page coordinate space")
            layer, metadata = prepare_layers(source, spec)
        args.output.mkdir(parents=True, exist_ok=False)
        picture = args.output / "picture.png"
        layer.save(picture)
        for name, color in (("light", "#F8F8F8"), ("dark", "#263238")):
            preview = Image.new("RGBA", layer.size, color)
            preview.alpha_composite(layer)
            preview.convert("RGB").save(args.output / f"preview-{name}.png")
        metadata.update(
            source_sha256=sha256(source_bytes).hexdigest(),
            plan_sha256=sha256(plan_bytes).hexdigest(),
            picture_sha256=sha256(picture.read_bytes()).hexdigest(),
        )
        (args.output / "layers.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        parser.exit(1, f"Photo layer preparation failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
