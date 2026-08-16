"""Basic DRIFT-X evaluation runner."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = Path(args.data)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    rows = []
    refs = sorted((data / "reference").glob("*.png"))

    for ref in refs:
        stem = ref.stem
        search = data / "search" / f"{stem}.png"
        gt = data / "ground_truth" / f"{stem}.json"

        if not search.exists() or not gt.exists():
            continue

        result = subprocess.run(
            [
                sys.executable,
                "inference/localize.py",
                "--reference", str(ref),
                "--search", str(search),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        pred_x, pred_y = map(float, result.stdout.strip().split())
        truth = json.loads(gt.read_text(encoding="utf-8"))

        dx = pred_x - truth["target_x"]
        dy = pred_y - truth["target_y"]
        error = (dx * dx + dy * dy) ** 0.5

        rows.append({
            "sample_id": stem,
            "pred_x": pred_x,
            "pred_y": pred_y,
            "true_x": truth["target_x"],
            "true_y": truth["target_y"],
            "error_px": error,
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(output / "metrics.csv", index=False)

    if len(df):
        print("Samples:", len(df))
        print("Mean error:", df["error_px"].mean())
        print("Median error:", df["error_px"].median())
        print("5px pass:", (df["error_px"] <= 5).mean())
        print("4px pass:", (df["error_px"] <= 4).mean())
        print("2px pass:", (df["error_px"] <= 2).mean())
        print("1px pass:", (df["error_px"] <= 1).mean())
    else:
        print("No evaluable samples found.")


if __name__ == "__main__":
    main()
