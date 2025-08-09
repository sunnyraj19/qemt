from typing import Callable, Dict, List
import numpy as np
def cdr_linear(circ, executor: Callable, near_clifford: List, noiseless_executor: Callable) -> Dict:
    X, y = [], []
    for c in near_clifford:
        x = float(executor(c))
        y_exact = float(noiseless_executor(c))
        X.append([1.0, x]); y.append(y_exact)
    X = np.array(X); y = np.array(y)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    x_target = float(executor(circ))
    y_pred = float(beta[0] + beta[1]*x_target)
    return {"coeffs": beta.tolist(), "mitigated": y_pred}
