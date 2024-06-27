# -------------------------------------------
# Module containing functionality for modifying circuit structure.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Generic, TypeVar, List
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.language.intrf_declarative_circuit import IDeclarativeCircuit
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.circuit_operations import (
    ICircuitOperation,
    SingleQubitOperation,
    ChannelIdentifier,
    DispersiveMeasure,
    VirtualVacant,
)
from qce_circuit.structure.intrf_circuit_operation import (
    QubitChannel,
)


TMaskedOperation = TypeVar('TMaskedOperation', bound=ICircuitOperation)
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
    for operation in circuit.operations:
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
class ChannelVacantMask(IOperationMask[TMaskedOperation, VirtualVacant], Generic[TMaskedOperation]):
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
        if not is_masked_operation:
            return False
        is_masked_channel: bool = self.qubit_channel_identifier in matched_operation.channel_identifiers
        return is_masked_channel

    def construct_operation_mask(self, masked_operation: TMaskedOperation) -> VirtualVacant:
        """:return: Newly constructed 'mask'-operation based on masked-operation."""
        return VirtualVacant(
            qubit_index=masked_operation.qubit_index,
            duration_strategy=masked_operation.duration_strategy,
            relation=masked_operation.relation_link,
        )
    # endregion

