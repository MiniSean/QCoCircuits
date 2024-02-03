# -------------------------------------------
# Module containing interface for stim circuit noise dresser.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import Type, List, Dict, Union, Any, Tuple, TypeVar
import stim
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.intrf_factory_manager import IFactoryManager
from qce_circuit.addon_stim.noise_settings_manager import IndexedNoiseSettings


class IStimNoiseDresserComponentFactory(ABC):
    """
    Interface class, describing methods for dressing specific circuit instruction with noise.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, instruction: stim.CircuitInstruction, settings: IndexedNoiseSettings) -> List[stim.CircuitInstruction]:
        """:return: Noise dressed Stim circuit."""
        raise InterfaceMethodException
    # endregion


class IStimNoiseDresserFactory(IFactoryManager[str], metaclass=ABCMeta):
    """
    Interface class, describing methods for dressing stim-circuit with noisy operations.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, circuit: stim.Circuit, settings: IndexedNoiseSettings) -> stim.Circuit:
        """:return: Noise dressed Stim circuit."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class StimNoiseDresserFactoryManager(IStimNoiseDresserFactory):
    """
    Behaviour class, implementing operation to dress stim-circuit with noise based on factory-lookup.
    """
    factory_lookup: Dict[str, IStimNoiseDresserComponentFactory] = field(default_factory=dict)
    """Lookup that maps operation-type to stim-operation factory."""

    # region Interface Properties
    @property
    def supported_factories(self) -> List[str]:
        """:return: Array-like of supported factory types."""
        return list(set(self.factory_lookup.keys()))
    # endregion

    # region Interface Methods
    def construct(self, circuit: stim.Circuit, settings: IndexedNoiseSettings) -> stim.Circuit:
        """:return: Noise dressed Stim circuit."""
        circuit_flattened: stim.Circuit = circuit.flattened()
        result_circuit: stim.Circuit = stim.Circuit()

        for i, instruction in enumerate(circuit_flattened):
            if not self.contains(factory_key=instruction.name):
                result_circuit.append(instruction)
                continue
            # Noise dress instruction
            dressed_instructions: List[stim.CircuitInstruction] = self.factory_lookup[instruction.name].construct(
                instruction=instruction,
                settings=settings,
            )
            for _instruction in dressed_instructions:
                result_circuit.append(_instruction)

        return result_circuit

    def contains(self, factory_key: str) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return factory_key in self.supported_factories
    # endregion


def extract_instruction_targets(instruction: stim.CircuitInstruction) -> List[int]:
    """:return: Hacky approach to obtaining targets from operation by processing the string representation."""
    targets: List[str] = str(instruction).split()[1:]
    return [int(target) for target in targets]
