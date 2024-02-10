# -------------------------------------------
# Module describing the interface language on top of the declarative structure.
# This code exposes intuitive methods to construct a declarative (circuit) structure.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass
from multipledispatch import dispatch
from typing import List, Union, Dict
from enum import Enum, unique
import numpy as np
from numpy.typing import NDArray
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
    IDurationComponent,
    ChannelIdentifier,
)
from qce_circuit.structure.intrf_circuit_operation_composite import (
    ICircuitCompositeOperation,
)
from qce_circuit.structure.intrf_acquisition_operation import (
    AcquisitionTag,
)
from qce_circuit.structure.circuit_operations import (
    Identity,
    Rx180,
    Rx90,
    Rxm90,
    Ry90,
    Rym90,
)
from qce_circuit.structure.registry_acquisition import (
    AcquisitionRegistry,
    IAcquisitionStrategy,
)


@unique
class InitialStateEnum(Enum):
    """Enum class, containing different initial state options. Mostly for cosmetic purposes."""
    ZERO = '0'
    ONE = '1'
    PLUS = '+'
    MINUS = '-'
    PLUS_I = '+i'
    MINUS_I = '-i'


@dataclass(frozen=True)
class InitialStateContainer:
    """
    Data class, holding reference to qubits and their initial state.
    """
    initial_states: Dict[int, InitialStateEnum]
    """Index pointers to data qubits only."""

    # region Class Properties
    @property
    def distance(self) -> int:
        return len(self.initial_states)

    @property
    def as_array(self) -> np.ndarray:
        sorted_indices: List[int] = list(sorted(self.initial_states.keys()))
        # Maps initial state to binary
        to_bit_conversion: Dict[InitialStateEnum, int] = {
            InitialStateEnum.ZERO: 0,
            InitialStateEnum.MINUS: 0,
            InitialStateEnum.MINUS_I: 0,
            InitialStateEnum.ONE: 1,
            InitialStateEnum.PLUS: 1,
            InitialStateEnum.PLUS_I: 1,
        }
        return np.asarray([to_bit_conversion[self.initial_states[index]] for index in sorted_indices])
    # endregion

    # region Class Methods
    def get_initial_state(self, qubit_index: int) -> InitialStateEnum:
        return self.initial_states[qubit_index]

    def get_operation(self, qubit_index: int, initial_state_index: int, **kwargs) -> ICircuitOperation:
        """
        :param qubit_index: Index corresponding to qubit-ID in circuit. Will be passed to operation constructor.
        :param initial_state_index: Index corresponding to qubit-ID in initial state container.
            Will be used to fetch corresponding initial state.
        :return: Circuit operation corresponding to initial state preparation.
        """
        # Data allocation
        state: InitialStateEnum = InitialStateEnum.ZERO

        if initial_state_index in self.initial_states:
            state = self.get_initial_state(qubit_index=initial_state_index)

        if state == InitialStateEnum.ZERO:
            return Identity(qubit_index, **kwargs)
        if state == InitialStateEnum.ONE:
            return Rx180(qubit_index, **kwargs)
        if state == InitialStateEnum.PLUS:
            return Ry90(qubit_index, **kwargs)
        if state == InitialStateEnum.MINUS:
            return Rym90(qubit_index, **kwargs)
        if state == InitialStateEnum.PLUS_I:
            return Rxm90(qubit_index, **kwargs)
        if state == InitialStateEnum.MINUS_I:
            return Rx90(qubit_index, **kwargs)

        raise NotImplementedError(f"Initial state {state} is not supported.")

    @classmethod
    def from_ordered_list(cls, initial_states: List[InitialStateEnum]) -> 'InitialStateContainer':
        """
        :return: Class method constructor based on ordered array of initial state.
        Where each element index corresponds to qubit index.
        """
        return InitialStateContainer(
            initial_states={i: state for i, state in enumerate(initial_states)}
        )
    # endregion


class IIndexKernelComponent(ABC):
    """
    Interface class, describing getter methods for acquisition indices and matching tags.
    """

    # region Interface Methods
    @dispatch(qubit_index=int)
    @abstractmethod
    def get_acquisition_indices(self, qubit_index: int) -> NDArray[np.int_]:
        """:return: Acquisition indices based on filter."""
        raise InterfaceMethodException

    @dispatch(tag=AcquisitionTag)
    @abstractmethod
    def get_acquisition_indices(self, tag: AcquisitionTag) -> NDArray[np.int_]:
        """:return: Acquisition indices based on filter."""
        raise InterfaceMethodException
    # endregion


class IDeclarativeCircuit(IDurationComponent, IIndexKernelComponent, metaclass=ABCMeta):
    """
    Interface class, describing top-level interface for methods and properties to construct circuit.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def occupied_qubit_channels(self) -> List[ChannelIdentifier]:
        """:return: Array-like of unique channel identifiers present in the circuit."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def circuit_structure(self) -> ICircuitCompositeOperation:
        """:return: Internal circuit structure."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def operations(self) -> List[ICircuitOperation]:
        """:return: Array-like of circuit operations."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def composite_operations(self) -> List[ICircuitCompositeOperation]:
        """:return: Array-like of all operations that are of instance ICircuitCompositeOperation."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def acquisition_registry(self) -> AcquisitionRegistry:
        """:return: Acquisition Registry."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    def add(self, operation: Union[ICircuitOperation, 'IDeclarativeCircuit']) -> 'ICircuitOperation':
        """:return: Added operation. Adds operation to circuit."""
        if isinstance(operation, IDeclarativeCircuit):
            return self.add_declarative_circuit(circuit=operation)
        if isinstance(operation, ICircuitCompositeOperation):
            return self.add_sub_circuit(operation=operation)
        if isinstance(operation, ICircuitOperation):
            return self.add_operation(operation=operation)
        raise InterfaceMethodException

    def add_declarative_circuit(self, circuit: 'IDeclarativeCircuit') -> 'ICircuitOperation':
        """:return: Added operation. Adds declarative-circuit to circuit."""
        return self.add_sub_circuit(operation=circuit.circuit_structure)

    @abstractmethod
    def add_operation(self, operation: ICircuitOperation) -> 'ICircuitOperation':
        """:return: Added operation. Adds operation to circuit."""
        raise InterfaceMethodException

    @abstractmethod
    def add_sub_circuit(self, operation: ICircuitCompositeOperation) -> 'ICircuitOperation':
        """:return: Added operation. Adds sub-circuit to circuit."""
        raise InterfaceMethodException

    @abstractmethod
    def get_last_entry(self) -> ICircuitOperation:
        """:return: Last (circuit) operation entry added to the circuit."""
        raise InterfaceMethodException

    @abstractmethod
    def apply_modifiers(self) -> 'IDeclarativeCircuit':
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        raise InterfaceMethodException

    @abstractmethod
    def set_qubit_initial_state(self, channel_index: int, state: InitialStateEnum) -> 'IDeclarativeCircuit':
        """
        Currently only used for visualization.
        :sets: A cosmetic representation of a channels (qubit) initial state.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_qubit_initial_state(self, channel_index: int) -> InitialStateEnum:
        """
        Currently only used for visualization.
        :return: A cosmetic representation of a channels (qubit) initial state. Defaults to InitialStateEnum.ZERO
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_acquisition_strategy(self) -> IAcquisitionStrategy:
        """:return: Acquisition Strategy based on internal registry."""
        raise InterfaceMethodException
    # endregion
