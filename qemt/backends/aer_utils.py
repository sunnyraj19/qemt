from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit_aer import AerSimulator

def noisy_backend(p1=0.001, p2=0.01, readout_p=0.02) -> AerSimulator:
    nm = NoiseModel()
    e1 = depolarizing_error(p1, 1)
    e2 = depolarizing_error(p2, 2)
    nm.add_all_qubit_quantum_error(e1, ['x','y','z','h','s','sdg','t','tdg','rx','ry','rz','id'])
    nm.add_all_qubit_quantum_error(e2, ['cx','cz','swap'])
    ro = ReadoutError([[1-readout_p, readout_p],[readout_p, 1-readout_p]])
    for q in range(32):
        nm.add_readout_error(ro, [q])
    sim = AerSimulator(noise_model=nm)
    return sim
