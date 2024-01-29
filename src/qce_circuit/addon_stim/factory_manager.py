# -------------------------------------------
# Module containing Singleton (default) stim factory manager.
# -------------------------------------------
from typing import List, Type, Union
import stim
from qce_circuit.utilities.singleton_base import Singleton
from qce_circuit.addon_stim.intrf_stim_factory import (
    IStimCircuitFactory,
    IStimOperationFactory,
    StimCircuitFactoryManager,
)
from qce_circuit.language.intrf_declarative_circuit import IDeclarativeCircuit
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
    Rym90,
    Ry90,
)
from qce_circuit.addon_stim.circuit_operations import (
    DetectorOperation,
    LogicalObservableOperation,
    CoordinateShiftOperation,
)
from qce_circuit.addon_stim.operation_factories.factory_basic_operations import NameBasedOperationsFactory


class StimFactoryManager(IStimCircuitFactory):
    """
    Behaviour Class, describing default declarative to stim circuit conversion.
    """
    _factory: IStimCircuitFactory = StimCircuitFactoryManager(
        factory_lookup={
            Reset: NameBasedOperationsFactory('R'),
            Barrier: NameBasedOperationsFactory('TICK'),
            Hadamard: NameBasedOperationsFactory('H'),
            Identity: NameBasedOperationsFactory('I'),
            CPhase: NameBasedOperationsFactory('CZ'),
            DispersiveMeasure: NameBasedOperationsFactory('M'),
            Rx180: NameBasedOperationsFactory('X'),
            Rym90: NameBasedOperationsFactory('H'),
            Ry90: NameBasedOperationsFactory('H'),
            # DetectorOperation: 'DETECTOR',
            # LogicalObservableOperation: 'OBSERVABLE_INCLUDE',
            # CoordinateShiftOperation: 'SHIFT_COORDS',
        }
    )

    # region Interface Properties
    @property
    def supported_factories(self) -> List[Type[ICircuitOperation]]:
        """:return: Array-like of supported factory types."""
        return self._factory.supported_factories
    # endregion

    # region Interface Methods
    def construct(self, circuit: Union[IDeclarativeCircuit, ICircuitCompositeOperation]) -> stim.Circuit:
        """:return: Stim circuit based on operation type."""
        return self._factory.construct(circuit=circuit)

    def contains(self, factory_key: Type[ICircuitOperation]) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return self._factory.contains(factory_key=factory_key)
    # endregion


if __name__ == '__main__':
    from qce_circuit import (
        DeclarativeCircuit,
        plot_circuit,
    )
    import matplotlib.pylab as plt

    factory = StimFactoryManager()
    circuit = DeclarativeCircuit()
    circuit.add(Hadamard(qubit_index=0))
    plot_circuit(circuit)
    stim_circuit = factory.construct(circuit=circuit)
    print(stim_circuit.diagram())
    plt.show()