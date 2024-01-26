# -------------------------------------------
# Module describing the declarative operations.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from qce_circuit.structure.intrf_circuit_operation import (
    QubitChannel,
    IRelationLink,
    RelationLink,
    ChannelIdentifier,
    ICircuitOperation,
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
class TwoQubitOperation(ICircuitOperation):
    """
    Minimal operation describes two-qubit implementation of ICircuitOperation.
    """
    control_qubit_index: int = field(init=True)
    target_qubit_index: int = field(init=True)
    relation: IRelationLink[ICircuitOperation] = field(default_factory=RelationLink.no_relation)
    duration_strategy: IDurationStrategy = field(default=FixedDurationStrategy(duration=0.0))

    # region Interface Properties
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

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'TwoQubitOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return TwoQubitOperation(
            control_qubit_index=self.control_qubit_index,
            target_qubit_index=self.target_qubit_index,
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
            control_qubit_index=self.control_qubit_index,
            target_qubit_index=self.target_qubit_index,
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
    duration_strategy: IDurationStrategy = field(init=False, default=FixedDurationStrategy(duration=0.5))

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
    # endregion

    # region Class Methods
    def __hash__(self):
        """Overwrites @dataclass behaviour. Circuit operation requires hash based on instance identity."""
        return id(self)
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

