# -------------------------------------------
# Module containing interface and implementation of (declarative) circuit operation.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from functools import lru_cache
from enum import unique, Enum, auto
from typing import TypeVar, Generic, List, Dict, Optional
from warnings import warn
from qce_circuit.utilities.custom_exceptions import (
    InterfaceMethodException,
    RelationTypeNotImplementedException,
)
from qce_circuit.utilities.custom_warnings import OperationNotFoundWarning


@unique
class QubitChannel(Enum):
    """
    Enumerator class, describing different channels for each qubit.
    RO (readout-channel), MW (microwave-channel), FL (flux-channel).
    """
    READOUT = auto()
    """Channel reserved for readout operations."""
    MICROWAVE = auto()
    """Channel reserved for microwave operations."""
    FLUX = auto()
    """Channel reserved for AC/DC flux bias operations."""
    ALL = auto()
    """Channel indicating participation in all of the above."""


@unique
class RelationType(Enum):
    """
    Enumerator class, describing (scheduling) relation type.
    """
    FOLLOWED_BY = auto()
    """Relationship by following element back-to-back."""
    JOINED_START = auto()
    """Relationship by starting together with other element."""
    JOINED_END = auto()
    """Relationship by ending together with other element."""


@unique
class MultiRelationType(Enum):
    """
    Enumerator class, describing (scheduling) relation type with respect to multiple elements.
    """
    EARLIEST = auto()
    """Relationship based on earliest element in the group."""
    LATEST = auto()
    """Relationship based on latest element in the group."""


class ICircuitNode(ABC):
    """
    Interface class, placeholder.
    """


class IRepetitionComponent(ABC):
    """
    Interface class, describing number of repetitions for this object.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        raise InterfaceMethodException
    # endregion


class IDurationComponent(ABC):
    """
    Interface class, describing a variable duration object.
    Exposes getter for duration value.
    Operations are encouraged to work with duration-strategies instead of fixed values.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def duration(self) -> float:
        """:return: Duration [a.u.]."""
        raise InterfaceMethodException

    @property
    def end_time(self) -> float:
        """:return: End time [a.u.]."""
        return self.start_time + self.duration
    # endregion


TDurationComponent = TypeVar('TDurationComponent', bound=IDurationComponent)


class IRelationLink(ABC, Generic[TDurationComponent]):
    """
    Interface class, describing relation between nodes.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def reference_node(self) -> Optional[TDurationComponent]:
        """:return: (Optional) Node which this relation references to."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def relation_type(self) -> RelationType:
        """:return: Type of relation to reference node."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_start_time(self, duration: float) -> float:
        """:return: Start time based on reference and self-duration."""
        raise InterfaceMethodException

    @abstractmethod
    def copy(self, relation_transfer_lookup: Optional[Dict[TDurationComponent, TDurationComponent]] = None) -> 'IRelationLink':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: (Optional) Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class RelationLink(IRelationLink[TDurationComponent], Generic[TDurationComponent]):
    """
    Data class, implementing IRelationLink interface.
    """
    _reference_node: Optional[TDurationComponent]
    _relation_type: RelationType = field(default=RelationType.FOLLOWED_BY)

    # region Interface Properties
    @property
    def reference_node(self) -> Optional[TDurationComponent]:
        """:return: (Optional) Node which this relation references to."""
        return self._reference_node

    @property
    def relation_type(self) -> RelationType:
        """:return: Type of relation to reference node."""
        return self._relation_type
    # endregion

    # region Interface Methods
    @lru_cache(maxsize=None)
    def get_start_time(self, duration: float) -> float:
        """:return: Start time based on reference and self-duration."""
        if self.reference_node is None:
            return 0.0
        if self._relation_type == RelationType.FOLLOWED_BY:
            return self.reference_node.end_time
        if self._relation_type == RelationType.JOINED_START:
            return self.reference_node.start_time
        if self._relation_type == RelationType.JOINED_END:
            return self.reference_node.end_time - duration
        raise RelationTypeNotImplementedException(f"Relation type: {self._relation_type}, not implemented.")

    def copy(self, relation_transfer_lookup: Optional[Dict[TDurationComponent, TDurationComponent]] = None) -> 'RelationLink':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: (Optional) Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        if relation_transfer_lookup is None:
            relation_transfer_lookup = {}
        transferred_reference_node: Optional[TDurationComponent] = relation_transfer_lookup.get(self._reference_node, None)

        return RelationLink(
            _reference_node=transferred_reference_node,
            _relation_type=self._relation_type,
        )
    # endregion

    # region Class Methods
    def __repr__(self):
        return f"<RelationLink>{self.reference_node.__class__.__name__}[{self._relation_type.name}]"

    @classmethod
    def no_relation(cls) -> 'RelationLink':
        """:return: Class method constructor for generating no-relation link (default)."""
        return RelationLink(
            _reference_node=None,
        )
    # endregion


@dataclass(frozen=True)
class ChannelIdentifier:
    """
    Data class, qubit (circuit) channel identifier.
    """
    _id: int = field(init=True, compare=True)
    _channel: QubitChannel = field(init=True, compare=True, default=QubitChannel.ALL)

    # region Class Properties
    @property
    def id(self) -> int:
        return self._id

    @property
    def channel(self) -> QubitChannel:
        return self._channel
    # endregion

    # region Class Methods
    def __eq__(self, other):
        """
        Implement equality check. Proceeds as normal, but if qubit channel is ALL, force equality.
        :param other:
        :return:
        """
        if not isinstance(other, ChannelIdentifier):
            return False
        # Updated equality
        equal_id: bool = self.id == other.id
        equal_channel: bool = self.channel == other.channel
        qubit_channel_included: bool = self.channel == QubitChannel.ALL or other.channel == QubitChannel.ALL
        if equal_id and equal_channel:
            return True
        if equal_id and qubit_channel_included:
            return True
        return False

    def __repr__(self) -> str:
        """:returns: Reference Identifier."""
        return f"#{self._id}-{self._channel}"
    # endregion


class IRelationComponent(ABC, Generic[TDurationComponent]):
    """
    Interface class, describing relation to other ICircuitOperations.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def relation_link(self) -> IRelationLink[TDurationComponent]:
        """:return: Description of relation to other circuit node."""
        raise InterfaceMethodException

    @relation_link.setter
    @abstractmethod
    def relation_link(self, link: IRelationLink[TDurationComponent]):
        """:sets: Description of relation to other circuit node."""
        raise InterfaceMethodException

    @property
    def has_relation(self) -> bool:
        """:return: Boolean, whether relation link is established."""
        return self.relation_link.reference_node is not None
    # endregion


class ICircuitOperation(ICircuitNode, IRelationComponent['ICircuitOperation'], IDurationComponent, IRepetitionComponent, metaclass=ABCMeta):
    """
    Interface class, exposing properties and methods for a single gate/operation.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def copy(self, relation_transfer_lookup: Optional[Dict['ICircuitOperation', 'ICircuitOperation']] = None) -> 'ICircuitOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        raise InterfaceMethodException

    @abstractmethod
    def apply_modifiers_to_self(self) -> 'ICircuitOperation':
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        raise InterfaceMethodException

    @abstractmethod
    def decomposed_operations(self) -> List['ICircuitOperation']:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        raise InterfaceMethodException
    # endregion

    # region Class Methods
    def __hash__(self):
        """Overwrites @dataclass behaviour. Circuit operation requires hash based on instance identity."""
        return id(self)
    # endregion


TCircuitOperation = TypeVar('TCircuitOperation', bound=ICircuitOperation)


@dataclass(frozen=True)
class MultiRelationLink(IRelationLink[TCircuitOperation], Generic[TCircuitOperation]):
    """
    Data class, implementing IRelationLink interface.
    References multiple reference nodes and links to 'latest'.
    """
    _reference_nodes: List[TCircuitOperation] = field(compare=False)
    _relation_to_group: MultiRelationType = field(default=MultiRelationType.LATEST)
    _relation_type: RelationType = field(default=RelationType.FOLLOWED_BY)

    # region Interface Properties
    @property
    def reference_node(self) -> Optional[TDurationComponent]:
        """:return: (Optional) Node which this relation references to."""
        # Guard clause, raise warning if no reference nodes are specified
        if len(self._reference_nodes) == 0:
            # raise NoReferenceOperationException(f"Expects at least 1 reference node, instead: {self._reference_nodes}.")
            return None
        # Iterate over reference node and determine latest
        latest_node: TCircuitOperation = self._reference_nodes[0]
        for node in self._reference_nodes:
            if node.end_time > latest_node.end_time:
                latest_node = node
        return latest_node

    @property
    def relation_type(self) -> RelationType:
        """:return: Type of relation to reference node."""
        return self._relation_type
    # endregion

    # region Interface Methods
    @lru_cache(maxsize=None)
    def get_start_time(self, duration: float) -> float:
        """:return: Start time based on reference and self-duration."""
        relation_link: RelationLink = RelationLink(
            _reference_node=self.reference_node,
            _relation_type=self.relation_type,
        )
        return relation_link.get_start_time(duration=duration)

    def copy(self, relation_transfer_lookup: Optional[Dict[TDurationComponent, TDurationComponent]] = None) -> 'MultiRelationLink':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: (Optional) Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        if relation_transfer_lookup is None:
            relation_transfer_lookup = {}

        transferred_reference_operations: List[TDurationComponent] = []
        for operation in self._reference_nodes:
            if operation not in relation_transfer_lookup:
                warn(**OperationNotFoundWarning.warning_format(value=operation.__class__.__name__))
                continue
            # Populated transferred reference operations
            transferred_reference_operations.append(relation_transfer_lookup[operation])

        return MultiRelationLink(
            _reference_nodes=transferred_reference_operations,
            _relation_to_group=self._relation_to_group,
            _relation_type=self._relation_type,
        )
    # endregion

    # region Class Methods
    def __repr__(self):
        return f"<RelationLinks>{[node.__class__.__name__ for node in self._reference_nodes]}[{self._relation_type.name}, {self._relation_to_group.name}]"
    # endregion
