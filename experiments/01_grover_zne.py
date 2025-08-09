import os, json
from qiskit import transpile
from qiskit_aer import AerSimulator
from qemt.circuits.grover import grover_2q
from qemt.backends.aer_utils import noisy_backend
from qemt.mitigation.zne import zne
from qemt.metrics.observables import z_expectation
from qemt.utils.plotting import plot_zne

os.makedirs('experiments/results', exist_ok=True)

qc = grover_2q()

backend = noisy_backend(p1=0.002, p2=0.02, readout_p=0.03)
sim_no_noise = AerSimulator()

def executor(circ, noiseless=False):
    sim = sim_no_noise if noiseless else backend
    tc = transpile(circ, sim, optimization_level=1)
    res = sim.run(tc, shots=4096).result()
    counts = res.get_counts()
    return z_expectation(counts, qubits=[0,1])

out = zne(qc.remove_final_measurements(inplace=False), backend, executor, scale_factors=[1,3,5], fit="richardson")

with open('experiments/results/grover_zne.json', 'w') as f:
    json.dump(out, f, indent=2)

plot_zne(out['scale_factors'], out['raw'], out['mitigated'], 'experiments/results/grover_zne.png')
print('Done. Results at experiments/results/grover_zne.*')

if __name__ == '__main__':
    pass
