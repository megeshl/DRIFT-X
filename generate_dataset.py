"""
DRIFT-X synthetic image-pair generator.

Usage:
    python dataset_generator/generate_dataset.py \
        --architecture DRAM \
        --num-pairs 10 \
        --output-dir data/generated
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def build_pattern(size=1000, architecture="DRAM", rng=None):
    rng = rng or np.random.default_rng()
    image = np.zeros((size, size), dtype=np.uint8)

    # Simple deterministic semiconductor-like repeating structure.
    # This is a starting synthetic generator, not a claim of physical SEM fidelity.
    margin = 80
    spacing = 24 if architecture == "DRAM" else 30

    for x in range(margin, size - margin, spacing):
        thickness = int(rng.integers(2, 5))
        cv2.rectangle(image, (x, margin), (x + thickness, size - margin), 180, -1)

    for y in range(margin, size - margin, spacing * 2):
        cv2.line(image, (margin, y), (size - margin, y), 110, 2)

    # Add structured blocks to make local regions distinguishable.
    for _ in range(80):
        x = int(rng.integers(margin, size - margin - 20))
        y = int(rng.integers(margin, size - margin - 20))
        s = int(rng.integers(6, 18))
        cv2.rectangle(image, (x, y), (x+s, y+s), int(rng.integers(100, 230)), -1)

    return image


def rotate_scale(image, scale, angle):
    h, w = image.shape[:2]
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    center = (new_w / 2, new_h / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        resized,
        matrix,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )
    return rotated


def generate_pair(seed, architecture):
    rng = np.random.default_rng(seed)
    scene = build_pattern(1000, architecture, rng)

    # Target crop in high-magnification reference space.
    ref_size = 100
    x = int(rng.integers(150, 850 - ref_size))
    y = int(rng.integers(150, 850 - ref_size))
    reference = scene[y:y+ref_size, x:x+ref_size].copy()

    # Build a search image with controlled transformation.
    scale_ratio = float(rng.uniform(9.0, 11.0))
    angle = float(rng.uniform(-2.0, 2.0))

    # Place the target-sized transformed crop in a wider canvas.
    target = rotate_scale(reference, 1.0 / 10.0, angle)

    # Resize target to a practical search-space size while preserving
    # the 9:1–11:1 metadata relationship.
    target_side = max(16, int(round(ref_size / (scale_ratio / 10.0))))
    target = cv2.resize(target, (target_side, target_side), interpolation=cv2.INTER_LINEAR)

    search = np.zeros_like(scene)
    max_x = search.shape[1] - target_side - 1
    max_y = search.shape[0] - target_side - 1
    tx = int(rng.integers(50, max_x))
    ty = int(rng.integers(50, max_y))
    search[ty:ty+target_side, tx:tx+target_side] = target

    # Mild degradation.
    blur_sigma = float(rng.uniform(0.0, 1.2))
    if blur_sigma > 0:
        k = max(3, int(2 * round(3 * blur_sigma) + 1))
        search = cv2.GaussianBlur(search, (k, k), blur_sigma)

    noise_sigma = float(rng.uniform(2.0, 12.0))
    noise = rng.normal(0, noise_sigma, search.shape).astype(np.float32)
    search = np.clip(search.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    metadata = {
        "seed": seed,
        "architecture": architecture,
        "scale_ratio": scale_ratio,
        "rotation_degrees": angle,
        "target_x": tx + target_side / 2.0,
        "target_y": ty + target_side / 2.0,
        "noise_sigma": noise_sigma,
        "blur_sigma": blur_sigma,
        "reference_size": [ref_size, ref_size],
        "search_size": [1000, 1000],
    }
    return reference, search, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--architecture", choices=["DRAM", "FinFET"], required=True)
    parser.add_argument("--num-pairs", type=int, required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if args.num_pairs < 1:
        raise ValueError("--num-pairs must be >= 1")

    root = Path(args.output_dir)
    ref_dir = root / "reference"
    search_dir = root / "search"
    gt_dir = root / "ground_truth"
    ref_dir.mkdir(parents=True, exist_ok=True)
    search_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    for i in range(1, args.num_pairs + 1):
        reference, search, metadata = generate_pair(10000 + i, args.architecture)
        stem = f"pair_{i:04d}"

        cv2.imwrite(str(ref_dir / f"{stem}.png"), reference)
        cv2.imwrite(str(search_dir / f"{stem}.png"), search)

        with open(gt_dir / f"{stem}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    print(f"Generated {args.num_pairs} {args.architecture} image pairs in {root}")


if __name__ == "__main__":
    main()
