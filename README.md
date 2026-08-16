DRIFT-X

Scale-Aware Visual Localization for Wafer Inspection

SEMICON India Hackathon 2026 — Applied Materials Track: Drift-Sense

When semiconductor patterns repeat, similarity is not enough.

DRIFT-X is a software-first computer-vision prototype for recovering the location of a high-magnification semiconductor inspection pattern inside a wider search image.

The repository is intentionally split into two layers:

Competition-critical Python layer — standalone dataset generation and localization inference.

Optional full-stack demonstration layer — React/Node interface that can be connected to the same Python engine.

The most important submission artifact is:

inference/localize.py

It is designed to accept a reference image path and a search image path and print a machine-readable (x, y) coordinate.

1. Problem

The Applied Materials Drift-Sense challenge focuses on recovering navigation coordinates from cross-magnification inspection imagery.

The target workflow is:

100× Reference Image
        +
10× Search Image
        ↓
DRIFT-X
        ↓
Predicted Target Centre
        ↓
(x, y)

The challenge introduces difficult conditions such as:

approximately 10:1 magnification difference

scale variation around the nominal relationship

small rotation variation

image noise and blur

repetitive semiconductor structures

multiple visually similar candidate locations

The final system should therefore avoid relying on a single fixed-scale template match.

2. DRIFT-X Approach

DRIFT-X is designed around a coarse-to-fine, multi-hypothesis localization pipeline:

Reference Image
       ↓
Preprocessing
       ↓
Structural Representation
       ↓
Multi-Scale Candidate Search
       ↓
Top-K Candidate Generation
       ↓
Geometric Verification
       ↓
Fine Scale / Rotation Refinement
       ↓
Evidence-Based Candidate Ranking
       ↓
Confidence
       ↓
(x, y)

Core principle

Search broadly → verify geometrically → refine precisely → select confidently.

Instead of immediately accepting the highest raw similarity score, the intended final engine evaluates several candidate locations using structural and geometric evidence.

3. Repository Structure

DRIFT-X/
│
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── inference/
│   ├── localize.py
│   ├── config.yaml
│   └── README.md
│
├── dataset_generator/
│   ├── generate_dataset.py
│   ├── config.yaml
│   └── README.md
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── features.py
│   ├── scale_search.py
│   ├── candidate_generation.py
│   ├── geometric_verification.py
│   ├── refinement.py
│   ├── ranking.py
│   ├── confidence.py
│   ├── metrics.py
│   └── utils.py
│
├── sample_data/
│   ├── reference/
│   ├── search/
│   └── ground_truth/
│
├── results/
│   └── visualizations/
│
├── evaluation/
│   ├── evaluate.py
│   ├── baseline.py
│   └── README.md
│
├── references/
│   ├── REFERENCES.md
│   └── methodology.md
│
├── docs/
│   ├── architecture.md
│   └── failure_analysis.md
│
└── app/
    ├── frontend/
    └── backend/

4. Competition-Critical Files

inference/localize.py

This is the most important file in the repository.

Applied Materials must be able to run the localization algorithm directly without editing source code.

Expected interface:

python inference/localize.py \
  --reference path/to/reference.png \
  --search path/to/search.png

Expected machine-readable output:

523.42 487.16

The two numbers represent:

x y

with the origin convention defined by the challenge.

Important

The full-stack application is not required to run the competition inference.

The Python inference script must remain independently executable.

5. Dataset Generator

dataset_generator/generate_dataset.py

The generator creates synthetic reference/search image pairs and records ground truth.

Basic command

python dataset_generator/generate_dataset.py \
  --architecture DRAM \
  --num-pairs 10 \
  --output-dir data/generated

Architecture options

DRAM
FinFET

Parameters

Parameter

Description

--architecture

Semiconductor architecture style

--num-pairs

Number of image pairs

--output-dir

Destination directory

Generated structure

data/generated/
│
├── reference/
│   ├── pair_0001.png
│   ├── pair_0002.png
│   └── ...
│
├── search/
│   ├── pair_0001.png
│   ├── pair_0002.png
│   └── ...
│
└── ground_truth/
    ├── pair_0001.json
    ├── pair_0002.json
    └── ...

Each ground-truth JSON records information such as:

{
  "seed": 10001,
  "architecture": "DRAM",
  "scale_ratio": 10.27,
  "rotation_degrees": 1.12,
  "target_x": 513.5,
  "target_y": 487.5,
  "noise_sigma": 7.2,
  "blur_sigma": 0.6
}

6. Installation

Requirements

Recommended environment:

Python 3.11+

pip

OpenCV-compatible system

Git

The current prototype uses:

NumPy

OpenCV

SciPy

scikit-image

Pandas

Matplotlib

PyYAML

Clone

git clone <YOUR_PUBLIC_GITHUB_URL>
cd DRIFT-X

Create virtual environment

Windows

python -m venv .venv
.venv\Scripts\activate

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate

Install dependencies

pip install -r requirements.txt

7. Generate a Sample Pair

Generate one DRAM pair:

python dataset_generator/generate_dataset.py \
  --architecture DRAM \
  --num-pairs 1 \
  --output-dir sample_data/generated

The command creates:

sample_data/generated/
├── reference/
├── search/
└── ground_truth/

8. Run Localization

Run the standalone inference script:

python inference/localize.py \
  --reference sample_data/generated/reference/pair_0001.png \
  --search sample_data/generated/search/pair_0001.png

Example output:

523.42 487.16

This means:

Predicted X = 523.42
Predicted Y = 487.16

The output is deliberately kept simple so that an external evaluator can parse it automatically.

9. Evaluate a Dataset

Run:

python evaluation/evaluate.py \
  --data sample_data/generated \
  --output results/metrics

The evaluation runner calculates:

sample count

localization error

mean error

median error

5-pixel pass rate

4-pixel pass rate

2-pixel pass rate

1-pixel pass rate

Results are written to:

results/metrics/metrics.csv

10. Localization Error

For a predicted coordinate:

(x_pred, y_pred)

and ground-truth coordinate:

(x_true, y_true)

the Euclidean localization error is:

error =
sqrt(
    (x_pred - x_true)^2 +
    (y_pred - y_true)^2
)

Threshold pass rates are calculated as:

≤ 5 pixels
≤ 4 pixels
≤ 2 pixels
≤ 1 pixel

11. Baseline

The repository reserves:

evaluation/baseline.py

for a simple fixed-scale template-matching baseline.

The purpose is to compare:

Baseline
   VS
DRIFT-X

The final submission should report real measurements rather than manually entered performance claims.

12. Source Code Architecture

The reusable computer-vision modules are located under:

src/

preprocessing.py

Image loading and preprocessing.

features.py

Structural, edge and gradient representations.

scale_search.py

Multi-scale candidate search.

candidate_generation.py

Top-K candidate extraction and duplicate suppression.

geometric_verification.py

Candidate geometry consistency checks.

refinement.py

Fine coordinate, scale and rotation refinement.

ranking.py

Evidence-based candidate ranking.

confidence.py

Confidence estimation.

metrics.py

Localization metrics.

utils.py

Shared utilities.

13. Synthetic Data Methodology

The generator is designed to create semiconductor-like repetitive structures with controlled transformations.

The intended augmentation space includes:

Base Structure
      ↓
Geometry Variation
      ↓
Scale Variation
      ↓
Rotation
      ↓
Blur
      ↓
Noise
      ↓
Contrast Variation
      ↓
Target Placement
      ↓
Ground Truth

Every generated sample should remain reproducible through its stored random seed and transformation metadata.

For the final competition version, every augmentation choice should be backed by the references listed in:

references/REFERENCES.md

and documented in:

references/methodology.md

14. Full-Stack Demonstration Layer

The folder:

app/

is reserved for the optional full-stack demonstration.

Recommended architecture:

React / Vite
      ↓
Node.js / Express API
      ↓
Python DRIFT-X Engine
      ↓
Prediction JSON
      ↓
Frontend Visualization

The full-stack layer should demonstrate:

image upload

localization execution

predicted coordinate

confidence

scale

rotation

runtime

top-K candidates

localization visualization

experiment history

evaluation dashboard

failure analysis

Important

The competition inference script must not depend on the frontend.

15. Recommended Full-Stack API

When the optional application is implemented, the backend can expose:

Health

GET /api/health

Localization

POST /api/localize

with:

reference
search

Experiments

GET /api/experiments

Evaluation

POST /api/evaluate

The Node backend should invoke the Python engine safely and return the real result.

16. Expected Localization Response

The full-stack layer can expose:

{
  "success": true,
  "prediction": {
    "x": 523.42,
    "y": 487.16,
    "confidence": 0.947,
    "scale": 10.24,
    "rotation": 0.82,
    "runtime_ms": 182
  },
  "candidates": []
}

These values must come from the actual inference engine.

17. Results and Visualization

The results/ directory is intended for generated artifacts:

results/
├── metrics/
├── predictions/
├── failures/
└── visualizations/

Recommended visual output:

Search Image
      │
      ├── Ground Truth ●
      ├── Prediction   ×
      └── Error Vector

The final prototype should make localization errors visually inspectable.

18. Failure Analysis

Failure cases should be saved under:

results/failures/

Recommended failure categories:

repeated-pattern ambiguity

scale mismatch

high noise

high blur

low structural confidence

edge-position failure

candidate-ranking failure

Each failure case should include:

Reference
Search Image
Ground Truth
Prediction
Error
Top-K Candidates
Transformation Metadata

19. Reproducibility

The project is designed around reproducible experiments.

Every generated sample should record:

Random Seed
Architecture
Scale
Rotation
Noise
Blur
Target X
Target Y

A fresh machine should be able to reproduce the same dataset when the same configuration and seed are supplied.

20. Clean-Machine Verification

Before submission, perform a clean test.

Step 1

Clone the repository into a new directory.

Step 2

Create a new virtual environment.

Step 3

Install:

pip install -r requirements.txt

Step 4

Generate data:

python dataset_generator/generate_dataset.py \
  --architecture DRAM \
  --num-pairs 1 \
  --output-dir test_data

Step 5

Run inference:

python inference/localize.py \
  --reference test_data/reference/pair_0001.png \
  --search test_data/search/pair_0001.png

Step 6

Verify that exactly two coordinate values are printed.

Step 7

Run evaluation:

python evaluation/evaluate.py \
  --data test_data \
  --output test_results

If this sequence works on a fresh machine, the repository is much safer for external evaluation.

21. No Hard-Coded Results

Never hard-code competition metrics or predictions.

Do not commit fake values such as:

94.7%
523.42
487.16
182 ms

unless those values were actually generated by the current implementation.

All final PPT numbers must come from:

results/metrics/

22. Development Status

Current repository scaffold

The repository contains:

standalone inference entry point

synthetic dataset generator

evaluation runner

reusable CV module structure

reference documentation structure

optional application structure

Final competition hardening required

Before submission, validate and replace any baseline/scaffold components with the final tested implementation of:

multi-scale search

top-K candidate generation

geometric verification

fine refinement

evidence-based ranking

confidence estimation

realistic semiconductor synthetic generation

failure analysis

baseline comparison

Do not claim these features are complete until they have been implemented and experimentally validated.

23. Submission Checklist

Before publishing the public repository:

[ ] README.md complete
[ ] Public GitHub repository
[ ] requirements.txt complete
[ ] inference/localize.py works independently
[ ] dataset_generator/generate_dataset.py works independently
[ ] DRAM generation tested
[ ] FinFET generation tested
[ ] Ground truth recorded
[ ] Localization tested on fresh samples
[ ] 5-pixel metric calculated
[ ] 4-pixel metric calculated
[ ] 2-pixel metric calculated
[ ] 1-pixel metric calculated
[ ] Mean error calculated
[ ] Median error calculated
[ ] Worst-case error calculated
[ ] Runtime measured
[ ] Failure cases documented
[ ] References added
[ ] PPT citations match repository references
[ ] Clean-machine test completed
[ ] No fake metrics
[ ] No hard-coded predictions
[ ] No manual source-code edits required

24. Competition-Critical Command Summary

Install

pip install -r requirements.txt

Generate DRAM dataset

python dataset_generator/generate_dataset.py \
  --architecture DRAM \
  --num-pairs 10 \
  --output-dir data/generated

Generate FinFET dataset

python dataset_generator/generate_dataset.py \
  --architecture FinFET \
  --num-pairs 10 \
  --output-dir data/generated_finFET

Run inference

python inference/localize.py \
  --reference data/generated/reference/pair_0001.png \
  --search data/generated/search/pair_0001.png

Evaluate

python evaluation/evaluate.py \
  --data data/generated \
  --output results/metrics

25. Final Architecture

                    DRIFT-X
                       │
          ┌────────────┴────────────┐
          │                         │
    DATA GENERATION             INFERENCE
          │                         │
    DRAM / FinFET             Reference + Search
          │                         │
    Transformations            Preprocessing
          │                         │
    Ground Truth               Multi-Scale Search
          │                         │
          │                    Top-K Candidates
          │                         │
          │                   Geometric Verification
          │                         │
          │                     Refinement
          │                         │
          └──────────────┬──────────┘
                         │
                    Evaluation
                         │
              ┌──────────┼──────────┐
              │          │          │
           Accuracy    Error     Runtime
              │          │          │
              └──────────┼──────────┘
                         │
                    Full-Stack Demo
                         │
                    React + Node

26. Vision

DRIFT-X aims to turn cross-magnification semiconductor image matching into a robust, measurable and explainable localization process.

The long-term direction is:

Synthetic Validation
        ↓
Robust Localization
        ↓
Sub-Pixel Refinement
        ↓
GPU Acceleration
        ↓
Real-Time Inspection
        ↓
Industrial Integration

27. Team

Project: DRIFT-X
Track: Applied Materials — Drift-Sense
Event: SEMICON India Hackathon 2026
Institution: Sri Sairam Engineering College
Domain: Computer Vision / AI / Semiconductor Inspection

Final Message

DRIFT-X

Precise. Robust. Explainable.

When semiconductor patterns repeat, similarity is not enough.
