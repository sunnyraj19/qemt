from typing import List
from qiskit import QuantumCircuit
def meas_cal_circuits(n_qubits: int) -> List[QuantumCircuit]:
    circs = []
    for b in range(2**n_qubits):
        qc = QuantumCircuit(n_qubits, n_qubits)
        for q in range(n_qubits):
            if (b >> q) & 1:
                qc.x(q)
        qc.measure(range(n_qubits), range(n_qubits))
        qc.name = f"mcal_{b:0{n_qubits}b}"
        circs.append(qc)
    return circs
