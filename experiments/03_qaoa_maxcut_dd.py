# experiments/03_qaoa_maxcut_dd.py
import os, json
import networkx as nx
import numpy as np
from math import pi
from qiskit import QuantumCircuit, transpile
from qiskit.passmanager import PassManager
from qiskit.transpiler import InstructionDurations
from qiskit.transpiler.passes import ALAPSchedule, ASAPSchedule
from qemt.backends.aer_utils import noisy_backend
from qemt.mitigation.dd import add_dd_pass
from qemt.metrics.observables import z_expectation
from qemt.utils.plotting import plot_bar

os.makedirs('experiments/results', exist_ok=True)

# 4-node ring graph (MaxCut)
G = nx.cycle_graph(4)
edges = list(G.edges())

def qaoa_circuit(gamma, beta):
    qc = QuantumCircuit(4, 4)
    # init |+>
    for q in range(4):
        qc.h(q)
    # problem unitary
    for (u,v) in edges:
        qc.cx(u,v)
        qc.rz(2*gamma, v)
        qc.cx(u,v)
    # mixer
    for q in range(4):
        qc.rx(2*beta, q)
    qc.measure(range(4), range(4))
    return qc

def cut_value(bits):
    assign = [int(b) for b in bits[::-1]]  # little endian
    return sum(1 for (u,v) in edges if assign[u] != assign[v])

def expected_cut(counts):
    shots = sum(counts.values()) or 1
    return sum(cut_value(b)*c for b,c in counts.items())/shots

backend = noisy_backend(p1=0.002, p2=0.02, readout_p=0.03)

# Grid search to find baseline best params
best = None
for gamma in np.linspace(0, pi, 6):
    for beta in np.linspace(0, pi/2, 6):
        qc = qaoa_circuit(gamma, beta)
        tc = transpile(qc, backend, optimization_level=1)
        res = backend.run(tc, shots=4096).result()
        val = expected_cut(res.get_counts())
        if best is None or val > best['value']:
            best = {"gamma": float(gamma), "beta": float(beta), "value": float(val)}

# Prepare DD pass and schedule with unit durations so Pass works on Aer
dd_pass = add_dd_pass(backend, sequence="XY4")
unit_durations = InstructionDurations()  # unit-time scheduling
pm = PassManager([ASAPSchedule(unit_durations), dd_pass])

qc_best = qaoa_circuit(best['gamma'], best['beta'])
tc_scheduled_dd = pm.run(transpile(qc_best, backend, optimization_level=1))
res_dd = backend.run(tc_scheduled_dd, shots=4096).result()
val_dd = expected_cut(res_dd.get_counts())

# Save + plot
artifact = {"grid_best": best, "with_dd": float(val_dd)}
with open('experiments/results/qaoa_maxcut_dd.json', 'w') as f:
    json.dump(artifact, f, indent=2)

plot_bar(['Baseline','With DD'], [best['value'], val_dd],
         'Setting','Expected cut','QAOA MaxCut: DD improvement',
         'experiments/results/qaoa_maxcut_dd.png')

print("Saved experiments/results/qaoa_maxcut_dd.json and qaoa_maxcut_dd.png")

