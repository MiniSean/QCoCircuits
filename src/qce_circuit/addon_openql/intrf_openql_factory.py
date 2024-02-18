# -------------------------------------------
# Module containing interface for conversion factory for openql circuit.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import Type, List, Dict, Union, Optional, TypeVar
import openql as ql
import uuid
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.intrf_factory_manager import IFactoryManager
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.structure.intrf_circuit_operation_composite import ICircuitCompositeOperation
from qce_circuit.language.intrf_declarative_circuit import IDeclarativeCircuit
from qce_circuit.addon_openql.platform_manager import PlatformManager


TOpenQLCircuit = TypeVar('TOpenQLCircuit', bound=ql.Program)


class IOpenQLCircuitFactory(IFactoryManager[Type[ICircuitOperation]], metaclass=ABCMeta):
    """
    Interface class, describing methods for constructing openql-circuit from (declarative) circuit operation.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, circuit: Union[IDeclarativeCircuit, ICircuitCompositeOperation], circuit_id: Optional[str] = None) -> ql.Program:
        """:return: OpenQL circuit based on operation type."""
        raise InterfaceMethodException
    # endregion


class IOpenQLOperationFactory(ABC):
    """
    Interface class, describing methods for constructing stim-operation from circuit operation.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, operation: ICircuitOperation, kernel: ql.Kernel) -> ql.Kernel:
        """:return: Updated OpenQL Kernel based on operation type."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class OpenQLCircuitFactoryManager(IOpenQLCircuitFactory):
    """
    Behaviour class, implementing operation to convert declarative circuit to openql-circuit based on factory-lookup.
    """
    factory_lookup: Dict[Type[ICircuitOperation], IOpenQLOperationFactory] = field(default_factory=dict)
    """Lookup that maps operation-type to openql (kernel extension) factory."""

    # region Interface Properties
    @property
    def supported_factories(self) -> List[Type[ICircuitOperation]]:
        """:return: Array-like of supported factory types."""
        return list(set(self.factory_lookup.keys()))
    # endregion

    # region Interface Methods
    def construct(self, circuit: Union[IDeclarativeCircuit, ICircuitCompositeOperation], circuit_id: Optional[str] = None) -> ql.Program:
        """:return: OpenQL circuit based on operation type."""

        process_circuit: ICircuitCompositeOperation = circuit
        if isinstance(circuit, IDeclarativeCircuit):
            process_circuit = circuit.circuit_structure

        # Use circuit generated UUID to provide unique name to program and kernel, otherwise use (optional) circuit ID
        circuit_uuid: str = str(OpenQLCircuitFactoryManager.construct_uuid(circuit=process_circuit))
        if circuit_id is not None:
            circuit_uuid = circuit_id
        result_program: ql.Program = PlatformManager.construct_program(name=f"program_id_{circuit_uuid}")
        kernel: ql.Kernel = PlatformManager.construct_kernel(name=f"kernel_id_{circuit_uuid}")

        for operation_node in process_circuit._circuit_graph.get_node_iterator():
            operation: ICircuitOperation = operation_node.operation

            # Recursion, if operation is a composite operation
            if isinstance(operation, ICircuitCompositeOperation):
                inner_program: ql.Program = self.construct(operation, circuit_id=f"sub_{circuit_uuid}")
                # TODO: deal with repetitions
                for i in range(operation.nr_of_repetitions):
                    result_program.add_program(inner_program)

            # Guard clause, if request not supported raise exception
            operation_supported: bool = self.contains(factory_key=type(operation))
            if not operation_supported:
                continue  # TODO: Maybe provide warning for skipped operation.
            
            # Extend kernel
            kernel = self.factory_lookup[type(operation)].construct(operation, kernel)

        result_program.add_kernel(kernel)
        return result_program

    def contains(self, factory_key: Type[ICircuitOperation]) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return factory_key in self.supported_factories
    # endregion

    # region Static Class Methods
    @staticmethod
    def construct_uuid(circuit: ICircuitCompositeOperation) -> uuid.UUID:
        """:return: Constructs unique identifier based on all (decomposed) circuit operation class names."""
        unique_identifier_parts: List[str] = [
            f"{operation.__class__.__name__}"
            for operation in circuit.decomposed_operations()
        ]
        # Join the parts into a single string to form a comprehensive unique identifier
        unique_identifier = "_".join(unique_identifier_parts)
        # Generate a UUID based on this unique identifier
        return uuid.uuid5(uuid.NAMESPACE_DNS, unique_identifier)
    # endregion
