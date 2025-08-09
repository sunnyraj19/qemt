from qiskit import QuantumCircuit

def grover_2q() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h([0,1])
    qc.cz(0,1)
    qc.h([0,1])
    qc.measure([0,1],[0,1])
    return qc
