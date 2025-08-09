
import os, json
import numpy as np
from math import pi
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from scipy.optimize import minimize

from qemt.backends.aer_utils import noisy_backend
from qemt.metrics.observables import z_expectation
from qemt.utils.plotting import plot_line

os.makedirs('experiments/results', exist_ok=True)

# H2 Hamiltonian terms (2-qubit) at ~0.735A
coeffs = {
    'I': -1.052373245772859,
    'Z0': 0.39793742484318045,
    'Z1': -0.39793742484318045,
    'Z0Z1': -0.01128010425623538,
    'X0X1': 0.18093119978423156,
    'Y0Y1': 0.18093119978423156
}

def ansatz(params):
    theta1, theta2 = params
    qc = QuantumCircuit(2, 2)
    qc.ry(theta1, 0)
    qc.ry(theta2, 1)
    qc.cx(0,1)
    return qc

def run_counts(qc, backend):
    tc = transpile(qc, backend, optimization_level=1)
    res = backend.run(tc, shots=8192).result()
    return res.get_counts()

def measure_term(qc_base, term, backend):
    qc = qc_base.copy()
    if term == 'Z0':
        qc.measure_all()
        return z_expectation(run_counts(qc, backend), [0])
    if term == 'Z1':
        qc.measure_all()
        return z_expectation(run_counts(qc, backend), [1])
    if term == 'Z0Z1':
        qc.measure_all()
        return z_expectation(run_counts(qc, backend), [0,1])
    if term == 'X0X1':
        rot = qc.copy(); rot.h(0); rot.h(1); rot.measure_all()
        return z_expectation(run_counts(rot, backend), [0,1])
    if term == 'Y0Y1':
        rot = qc.copy()
        rot.sdg(0); rot.h(0); rot.sdg(1); rot.h(1)
        rot.measure_all()
        return z_expectation(run_counts(rot, backend), [0,1])
    if term == 'I':
        return 1.0
    raise ValueError('Unknown term')

def energy(params, backend):
    base = ansatz(params)
    e = 0.0
    for t, c in coeffs.items():
        e += c * measure_term(base, t, backend)
    return e

def main():
    backend_noisy = noisy_backend(p1=0.002, p2=0.02, readout_p=0.03)
    backend_ideal = AerSimulator()

    history = {'x': [], 'f': []}

    def objective(x):
        val = energy(x, backend_noisy)
        history['x'].append([float(x[0]), float(x[1])])
        history['f'].append(float(val))
        return val

    x0 = np.array([0.7, 1.1])
    res = minimize(objective, x0, method='COBYLA', options={'maxiter': 40, 'rhobeg': 0.2})

    E_noisy_opt = float(energy(res.x, backend_noisy))
    E_ideal_opt = float(energy(res.x, backend_ideal))

    # Save results
    artifact = {'x_opt': res.x.tolist(), 'E_noisy_opt': E_noisy_opt, 'E_ideal_opt': E_ideal_opt, 'history': history}
    with open('experiments/results/vqe_h2_opt.json', 'w') as f:
        json.dump(artifact, f, indent=2)

    # Plot convergence
    plot_line(list(range(1, len(history['f'])+1)), history['f'],
              'Iteration', 'Energy (Ha)', 'VQE(H2) COBYLA convergence (noisy)',
              'experiments/results/vqe_h2_opt.png')

    print('Saved experiments/results/vqe_h2_opt.json and vqe_h2_opt.png')

if __name__ == '__main__':
    main()
