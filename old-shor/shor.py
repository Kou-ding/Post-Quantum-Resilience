"""
This code runs Shor's algorithm on a quantum simulator.

Patameters:
    qiskit version: 0.24
    python version: 3.8
"""
from qiskit.aqua.algorithms import Shor
from qiskit.aqua import QuantumInstance
from qiskit import Aer

key = 15
base = 2

backend = Aer.get_backend('qasm_simulator')

quantum_instance = QuantumInstance(backend, shots=1024)

my_shor = Shor(N=key, a=base, quantum_instance=quantum_instance)

result = my_shor.run()

# Print results
print("Factors found:", result['factors'])