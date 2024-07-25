# -------------------------------------------
# Module containing functionality for modifying circuit structure.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Type, Generic, TypeVar, List, Optional, Union
from tqdm import tqdm
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.language.intrf_declarative_circuit import IDeclarativeCircuit
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.circuit_operations import (
    ICircuitOperation,
    SingleQubitOperation,
    TwoQubitOperation,
    ChannelIdentifier,
    DispersiveMeasure,
    VirtualVacant,
    VirtualTwoQubitVacant,
    VirtualEmpty,
    Wait,
    VirtualPark,
)
from qce_circuit.structure.intrf_circuit_operation import (
    QubitChannel,
)


TMaskedOperation = TypeVar('TMaskedOperation', bound=SingleQubitOperation)
TMaskedTwoQubitOperation = TypeVar('TMaskedTwoQubitOperation', bound=TwoQubitOperation)
TMaskOperation = TypeVar('TMaskOperation', bound=ICircuitOperation)


class IOperationMask(ABC, Generic[TMaskedOperation, TMaskOperation]):
    """
    Interface class, describing operation masking.
    """

    # region Interface Methods
    @abstractmethod
    def match(self, matched_operation: ICircuitOperation) -> bool:
        """:return: Boolean whether matched operation should be masked or not."""
        raise InterfaceMethodException

    @abstractmethod
    def construct_operation_mask(self, masked_operation: ICircuitOperation) -> ICircuitOperation:
        """:return: Newly constructed 'mask'-operation based on masked-operation."""
        raise InterfaceMethodException
    # endregion


def replace_operation(circuit: IDeclarativeCircuit, operation_masks: List[IOperationMask]) -> DeclarativeCircuit:
    """
    Iterates over existing declarative circuit.
    Reconstructs and replaces based on operation mask.
    :param circuit: Declarative circuit to be modified.
    :param operation_masks: Array-like of operation masks.
    :return: Newly constructed declarative circuit with modified operations.
    """
    result = DeclarativeCircuit()
    relation_transfer_lookup = {}

    # Iterate through nodes and rebuild circuit composite
    for operation in tqdm(circuit.operations, desc="Replacing Circuit Operations"):
        operation_copy: ICircuitOperation = operation.copy(relation_transfer_lookup=relation_transfer_lookup)

        for operation_mask in operation_masks:
            if operation_mask.match(matched_operation=operation_copy):
                operation_copy = operation_mask.construct_operation_mask(masked_operation=operation_copy)

        # Keep track of copied operations for relation transfer
        relation_transfer_lookup[operation] = operation_copy
        result.add(operation_copy)

    return result


@dataclass(frozen=True)
class OperationVacantMask(IOperationMask[TMaskedOperation, VirtualVacant], Generic[TMaskedOperation]):
    operation_type: Type[ICircuitOperation]
    qubit_index: int

    # region Interface Methods
    def match(self, matched_operation: TMaskedOperation) -> bool:
        """:return: Boolean whether matched operation should be masked or not."""
        is_masked_operation: bool = isinstance(matched_operation, self.operation_type)
        if not is_masked_operation:
            return False
        is_masked_qubit_id = matched_operation.qubit_index == self.qubit_index
        return is_masked_qubit_id

    def construct_operation_mask(self, masked_operation: TMaskedOperation) -> VirtualVacant:
        """:return: Newly constructed 'mask'-operation based on masked-operation."""
        return VirtualVacant(
            qubit_index=masked_operation.qubit_index,
            duration_strategy=masked_operation.duration_strategy,
            relation=masked_operation.relation_link,
        )
    # endregion


@dataclass(frozen=True)
class ChannelVacantMask(IOperationMask[TMaskedOperation, Union[VirtualVacant, VirtualEmpty]], Generic[TMaskedOperation]):
    qubit_channel: QubitChannel
    qubit_index: int

    # region Class Properties
    @property
    def qubit_channel_identifier(self) -> ChannelIdentifier:
        """:return: Identifier for qubit index and channel type."""
        return ChannelIdentifier(_id=self.qubit_index, _channel=self.qubit_channel)
    # endregion

    # region Interface Methods
    def match(self, matched_operation: TMaskedOperation) -> bool:
        """:return: Boolean whether matched operation should be masked or not."""
        is_masked_operation: bool = (isinstance(matched_operation, SingleQubitOperation)
                                     or isinstance(matched_operation, DispersiveMeasure))
        is_mask_operation: bool = (isinstance(matched_operation, VirtualVacant)
                                   or isinstance(matched_operation, VirtualEmpty))
        if not is_masked_operation or is_mask_operation:
            return False
        is_masked_channel: bool = self.qubit_channel_identifier in matched_operation.channel_identifiers
        return is_masked_channel

    def construct_operation_mask(self, masked_operation: TMaskedOperation) -> Union[VirtualVacant, VirtualEmpty]:
        """:return: Newly constructed 'mask'-operation based on masked-operation."""
        # Guard clause, some operations should be masked with a VirtualEmpty operation
        requires_empty_mask: bool = (isinstance(masked_operation, VirtualPark)
                                     or isinstance(masked_operation, Wait))

        if requires_empty_mask:
            return VirtualEmpty(
                qubit_index=masked_operation.qubit_index,
                duration_strategy=masked_operation.duration_strategy,
                relation=masked_operation.relation_link,
            )

        return VirtualVacant(
            qubit_index=masked_operation.qubit_index,
            duration_strategy=masked_operation.duration_strategy,
            relation=masked_operation.relation_link,
        )
    # endregion


@dataclass(frozen=True)
class ChannelTwoQubitVacantMask(IOperationMask[TMaskedTwoQubitOperation, VirtualTwoQubitVacant], Generic[TMaskedTwoQubitOperation]):
    """
    Behaviour class, describes masking of two-qubit operations.
    By default, the control qubit is specified and all target qubit pairs are considered.
    By default, the flux-channel is considered.
    Additional target qubit specification allows for unique operation masking.
    """
    control_qubit_index: int
    target_qubit_index: Optional[int] = field(default=None)
    qubit_channel: QubitChannel = field(default=QubitChannel.FLUX)

    # region Class Properties
    @property
    def qubit_channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Identifier for qubit index and channel type."""
        result: List[ChannelIdentifier] = [ChannelIdentifier(_id=self.control_qubit_index, _channel=self.qubit_channel)]
        if self.target_qubit_index is not None:
            result.append(ChannelIdentifier(_id=self.target_qubit_index, _channel=self.qubit_channel))
        return result
    # endregion

    # region Interface Methods
    def match(self, matched_operation: TMaskedTwoQubitOperation) -> bool:
        """:return: Boolean whether matched operation should be masked or not."""
        is_masked_operation: bool = isinstance(matched_operation, TwoQubitOperation)
        is_mask_operation: bool = isinstance(matched_operation, VirtualTwoQubitVacant)
        if not is_masked_operation or is_mask_operation:
            return False
        is_masked_channel: bool = all([
            identifier in matched_operation.channel_identifiers
            for identifier in self.qubit_channel_identifiers
        ])
        return is_masked_channel

    def construct_operation_mask(self, masked_operation: TMaskedTwoQubitOperation) -> VirtualTwoQubitVacant:
        """:return: Newly constructed 'mask'-operation based on masked-operation."""
        return VirtualTwoQubitVacant(
            control_qubit_index=masked_operation.control_qubit_index,
            target_qubit_index=masked_operation.target_qubit_index,
            relation=masked_operation.relation_link,
            duration_strategy=masked_operation.duration_strategy,
        )
    # endregion
