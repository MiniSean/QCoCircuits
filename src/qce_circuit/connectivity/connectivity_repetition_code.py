# -------------------------------------------
# Module containing implementation of repetition-code connectivity structure.
# -------------------------------------------
from typing import List, Union
from qce_circuit.utilities.singleton_base import SingletonABCMeta
from qce_circuit.utilities.custom_exceptions import ElementNotIncludedException
from qce_circuit.connectivity.intrf_connectivity_dance import (
    IFluxDanceLayer,
    FluxDanceLayer,
)
from qce_circuit.connectivity.intrf_channel_identifier import (
    IFeedlineID,
    IQubitID,
    IEdgeID,
    QubitIDObj,
    EdgeIDObj,
)
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    IParityGroup,
    ParityType,
    FrequencyGroupIdentifier,
)
from qce_circuit.connectivity.connectivity_surface_code import (
    ParityGroup,
    Surface17Layer,
)


class Repetition9Layer(ISurfaceCodeLayer, IFluxDanceLayer, metaclass=SingletonABCMeta):
    """
    Singleton class, implementing ISurfaceCodeLayer interface to describe a repetition-9 layout.
    """
    _parity_group_x: List[IParityGroup] = [
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X1'),
            _data_qubits=[QubitIDObj('D2'), QubitIDObj('D1')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X2'),
            _data_qubits=[QubitIDObj('D2'), QubitIDObj('D3')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X3'),
            _data_qubits=[QubitIDObj('D8'), QubitIDObj('D7')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X4'),
            _data_qubits=[QubitIDObj('D9'), QubitIDObj('D8')]
        ),
    ]
    _parity_group_z: List[IParityGroup] = [
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z1'),
            _data_qubits=[QubitIDObj('D4'), QubitIDObj('D5')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z2'),
            _data_qubits=[QubitIDObj('D6'), QubitIDObj('D3')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z3'),
            _data_qubits=[QubitIDObj('D7'), QubitIDObj('D4')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z4'),
            _data_qubits=[QubitIDObj('D5'), QubitIDObj('D6')]
        ),
    ]
    _flux_dances: List[FluxDanceLayer] = [
        FluxDanceLayer(
            _edge_ids=[
                EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D1')),
                EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D4')),
                EdgeIDObj(QubitIDObj('X3'), QubitIDObj('D7')),
                EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D6')),
            ]
        ),
        FluxDanceLayer(
            _edge_ids=[
                EdgeIDObj(QubitIDObj('X1'), QubitIDObj('D2')),
                EdgeIDObj(QubitIDObj('Z1'), QubitIDObj('D5')),
                EdgeIDObj(QubitIDObj('X3'), QubitIDObj('D8')),
                EdgeIDObj(QubitIDObj('Z2'), QubitIDObj('D3')),
            ]
        ),
        FluxDanceLayer(
            _edge_ids=[
                EdgeIDObj(QubitIDObj('Z3'), QubitIDObj('D7')),
                EdgeIDObj(QubitIDObj('X4'), QubitIDObj('D8')),
                EdgeIDObj(QubitIDObj('Z4'), QubitIDObj('D5')),
                EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D2')),
            ]
        ),
        FluxDanceLayer(
            _edge_ids=[
                EdgeIDObj(QubitIDObj('Z3'), QubitIDObj('D4')),
                EdgeIDObj(QubitIDObj('X4'), QubitIDObj('D9')),
                EdgeIDObj(QubitIDObj('Z4'), QubitIDObj('D6')),
                EdgeIDObj(QubitIDObj('X2'), QubitIDObj('D3')),
            ]
        ),
    ]

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
        return Surface17Layer().data_qubit_ids

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        return Surface17Layer().ancilla_qubit_ids
    # endregion

    # region IFluxDanceLayer Interface Properties
    @property
    def flux_dance_count(self) -> int:
        """:return: Number of flux-dances in layer."""
        return len(self._flux_dances)
    # endregion

    # region Class Properties
    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's."""
        return Surface17Layer().feedline_ids

    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: All qubit-ID's."""
        return Surface17Layer().qubit_ids

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: All edge-ID's."""
        return Surface17Layer().edge_ids
    # endregion

    # region ISurfaceCodeLayer Interface Methods
    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> IParityGroup:
        """:return: Parity group of which element (edge- or qubit-ID) is part of."""
        # Assumes element is part of only a single parity group
        for parity_group in self.parity_group_x + self.parity_group_z:
            if parity_group.contains(element=element):
                return parity_group
        raise ElementNotIncludedException(f"Element: {element} is not included in any parity group.")
    
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
    
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        return Surface17Layer().get_neighbors(qubit=qubit, order=order)

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        return Surface17Layer().get_edges(qubit=qubit)

    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        return Surface17Layer().contains(element=element)
    # endregion

    # region IFluxDanceLayer Interface Methods
    def get_flux_dance_at_index(self, index: int) -> FluxDanceLayer:
        """:return: Flux-dance object based on round index."""
        try:
            flux_dance_layer: FluxDanceLayer = self._flux_dances[index]
            return flux_dance_layer
        except:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for flux dance of length: {len(self._flux_dances)}.")

    def get_flux_dance_from_element(self, element: IEdgeID) -> FluxDanceLayer:
        """:return: Flux-dance layer of which edge element is part of."""
        # Assumes element is part of only a single flux-dance layer
        for flux_dance_layer in self._flux_dances:
            if flux_dance_layer.contains(element=element):
                return flux_dance_layer
        raise ElementNotIncludedException(f"Element: {element} is not included in any flux-dance layer.")
    # endregion
