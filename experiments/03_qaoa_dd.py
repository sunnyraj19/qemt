import os, json
import networkx as nx
from qiskit import transpile
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qemt.backends.aer_utils import noisy_backend
from qemt.mitigation.dd import add_dd_pass

os.makedirs('experiments/results', exist_ok=True)

# Graph for MaxCut
G = nx.Graph()
G.add_edges_from([(0,1),(1,2),(2,3),(3,0),(0,2)])
qp = QuadraticProgram()
for i in G.nodes:
    qp.binary_var(name=str(i))
# MaxCut objective
objective = sum(-1 for _ in G.edges)
for i,j in G.edges:
    qp.minimize(linear=[0]*len(G.nodes), quadratic={(i,j):-1})

backend = noisy_backend()
dd_pass = add_dd_pass(backend, sequence="XY4")

qaoa = QAOA(optimizer=COBYLA(maxiter=50), reps=1, quantum_instance=backend)
meo = MinimumEigenOptimizer(qaoa)
result = meo.solve(qp)

with open('experiments/results/qaoa_dd.json', 'w') as f:
    json.dump({"solution": result.x, "fval": result.fval}, f, indent=2)

print("QAOA+DD result saved.")
