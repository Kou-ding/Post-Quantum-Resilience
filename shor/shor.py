"""
This is a modern implementation of Shor's algorithm using Qiskit. It is built to 
replace the deprecated Aqua module and features both an online and offline mode.

Example usage:
    >>> conda env create -f environment.yml 
    >>> python3 shor.py

Author: 
Date: 11/04/2025
"""
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
# from qiskit import QuantumCircuit
from fractions import Fraction
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
# from qiskit.quantum_info import SparsePauliOp
# from qiskit.transpiler import generate_preset_pass_manager
# from qiskit_ibm_runtime import EstimatorV2 as Estimator
# import matplotlib.pyplot as plt
from qiskit_aer import Aer
import numpy as np
from dotenv import load_dotenv
import os
import time

def backend_connect(chooser):
    # Online or offline backend
    if chooser == "1":
        # Load .env
        load_dotenv()
        api_token = os.getenv("qiskit_token")
        # Connection to Qunatum Computing service
        QiskitRuntimeService.save_account(channel="ibm_quantum", token=api_token, overwrite=True, set_as_default=True, name="shor")
        # service = QiskitRuntimeService(name="shor")
        service = QiskitRuntimeService(channel="ibm_quantum")
        backend = service.backend("ibm_sherbrooke")   
    elif chooser == "2":
        backend = Aer.get_backend('qasm_simulator')
    return backend  

def get_mod_exp_circuit(a, N, n_qubits):
    """Creates the modular exponentiation circuit for a^x % N."""
    qc = QuantumCircuit(n_qubits)

    for exp in range(n_qubits):
        power = 2**exp
        qc.append(mod_exp_gate(a, power, N, n_qubits), range(n_qubits))

    return qc

def mod_exp_gate(a, power, N, n_qubits):
    """Gate for modular exponentiation a^power % N."""
    U = QuantumCircuit(n_qubits)

    for i in range(power):
        U = apply_mod_mult(U, a, N)

    return U.to_gate(label=f"{a}^{power} % {N}")

def apply_mod_mult(qc, a, N):
    """Apply modular multiplication a*x % N using classical precomputation."""
    N_bits = len(bin(N)[2:])
    for i in range(N_bits):
        for j in range(i, N_bits):
            if (a * (2 ** i)) % N == (2 ** j) % N:
                if i != j:
                    qc.swap(i, j)

    return qc

def quantum_phase_estimation(a, N):
    """Create the Quantum Phase Estimation circuit for a^x % N."""
    n_count = 8  # Number of counting qubits (can adjust for larger N)
    N_bits = len(bin(N)[2:])

    qc = QuantumCircuit(N_bits + n_count, n_count)

    for q in range(n_count):
        qc.h(q)

    qc.x(n_count)

    for q in range(n_count):
        qc.append(
            controlled_mod_exp_gate(a, 2**q, N, N_bits),
            [q] + list(range(n_count, n_count + N_bits))
        )

    qc.append(QFT(n_count, do_swaps=False).inverse(), range(n_count))

    qc.measure(range(n_count), range(n_count))

    return qc

def controlled_mod_exp_gate(a, power, N, n_qubits):
    """Controlled modular exponentiation for a^power % N."""
    base_gate = mod_exp_gate(a, power, N, n_qubits)
    return base_gate.control()

def get_factors(N, chooser):
    """Run generalized Shor's algorithm to find non-trivial factors of N."""
    if N % 2 == 0:
        return [2, N // 2]

    # backend = Aer.get_backend('qasm_simulator')
    # backend = service.backend('ibm_sherbrooke')
    backend = backend_connect(chooser)

    candidates = [a for a in range(2, N) if np.gcd(a, N) == 1]
    np.random.shuffle(candidates)

    for a in candidates:
        print(f"Trying a = {a}")

        qc = quantum_phase_estimation(a, N)

        t_qc = transpile(qc, backend)
        job = backend.run(t_qc, shots=1024)
        result = job.result()

        counts = result.get_counts()
        measured_phases = []
        for output in counts:
            phase = int(output, 2) / (2 ** 8)
            measured_phases.append(phase)

        for phase in measured_phases:
            frac = Fraction(phase).limit_denominator(N)
            r = frac.denominator

            if r % 2 == 1:
                continue

            guess1 = np.gcd(pow(a, r // 2, N) - 1, N)
            guess2 = np.gcd(pow(a, r // 2, N) + 1, N)


            if guess1 not in [1, N] and (N % guess1 == 0):
                return [guess1, N // guess1]
            if guess2 not in [1, N] and (N % guess2 == 0):
                return [guess2, N // guess2]

    return None

if __name__ == "__main__":
    # Choose backend
    chooser = input("Select backend\n"
                    "1. online\n"
                    "2. offline\n")
    N = 21 #int(input("Enter integer N to factor: "))
    time_start = time.time()
    factors = get_factors(N, chooser)
    time_end = time.time()
    print(f"Time taken: {time_end - time_start} seconds")
    if factors:
        factors = [int(f) for f in factors]
        print(f"Non-trivial factors of {N} are {factors}")
    else:
        print(f"No non-trivial factors found for {N}")