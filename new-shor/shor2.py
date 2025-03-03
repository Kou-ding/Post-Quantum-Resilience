import numpy as np
from fractions import Fraction
from qiskit_aer import Aer
from qiskit import QuantumCircuit, transpile

def qpe_amod15(a):
    """Create Quantum Phase Estimation circuit for modular exponentiation a^x % 15"""
    n_count = 8
    qc = QuantumCircuit(4 + n_count, n_count)

    # Initialize counting qubits in superposition
    for q in range(n_count):
        qc.h(q)

    # Initialize target qubit in |1>
    qc.x(n_count)

    for q in range(n_count):
        qc.append(c_amod15(a, 2**q), 
                  [q] + list(range(n_count, 4 + n_count)))

    # Apply inverse QFT
    qc.append(qft_dagger(n_count), range(n_count))

    # Measure
    qc.measure(range(n_count), range(n_count))

    return qc

def qft_dagger(n):
    """n-qubit inverse QFT"""
    qc = QuantumCircuit(n)
    for qubit in range(n//2):
        qc.swap(qubit, n-qubit-1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi/float(2**(j-m)), m, j)
        qc.h(j)
    qc.name = "QFT†"
    return qc

def c_amod15(a, power):
    """Controlled multiplication by a^power % 15"""
    U = QuantumCircuit(4)

    for _ in range(power):
        if a == 2:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        elif a == 7:
            U.swap(1, 3)
            U.swap(0, 2)
        elif a == 8:
            U.swap(0, 3)
            U.swap(1, 2)
        elif a == 11:
            U.swap(0, 2)
            U.swap(1, 3)
        elif a == 13:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)

    U = U.to_gate()
    U.name = "%i^%i mod 15" % (a, power)

    c_U = U.control()

    return c_U

def get_factors(N):
    """Run Shor's algorithm to find non-trivial factors of N."""
    if N % 2 == 0:
        return [2, N // 2]

    backend = Aer.get_backend('qasm_simulator')

    # Use 2, 7, 8, 11, 13 as candidates for 'a'
    for a in [2, 7, 8, 11, 13]:
        if np.gcd(a, N) != 1:
            return [np.gcd(a, N), N//np.gcd(a, N)]

        qc = qpe_amod15(a)

        # Transpile and run directly
        t_qc = transpile(qc, backend)
        job = backend.run([t_qc],shots=1024)
        result = job.result()

        # Get counts
        counts = result.get_counts()

        # Extract measured phases
        measured_phases = []
        for output in counts:
            phase = int(output, 2) / (2**8)
            measured_phases.append(phase)

        # Process the phases into candidate factors
        for phase in measured_phases:
            frac = Fraction(phase).limit_denominator(N)
            r = frac.denominator

            # Ignore odd periods
            if r % 2 == 1:
                continue

            guess1 = np.gcd(a**(r // 2) - 1, N)
            guess2 = np.gcd(a**(r // 2) + 1, N)

            if guess1 not in [1, N] and (N % guess1 == 0):
                return [guess1, N//guess1]
            if guess2 not in [1, N] and (N % guess2 == 0):
                return [guess2, N // guess2]

    return None

# Run the factoring for N = 15
N = 15
factors = get_factors(N)
factors = [int(f) for f in factors]

if factors:
    print(f"Non-trivial factors of {N} are {factors}")
else:
    print(f"No non-trivial factors found for {N}")
