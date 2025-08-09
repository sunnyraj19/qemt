from typing import Callable, List, Dict, Optional
import numpy as np
from qiskit import transpile
from qiskit.circuit import QuantumCircuit

def fold_circuit(circ: QuantumCircuit, scale: int) -> QuantumCircuit:
    if scale % 2 == 0 or scale < 1:
        raise ValueError("scale must be odd positive integer: e.g., 1,3,5")
    if scale == 1:
        return circ.copy()
    k = (scale - 1) // 2
    u = circ.copy()
    u_dag = circ.inverse()
    folded = QuantumCircuit(circ.num_qubits, circ.num_clbits)
    for _ in range(k):
        folded.compose(u, inplace=True)
        folded.compose(u_dag, inplace=True)
    folded.compose(u, inplace=True)
    return folded

def zne(circ: QuantumCircuit, backend, executor: Callable[[QuantumCircuit], float],
        scale_factors: List[int] = [1,3,5], fit: str = "richardson",
        transpile_opts: Optional[Dict] = None) -> Dict:
    vals, xs = [], []
    for s in scale_factors:
        fc = fold_circuit(circ, s)
        tc = transpile(fc, backend=backend, optimization_level=1, **(transpile_opts or {}))
        vals.append(float(executor(tc)))
        xs.append(s)
    import numpy as np
    xs = np.array(xs, dtype=float); ys = np.array(vals, dtype=float)
    if fit == "richardson":
        A = np.vstack([xs, np.ones_like(xs)]).T
        b, a = np.linalg.lstsq(A, ys, rcond=None)[0]
        mitigated = float(a); fit_params = {"a": float(a), "b": float(b)}
    elif fit == "poly2":
        coeffs = np.polyfit(xs, ys, deg=2)
        mitigated = float(np.polyval(coeffs, 0.0))
        fit_params = {"coeffs": list(map(float, coeffs))}
    else:
        raise ValueError("fit must be 'richardson' or 'poly2'")
    return {"scale_factors": xs.tolist(), "raw": ys.tolist(), "mitigated": mitigated, "fit": fit_params}
