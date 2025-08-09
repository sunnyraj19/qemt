# QEMT — Quantum Error Mitigation Toolkit (Qiskit)
![CI](https://github.com/sunnyraj19/qemt/actions/workflows/ci.yml/badge.svg)

A compact, research-oriented toolkit to implement and benchmark error-mitigation methods on noisy quantum circuits using Qiskit.

## Methods
- ZNE (Zero-Noise Extrapolation) with circuit folding + Richardson/poly fits
- EMM (Readout/measurement mitigation) — minimal helper for calibration
- DD (Dynamical decoupling) — XY4 / CPMG padding pass
- CDR (Clifford Data Regression) — minimal linear-regression variant

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python experiments/01_grover_zne.py
```
Outputs artifacts under `experiments/results/`.

