"""
As of 07/04/2025 this code is no longer working. qiskit-ibmq-provider is no longer supported.

Example usage:
    >>> conda env create -f environment.yml 
    >>> python3 ibmq.py

Author: Macauley Coggins (https://thequantuminsider.com/2020/02/07/quantum-programming-101-shors-algorithm/)
Date: 07/02/2020
"""
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import time

# Online or offline backend
chooser = input("Select backend\n"
                "1. online\n"
                "2. offline): \n")
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
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2
    backend = FakeManilaV2()

# Quantum Circuit (two qubits)
qc = QuantumCircuit(2)
 
# Add a Hadamard gate to qubit 0
qc.h(0)
 
# Perform a controlled-X gate on qubit 1, controlled by qubit 0
qc.cx(0, 1)

# Draw the circuit
qc.draw("mpl") # Remove the "mpl" (matplotlib) argument to get a text drawing.
plt.show()  # <-- This is necessary outside notebooks!

estimator = Estimator(backend)

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)

# Benchmarking
start_time = time.time()
isa_circuit = pm.run(qc)
end_time = time.time()
print(f"Time taken to transpile: {end_time - start_time} seconds")

# Plot
isa_circuit.draw("mpl", idle_wires=False)
plt.show()  # <-- This is necessary outside notebooks!