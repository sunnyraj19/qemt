# ---------- settings ----------
$ProjectPath = "C:\Users\raj45\Downloads\qemt_repo_v3"
$GithubUser  = "sunnyraj19"
$RepoName    = "qemt"
$Visibility  = "public"   # or "private"
$GitName     = "Sunny Raj"
$GitEmail    = "imh10018.21@bitmesra.ac.in"
# ------------------------------

Set-Location $ProjectPath

# Git identity (set globally so future repos also use this)
git config --global user.name  "$GitName"
git config --global user.email "$GitEmail"

# README.md
$Readme = @"
# QEMT — Quantum Error Mitigation Toolkit (Qiskit)

[![CI](https://github.com/$GithubUser/$RepoName/actions/workflows/ci.yml/badge.svg)](https://github.com/$GithubUser/$RepoName/actions)

A compact, research-oriented toolkit to implement and benchmark **error mitigation** on noisy quantum circuits using **Qiskit**.

## Features
- ZNE (Zero-Noise Extrapolation)  
- DD (Dynamical Decoupling) sequences  
- EMM (readout/measurement calibration)  
- CDR (Clifford Data Regression)  
- Benchmarks: Grover, VQE(H₂), QAOA(MaxCut)  
- CLI to run experiments; pytest + GitHub Actions CI

## Quickstart
```powershell
cd "$ProjectPath"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
pip install scipy
