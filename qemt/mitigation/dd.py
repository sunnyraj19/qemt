from qiskit.transpiler import InstructionDurations
from qiskit.transpiler.passes import PadDynamicalDecoupling
from qiskit.circuit.library import XGate, YGate

def add_dd_pass(backend, sequence: str = "XY4"):
    inst_durations = getattr(getattr(backend, "target", None), "durations", None)
    if callable(inst_durations):
        durations = inst_durations()
    else:
        durations = InstructionDurations()
    seq = sequence.upper()
    if seq == "XY4":
        dd_seq = [XGate(), YGate(), XGate(), YGate()]
    elif seq == "CPMG":
        dd_seq = [XGate(), XGate()]
    else:
        dd_seq = [XGate()]
    return PadDynamicalDecoupling(durations, dd_seq)
