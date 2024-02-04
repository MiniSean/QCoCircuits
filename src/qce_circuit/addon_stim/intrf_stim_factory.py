# -------------------------------------------
# Module containing interface for conversion factory for stim circuit.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import Type, List, Dict, Union, Any, Tuple, TypeVar
import stim
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.intrf_factory_manager import IFactoryManager
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.structure.intrf_circuit_operation_composite import ICircuitCompositeOperation
from qce_circuit.language.intrf_declarative_circuit import IDeclarativeCircuit

TStimCircuit = TypeVar('TStimCircuit', bound=stim.Circuit)


class IStimCircuitFactory(IFactoryManager[Type[ICircuitOperation]], metaclass=ABCMeta):
    """
    Interface class, describing methods for constructing stim-circuit from (declarative) circuit operation.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, circuit: Union[IDeclarativeCircuit, ICircuitCompositeOperation]) -> stim.Circuit:
        """:return: Stim circuit based on operation type."""
        raise InterfaceMethodException
    # endregion


class IStimOperationFactory(ABC):
    """
    Interface class, describing methods for constructing stim-operation from circuit operation.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, operation: ICircuitOperation) -> stim.CircuitInstruction:
        """:return: Stim operation based on operation type."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class StimCircuitFactoryManager(IStimCircuitFactory):
    """
    Behaviour class, implementing operation to convert declarative circuit to stim-circuit based on factory-lookup.
    """
    factory_lookup: Dict[Type[ICircuitOperation], IStimOperationFactory] = field(default_factory=dict)
    """Lookup that maps operation-type to stim-operation factory."""

    # region Interface Properties
    @property
    def supported_factories(self) -> List[Type[ICircuitOperation]]:
        """:return: Array-like of supported factory types."""
        return list(set(self.factory_lookup.keys()))
    # endregion

    # region Interface Methods
    def construct(self, circuit: Union[IDeclarativeCircuit, ICircuitCompositeOperation]) -> stim.Circuit:
        """:return: Stim circuit based on operation type."""
        result_circuit: stim.Circuit = stim.Circuit()
        process_circuit: ICircuitCompositeOperation = circuit
        if isinstance(circuit, IDeclarativeCircuit):
            process_circuit = circuit.circuit_structure

        for operation_node in process_circuit._circuit_graph.get_node_iterator():
            operation: ICircuitOperation = operation_node.operation

            # Recursion, if operation is a composite operation
            if isinstance(operation, ICircuitCompositeOperation):
                inner_circuit: stim.Circuit = self.construct(operation)
                result_circuit += inner_circuit * operation.nr_of_repetitions

            # Guard clause, if request not supported raise exception
            operation_supported: bool = self.contains(factory_key=type(operation))
            if not operation_supported:
                continue  # TODO: Maybe provide warning for skipped operation.

            stim_operation: stim.CircuitInstruction = self.factory_lookup[type(operation)].construct(operation)
            result_circuit.append(stim_operation)

        return result_circuit

    def contains(self, factory_key: Type[ICircuitOperation]) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return factory_key in self.supported_factories
    # endregion
