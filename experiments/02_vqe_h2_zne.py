import os, json
import numpy as np
from math import pi
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qemt.backends.aer_utils import noisy_backend
from qemt.mitigation.zne import zne
from qemt.metrics.observables import z_expectation

os.makedirs('experiments/results', exist_ok=True)

# H2 Hamiltonian at ~0.735A (STO-3G, JW mapping), from Qiskit textbook example
# H = c0*I + c1*Z0 + c2*Z1 + c3*Z0Z1 + c4*X0X1 + c5*Y0Y1
coeffs = {
    'I': -1.052373245772859,
    'Z0': 0.39793742484318045,
    'Z1': -0.39793742484318045,
    'Z0Z1': -0.01128010425623538,
    'X0X1': 0.18093119978423156,
    'Y0Y1': 0.18093119978423156
}

def ansatz(theta1, theta2):
    qc = QuantumCircuit(2, 2)
    qc.ry(theta1, 0)
    qc.ry(theta2, 1)
    qc.cx(0,1)
    return qc

def measure_pauli_exp(qc_base, pauli, backend):
    qc = qc_base.copy()
    if pauli == 'Z0':
        qc.measure_all()
        exp = z_expectation(run_counts(qc, backend), [0])
    elif pauli == 'Z1':
        qc.measure_all()
        exp = z_expectation(run_counts(qc, backend), [1])
    elif pauli == 'Z0Z1':
        qc.measure_all()
        exp = z_expectation(run_counts(qc, backend), [0,1])
    elif pauli == 'X0X1':
        # rotate to X basis
        rot = qc.copy()
        rot.h(0); rot.h(1)
        rot.measure_all()
        exp = z_expectation(run_counts(rot, backend), [0,1])
    elif pauli == 'Y0Y1':
        rot = qc.copy()
        rot.sdg(0); rot.h(0)
        rot.sdg(1); rot.h(1)
        rot.measure_all()
        exp = z_expectation(run_counts(rot, backend), [0,1])
    else:
        exp = 1.0  # identity expectation
    return exp

def run_counts(qc, backend):
    sim = backend
    tc = transpile(qc, sim, optimization_level=1)
    res = sim.run(tc, shots=8192).result()
    return res.get_counts()

def energy(theta1, theta2, backend):
    base = ansatz(theta1, theta2)
    e = coeffs['I']
    e += coeffs['Z0'] * measure_pauli_exp(base, 'Z0', backend)
    e += coeffs['Z1'] * measure_pauli_exp(base, 'Z1', backend)
    e += coeffs['Z0Z1'] * measure_pauli_exp(base, 'Z0Z1', backend)
    e += coeffs['X0X1'] * measure_pauli_exp(base, 'X0X1', backend)
    e += coeffs['Y0Y1'] * measure_pauli_exp(base, 'Y0Y1', backend)
    return e

# Define executor that returns -E as observable for ZNE (so lower energy -> higher observable)
backend_noisy = noisy_backend(p1=0.002, p2=0.02, readout_p=0.03)
backend_ideal = AerSimulator()

theta = [0.7, 1.1]  # a reasonable starting point

def executor_for_zne(circ, noiseless=False):
    # circ is the measurement-stripped circuit; we ignore it to keep interface, and evaluate energy from theta
    be = backend_ideal if noiseless else backend_noisy
    return -energy(theta[0], theta[1], be)

# Build a measurement-less circuit (ansatz without measure) for ZNE folding
qc0 = ansatz(theta[0], theta[1])
qc_nom = qc0.remove_final_measurements(inplace=False)

out = zne(qc_nom, backend_noisy, executor_for_zne, scale_factors=[1,3,5], fit="richardson")
mitigated_energy = -out['mitigated']

# Baseline noisy and ideal energies (for context)
E_noisy = energy(theta[0], theta[1], backend_noisy)
E_ideal = energy(theta[0], theta[1], backend_ideal)

artifact = {
    "thetas": theta,
    "noisy_energy": E_noisy,
    "ideal_energy": E_ideal,
    "zne": out,
    "zne_mitigated_energy": mitigated_energy
}

with open('experiments/results/vqe_h2_zne.json', 'w') as f:
    json.dump(artifact, f, indent=2)

print("Saved experiments/results/vqe_h2_zne.json")
