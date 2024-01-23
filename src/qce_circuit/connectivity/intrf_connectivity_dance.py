# -------------------------------------------
# Module containing interface for inter-qubit interaction gate connectivity.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException, ElementNotIncludedException
from qce_circuit.connectivity.intrf_channel_identifier import IEdgeID, IQubitID
from qce_circuit.connectivity.intrf_connectivity import IDeviceLayer
from qce_circuit.connectivity.intrf_connectivity_surface_code import ISurfaceCodeLayer, FrequencyGroupIdentifier


@dataclass(frozen=True)
class FluxDanceLayer:
    """
    Data class, containing directional gates played during 'flux-dance' layer.
    """
    _edge_ids: List[IEdgeID]
    """Non-directional edges, part of flux-dance layer."""

    # region Class Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: All qubit-ID's."""
        return list(set([qubit_id for edge in self.edge_ids for qubit_id in edge.qubit_ids]))

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: Array-like of directional edge identifiers, specific for this flux dance."""
        return self._edge_ids
    # endregion

    # region Class Methods
    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of flux-dance layer or not."""
        if element in self.qubit_ids:
            return True
        if element in self.edge_ids:
            return True
        return False

    def get_involved_edge(self, qubit_id: IQubitID) -> IEdgeID:
        """:return: Edge in which qubit-ID is involved. If qubit-ID not part of self, raise error."""
        for edge in self.edge_ids:
            if edge.contains(element=qubit_id):
                return edge
        raise ElementNotIncludedException(f'Element {qubit_id} is not part of self ({self}) and cannot be part of an edge.')

    def get_spectating_qubit_ids(self, device_layer: IDeviceLayer) -> List[IQubitID]:
        """:return: Direct spectator (nearest neighbor) to qubit-ID's participating in flux-dance."""
        participating_qubit_ids: List[IQubitID] = self.qubit_ids
        nearest_neighbor_ids: List[IQubitID] = [neighbor_id for qubit_id in participating_qubit_ids for neighbor_id in device_layer.get_neighbors(qubit_id, order=1)]
        filtered_nearest_neighbor_ids: List[IQubitID] = list(set([qubit_id for qubit_id in nearest_neighbor_ids if qubit_id not in participating_qubit_ids]))
        return filtered_nearest_neighbor_ids

    def requires_parking(self, qubit_id: IQubitID, device_layer: ISurfaceCodeLayer) -> bool:
        """
        Determines whether qubit-ID is required to park based on participation in flux dance and frequency group.
        :return: Boolean, whether qubit-ID requires some form of parking.
        """
        spectating_qubit_ids: List[IQubitID] = self.get_spectating_qubit_ids(device_layer=device_layer)
        # Guard clause, if qubit-ID does not spectate the flux-dance, no need for parking
        if qubit_id not in spectating_qubit_ids:
            return False
        # Check if qubit-ID requires parking based on its frequency group ID and active two-qubit gates.
        frequency_group: FrequencyGroupIdentifier = device_layer.get_frequency_group_identifier(element=qubit_id)
        # Parking is required if any neighboring qubit from a higher frequency group is part of an edge.
        neighboring_qubit_ids: List[IQubitID] = device_layer.get_neighbors(qubit=qubit_id, order=1)
        involved_neighbors: List[IQubitID] = [qubit_id for qubit_id in neighboring_qubit_ids if self.contains(qubit_id)]
        involved_frequency_groups: List[FrequencyGroupIdentifier] = [device_layer.get_frequency_group_identifier(element=qubit_id) for qubit_id in involved_neighbors]
        return any([neighbor_frequency_group.is_higher_than(frequency_group) for neighbor_frequency_group in involved_frequency_groups])
    # endregion


class IFluxDanceLayer(ABC):
    """
    Interface class, describing methods for obtaining flux-dance information.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def flux_dance_count(self) -> int:
        """:return: Number of flux-dances in layer."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_flux_dance_at_index(self, index: int) -> FluxDanceLayer:
        """:return: Flux-dance object based on round index."""
        raise InterfaceMethodException

    @abstractmethod
    def get_flux_dance_from_element(self, element: IEdgeID) -> FluxDanceLayer:
        """:return: Flux-dance layer of which edge element is part of."""
        raise InterfaceMethodException
    # endregion
