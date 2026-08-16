"""
DRIFT-X standalone localization entry point.

Usage:
    python inference/localize.py --reference path/to/reference.png --search path/to/search.png

Outputs:
    x y

This file is intentionally the competition-facing entry point.
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np


def load_gray(path: str) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {path}")
    return image


def localize(reference: np.ndarray, search: np.ndarray):
    """
    Baseline, deterministic localization implementation.

    NOTE:
    Replace/extend this function with the validated DRIFT-X
    multi-scale + geometric verification engine before submission.
    """
    # Competition-friendly baseline: search a range of resized
    # reference templates and keep the strongest normalized correlation.
    best = None

    # A practical starting range around the nominal 10:1 relationship.
    # The generated search image should be compatible with the reference
    # after the appropriate scale transformation.
    for scale in np.linspace(0.85, 1.15, 13):
        h = max(8, int(reference.shape[0] * scale))
        w = max(8, int(reference.shape[1] * scale))
        if h > search.shape[0] or w > search.shape[1]:
            continue

        template = cv2.resize(reference, (w, h), interpolation=cv2.INTER_AREA)
        result = cv2.matchTemplate(search, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(result)

        cx = loc[0] + w / 2.0
        cy = loc[1] + h / 2.0

        candidate = (float(score), float(cx), float(cy))
        if best is None or candidate[0] > best[0]:
            best = candidate

    if best is None:
        raise RuntimeError("No valid localization candidate was generated.")

    return best[1], best[2]


def main():
    parser = argparse.ArgumentParser(description="DRIFT-X wafer localization inference")
    parser.add_argument("--reference", required=True, help="Path to reference image")
    parser.add_argument("--search", required=True, help="Path to search image")
    args = parser.parse_args()

    reference = load_gray(args.reference)
    search = load_gray(args.search)

    x, y = localize(reference, search)

    # Keep stdout machine-readable for evaluator integration.
    print(f"{x:.2f} {y:.2f}")


if __name__ == "__main__":
    main()
