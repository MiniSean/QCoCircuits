# -------------------------------------------
# Module containing repetition-code connectivity.
# -------------------------------------------
from qce_circuit.utilities.singleton_base import SingletonABCMeta
from qce_circuit.connectivity.intrf_channel_identifier import (
    QubitIDObj,
    EdgeIDObj,
)
from qce_circuit.connectivity.connectivity_surface_code import (
    ParityGroup,
    StabilizerType,
)
from qce_circuit.connectivity.generic_gate_sequence import (
    IGenericSurfaceCodeLayer,
    GenericSurfaceCode,
)
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    GateSequenceLayer,
    Operation,
)


class Repetition9Code(GenericSurfaceCode, IGenericSurfaceCodeLayer, metaclass=SingletonABCMeta):

    # region Class Constructor
    def __init__(self):
        super().__init__(
            gate_sequences=[
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('Z3')),
                        Operation.type_park(QubitIDObj('D8')),
                        Operation.type_park(QubitIDObj('Z4')),
                        Operation.type_park(QubitIDObj('D9')),
                        Operation.type_park(QubitIDObj('X2')),
                        Operation.type_park(QubitIDObj('D2')),
                        Operation.type_park(QubitIDObj('D3')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D1'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D4'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X3'), QubitIDObj('D7'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D6'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('D7')),
                        Operation.type_park(QubitIDObj('Z4')),
                        Operation.type_park(QubitIDObj('D9')),
                        Operation.type_park(QubitIDObj('X2')),
                        Operation.type_park(QubitIDObj('D1')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D2'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D5'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X3'), QubitIDObj('D8'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D3'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('X3')),
                        Operation.type_park(QubitIDObj('D9')),
                        Operation.type_park(QubitIDObj('Z1')),
                        Operation.type_park(QubitIDObj('D1')),
                        Operation.type_park(QubitIDObj('D3')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D2'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z4'), QubitIDObj('D5'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X4'), QubitIDObj('D8'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z3'), QubitIDObj('D7'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('X3')),
                        Operation.type_park(QubitIDObj('D7')),
                        Operation.type_park(QubitIDObj('D8')),
                        Operation.type_park(QubitIDObj('Z1')),
                        Operation.type_park(QubitIDObj('D1')),
                        Operation.type_park(QubitIDObj('D2')),
                        Operation.type_park(QubitIDObj('Z2')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D3'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z4'), QubitIDObj('D6'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X4'), QubitIDObj('D9'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z3'), QubitIDObj('D4'))),
                    ],
                ),
            ],
            parity_group_z=[
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('X1'),
                    _data_qubits=[QubitIDObj('D1'), QubitIDObj('D2')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('X2'),
                    _data_qubits=[QubitIDObj('D2'), QubitIDObj('D3')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('X3'),
                    _data_qubits=[QubitIDObj('D7'), QubitIDObj('D8')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('X4'),
                    _data_qubits=[QubitIDObj('D8'), QubitIDObj('D9')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z1'),
                    _data_qubits=[QubitIDObj('D4'), QubitIDObj('D5')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z2'),
                    _data_qubits=[QubitIDObj('D3'), QubitIDObj('D6')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z3'),
                    _data_qubits=[QubitIDObj('D4'), QubitIDObj('D7')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z4'),
                    _data_qubits=[QubitIDObj('D5'), QubitIDObj('D6')]
                ),
            ],
            parity_group_x=[],
        )
    # endregion


class Repetition9Round6Code(GenericSurfaceCode, IGenericSurfaceCodeLayer, metaclass=SingletonABCMeta):

    # region Class Constructor
    def __init__(self):
        super().__init__(
            gate_sequences=[
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('Z4')),
                        Operation.type_park(QubitIDObj('D2')),
                        Operation.type_park(QubitIDObj('X3')),
                        Operation.type_park(QubitIDObj('X2')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D1'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D6'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D5'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('X3')),
                        Operation.type_park(QubitIDObj('Z3')),
                        Operation.type_park(QubitIDObj('D1')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D2'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D3'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D4'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('D9')),
                        Operation.type_park(QubitIDObj('Z2')),
                        Operation.type_park(QubitIDObj('X2')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X4'), QubitIDObj('D8'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z3'), QubitIDObj('D7'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z4'), QubitIDObj('D6'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('D8')),
                        Operation.type_park(QubitIDObj('X3')),
                        Operation.type_park(QubitIDObj('Z1')),
                        Operation.type_park(QubitIDObj('X2')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X4'), QubitIDObj('D9'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z3'), QubitIDObj('D4'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('Z4'), QubitIDObj('D5'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('D3')),
                        Operation.type_park(QubitIDObj('D7')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D2'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X3'), QubitIDObj('D8'))),
                    ],
                ),
                GateSequenceLayer(
                    _park_operations=[
                        Operation.type_park(QubitIDObj('D8')),
                        Operation.type_park(QubitIDObj('D2')),
                    ],
                    _gate_operations=[
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D3'))),
                        Operation.type_gate(EdgeIDObj(QubitIDObj('X3'), QubitIDObj('D7'))),
                    ],
                ),
            ],
            parity_group_z=[
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_X,
                    _ancilla_qubit=QubitIDObj('X1'),
                    _data_qubits=[QubitIDObj('D1'), QubitIDObj('D2')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_X,
                    _ancilla_qubit=QubitIDObj('X2'),
                    _data_qubits=[QubitIDObj('D2'), QubitIDObj('D3')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_X,
                    _ancilla_qubit=QubitIDObj('X3'),
                    _data_qubits=[QubitIDObj('D7'), QubitIDObj('D8')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_X,
                    _ancilla_qubit=QubitIDObj('X4'),
                    _data_qubits=[QubitIDObj('D8'), QubitIDObj('D9')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z1'),
                    _data_qubits=[QubitIDObj('D4'), QubitIDObj('D5')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z2'),
                    _data_qubits=[QubitIDObj('D3'), QubitIDObj('D6')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z3'),
                    _data_qubits=[QubitIDObj('D4'), QubitIDObj('D7')]
                ),
                ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z,
                    _ancilla_qubit=QubitIDObj('Z4'),
                    _data_qubits=[QubitIDObj('D5'), QubitIDObj('D6')]
                ),
            ],
            parity_group_x=[],
        )
    # endregion
