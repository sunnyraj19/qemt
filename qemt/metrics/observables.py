from typing import Dict, List
def z_expectation(counts: Dict[str,int], qubits: List[int]) -> float:
    shots = sum(counts.values()) or 1
    exp = 0.0
    for bitstr, c in counts.items():
        val = 1
        for q in qubits:
            bit = bitstr[::-1][q]
            val *= (1 if bit == '0' else -1)
        exp += val * c
    return exp / shots
