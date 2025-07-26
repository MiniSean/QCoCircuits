# -------------------------------------------
# Module containing interface for inter-qubit interaction gate connectivity.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union, TypeVar, Generic
from enum import Enum, unique, auto
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.connectivity.intrf_channel_identifier import IEdgeID, IQubitID


@unique
class OperationType(Enum):
    IDLE = auto()
    PARK = auto()
    GATE = auto()  # Refers to 2-qubit gate


TIdentifier = TypeVar('TIdentifier', bound=Union[IQubitID, IEdgeID])


@dataclass(frozen=True)
class Operation(Generic[TIdentifier]):
    identifier: TIdentifier
    type: OperationType

    # region Class Methods
    def contains(self, element: TIdentifier) -> bool:
        if self.identifier == element:
            return True
        if isinstance(self.identifier, IEdgeID) and self.identifier.contains(element):
            return True
        return False

    @classmethod
    def type_idle(cls, qubit_id: IQubitID) -> 'Operation':
        return Operation[IQubitID](
            identifier=qubit_id,
            type=OperationType.IDLE,
        )

    @classmethod
    def type_park(cls, qubit_id: IQubitID) -> 'Operation':
        return Operation[IQubitID](
            identifier=qubit_id,
            type=OperationType.PARK,
        )

    @classmethod
    def type_gate(cls, edge_id: IEdgeID) -> 'Operation':
        return Operation[IEdgeID](
            identifier=edge_id,
            type=OperationType.GATE,
        )
    # endregion


@dataclass(frozen=True)
class GateSequenceLayer:
    """
    Data class, containing directional gates played during 'flux-dance' layer.
    """
    _park_operations: List[Operation[IQubitID]]
    """Parking operations, identified by IQubitID."""
    _gate_operations: List[Operation[IEdgeID]]
    """Gate operations, identified by non-directional IEdgeID."""

    # region Class Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: All qubit-ID's, both gate and parking candidates."""
        park_qubits: List[IQubitID] = [operation.identifier for operation in self._park_operations]
        gate_qubits: List[IQubitID] = [identifier for operation in self._gate_operations for identifier in operation.identifier.qubit_ids]
        return unique_in_order(park_qubits + gate_qubits)

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: Array-like of directional edge identifiers, specific for this flux dance."""
        gate_edges: List[IEdgeID] = [operation.identifier for operation in self._gate_operations]
        return unique_in_order(gate_edges)

    @property
    def park_operations(self) -> List[Operation[IQubitID]]:
        """:return: Array-like of parking operations."""
        return self._park_operations

    @property
    def gate_operations(self) -> List[Operation[IEdgeID]]:
        """:return: Array-like of gate operations."""
        return self._gate_operations
    # endregion

    # region Class Methods
    def contains(self, element: Union[IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of flux-dance layer or not."""
        if element in self.qubit_ids:
            return True
        if element in self.edge_ids:
            return True
        return False

    @classmethod
    def empty(cls) -> 'GateSequenceLayer':
        """
        :return: Class method constructor for 'empty' gate-sequence.
        """
        return GateSequenceLayer(
            _park_operations=[],
            _gate_operations=[],
        )
    # endregion


class IGateSequenceLayer(ABC):
    """
    Interface class, describing methods for obtaining flux-dance information.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def gate_sequence_count(self) -> int:
        """:return: Number of gate-sequences in layer."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def involved_qubit_ids(self) -> List[IQubitID]:
        """:return: (Only) involved qubit-ID's in gate sequence."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_gate_sequence_at_index(self, index: int) -> GateSequenceLayer:
        """:return: Gate-sequence object based on round index."""
        raise InterfaceMethodException

    @abstractmethod
    def get_gate_sequence_from_element(self, element: IEdgeID) -> GateSequenceLayer:
        """:return: Gate-sequence layer of which edge element is part of."""
        raise InterfaceMethodException
    # endregion
