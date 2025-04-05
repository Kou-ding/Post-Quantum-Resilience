"""
This code runs Shor's algorithm on a quantum simulator.

Patameters:
    qiskit version: 0.24
    ibm_runtime version: 0.1.0
    python version: 3.8
"""

# from qiskit import IBMQ
# IBMQ.save_account('qiskit_token')  # Only once
# IBMQ.load_account()
# provider = IBMQ.get_provider(hub='ibm-q')
# backend = provider.get_backend('ibm_sherbrooke')


# from qiskit.aqua.algorithms import Shor
# from qiskit.aqua import QuantumInstance
# from qiskit import Aer

# from qiskit_ibm_runtime import QiskitRuntimeService
# # Set up the Qiskit Runtime service
# service = QiskitRuntimeService(channel='ibm_quantum',
#                                token='qiskit_token')
# import time

# key = 15
# base = 2

# # backend = Aer.get_backend('qasm_simulator')
# backend = service.backend('ibm_sherbrooke')

# quantum_instance = QuantumInstance(backend, shots=1024)

# start_time = time.time()
# my_shor = Shor(N=key, a=base, quantum_instance=quantum_instance)

# result = my_shor.run()
# end_time = time.time()

# # Print the factors and the time taken
# print(f"Time taken: {end_time - start_time} seconds")
# print("Factors found:", result['factors'])

# from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
# from qiskit.algorithms import Shor
# import time

# # Step 1: Initialize Runtime Service
# service = QiskitRuntimeService(channel="ibm_quantum", token="qiskit_token")

# # Step 2: Choose a backend (real quantum computer)
# backend = service.backend("ibmq_qasm_simulator")  # Or another backend with enough qubits

# # Step 3: Create Runtime Sampler
# sampler = Sampler(backend=backend, options={"shots": 1024})

# # Step 4: Run Shor's Algorithm (e.g., factor 15)
# shor = Shor(sampler=sampler)

# start_time = time.time()
# result = shor.factor(15)
# end_time = time.time()

# # Step 5: Output result
# print("Factors found:", result.factors)
# print(f"Time taken: {end_time - start_time:.2f} seconds")

from qiskit import IBMQ
from qiskit.aqua import QuantumInstance
from qiskit.aqua.algorithms import Shor
import time

IBMQ.enable_account('qiskit_token') # Enter your API token here
provider = IBMQ.get_provider(hub='ibm-q')

backend = provider.get_backend('ibmq_qasm_simulator') # Specifies the quantum device

print('\n Shors Algorithm')
print('--------------------')
print('\nExecuting...\n')
time_start = time.time()
factors = Shor(21) #Function to run Shor's algorithm where 21 is the integer to be factored
result_dict = factors.run(QuantumInstance(backend, shots=1, skip_qobj_validation=False))
time_end = time.time()
print(f"Time taken: {time_end - time_start} seconds\n") # Print the time taken to run the algorithm
result = result_dict['factors'] # Get factors from results

print(result)
print('\nPress any key to close')
input()