# -------------------------------------------
# Module describing the declarative operations.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.intrf_circuit_operation import (
    QubitChannel,
    IRelationLink,
    RelationLink,
    ChannelIdentifier,
    ICircuitOperation,
    ITwoQubitOperation,
)
from qce_circuit.structure.intrf_acquisition_operation import (
    IAcquisitionOperation,
    AcquisitionIdentifier,
)
from qce_circuit.structure.registry_duration import (
    IDurationStrategy,
    FixedDurationStrategy,
    GlobalDurationStrategy,
    GlobalRegistryKey,
)
from qce_circuit.structure.registry_acquisition import (
    IAcquisitionStrategy,
)


@dataclass(frozen=False, unsafe_hash=True)
class SingleQubitOperation(ICircuitOperation):
    """
    Minimal operation describes single-qubit implementation of ICircuitOperation.
    """
    qubit_index: int = field(init=True)
    relation: IRelationLink[ICircuitOperation] = field(default_factory=RelationLink.no_relation)
    duration_strategy: IDurationStrategy = field(default=FixedDurationStrategy(duration=0.0))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.ALL),
        ]

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return 1

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.relation_link.get_start_time(duration=self.duration)

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.duration_strategy.get_variable_duration(task=self)
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'SingleQubitOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return SingleQubitOperation(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            duration_strategy=self.duration_strategy,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Reset(SingleQubitOperation, ICircuitOperation):
    """
    Reset operation covers all qubit channels.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.RESET))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.ALL),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Reset':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Reset(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Wait(SingleQubitOperation, ICircuitOperation):
    """
    Wait (delay) operation.
    Allow to wait on specific (qubit) channel.
    """
    qubit_channel: QubitChannel = field(init=True, default=QubitChannel.ALL)
    duration_strategy: IDurationStrategy = field(init=True, default=FixedDurationStrategy(duration=0.0))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=self.qubit_channel),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Wait':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Wait(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            qubit_channel=self.qubit_channel,
            duration_strategy=self.duration_strategy,
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Identity(SingleQubitOperation, ICircuitOperation):
    """
    Identity operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Identity':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Identity(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Hadamard(SingleQubitOperation, ICircuitOperation):
    """
    Hadamard operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Hadamard':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Hadamard(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Rx180(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-X (180 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Rx180':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Rx180(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Rx90(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-X (90 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Rx90':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Rx90(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Rxm90(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-X (-90 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Rxm90':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Rxm90(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class RxTheta(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-X (theta degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'RxTheta':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return RxTheta(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Ry180(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-Y (180 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Ry180':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Ry180(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Ry90(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-Y (90 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Ry90':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Ry90(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Rym90(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-Y (-90 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Rym90':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Rym90(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class RyTheta(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-Y (theta degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'RyTheta':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return RyTheta(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Rx180ef(SingleQubitOperation, ICircuitOperation):
    """
    Rotation-X (180 degrees) operation between excited (e) and second-excited (f) state.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Rx180ef':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Rx180ef(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualPhase(SingleQubitOperation, ICircuitOperation):
    """
    Virtual (Z) phase rotation operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualPhase':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualPhase(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualPark(SingleQubitOperation, ICircuitOperation):
    """
    Virtual park operation.
    Usually only interesting when working with frequency-tunable qubits.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.FLUX))
    net_zero: bool = field(init=True, default=False)
    """Boolean describing the net-zero behaviour of the virtual parking. - Mainly useful for visualization."""

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.FLUX),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualPark':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualPark(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class Rphi90(SingleQubitOperation, ICircuitOperation):
    """
    Rotation- [Xcos(phi) + Ysin(phi)] (90 degrees) operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Rphi90':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Rphi90(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class TwoQubitOperation(ITwoQubitOperation):
    """
    Minimal operation describes two-qubit implementation of ICircuitOperation.
    """
    _control_qubit_index: int = field(init=True)
    _target_qubit_index: int = field(init=True)
    relation: IRelationLink[ICircuitOperation] = field(default_factory=RelationLink.no_relation)
    duration_strategy: IDurationStrategy = field(default=FixedDurationStrategy(duration=0.0))

    # region ICircuitOperation Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.control_qubit_index, _channel=QubitChannel.ALL),
            ChannelIdentifier(_id=self.target_qubit_index, _channel=QubitChannel.ALL),
        ]

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return 1

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.relation_link.get_start_time(duration=self.duration)

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.duration_strategy.get_variable_duration(task=self)
    # endregion

    # region ITwoQubitOperation Properties
    @property
    def control_qubit_index(self) -> int:
        """:return: Index of control qubit."""
        return self._control_qubit_index

    @property
    def target_qubit_index(self) -> int:
        """:return: Index of target qubit."""
        return self._target_qubit_index
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'TwoQubitOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return TwoQubitOperation(
            _control_qubit_index=self.control_qubit_index,
            _target_qubit_index=self.target_qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            duration_strategy=self.duration_strategy,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class CPhase(TwoQubitOperation, ICircuitOperation):
    """
    Control-Phase operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.FLUX))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.control_qubit_index, _channel=QubitChannel.FLUX),
            ChannelIdentifier(_id=self.control_qubit_index, _channel=QubitChannel.MICROWAVE),
            ChannelIdentifier(_id=self.target_qubit_index, _channel=QubitChannel.FLUX),
            ChannelIdentifier(_id=self.target_qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'CPhase':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return CPhase(
            _control_qubit_index=self.control_qubit_index,
            _target_qubit_index=self.target_qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class TwoQubitVirtualPhase(TwoQubitOperation, ICircuitOperation):
    """
    Virtual (Z) phase rotation operation.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=FixedDurationStrategy(duration=0.0))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.control_qubit_index, _channel=QubitChannel.MICROWAVE),
            ChannelIdentifier(_id=self.target_qubit_index, _channel=QubitChannel.MICROWAVE),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'TwoQubitVirtualPhase':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return TwoQubitVirtualPhase(
            _control_qubit_index=self.control_qubit_index,
            _target_qubit_index=self.target_qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class DispersiveMeasure(IAcquisitionOperation):
    """
    Dispersive measure operation.
    """
    qubit_index: int = field(init=True, repr=True)
    acquisition_strategy: IAcquisitionStrategy = field(init=True, repr=False)
    acquisition_tag: str = field(init=True, default='', repr=True)
    relation: IRelationLink[ICircuitOperation] = field(default_factory=RelationLink.no_relation, repr=False)
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.READOUT), repr=False)
    _acquisition_identifier: AcquisitionIdentifier = field(init=False, repr=False)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.READOUT),
        ]

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return 1

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.relation_link.get_start_time(duration=self.duration)

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.duration_strategy.get_variable_duration(task=self)

    @property
    def acquisition_identifier(self) -> AcquisitionIdentifier:
        """:return: Unique acquisition identifier."""
        return self._acquisition_identifier

    @property
    def acquisition_index(self) -> int:
        """
        :return: Unique acquisition index on qubit level.
        Every (measure) operation acquisition is processed at its own index.
        """
        return self.acquisition_strategy.get_acquisition_info(task=self).qubit_level_index

    @property
    def circuit_level_acquisition_index(self) -> int:
        """
        :return: Unique acquisition index on circuit level.
        Every (measure) operation acquisition is processed at its own index.
        """
        return self.acquisition_strategy.get_acquisition_info(task=self).circuit_level_index
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'DispersiveMeasure':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return DispersiveMeasure(
            qubit_index=self.qubit_index,
            acquisition_strategy=self.acquisition_strategy.copy(strategy_transfer_lookup=relation_transfer_lookup),
            acquisition_tag=self.acquisition_tag,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )

    def apply_modifiers_to_self(self) -> IAcquisitionOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[IAcquisitionOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion

    # region Class Methods
    def __post_init__(self):
        object.__setattr__(self, '_acquisition_identifier', AcquisitionIdentifier(
            qubit_index=self.qubit_index,
            tag=self.acquisition_tag,
        ))
    # endregion


@dataclass(frozen=False)
class Barrier(ICircuitOperation):
    """
    Multi-qubit barrier operation. Forces time-wise separation of operations.
    """
    qubit_indices: List[int] = field(init=True)
    relation: IRelationLink[ICircuitOperation] = field(init=False, default_factory=RelationLink.no_relation)
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.BARRIER))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=qubit_index, _channel=QubitChannel.ALL)
            for qubit_index in self.qubit_indices
        ]

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return 1

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.relation_link.get_start_time(duration=self.duration)

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.duration_strategy.get_variable_duration(task=self)
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'Barrier':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return Barrier(
            qubit_indices=self.qubit_indices,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion

    # region Class Methods
    def __hash__(self):
        """Overwrites @dataclass behaviour. Circuit operation requires hash based on instance identity."""
        return id(self)
    # endregion


@dataclass(frozen=False)
class VirtualQECOperation(ICircuitOperation):
    """
    Virtual QEC-block operation.
    """
    qubit_indices: List[int] = field(init=True)
    relation: IRelationLink[ICircuitOperation] = field(default_factory=RelationLink.no_relation)
    duration_strategy: IDurationStrategy = field(default=GlobalDurationStrategy(GlobalRegistryKey.QEC_BLOCK))

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=qubit_index, _channel=QubitChannel.ALL)
            for qubit_index in self.qubit_indices
        ]

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return 1

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.relation_link.get_start_time(duration=self.duration)

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.duration_strategy.get_variable_duration(task=self)
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualQECOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualQECOperation(
            qubit_indices=self.qubit_indices,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            duration_strategy=self.duration_strategy,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion

    # region Class Methods
    def __hash__(self):
        """Overwrites @dataclass behaviour. Circuit operation requires hash based on instance identity."""
        return id(self)
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualVacant(SingleQubitOperation, ICircuitOperation):
    """
    Virtual vacant operation (behaves as Wait).
    Allow to wait on specific (qubit) channel.
    """
    qubit_channel: QubitChannel = field(init=True, default=QubitChannel.ALL)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=self.qubit_channel),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualVacant':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualVacant(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            qubit_channel=self.qubit_channel,
            duration_strategy=self.duration_strategy,
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualTwoQubitVacant(TwoQubitOperation, ICircuitOperation):
    """
    Virtual vacant operation (behaves as TwoQubitOperation).
    Allow to wait on specific (qubit) channel.
    """
    qubit_channel: QubitChannel = field(init=True, default=QubitChannel.ALL)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.control_qubit_index, _channel=self.qubit_channel),
            ChannelIdentifier(_id=self.target_qubit_index, _channel=self.qubit_channel),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualTwoQubitVacant':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualTwoQubitVacant(
            _control_qubit_index=self.control_qubit_index,
            _target_qubit_index=self.target_qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualEmpty(SingleQubitOperation, ICircuitOperation):
    """
    Virtual empty position (behaves as Wait).
    Allow to wait on specific (qubit) channel.
    """
    qubit_channel: QubitChannel = field(init=True, default=QubitChannel.ALL)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=self.qubit_channel),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualEmpty':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualEmpty(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            qubit_channel=self.qubit_channel,
            duration_strategy=self.duration_strategy,
        )
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualOptional(ICircuitOperation):
    """
    Data class, containing single-qubit operation.
    Acts as a visualization wrapper.
    """
    operation: ICircuitOperation

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return self.operation.channel_identifiers

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return self.operation.nr_of_repetitions

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.operation.relation_link

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.operation.relation_link = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.operation.start_time

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.operation.duration
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualOptional':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualOptional(
            operation=self.operation.copy(
                relation_transfer_lookup=relation_transfer_lookup,
            )
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualInjectedError(ICircuitOperation):
    """
    Data class, containing single-qubit operation.
    Acts as a visualization wrapper for injected errors.
    """
    operation: SingleQubitOperation
    line_style_border_overwrite: str = field(default="--")
    color_background_overwrite: str = field(default="#ff9999")

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return self.operation.channel_identifiers

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return self.operation.nr_of_repetitions

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.operation.relation

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.operation.relation = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.operation.start_time

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.operation.duration
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualInjectedError':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualInjectedError(
            operation=self.operation.copy(
                relation_transfer_lookup=relation_transfer_lookup,
            ),
            line_style_border_overwrite=self.line_style_border_overwrite,
            color_background_overwrite=self.color_background_overwrite,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualWait(SingleQubitOperation, ICircuitOperation):
    """
    Virtual wait position (behaves as Wait).
    Allow to wait on specific (qubit) channel.
    Intended to display wait time.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=GlobalDurationStrategy(GlobalRegistryKey.MICROWAVE))
    qubit_channel: QubitChannel = field(init=True, default=QubitChannel.ALL)
    header_text: str = field(init=True, default="W")
    body_text: str = field(init=True, default="")

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=self.qubit_channel),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualWait':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualWait(
            qubit_index=self.qubit_index,
            relation=self.relation.copy(relation_transfer_lookup=relation_transfer_lookup),
            qubit_channel=self.qubit_channel,
            header_text=self.header_text,
            body_text=self.body_text,
        )
    # endregion


class IColorOverwrite(ABC):

    # region Interface Properties
    @property
    @abstractmethod
    def wrapped_operation(self) -> ICircuitOperation:
        """:return: Wrapped operation used to pass to sub-draw factories."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def color_overwrite(self) -> str:
        """:return: Color identifier for overwriting draw factory colors."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualColorOverwrite(ICircuitOperation, IColorOverwrite):
    """
    Data class, containing single-qubit operation.
    Acts as a visualization wrapper for coloring visualization.
    """
    operation: ICircuitOperation
    _color_overwrite: str = field(init=True, default="k")

    # region ICircuitOperation Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return self.operation.channel_identifiers

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return self.operation.nr_of_repetitions

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.operation.relation_link

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.operation.relation_link = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.operation.start_time

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.operation.duration
    # endregion

    # region IColorOverwrite Properties
    @property
    def wrapped_operation(self) -> ICircuitOperation:
        """:return: Wrapped operation used to pass to sub-draw factories."""
        return self.operation

    @property
    def color_overwrite(self) -> str:
        """:return: Color identifier for overwriting draw factory colors."""
        return self._color_overwrite
    # endregion

    # region Class Constructor
    def __new__(cls, operation: ICircuitOperation, _color_overwrite: str = "k"):
        """
        Factory method to select the correct wrapper class at instantiation.
        """
        # Check if the operation is a two-qubit operation.
        if isinstance(operation, ITwoQubitOperation):
            # If so, instantiate and return the specialized two-qubit wrapper.
            return VirtualTwoQubitColorOverwrite(
                operation=operation,
                _color_overwrite=_color_overwrite
            )
        else:
            # Otherwise, proceed with the standard instantiation of this class.
            return super().__new__(cls)
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualColorOverwrite':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualColorOverwrite(
            operation=self.operation.copy(
                relation_transfer_lookup=relation_transfer_lookup,
            ),
            _color_overwrite=self._color_overwrite,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class VirtualTwoQubitColorOverwrite(ITwoQubitOperation, IColorOverwrite):
    """
    Virtual color overwrite operation (behaves as TwoQubitOperation).
    Acts as a visualization wrapper for coloring visualization.
    """
    operation: ITwoQubitOperation = field(init=True)
    _color_overwrite: str = field(init=True)

    # region ICircuitOperation Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return self.operation.channel_identifiers

    @property
    def nr_of_repetitions(self) -> int:
        """:return: Number of repetitions for this object."""
        return self.operation.nr_of_repetitions

    @property
    def relation_link(self) -> IRelationLink[ICircuitOperation]:
        """:return: Description of relation to other circuit node."""
        return self.operation.relation_link

    @relation_link.setter
    def relation_link(self, link: IRelationLink[ICircuitOperation]):
        """:sets: Description of relation to other circuit node."""
        self.operation.relation_link = link

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self.operation.start_time

    @property
    def duration(self) -> float:
        """:return: Duration [ns]."""
        return self.operation.duration
    # endregion

    # region ITwoQubitOperation Properties
    @property
    def control_qubit_index(self) -> int:
        """:return: Index of control qubit."""
        return self.operation.control_qubit_index

    @property
    def target_qubit_index(self) -> int:
        """:return: Index of target qubit."""
        return self.operation.target_qubit_index
    # endregion

    # region IColorOverwrite Properties
    @property
    def wrapped_operation(self) -> ICircuitOperation:
        """:return: Wrapped operation used to pass to sub-draw factories."""
        return self.operation

    @property
    def color_overwrite(self) -> str:
        """:return: Color identifier for overwriting draw factory colors."""
        return self._color_overwrite
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'VirtualTwoQubitColorOverwrite':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return VirtualTwoQubitColorOverwrite(
            operation=self.operation.copy(
                relation_transfer_lookup=relation_transfer_lookup,
            ),
            _color_overwrite=self._color_overwrite,
        )

    def apply_modifiers_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        return self

    def decomposed_operations(self) -> List[ICircuitOperation]:
        """
        Functions similar to a 'flatten' operation.
        Mostly intended for composite-operations such that they can apply repetition and state-dependent registries.
        :return: Array-like of decomposed operations.
        """
        return [self]

    def apply_flatten_to_self(self) -> ICircuitOperation:
        """
        WARNING: Applies a flatten modification inplace.
        :return: Modified self.
        """
        return self
    # endregion


if __name__ == '__main__':
    from qce_circuit.structure.registry_duration import (
        DurationRegistry,
        RegistryDurationStrategy, IDurationStrategy, FixedDurationStrategy,
    )
    from qce_circuit.structure.intrf_circuit_operation import (
        RelationLink,
        RelationType,
    )

    registry: DurationRegistry = DurationRegistry()
    operation_duration_strategy = RegistryDurationStrategy(registry)
    key: str = operation_duration_strategy.unique_key  # Example
    operation = SingleQubitOperation(
        qubit_index=0,
        duration_strategy=operation_duration_strategy,
    )
    reset_operation = Reset(
        qubit_index=1,
        relation=RelationLink(operation, RelationType.FOLLOWED_BY)
    )
    print(key)
    print('dynamic operation: ', operation.start_time, operation.duration, operation.end_time)
    print('global operation: ', reset_operation.start_time, reset_operation.duration, reset_operation.end_time)
    registry.set_registry_at(key, value=1.0)
    print('dynamic operation: ', operation.start_time, operation.duration, operation.end_time)
    print('global operation: ', reset_operation.start_time, reset_operation.duration, reset_operation.end_time)

