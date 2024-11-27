# -------------------------------------------
# Module containing interface for surface-code connectivity structure.
# -------------------------------------------
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import List, Union
from enum import Enum, unique, auto
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.connectivity.intrf_channel_identifier import (
    IQubitID,
    IEdgeID,
)
from qce_circuit.connectivity.intrf_connectivity import IDeviceLayer


@unique
class StabilizerType(Enum):
    STABILIZER_X = 0
    STABILIZER_Z = 1


class IParityGroup(ABC):
    """
    Interface class, describing qubit (nodes) and edges related to the parity group.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def parity_type(self) -> StabilizerType:
        """:return: Parity type (X or Z type stabilizer)."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def ancilla_id(self) -> IQubitID:
        """:return: (Main) ancilla-qubit-ID from parity."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def data_ids(self) -> List[IQubitID]:
        """:return: (All) data-qubit-ID's from parity."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's between ancilla and data qubit-ID's."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of parity group or not."""
        raise InterfaceMethodException
    # endregion


class IGateGroup(ABC):
    """
    Interface class, describing 2-qubit gate (edge) and corresponding 'spectator' qubits (nodes).
    Spectators are nearest neighbors around both qubits involved in the 2-qubit gate.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def gate_id(self) -> IEdgeID:
        """:return: Edge involved in the 2-qubit gate."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def involved_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's (directly) involved with 2-qubit gate."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def spectator_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's (indirectly) involved with 2-qubit gate."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of gate group or not."""
        raise InterfaceMethodException

    @abstractmethod
    def get_spectator_edge(self, spectator: IQubitID) -> IEdgeID:
        """
        Checks if spectator is part of group-spectators, if not raise ElementNotIncludedException.
        :return: Edge that links spectator to one of the involved qubits.
        """
        raise InterfaceMethodException
    # endregion


@unique
class FrequencyGroup(Enum):
    LOW = auto()
    MID = auto()
    HIGH = auto()


@dataclass(frozen=True)
class FrequencyGroupIdentifier:
    """
    Data class, representing (qubit) frequency group identifier.
    """
    _id: FrequencyGroup

    # region Class Properties
    @property
    def id(self) -> FrequencyGroup:
        """:return: Self identifier."""
        return self._id
    # endregion

    # region Class Methods
    def is_equal_to(self, other: 'FrequencyGroupIdentifier') -> bool:
        """:return: Boolean, whether other frequency group identifier is equal self."""
        return self.id == other.id

    def is_higher_than(self, other: 'FrequencyGroupIdentifier') -> bool:
        """:return: Boolean, whether other frequency group identifier is 'lower' than self."""
        # Guard clause, if frequency groups are equal, return False
        if self.is_equal_to(other):
            return False
        if self.id == FrequencyGroup.MID and other.id == FrequencyGroup.LOW:
            return True
        if self.id == FrequencyGroup.HIGH:
            return True
        return False

    def is_lower_than(self, other: 'FrequencyGroupIdentifier') -> bool:
        """:return: Boolean, whether other frequency group identifier is 'higher' than self."""
        # Guard clause, if frequency groups are equal, return False
        if self.is_equal_to(other):
            return False
        if self.is_higher_than(other):
            return False
        return True
    # endregion


class ISurfaceCodeLayer(IDeviceLayer, metaclass=ABCMeta):
    """
    Interface class, describing surface-code relation based connectivity.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def parity_group_x(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of X-stabilizers."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def parity_group_z(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of Z-stabilizers."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (Data) qubit-ID's in device layer."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> List[IParityGroup]:
        """:return: Parity group(s) of which element (edge- or qubit-ID) is part of."""
        raise InterfaceMethodException
    
    @abstractmethod
    def get_frequency_group_identifier(self, element: IQubitID) -> FrequencyGroupIdentifier:
        """:return: Frequency group identifier based on qubit-ID."""
        raise InterfaceMethodException
    # endregion
