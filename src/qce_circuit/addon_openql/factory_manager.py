# -------------------------------------------
# Module containing Singleton (default) openQL factory manager.
# -------------------------------------------
from typing import List, Type, Union, Optional
import openql as ql
from qce_circuit.utilities.singleton_base import SingletonABCMeta
from qce_circuit.addon_openql.intrf_openql_factory import (
    IOpenQLCircuitFactory,
    IOpenQLOperationFactory,
    OpenQLCircuitFactoryManager,
)
from qce_circuit.language.intrf_declarative_circuit import IDeclarativeCircuit
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.structure.intrf_circuit_operation_composite import ICircuitCompositeOperation
from qce_circuit.structure.circuit_operations import (
    Reset,
    Barrier,
    Hadamard,
    Identity,
    CPhase,
    DispersiveMeasure,
    Rx180,
    Rx90,
    Rxm90,
    Ry180,
    Ry90,
    Rym90,
    Wait,
)
from qce_circuit.addon_openql.operation_factories.factory_basic_operations import NameBasedOperationsFactory
from qce_circuit.addon_openql.operation_factories.factory_barrier_operations import BarrierOperationsFactory
from qce_circuit.addon_openql.operation_factories.factory_wait_operations import WaitOperationsFactory
from qce_circuit.addon_openql.operation_factories.factory_composite_operation import CompositeCPhaseOperationsFactory


class OpenQLFactoryManager(IOpenQLCircuitFactory, metaclass=SingletonABCMeta):
    """
    Behaviour Class, describing default declarative to openql circuit conversion.
    """
    _factory: IOpenQLCircuitFactory = OpenQLCircuitFactoryManager(
        factory_lookup={
            Reset: NameBasedOperationsFactory('prepz'),
            Barrier: BarrierOperationsFactory(),
            Wait: WaitOperationsFactory(),
            Hadamard: NameBasedOperationsFactory('h'),
            Identity: NameBasedOperationsFactory('i'),
            CPhase: CompositeCPhaseOperationsFactory(),
            DispersiveMeasure: NameBasedOperationsFactory('measure'),
            Rx180: NameBasedOperationsFactory('x180'),
            Rx90: NameBasedOperationsFactory('x90'),
            Rxm90: NameBasedOperationsFactory('mx90'),
            Ry180: NameBasedOperationsFactory('y180'),
            Ry90: NameBasedOperationsFactory('y90'),
            Rym90: NameBasedOperationsFactory('my90'),
        }
    )

    # region Interface Properties
    @property
    def supported_factories(self) -> List[Type[ICircuitOperation]]:
        """:return: Array-like of supported factory types."""
        return self._factory.supported_factories
    # endregion

    # region Interface Methods
    def construct(self, circuit: Union[IDeclarativeCircuit, ICircuitCompositeOperation], circuit_id: Optional[str] = None) -> ql.Program:
        """:return: OpenQL circuit based on operation type."""
        return self._factory.construct(circuit=circuit, circuit_id=circuit_id)

    def contains(self, factory_key: Type[ICircuitOperation]) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return self._factory.contains(factory_key=factory_key)
    # endregion


def to_openql(circuit: IDeclarativeCircuit, factory: IOpenQLCircuitFactory = OpenQLFactoryManager(), circuit_id: Optional[str] = None) -> ql.Program:
    return factory.construct(circuit=circuit, circuit_id=circuit_id)
