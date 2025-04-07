# Cirq

Cirq is google's quantum computing library capable of running quantum code via:
- Quantum Virtual Machine [(QVM)](https://quantumai.google/cirq/simulate/quantum_virtual_machine)
    - Can simulate noise to better prepare for running code on real hardware.  
- Quantum Simulator (cirq.Simulator)
    - Is an ideal quantum simulator not factoring in noise.
- Quantum Hardware Devices [google quantum computers](https://quantumai.google/cirq/hardware/devices)
    - Can run code on an actual quantum computer.