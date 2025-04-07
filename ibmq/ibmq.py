"""
As of 07/04/2025 this code is no longer working. qiskit-ibmq-provider is no longer supported.

Example usage:
    >>> conda env create -f environment.yml 
    >>> python3 ibmq.py

Author: Macauley Coggins (https://thequantuminsider.com/2020/02/07/quantum-programming-101-shors-algorithm/)
Date: 07/02/2020
"""
from qiskit import IBMQ
from qiskit import Aer
from qiskit.aqua import QuantumInstance
from qiskit.aqua.algorithms import Shor
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
api_token = os.getenv("qiskit_token")
# print(f"My token is: {api_token}") # Uncomment to check if the token is loaded correctly

# # Uncomment the following lines to try running the code on a real IBMQ device
# # Enable IBMQ
# IBMQ.enable_account(api_token)
# provider = IBMQ.get_provider(hub='ibm-q') # Get the provider for the IBM Quantum Experience
# backend = provider.get_backend('ibmq_qasm_simulator') # Specifies the quantum device simulator: 'ibmq_qasm_simulator' vs real device 'ibm_sherbrooke'

backend = Aer.get_backend('qasm_simulator')

print('\n Shor\'s Algorithm')
print('\n Executing...\n')

# Shor parameters
pk = 15 # public key to be factored
base = 2 # base for the modular exponentiation
quantum_instance = QuantumInstance(backend, shots=1024)

# Run Shor's algorithm
factors = Shor(N=pk, a=base, quantum_instance=quantum_instance)
result = factors.run()
print("Factors:", result['factors']) # Print the factors