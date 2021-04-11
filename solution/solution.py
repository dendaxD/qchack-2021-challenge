from typing import List, Tuple

import numpy as np
import cirq


def matrix_to_sycamore_operations(
    target_qubits: List[cirq.GridQubit], matrix: np.ndarray
) -> Tuple[cirq.OP_TREE, List[cirq.GridQubit]]:
    """A method to convert a unitary matrix to a list of Sycamore operations.

    This method will return a list of `cirq.Operation`s using the qubits and (optionally) ancilla
    qubits to implement the unitary matrix `matrix` on the target qubits `qubits`.
    The operations are also supported by `cirq.google.gate_sets.SYC_GATESET`.

    Args:
        target_qubits: list of qubits the returned operations will act on. The qubit order defined by the list
            is assumed to be used by the operations to implement `matrix`.
        matrix: a matrix that is guaranteed to be unitary and of size (2**len(qs), 2**len(qs)).
    Returns:
        A tuple of operations and ancilla qubits allocated.
            Operations: In case the matrix is supported, a list of operations `ops` is returned.
                `ops` acts on `qs` qubits and for which `cirq.unitary(ops)` is equal to `matrix` up
                 to certain tolerance. In case the matrix is not supported, it might return NotImplemented to
                 reduce the noise in the judge output.
            Ancilla qubits: In case ancilla qubits are allocated a list of ancilla qubits. Otherwise
                an empty list.
        .
    """

    converter = cirq.google.ConvertToSycamoreGates()
    print(matrix)

    #special case of identity
    if np.array_equal(matrix, np.identity(matrix.shape[0])):
        return [], []

    #special case of 1-qubit gates
    if len(target_qubits) == 1:
        for gate in [cirq.X, cirq.Y, cirq.Z, cirq.S, cirq.T]:
            if np.array_equal(matrix, cirq.unitary(gate)):
                return [gate(target_qubits[0])], []
    for gate in [cirq.TOFFOLI, cirq.FREDKIN, cirq.CCZ]:
        if np.array_equal(matrix, cirq.unitary(gate)):
            converted = converter.convert(gate.on(*target_qubits))
            circuit = cirq.Circuit(converted)
            circuit = cirq.google.optimized_for_sycamore(circuit)
            return list(circuit.all_operations()), []

    
    # m = unitary_as_gate(matrix, target_qubits)
    m = cirq.ops.MatrixGate(matrix)
    try:
        converted = converter.convert(m.on(*target_qubits))
        circuit = cirq.Circuit(converted)
        circuit = cirq.google.optimized_for_sycamore(circuit)
        return list(circuit.all_operations()), []
    except:
        # TODO:
        # diagonal cases: https://arxiv.org/pdf/1412.5608.pdf
        # generally: implementation of the algorithm from https://arxiv.org/pdf/1210.7366.pdf
        return NotImplemented, []
