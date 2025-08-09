# experiments/01_grover_zne.py
import os, json
from qiskit import transpile
from qiskit_aer import AerSimulator

from qemt.circuits.grover import grover_2q
from qemt.backends.aer_utils import noisy_backend
from qemt.mitigation.zne import zne
from qemt.metrics.observables import z_expectation
from qemt.utils.plotting import plot_zne

os.makedirs('experiments/results', exist_ok=True)

# Build the base Grover circuit (the helper returns a measured circuit),
# then strip measurements so ZNE can fold the *unitary* part safely.
qc_measured = grover_2q()
qc_nom = qc_measured.remove_final_measurements(inplace=False)

# Backends
backend_noisy = noisy_backend(p1=0.002, p2=0.02, readout_p=0.03)
backend_ideal = AerSimulator()

def executor(circ, noiseless=False):
    """
    Takes a *measurement-free* circuit, appends measurements, runs it,
    and returns the observable <Z ⊗ Z> as a float.
    Ensures counts exist by always measuring & using explicit shots.
    """
    # 1) copy and add measurements
    run_circ = circ.copy()
    run_circ.measure_all()

    # 2) choose backend
    sim = backend_ideal if noiseless else backend_noisy

    # 3) transpile & execute
    tc = transpile(run_circ, sim, optimization_level=1)
    res = sim.run(tc, shots=4096).result()

    # 4) get counts for this (single) experiment explicitly by index 0
    counts = res.get_counts(0)

    # 5) compute <Z ⊗ Z> over both qubits (0,1)
    return z_expectation(counts, qubits=[0, 1])

# Run ZNE on the *measurement-free* circuit
out = zne(qc_nom, backend_noisy, executor, scale_factors=[1, 3, 5], fit="richardson")

# Save artifacts and plot
with open('experiments/results/grover_zne.json', 'w') as f:
    json.dump(out, f, indent=2)

plot_zne(out['scale_factors'], out['raw'], out['mitigated'], 'experiments/results/grover_zne.png')
print('Done. Results at experiments/results/grover_zne.*')

