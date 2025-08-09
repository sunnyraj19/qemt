import numpy as np
from qiskit import QuantumCircuit
from qemt.mitigation.zne import zne

def test_zne_linear_recovery():
    # Synthetic linear model: y = a + b*s; intercept at s=0 is 'a'
    a, b = 0.7, -0.1
    scales = [1, 3, 5]
    vals = [a + b*s for s in scales]

    # Executor returns the next synthetic value each call
    current = {'i': 0}
    def executor(_circ):
        i = current['i']; current['i'] += 1
        return vals[i]

    qc = QuantumCircuit(1)
    out = zne(qc, backend=None, executor=executor, scale_factors=scales, fit='richardson')
    assert np.isclose(out['mitigated'], a, atol=1e-6)

