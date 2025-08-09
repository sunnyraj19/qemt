import numpy as np
from qiskit import QuantumCircuit
from qemt.mitigation.zne import zne

def test_zne_linear_recovery():
    a, b = 0.7, -0.1
    qc = QuantumCircuit(1)
    class DummyBackend: pass
    dummy = DummyBackend()
    scales = [1,3,5]
    vals = [a + b*s for s in scales]
    current = {'i': 0}
    def ex(_circ):
        i = current['i']; current['i'] += 1
        return vals[i]
    out = zne(qc, dummy, ex, scale_factors=scales, fit='richardson')
    assert np.isclose(out['mitigated'], a, atol=1e-6)
