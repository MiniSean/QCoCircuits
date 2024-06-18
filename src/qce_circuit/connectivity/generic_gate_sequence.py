# -------------------------------------------
# Module containing interface and implementation of generic (Surface17) gate sequences.
# -------------------------------------------
from abc import ABCMeta
from typing import List, Union
from qce_circuit.utilities.custom_exceptions import ElementNotIncludedException
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.connectivity.intrf_channel_identifier import (
    IQubitID,
    IEdgeID,
    IFeedlineID,
)
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    IParityGroup,
    FrequencyGroupIdentifier,
)
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    IGateSequenceLayer,
    GateSequenceLayer,
)
from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer


class IGenericSurfaceCodeLayer(ISurfaceCodeLayer, IGateSequenceLayer, metaclass=ABCMeta):
    """
    Interface class, combining ISurfaceCodeLayer and IGateSequenceLayer.
    """
    pass


class GenericSurfaceCode(IGenericSurfaceCodeLayer):

    # region IGateSequenceLayer Interface Properties
    @property
    def gate_sequence_count(self) -> int:
        """:return: Number of gate-sequences in layer."""
        return len(self._gate_sequences)

    @property
    def involved_qubit_ids(self) -> List[IQubitID]:
        """:return: (Only) involved qubit-ID's in gate sequence."""
        gate_sequence_layers: List[GateSequenceLayer] = [self.get_gate_sequence_at_index(layer_index) for layer_index in range(self.gate_sequence_count)]
        return unique_in_order([qubit_id for gate_sequence_layer in gate_sequence_layers for qubit_id in gate_sequence_layer.qubit_ids])
    # endregion

    # region ISurfaceCodeLayer Interface Properties
    @property
    def parity_group_x(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of X-stabilizers."""
        return self._parity_group_x

    @property
    def parity_group_z(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of Z-stabilizers."""
        return self._parity_group_z

    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (Data) qubit-ID's in device layer."""
        return unique_in_order([data_id for parity_group in self.parity_group_x + self.parity_group_z for data_id in parity_group.data_ids])

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        return unique_in_order([parity_group.ancilla_id for parity_group in self.parity_group_x + self.parity_group_z])
    # endregion

    # region IDeviceLayer Interface Properties
    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's in device layer."""
        return Surface17Layer().feedline_ids
    # endregion

    # region IConnectivityLayer Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        return Surface17Layer().qubit_ids

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        return Surface17Layer().edge_ids
    # endregion

    # region Class Constructor
    def __init__(self, gate_sequences: List[GateSequenceLayer], parity_group_z: List[IParityGroup], parity_group_x: List[IParityGroup]):
        self._gate_sequences: List[GateSequenceLayer] = gate_sequences
        self._parity_group_z: List[IParityGroup] = parity_group_z
        self._parity_group_x: List[IParityGroup] = parity_group_x
    # endregion

    # region IGateSequenceLayer Interface Methods
    def get_gate_sequence_at_index(self, index: int) -> GateSequenceLayer:
        """:return: Gate-sequence object based on round index."""
        gate_sequences: List[GateSequenceLayer] = self._gate_sequences
        try:
            gate_sequence: GateSequenceLayer = gate_sequences[index]
            return gate_sequence
        except IndexError:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for gate-sequence of length: {len(gate_sequences)}.")

    def get_gate_sequence_from_element(self, element: IEdgeID) -> GateSequenceLayer:
        """:return: Gate-sequence layer of which edge element is part of."""
        gate_sequences: List[GateSequenceLayer] = self._gate_sequences
        # Assumes element is part of only a single flux-dance layer
        for gate_sequence in gate_sequences:
            if gate_sequence.contains(element=element):
                return gate_sequence
        raise ElementNotIncludedException(f"Element: {element} is not included in any gate-sequence layer.")
    # endregion

    # region ISurfaceCodeLayer Interface Methods
    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> List[IParityGroup]:
        """:return: Parity group(s) of which element (edge- or qubit-ID) is part of."""
        result: List[IParityGroup] = []
        # Assumes element is part of only a single parity group
        for parity_group in self.parity_group_x + self.parity_group_z:
            if parity_group.contains(element=element):
                result.append(parity_group)
        return result

    def get_frequency_group_identifier(self, element: IQubitID) -> FrequencyGroupIdentifier:
        """:return: Frequency group identifier based on qubit-ID."""
        return Surface17Layer().get_frequency_group_identifier(element=element)
    # endregion

    # region IDeviceLayer Interface Methods
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """:return: Qubit-ID's connected to feedline-ID."""
        return Surface17Layer().get_connected_qubits(feedline=feedline)

    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """:return: Feedline-ID's connected to qubit-ID."""
        return Surface17Layer().get_connected_feedline(qubit=qubit)

    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        return Surface17Layer().contains(element=element)
    # endregion

    # region IConnectivityLayer Interface Methods
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        return Surface17Layer().get_neighbors(qubit=qubit, order=order)

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        return Surface17Layer().get_edges(qubit=qubit)
    # endregion
