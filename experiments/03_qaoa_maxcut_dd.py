# experiments/03_qaoa_maxcut_dd.py
import os, json
import networkx as nx
import numpy as np
from math import pi
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager, InstructionDurations
from qemt.backends.aer_utils import noisy_backend
from qemt.mitigation.dd import add_dd_pass
from qemt.utils.plotting import plot_bar

# Try to import ALAPSchedule across Qiskit versions
ALAPSchedule = None
try:
    from qiskit.transpiler.passes.scheduling import ALAPSchedule  # newer
except Exception:
    try:
        from qiskit.transpiler.passes import ALAPSchedule  # older
    except Exception:
        ALAPSchedule = None

os.makedirs('experiments/results', exist_ok=True)

# 4-node ring graph (MaxCut)
G = nx.cycle_graph(4)
edges = list(G.edges())

def qaoa_circuit(gamma, beta):
    qc = QuantumCircuit(4, 4)
    # init |+>
    for q in range(4):
        qc.h(q)
    # problem unitary (p=1)
    for (u, v) in edges:
        qc.cx(u, v)
        qc.rz(2 * gamma, v)
        qc.cx(u, v)
    # mixer
    for q in range(4):
        qc.rx(2 * beta, q)
    qc.measure(range(4), range(4))
    return qc

def cut_value(bits):
    assign = [int(b) for b in bits[::-1]]  # little endian
    return sum(1 for (u, v) in edges if assign[u] != assign[v])

def expected_cut(counts):
    shots = sum(counts.values()) or 1
    return sum(cut_value(b) * c for b, c in counts.items()) / shots

backend = noisy_backend(p1=0.002, p2=0.02, readout_p=0.03)

# ---- 1) Grid search baseline (no DD) ----
best = None
for gamma in np.linspace(0, pi, 6):
    for beta in np.linspace(0, pi / 2, 6):
        qc = qaoa_circuit(gamma, beta)
        tc = transpile(qc, backend, optimization_level=1)  # no scheduling here
        res = backend.run(tc, shots=4096).result()
        val = expected_cut(res.get_counts())
        if best is None or val > best["value"]:
            best = {"gamma": float(gamma), "beta": float(beta), "value": float(val)}

# ---- 2) Schedule (manually) then apply DD ----
val_dd = best["value"]          # fallback if DD not available
note = "baseline only (DD skipped)"

if ALAPSchedule is not None:
    try:
        # Explicit durations so scheduling works even on Aer
        durations = InstructionDurations([
            ("h",        None, 50),
            ("rx",       None, 50),
            ("rz",       None, 50),
            ("cx",       None, 200),
            ("measure",  None, 800),
        ])

        qc_best = qaoa_circuit(best["gamma"], best["beta"])

        # 2a) Transpile WITHOUT scheduling (mapping/opt only)
        tc = transpile(qc_best, backend, optimization_level=1)

        # 2b) Manually schedule with ALAP using our durations
        pm_sched = PassManager([ALAPSchedule(durations)])
        tc_sched = pm_sched.run(tc)

        # 2c) Apply DD on the scheduled circuit
        dd_pass = add_dd_pass(backend, sequence="XY4")
        pm_dd = PassManager([dd_pass])
        tc_dd = pm_dd.run(tc_sched)

        res_dd = backend.run(tc_dd, shots=4096).result()
        val_dd = expected_cut(res_dd.get_counts())
        note = "DD applied (XY4)"
    except Exception as e:
        # Graceful fallback if anything goes wrong
        note = f"DD skipped due to: {type(e).__name__}: {e}".splitlines()[0]

# ---- 3) Save + plot ----
artifact = {"grid_best": best, "with_dd": float(val_dd), "note": note}
with open("experiments/results/qaoa_maxcut_dd.json", "w") as f:
    json.dump(artifact, f, indent=2)

plot_bar(
    ["Baseline", "With DD"],
    [best["value"], val_dd],
    "Setting", "Expected cut", f"QAOA MaxCut: {note}",
    "experiments/results/qaoa_maxcut_dd.png"
)

print("Saved experiments/results/qaoa_maxcut_dd.json and qaoa_maxcut_dd.png")
