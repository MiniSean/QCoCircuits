# -------------------------------------------
# Module describing the implementation of declarative circuit language.
# -------------------------------------------
from multipledispatch import dispatch
from typing import List, Dict
import numpy as np
from numpy.typing import NDArray
from qce_circuit.utilities.custom_exceptions import NoReferenceOperationException
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.structure.intrf_circuit_operation_composite import (
    ICircuitCompositeOperation,
    CircuitCompositeOperation,
)
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
    ChannelIdentifier,
    RelationLink,
)
from qce_circuit.structure.registry_repetition import (
    IRepetitionStrategy,
    FixedRepetitionStrategy,
)
from qce_circuit.structure.registry_acquisition import (
    AcquisitionRegistry,
    RegistryAcquisitionStrategy,
)
from qce_circuit.structure.intrf_acquisition_operation import (
    IAcquisitionOperation,
    AcquisitionTag,
)
from qce_circuit.language.intrf_declarative_circuit import (
    IDeclarativeCircuit,
    InitialStateEnum,
)


class DeclarativeCircuit(IDeclarativeCircuit):
    """
    Behaviour class, implements IDeclarativeCircuit interface.
    Describing circuit on gate (operation) level.
    """

    # region Interface Properties
    @property
    def occupied_qubit_channels(self) -> List[ChannelIdentifier]:
        """:return: Array-like of unique channel identifiers present in the circuit."""
        return unique_in_order(self._structure.channel_identifiers)

    @property
    def circuit_structure(self) -> ICircuitCompositeOperation:
        """:return: Internal circuit structure."""
        return self._structure

    @property
    def operations(self) -> List[ICircuitOperation]:
        """:return: Array-like of circuit operations."""
        return self.circuit_structure.decomposed_operations()

    @property
    def composite_operations(self) -> List[ICircuitCompositeOperation]:
        """:return: Array-like of all operations that are of instance ICircuitCompositeOperation."""
        return self._structure.get_sub_composite_operations()

    @property
    def acquisition_registry(self) -> AcquisitionRegistry:
        """:return: Acquisition Registry."""
        return self._acquisition_registry

    @property
    def start_time(self) -> float:
        """:return: Start time [a.u.]."""
        return self._structure.start_time

    @property
    def duration(self) -> float:
        """:return: Duration [a.u.]."""
        return self._structure.duration
    # endregion

    # region Class Constructor
    def __init__(self, nr_qubits: int = 0, relation: RelationLink = RelationLink.no_relation(), repetition_strategy: IRepetitionStrategy = FixedRepetitionStrategy(1)):
        self.nr_qubits: int = nr_qubits
        self._structure: CircuitCompositeOperation = CircuitCompositeOperation(
            relation=relation,
            repetition_strategy=repetition_strategy,
        )
        self._added_operations: List[ICircuitOperation] = list()
        self._initial_state_lookup: Dict[int, InitialStateEnum] = {}
        self._acquisition_registry: AcquisitionRegistry = AcquisitionRegistry(circuit=self.circuit_structure)
    # endregion

    # region Interface Methods
    def add_operation(self, operation: ICircuitOperation) -> 'ICircuitOperation':
        """:return: Added operation. Adds operation to circuit."""
        self._structure.add(operation)
        self._added_operations.append(operation)
        return operation

    def add_sub_circuit(self, operation: ICircuitCompositeOperation) -> 'ICircuitCompositeOperation':
        """:return: Added operation. Adds sub-circuit to circuit."""
        reference_transfer_lookup = {operation: self._structure}
        copied_operation: ICircuitCompositeOperation = operation.copy(relation_transfer_lookup=reference_transfer_lookup)
        self._structure.add(copied_operation)
        self._added_operations.append(copied_operation)
        return copied_operation

    def get_last_entry(self) -> ICircuitOperation:
        """:return: Last (circuit) operation entry added to the circuit."""
        # Guard clause, if no operations are added yet, raise exception
        if len(self._added_operations) == 0:
            raise NoReferenceOperationException(f"Expects at least 1 entry in circuit, instead none are provided.")
        return self._added_operations[-1]

    def apply_modifiers(self) -> 'DeclarativeCircuit':
        """
        WARNING: Applies modifiers inplace.
        Applies modifiers such as repetition and state-control.
        :return: Modified self.
        """
        result: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=self.nr_qubits,
        )
        result._structure = self._structure.apply_modifiers_to_self()
        result._added_operations = self._added_operations
        return result

    def set_qubit_initial_state(self, channel_index: int, state: InitialStateEnum) -> 'DeclarativeCircuit':
        """
        Currently only used for visualization.
        :sets: A cosmetic representation of a channels (qubit) initial state.
        """
        self._initial_state_lookup[channel_index] = state
        return self

    def get_qubit_initial_state(self, channel_index: int) -> InitialStateEnum:
        """
        Currently only used for visualization.
        :return: A cosmetic representation of a channels (qubit) initial state. Defaults to InitialStateEnum.ZERO
        """
        # Guard clause, default to InitialStateEnum.ZERO
        if channel_index not in self._initial_state_lookup:
            return InitialStateEnum.ZERO
        return self._initial_state_lookup[channel_index]

    @dispatch(qubit_index=int)
    def get_acquisition_indices(self, qubit_index: int) -> NDArray[np.int_]:
        """:return: Acquisition indices based on filter."""
        result: List[int] = []
        for operation in self.operations:
            if isinstance(operation, IAcquisitionOperation):
                key_match: bool = operation.acquisition_identifier.qubit_index == qubit_index
                if key_match:
                    result.append(operation.acquisition_index)
        return np.asarray(result)

    @dispatch(tag=AcquisitionTag)
    def get_acquisition_indices(self, tag: AcquisitionTag) -> NDArray[np.int_]:
        """:return: Acquisition indices based on filter."""
        result: List[int] = []
        for operation in self.operations:
            if isinstance(operation, IAcquisitionOperation):
                key_match: bool = operation.acquisition_identifier.equal_tag(tag)
                if key_match:
                    result.append(operation.acquisition_index)
        return np.asarray(result)

    def get_acquisition_strategy(self) -> RegistryAcquisitionStrategy:
        """:return: Acquisition Strategy based on internal registry."""
        return RegistryAcquisitionStrategy(registry=self.acquisition_registry)
    # endregion
