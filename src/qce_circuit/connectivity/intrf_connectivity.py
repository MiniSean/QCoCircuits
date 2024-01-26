# -------------------------------------------
# Module containing interface for device connectivity structure.
# -------------------------------------------
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Tuple, Union
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.connectivity.intrf_channel_identifier import (
    IFeedlineID,
    IQubitID,
    IEdgeID,
)


class IIdentifier(ABC):
    """
    Interface class, describing equality identifier method.
    """

    # region Interface Methods
    @abstractmethod
    def __eq__(self, other):
        """:return: Boolean, whether 'other' equals 'self'."""
        raise InterfaceMethodException
    # endregion


class INode(IIdentifier, metaclass=ABCMeta):
    """
    Interface class, describing the node in a connectivity layer.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def edges(self) -> List['IEdge']:
        """:return: (N) Edges connected to this node."""
        raise InterfaceMethodException
    # endregion


class IEdge(IIdentifier, metaclass=ABCMeta):
    """
    Interface class, describing a connection between two nodes.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def nodes(self) -> Tuple[INode, INode]:
        """:return: (2) Nodes connected by this edge."""
        raise InterfaceMethodException
    # endregion


class IConnectivityLayer(ABC):
    """
    Interface class, describing a connectivity (graph) layer containing nodes and edges.
    Note that a connectivity layer can include 'separated' graphs
    where not all nodes have a connection path to all other nodes.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        raise InterfaceMethodException

    @abstractmethod
    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of connectivity layer or not."""
        raise InterfaceMethodException
    # endregion


class IConnectivityStack(ABC):
    """
    Interface class, describing an array-like of connectivity layers.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def layers(self) -> List[IConnectivityLayer]:
        """:return: Array-like of connectivity layers."""
        raise InterfaceMethodException
    # endregion


class IDeviceLayer(IConnectivityLayer, metaclass=ABCMeta):
    """
    Interface class, describing relation based connectivity.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's in device layer."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """:return: Qubit-ID's connected to feedline-ID."""
        raise InterfaceMethodException

    @abstractmethod
    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """:return: Feedline-ID's connected to qubit-ID."""
        raise InterfaceMethodException

    @abstractmethod
    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        raise InterfaceMethodException
    # endregion


if __name__ == '__main__':
    # Connectivity layers:
    # - readout (feedline) layer, all nodes connected to feedline.
    # - bus layer, physical bus-resonator connection from transmon to transmon.
    # - First order connectivity layer.
    # - Second order connectivity layer.
    # - microwave cross-talk layer, indicating microwave cross-talk channels based on cpw cross-overs.
    # - flux cross-talk layer, indicating flux cross-talk channels based on cpw cross-overs.
    pass
