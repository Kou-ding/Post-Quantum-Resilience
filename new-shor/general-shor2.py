"""
This is a from scratch approach to Shor's algorithm utilizing the current
version of Qiskit. It is meant to simplify the process by creating the 
necessary functions on a higher level, as the qiskit version 0.24 was 
able to do through qiskit.aqua.algorithms's Shor class.

Classes:
    [ClassName]: [Brief description of the class]

Functions:
    [function_name]: [Brief description of the function]

Usage example:
    [Provide a brief example of how to use the module]

Author:
    [Papadakis Fotis]

Date:
    [3/3/2025]

"""

import numpy as np
from fractions import Fraction
from qiskit_aer import Aer
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT

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

def get_factors(N):
    """Run generalized Shor's algorithm to find non-trivial factors of N."""
    if N % 2 == 0:
        return [2, N // 2]

    backend = Aer.get_backend('qasm_simulator')

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
    N = int(input("Enter integer N to factor: "))
    factors = get_factors(N)
    if factors:
        factors = [int(f) for f in factors]
        print(f"Non-trivial factors of {N} are {factors}")
    else:
        print(f"No non-trivial factors found for {N}")
