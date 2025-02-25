import numpy as np
from qiskit import Aer, QuantumCircuit, transpile, assemble, execute
from qiskit.visualization import plot_histogram
from math import gcd
from numpy.random import randint
import matplotlib.pyplot as plt

# Function to find the continued fraction expansion of a number
def continued_fraction(x, max_denominator=100):
    cf = []
    while x != 0 and len(cf) < max_denominator:
        cf.append(int(np.floor(x)))
        x = x - np.floor(x)
        if x != 0:
            x = 1 / x
    return cf

# Function to find the period using continued fractions
def find_period(a, N):
    for r in range(1, N):
        if (a ** r) % N == 1:
            return r
    return None

# Function to implement Shor's algorithm
def shors_algorithm(N):
    if N % 2 == 0:
        return 2
    
    # Step 1: Choose a random number a < N
    a = randint(2, N)
    
    # Step 2: Compute the greatest common divisor (gcd) of a and N
    g = gcd(a, N)
    if g != 1:
        return g
    
    # Step 3: Find the period r of the function f(x) = a^x mod N
    r = find_period(a, N)
    if r is None:
        return None
    
    # Step 4: If r is odd, go back to step 1
    if r % 2 != 0:
        return shors_algorithm(N)
    
    # Step 5: Compute the candidates for the factors
    candidate1 = gcd(a ** (r // 2) - 1, N)
    candidate2 = gcd(a ** (r // 2) + 1, N)
    
    # Step 6: Return the non-trivial factors
    if candidate1 != 1 and candidate1 != N:
        return candidate1
    elif candidate2 != 1 and candidate2 != N:
        return candidate2
    else:
        return None

# Function to create a quantum circuit for modular exponentiation
def create_qft_circuit(n):
    qc = QuantumCircuit(n)
    for qubit in range(n // 2):
        qc.swap(qubit, n - qubit - 1)
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), m, j)
        qc.h(j)
    return qc

# Function to create a quantum circuit for Shor's algorithm
def create_shors_circuit(N, a):
    n = N.bit_length()
    qc = QuantumCircuit(2 * n, n)
    
    # Initialize the qubits
    qc.h(range(n))
    qc.x(2 * n - 1)
    
    # Apply controlled-U gates for modular exponentiation
    for q in range(n):
        qc.append(create_qft_circuit(n), range(n))
        qc.cx(q, n + q)
        qc.append(create_qft_circuit(n).inverse(), range(n))
    
    # Apply inverse QFT
    qc.append(create_qft_circuit(n).inverse(), range(n))
    
    # Measure the first n qubits
    qc.measure(range(n), range(n))
    
    return qc

# Main function to run Shor's algorithm
def run_shors_algorithm(N):
    # Step 1: Choose a random number a < N
    a = randint(2, N)
    
    # Step 2: Compute the greatest common divisor (gcd) of a and N
    g = gcd(a, N)
    if g != 1:
        print(f"Found a non-trivial factor: {g}")
        return g
    
    # Step 3: Create and run the quantum circuit
    qc = create_shors_circuit(N, a)
    simulator = Aer.get_backend('qasm_simulator')
    compiled_circuit = transpile(qc, simulator)
    qobj = assemble(compiled_circuit)
    result = execute(qc, simulator).result()
    counts = result.get_counts(qc)
    
    # Step 4: Find the period r from the measurement results
    measured_value = int(max(counts, key=counts.get), 2)
    r = find_period(a, N)
    
    # Step 5: If r is odd, go back to step 1
    if r % 2 != 0:
        return run_shors_algorithm(N)
    
    # Step 6: Compute the candidates for the factors
    candidate1 = gcd(a ** (r // 2) - 1, N)
    candidate2 = gcd(a ** (r // 2) + 1, N)
    
    # Step 7: Return the non-trivial factors
    if candidate1 != 1 and candidate1 != N:
        print(f"Found a non-trivial factor: {candidate1}")
        return candidate1
    elif candidate2 != 1 and candidate2 != N:
        print(f"Found a non-trivial factor: {candidate2}")
        return candidate2
    else:
        print("No non-trivial factors found.")
        return None

# Example usage
N = 15
print(f"Running Shor's algorithm to factor {N}...")
factor = run_shors_algorithm(N)
if factor:
    print(f"A non-trivial factor of {N} is: {factor}")
else:
    print(f"No non-trivial factors of {N} were found.")