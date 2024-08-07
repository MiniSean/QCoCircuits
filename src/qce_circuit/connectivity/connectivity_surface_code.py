# -------------------------------------------
# Module containing implementation of surface-code connectivity structure.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List, Union, Dict
import numpy as np
from qce_circuit.utilities.singleton_base import SingletonABCMeta
from qce_circuit.utilities.custom_exceptions import ElementNotIncludedException
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.connectivity.intrf_channel_identifier import (
    IFeedlineID,
    IQubitID,
    IEdgeID,
    FeedlineIDObj,
    QubitIDObj,
    EdgeIDObj,
)
from qce_circuit.connectivity.intrf_connectivity import IConnectivityLayer
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    IParityGroup,
    IGateGroup,
    ParityType,
    FrequencyGroup,
    FrequencyGroupIdentifier,
)


@dataclass(frozen=True)
class ParityGroup(IParityGroup):
    """
    Data class, implementing IParityGroup interface.
    """
    _parity_type: ParityType = field(init=True)
    """X or Z type stabilizer."""
    _ancilla_qubit: IQubitID = field(init=True)
    """Ancilla qubit."""
    _data_qubits: List[IQubitID] = field(init=True)
    """Data qubits."""
    _edges: List[IEdgeID] = field(init=False)
    """Edges between ancilla and data qubits."""

    # region Interface Properties
    @property
    def parity_type(self) -> ParityType:
        """:return: Parity type (X or Z type stabilizer)."""
        return self._parity_type

    @property
    def ancilla_id(self) -> IQubitID:
        """:return: (Main) ancilla-qubit-ID from parity."""
        return self._ancilla_qubit

    @property
    def data_ids(self) -> List[IQubitID]:
        """:return: (All) data-qubit-ID's from parity."""
        return self._data_qubits

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's between ancilla and data qubit-ID's."""
        return self._edges
    # endregion

    # region Interface Methods
    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of parity group or not."""
        if element in self.data_ids + [self.ancilla_id]:
            return True
        if element in self.edge_ids:
            return True
        return False
    # endregion

    # region Class Methods
    def __post_init__(self):
        edges: List[IEdgeID] = [
            EdgeIDObj(
                qubit_id0=self.ancilla_id,
                qubit_id1=data_qubit_id,
            )
            for data_qubit_id in self.data_ids
        ]
        object.__setattr__(self, '_edges', edges)
    # endregion


class Surface17Layer(ISurfaceCodeLayer, metaclass=SingletonABCMeta):
    """
    Singleton class, implementing ISurfaceCodeLayer interface to describe a surface-17 layout.
    """
    _feedline_qubit_lookup: Dict[IFeedlineID, List[IQubitID]] = {
        FeedlineIDObj('FL1'): [QubitIDObj('D9'), QubitIDObj('D8'), QubitIDObj('X4'), QubitIDObj('Z4'), QubitIDObj('Z2'), QubitIDObj('D6')],
        FeedlineIDObj('FL2'): [QubitIDObj('D3'), QubitIDObj('D7'), QubitIDObj('D2'), QubitIDObj('X3'), QubitIDObj('Z1'), QubitIDObj('X2'), QubitIDObj('Z3'), QubitIDObj('D5'), QubitIDObj('D4')],
        FeedlineIDObj('FL3'): [QubitIDObj('D1'), QubitIDObj('X1')],
    }
    _qubit_edges: List[IEdgeID] = [
        EdgeIDObj(QubitIDObj('D1'), QubitIDObj('Z1')),
        EdgeIDObj(QubitIDObj('D1'), QubitIDObj('X1')),
        EdgeIDObj(QubitIDObj('D2'), QubitIDObj('X1')),
        EdgeIDObj(QubitIDObj('D2'), QubitIDObj('Z1')),
        EdgeIDObj(QubitIDObj('D2'), QubitIDObj('X2')),
        EdgeIDObj(QubitIDObj('D3'), QubitIDObj('X2')),
        EdgeIDObj(QubitIDObj('D3'), QubitIDObj('Z2')),
        EdgeIDObj(QubitIDObj('D4'), QubitIDObj('Z3')),
        EdgeIDObj(QubitIDObj('D4'), QubitIDObj('X3')),
        EdgeIDObj(QubitIDObj('D4'), QubitIDObj('Z1')),
        EdgeIDObj(QubitIDObj('D5'), QubitIDObj('Z1')),
        EdgeIDObj(QubitIDObj('D5'), QubitIDObj('X3')),
        EdgeIDObj(QubitIDObj('D5'), QubitIDObj('Z4')),
        EdgeIDObj(QubitIDObj('D5'), QubitIDObj('X2')),
        EdgeIDObj(QubitIDObj('D6'), QubitIDObj('X2')),
        EdgeIDObj(QubitIDObj('D6'), QubitIDObj('Z4')),
        EdgeIDObj(QubitIDObj('D6'), QubitIDObj('Z2')),
        EdgeIDObj(QubitIDObj('D7'), QubitIDObj('Z3')),
        EdgeIDObj(QubitIDObj('D7'), QubitIDObj('X3')),
        EdgeIDObj(QubitIDObj('D8'), QubitIDObj('X3')),
        EdgeIDObj(QubitIDObj('D8'), QubitIDObj('X4')),
        EdgeIDObj(QubitIDObj('D8'), QubitIDObj('Z4')),
        EdgeIDObj(QubitIDObj('D9'), QubitIDObj('Z4')),
        EdgeIDObj(QubitIDObj('D9'), QubitIDObj('X4')),
    ]
    _parity_group_x: List[IParityGroup] = [
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X1'),
            _data_qubits=[QubitIDObj('D1'), QubitIDObj('D2')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X2'),
            _data_qubits=[QubitIDObj('D2'), QubitIDObj('D3'), QubitIDObj('D5'), QubitIDObj('D6')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X3'),
            _data_qubits=[QubitIDObj('D4'), QubitIDObj('D5'), QubitIDObj('D7'), QubitIDObj('D8')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_X,
            _ancilla_qubit=QubitIDObj('X4'),
            _data_qubits=[QubitIDObj('D8'), QubitIDObj('D9')]
        ),
    ]
    _parity_group_z: List[IParityGroup] = [
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z1'),
            _data_qubits=[QubitIDObj('D1'), QubitIDObj('D2'), QubitIDObj('D4'), QubitIDObj('D5')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z2'),
            _data_qubits=[QubitIDObj('D3'), QubitIDObj('D6')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z3'),
            _data_qubits=[QubitIDObj('D4'), QubitIDObj('D7')]
        ),
        ParityGroup(
            _parity_type=ParityType.STABILIZER_Z,
            _ancilla_qubit=QubitIDObj('Z4'),
            _data_qubits=[QubitIDObj('D5'), QubitIDObj('D6'), QubitIDObj('D8'), QubitIDObj('D9')]
        ),
    ]
    _frequency_group_lookup: Dict[IQubitID, FrequencyGroupIdentifier] = {
        QubitIDObj('D1'): FrequencyGroupIdentifier(_id=FrequencyGroup.LOW),
        QubitIDObj('D2'): FrequencyGroupIdentifier(_id=FrequencyGroup.LOW),
        QubitIDObj('D3'): FrequencyGroupIdentifier(_id=FrequencyGroup.LOW),
        QubitIDObj('D4'): FrequencyGroupIdentifier(_id=FrequencyGroup.HIGH),
        QubitIDObj('D5'): FrequencyGroupIdentifier(_id=FrequencyGroup.HIGH),
        QubitIDObj('D6'): FrequencyGroupIdentifier(_id=FrequencyGroup.HIGH),
        QubitIDObj('D7'): FrequencyGroupIdentifier(_id=FrequencyGroup.LOW),
        QubitIDObj('D8'): FrequencyGroupIdentifier(_id=FrequencyGroup.LOW),
        QubitIDObj('D9'): FrequencyGroupIdentifier(_id=FrequencyGroup.LOW),
        QubitIDObj('Z1'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('Z2'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('Z3'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('Z4'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('X1'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('X2'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('X3'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
        QubitIDObj('X4'): FrequencyGroupIdentifier(_id=FrequencyGroup.MID),
    }

    # region IDeviceLayer Interface Properties
    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's in device layer."""
        return list(self._feedline_qubit_lookup.keys())

    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        return [qubit_id for qubit_ids in self._feedline_qubit_lookup.values() for qubit_id in qubit_ids]

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        return self._qubit_edges
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
        all_qubit_ids: List[IQubitID] = self.qubit_ids
        ancilla_qubit_ids: List[IQubitID] = self.ancilla_qubit_ids
        return [qubit_id for qubit_id in all_qubit_ids if qubit_id not in ancilla_qubit_ids]

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        return [parity_group.ancilla_id for parity_group in self.parity_group_x + self.parity_group_z]
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
        return self._frequency_group_lookup[element]
    # endregion

    # region IDeviceLayer Interface Methods
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """:return: Qubit-ID's connected to feedline-ID."""
        # Guard clause, if feedline not in lookup, raise exception
        if feedline not in self._feedline_qubit_lookup:
            raise ElementNotIncludedException(f"Element: {feedline} is not included in any feedline group.")
        return self._feedline_qubit_lookup[feedline]

    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """:return: Feedline-ID's connected to qubit-ID."""
        for feedline_id in self.feedline_ids:
            if qubit in self.get_connected_qubits(feedline=feedline_id):
                return feedline_id
        raise ElementNotIncludedException(f"Element: {qubit} is not included in any feedline.")

    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        if order > 1:
            raise NotImplementedError("Apologies, so far there has not been a use for. But feel free to implement.")
        edges: List[IEdgeID] = self.get_edges(qubit=qubit)
        result: List[IQubitID] = []
        for edge in edges:
            result.append(edge.get_connected_qubit_id(element=qubit))
        return result

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        result: List[IEdgeID] = []
        for edge in self.edge_ids:
            if edge.contains(element=qubit):
                result.append(edge)
        return result

    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        if element in self.feedline_ids:
            return True
        if element in self.qubit_ids:
            return True
        if element in self.edge_ids:
            return True
        return False
    # endregion


def get_neighbors(element: Union[IQubitID, IEdgeID], connectivity: IConnectivityLayer, order: int = 1) -> List[IQubitID]:
    """
    Functionality for both qubit-ID and edge-ID.
    Requires :param order: to be higher or equal to 1.
    :return: qubit neighbors separated by order. (order=1, nearest neighbors).
    """
    if isinstance(element, IQubitID):
        return connectivity.get_neighbors(element, order=order)
    elif isinstance(element, IEdgeID):
        combined_neighbors: List[IQubitID] = []
        for qubit_id in element.qubit_ids:
            combined_neighbors.extend(connectivity.get_neighbors(qubit_id, order=order))
        return unique_in_order(combined_neighbors)
    raise NotImplementedError(f"Finding the neighbor qubits of element with type {type(element)} is not supported. Try {IQubitID} or {IEdgeID}.")


def on_moving_side(qubit_id: IQubitID, edge_id: IEdgeID, connectivity: ISurfaceCodeLayer) -> bool:
    """:return: True if qubit is the higher-frequency qubit of the edge, otherwise False."""
    if not edge_id.contains(qubit_id):
        return False
    qubit_frequency_identifier = connectivity.get_frequency_group_identifier(qubit_id)
    other_frequency_identifier = connectivity.get_frequency_group_identifier(edge_id.get_connected_qubit_id(qubit_id))
    return qubit_frequency_identifier.is_higher_than(other_frequency_identifier)


def get_requires_parking(element: IQubitID, edge_ids: List[IEdgeID], connectivity: ISurfaceCodeLayer) -> bool:
    """
    Determines whether qubit-ID is required to park based on participation in flux dance and frequency group.
    :return: Boolean, whether qubit-ID requires some form of parking.
    """
    spectator: bool = np.any([element in get_neighbors(edge_id, connectivity) for edge_id in edge_ids])
    # Guard clause, if qubit-ID does not spectate the flux-dance, no hard requirement for parking
    if not spectator:
        return False
    # Guard clause, if qubit-ID is part of edge-ID's, no hard requirement for parking
    edge_included: bool = np.any([edge_id.contains(element) for edge_id in edge_ids])
    if edge_included:
        return False

    # Check if qubit-ID requires parking based on its frequency group ID and active two-qubit gates.
    frequency_group: FrequencyGroupIdentifier = connectivity.get_frequency_group_identifier(element=element)
    # Parking is required if any neighboring qubit from a higher frequency group is part of an edge.
    neighboring_qubit_ids: List[IQubitID] = connectivity.get_neighbors(qubit=element, order=1)
    involved_qubits: List[IQubitID] = [qubit_id for edge_id in edge_ids for qubit_id in edge_id.qubit_ids]
    involved_edges: List[IEdgeID] = [edge_id for edge_id in edge_ids for _ in edge_id.qubit_ids]
    involved_neighbors: List[IQubitID] = [qubit_id for qubit_id in neighboring_qubit_ids if qubit_id in involved_qubits]
    involved_neighbor_edges: List[IEdgeID] = [involved_edges[involved_qubits.index(qubit_id)] for qubit_id in neighboring_qubit_ids if qubit_id in involved_qubits]
    involved_frequency_groups: List[FrequencyGroupIdentifier] = [connectivity.get_frequency_group_identifier(element=qubit_id) for qubit_id in involved_neighbors]
    return any([
        neighbor_frequency_group.is_higher_than(frequency_group) and on_moving_side(neighbor_qubit_id, neighbor_edge_id, connectivity)
        for neighbor_qubit_id, neighbor_frequency_group, neighbor_edge_id in zip(involved_neighbors, involved_frequency_groups, involved_neighbor_edges)
    ])


def get_higher_frequency_qubit_id(edge_id: IEdgeID, connectivity: ISurfaceCodeLayer) -> IQubitID:
    """:return: Higher frequency qubit-ID based on which qubit is on the 'moving' side of the gate (edge)."""
    potential_qubit_id: IQubitID = edge_id.qubit_ids[0]
    if on_moving_side(qubit_id=potential_qubit_id, edge_id=edge_id, connectivity=connectivity):
        return potential_qubit_id
    return edge_id.get_connected_qubit_id(potential_qubit_id)


def get_lower_frequency_qubit_id(edge_id: IEdgeID, connectivity: ISurfaceCodeLayer) -> IQubitID:
    """:return: Lower frequency qubit-ID based on which qubit is NOT on the 'moving' side of the gate (edge)."""
    potential_qubit_id: IQubitID = edge_id.qubit_ids[0]
    if not on_moving_side(qubit_id=potential_qubit_id, edge_id=edge_id, connectivity=connectivity):
        return potential_qubit_id
    return edge_id.get_connected_qubit_id(potential_qubit_id)