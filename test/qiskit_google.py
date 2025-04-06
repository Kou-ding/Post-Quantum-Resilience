"""Imports for the notebook."""
import fractions
import math
import random

import numpy as np
import sympy
from typing import Callable, Iterable, List, Optional, Sequence, Union

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.primitives import Sampler
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Operator

# For visualization
try:
    from qiskit_visualizations import plot_histogram
except ImportError:
    try:
        from qiskit.visualization import plot_histogram
    except ImportError:
        plot_histogram = None
        print("Visualization functions not available")

"""Function to compute the elements of Z_n."""
def multiplicative_group(n: int) -> List[int]:
    """Returns the multiplicative group modulo n.
    
    Args:
        n: Modulus of the multiplicative group.
    """
    assert n > 1
    group = [1]
    for x in range(2, n):
        if math.gcd(x, n) == 1:
            group.append(x)
    return group

"""Example of a multiplicative group."""
n = 15
print(f"The multiplicative group modulo n = {n} is:")
print(multiplicative_group(n))

"""Function for classically computing the order of an element of Z_n."""
def classical_order_finder(x: int, n: int) -> Optional[int]:
    """Computes smallest positive r such that x**r mod n == 1.

    Args:
        x: Integer whose order is to be computed, must be greater than one
           and belong to the multiplicative group of integers modulo n (which
           consists of positive integers relatively prime to n),
        n: Modulus of the multiplicative group.

    Returns:
        Smallest positive integer r such that x**r == 1 mod n.
        Always succeeds (and hence never returns None).

    Raises:
        ValueError when x is 1 or not an element of the multiplicative
        group of integers modulo n.
    """
    # Make sure x is both valid and in Z_n.
    if x < 2 or x >= n or math.gcd(x, n) > 1:
        raise ValueError(f"Invalid x={x} for modulus n={n}.")
    
    # Determine the order.
    r, y = 1, x
    while y != 1:
        y = (x * y) % n
        r += 1
    return r

"""Example of (classically) computing the order of an element."""
n = 15  # The multiplicative group is [1, 2, 4, 7, 8, 11, 13, 14].
x = 8
r = classical_order_finder(x, n)

# Check that the order is indeed correct.
print(f"x^r mod n = {x}^{r} mod {n} = {x**r % n}")

"""Helper functions for quantum modular exponentiation in Qiskit."""
def controlled_modular_multiplication(
    circuit: QuantumCircuit,
    control: int,
    target_register: List[int],
    a: int,
    mod: int,
    ancillae: List[int] = None
) -> None:
    """Implements controlled modular multiplication |y⟩ → |a·y mod N⟩.
    
    This is a simplified implementation that uses classical computation
    to determine the permutation and implements it as a series of CSWAP gates.
    In a real implementation, this would be built from quantum adders.
    
    Args:
        circuit: The quantum circuit to add the operation to
        control: The control qubit index
        target_register: The target register qubit indices
        a: The multiplier
        mod: The modulus
        ancillae: Optional ancilla qubit indices
    """
    n_bits = len(target_register)
    max_value = 2**n_bits
    
    # Compute all possible mappings
    mapping = {}
    for y in range(min(max_value, mod)):
        result = (a * y) % mod
        bin_y = format(y, f'0{n_bits}b')
        bin_result = format(result, f'0{n_bits}b')
        mapping[bin_y] = bin_result
    
    # For each possible input state, conditionally map to the output state
    for input_bin, output_bin in mapping.items():
        # Skip if no change
        if input_bin == output_bin:
            continue
        
        # Find differing bit positions
        diff_positions = [i for i in range(n_bits) if input_bin[i] != output_bin[i]]
        
        # Add gates to conditionally flip these bits
        for pos in diff_positions:
            # Condition on control qubit and input state
            if input_bin[pos] == '0' and output_bin[pos] == '1':
                # Need to conditionally set this bit to 1
                controls = [control] + [target_register[i] for i in range(n_bits) 
                                     if input_bin[i] == '1']
                anti_controls = [target_register[i] for i in range(n_bits) 
                               if input_bin[i] == '0' and i != pos]
                
                # Add multi-controlled X gate
                if len(anti_controls) == 0:
                    if len(controls) == 1:
                        circuit.cx(controls[0], target_register[pos])
                    else:
                        circuit.mcx(controls, target_register[pos])
                else:
                    # For simplicity, we'll just note that in a full implementation,
                    # this would use ancilla qubits to implement gates with anti-controls
                    raise NotImplementedError("Anti-control not implemented in this example")
            
            # Similar logic for setting bit to 0

def controlled_modular_exponentiation(
    circuit: QuantumCircuit,
    exponent_register: List[int],
    target_register: List[int],
    base: int,
    modulus: int,
    ancillae: List[int] = None
) -> None:
    """Implements the controlled modular exponentiation operation.
    
    Computes |y⟩|e⟩ → |y·base^e mod modulus⟩|e⟩.
    
    Args:
        circuit: The quantum circuit to add the operation to
        exponent_register: The exponent register qubit indices 
        target_register: The target register qubit indices
        base: The base of the exponentiation
        modulus: The modulus
        ancillae: Optional ancilla qubit indices
    """
    # For each qubit in the exponent register
    for i, qubit in enumerate(exponent_register):
        # If this qubit is |1⟩, multiply by base^(2^i)
        power = pow(base, 2**i, modulus)
        controlled_modular_multiplication(
            circuit, qubit, target_register, power, modulus, ancillae
        )

"""Function to make the quantum circuit for order finding."""
def make_order_finding_circuit(x: int, n: int) -> QuantumCircuit:
    """Returns quantum circuit which computes the order of x modulo n.

    The circuit uses Quantum Phase Estimation to compute an eigenvalue of
    the modular multiplication unitary.

    Args:
        x: positive integer whose order modulo n is to be found
        n: modulus relative to which the order of x is to be found

    Returns:
        Quantum circuit for finding the order of x modulo n
    """
    L = n.bit_length()
    
    # In Qiskit we define registers first
    target = QuantumRegister(L, name='target')
    exponent = QuantumRegister(2*L + 3, name='exponent')
    result = ClassicalRegister(2*L + 3, name='result')
    
    # Create the circuit
    circuit = QuantumCircuit(target, exponent, result)
    
    # Initialize target to |1⟩
    circuit.x(target[L-1])
    
    # Apply Hadamard gates to the exponent register
    for qubit in exponent:
        circuit.h(qubit)
    
    # Apply controlled U^(2^j) operations
    controlled_modular_exponentiation(
        circuit, exponent, target, x, n
    )
    
    # Apply inverse QFT to the exponent register
    circuit.append(
        QFT(len(exponent)).inverse(),
        exponent
    )
    
    # Measure the exponent register
    circuit.measure(exponent, result)
    
    return circuit

"""Example of the quantum circuit for period finding."""
n = 15
x = 7
circuit = make_order_finding_circuit(x, n)
print(circuit)

"""Function to simulate the order finding circuit."""
def simulate_order_finding(circuit: QuantumCircuit, shots: int = 8) -> dict:
    """Simulates the order finding circuit and returns the measurement counts."""
    # Using Qiskit's primitives-based approach (for latest versions)
    sampler = Sampler()
    job = sampler.run(circuit, shots=shots)
    result = job.result()
    return result.quasi_dists[0]

"""Example of processing the measurement results."""
def process_measurement(counts: dict, x: int, n: int) -> Optional[int]:
    """Interprets the output of the order finding circuit.

    Args:
        counts: measurement counts obtained from simulating the circuit
        x: the base of the modular exponentiation
        n: the modulus

    Returns:
        r, the order of x modulo n or None.
    """
    # Take the most frequent measurement result
    if not counts:
        return None
    
    # In the primitives-based approach, keys are integers not bit strings
    result = max(counts, key=counts.get)
    exponent_num_bits = result.bit_length()
    eigenphase = float(result / 2**exponent_num_bits)
    
    # Run the continued fractions algorithm to determine f = s / r.
    f = fractions.Fraction.from_float(eigenphase).limit_denominator(n)
    
    # If the numerator is zero, the order finder failed.
    if f.numerator == 0:
        return None
    
    # Else, return the denominator if it is valid.
    r = f.denominator
    if x**r % n != 1:
        return None
    return r

"""Full quantum order finder function."""
def quantum_order_finder(x: int, n: int) -> Optional[int]:
    """Computes smallest positive r such that x**r mod n == 1.
    
    Args:
        x: integer whose order is to be computed, must be greater than one
           and belong to the multiplicative group of integers modulo n (which
           consists of positive integers relatively prime to n),
        n: modulus of the multiplicative group.
    """
    # Check that the integer x is a valid element of the multiplicative group
    # modulo n.
    if x < 2 or n <= x or math.gcd(x, n) > 1:
        raise ValueError(f'Invalid x={x} for modulus n={n}.')

    # Create the order finding circuit.
    circuit = make_order_finding_circuit(x, n)
    
    # Simulate the circuit
    counts = simulate_order_finding(circuit)
    
    # Return the processed measurement result.
    return process_measurement(counts, x, n)

"""Functions for factoring from start to finish."""
def find_factor_of_prime_power(n: int) -> Optional[int]:
    """Returns non-trivial factor of n if n is a prime power, else None."""
    for k in range(2, math.floor(math.log2(n)) + 1):
        c = math.pow(n, 1 / k)
        c1 = math.floor(c)
        if c1**k == n:
            return c1
        c2 = math.ceil(c)
        if c2**k == n:
            return c2
    return None

def find_factor(
    n: int,
    order_finder: Callable[[int, int], Optional[int]] = quantum_order_finder,
    max_attempts: int = 30
) -> Optional[int]:
    """Returns a non-trivial factor of composite integer n.

    Args:
        n: Integer to factor.
        order_finder: Function for finding the order of elements of the
            multiplicative group of integers modulo n.
        max_attempts: number of random x's to try, also an upper limit
            on the number of order_finder invocations.

    Returns:
        Non-trivial factor of n or None if no such factor was found.
        Factor k of n is trivial if it is 1 or n.
    """
    # If the number is prime, there are no non-trivial factors.
    if sympy.isprime(n):
        print("n is prime!")
        return None
    
    # If the number is even, two is a non-trivial factor.
    if n % 2 == 0:
        return 2
    
    # If n is a prime power, we can find a non-trivial factor efficiently.
    c = find_factor_of_prime_power(n)
    if c is not None:
        return c
    
    for _ in range(max_attempts):
        # Choose a random number between 2 and n - 1.
        x = random.randint(2, n - 1)
        
        # Most likely x and n will be relatively prime.
        c = math.gcd(x, n)
        
        # If x and n are not relatively prime, we got lucky and found
        # a non-trivial factor.
        if 1 < c < n:
            return c
        
        # Compute the order r of x modulo n using the order finder.
        r = order_finder(x, n)
        
        # If the order finder failed, try again.
        if r is None:
            continue
        
        # If the order r is even, try again.
        if r % 2 != 0:
            continue
        
        # Compute the non-trivial factor.
        y = x**(r // 2) % n
        assert 1 < y < n
        c = math.gcd(y - 1, n)
        if 1 < c < n:
            return c

    print(f"Failed to find a non-trivial factor in {max_attempts} attempts.")
    return None

"""Example usage for factoring a number."""
import time
# Number to factor
n = 184573

time_start = time.time()
# Attempt to find a factor
p = find_factor(n, order_finder=classical_order_finder)
time_end = time.time()
q = n // p
print("Time taken to factor n =", time_end - time_start, "seconds")
print("Factoring n = pq =", n)
print("p =", p)
print("q =", q)

