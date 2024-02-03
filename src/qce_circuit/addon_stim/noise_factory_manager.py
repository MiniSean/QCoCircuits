# -------------------------------------------
# Module containing Singleton circuit noise factory manager.
# Extends existing stim circuit with circuit level noise based on preset.
# -------------------------------------------
from typing import List, Type, Union, Dict, Optional
import stim
from qce_circuit.utilities.singleton_base import SingletonABCMeta
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID
from qce_circuit.addon_stim.intrf_stim_factory import (
    IStimCircuitFactory,
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
from qce_circuit.addon_stim.operation_factories.factory_barrier_operations import TickOperationsFactory
from qce_circuit.addon_stim.operation_factories.factory_detector_operations import (
    DetectorOperationsFactory,
    CoordinateShiftOperationsFactory,
    LogicalObservableOperationsFactory,
)
from qce_circuit.addon_stim.noise_settings_manager import NoiseSettingManager
from qce_circuit.addon_stim.intrf_noise_factory import (
    IStimNoiseDresserFactory,
    StimNoiseDresserFactoryManager
)
from qce_circuit.addon_stim.noise_settings_manager import IndexedNoiseSettings
from qce_circuit.addon_stim.noise_factories.factory_measurement_noise import MeasurementNoiseDresserFactory


class NoiseFactoryManager(IStimNoiseDresserFactory, metaclass=SingletonABCMeta):
    """
    Behaviour Class, describing default noise dressing of stim-circuit.
    """
    _factory: IStimNoiseDresserFactory = StimNoiseDresserFactoryManager(
        factory_lookup={
            'M': MeasurementNoiseDresserFactory('MZ'),
        }
    )

    # region Interface Properties
    @property
    def supported_factories(self) -> List[str]:
        """:return: Array-like of supported factory types."""
        return self._factory.supported_factories
    # endregion

    # region Interface Methods
    def construct(self, circuit: stim.Circuit, settings: IndexedNoiseSettings) -> stim.Circuit:
        """:return: Noise dressed Stim circuit."""
        return self._factory.construct(circuit=circuit, settings=settings)

    def contains(self, factory_key: str) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return self._factory.contains(factory_key=factory_key)
    # endregion


def apply_noise(circuit: stim.Circuit, qubit_index_map: Optional[Dict[int, IQubitID]] = None, factory: IStimNoiseDresserFactory = NoiseFactoryManager()) -> stim.Circuit:
    """
    :param circuit: Circuit to be dressed with noise.
    :param qubit_index_map: (Optional) Dictionary mapping from (circuit) qubit index to qubit-ID (used for retrieving noise parameters).
    :param factory: (Optional) IStimNoiseDresserFactory for specialized noise application.
    :return: New stim circuit, dressed with noisy operations based on noise-dresser factory.
    """
    if qubit_index_map is None:
        qubit_index_map = {}

    index_noise_settings: IndexedNoiseSettings = IndexedNoiseSettings(
        noise_settings=NoiseSettingManager.read_config(),
        qubit_index_lookup=qubit_index_map,
    )
    return factory.construct(circuit=circuit, settings=index_noise_settings)


if __name__ == '__main__':
    import stim
    from qce_circuit.language.intrf_declarative_circuit import (
        IDeclarativeCircuit,
        InitialStateEnum,
    )
    from qce_circuit.library.repetition_code_circuit import (
        construct_repetition_code_circuit,
        InitialStateContainer,
    )
    from qce_circuit.addon_stim import to_stim

    initial_state = InitialStateContainer.from_ordered_list([
        InitialStateEnum.ZERO,
        InitialStateEnum.ONE,
        InitialStateEnum.ZERO,
    ])
    circuit_with_detectors: IDeclarativeCircuit = construct_repetition_code_circuit(
        initial_state=initial_state,
        qec_cycles=1,
    )
    stim_circuit: stim.Circuit = to_stim(circuit_with_detectors)
    print(stim_circuit.diagram())

    noisy_stim_circuit: stim.Circuit = apply_noise(
        circuit=stim_circuit,
        qubit_index_map=dict()
    )
    print(noisy_stim_circuit.diagram())
