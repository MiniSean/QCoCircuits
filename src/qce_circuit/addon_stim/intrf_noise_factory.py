# -------------------------------------------
# Module containing interface for stim circuit noise dresser.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import List, Dict
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


class IStimAdditiveCircuitNoiseFactory(ABC):
    """
    Interface class, describing methods for dressing multiple circuit instruction with noise.
    """

    # region Interface Methods
    @abstractmethod
    def construct(self, circuit: stim.Circuit, settings: IndexedNoiseSettings) -> stim.Circuit:
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
    factory_additives: List[IStimAdditiveCircuitNoiseFactory] = field(default_factory=list)
    """Array-like of factories that apply noise to arbitrary instruction groups."""

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

        circuit_instructions: List[stim.CircuitInstruction] = []
        for i, instruction in enumerate(circuit_flattened):
            if not self.contains(factory_key=instruction.name):
                circuit_instructions.append(instruction)
                continue
            # Noise dress instruction
            dressed_instructions: List[stim.CircuitInstruction] = self.factory_lookup[instruction.name].construct(
                instruction=instruction,
                settings=settings,
            )
            circuit_instructions.extend(dressed_instructions)

        # Construct result circuit
        for instruction in circuit_instructions:
            result_circuit.append(instruction)

        # Perform bulk operations
        for bulk_factory in self.factory_additives:
            result_circuit = bulk_factory.construct(result_circuit, settings=settings)

        return result_circuit

    def contains(self, factory_key: str) -> bool:
        """:return: Boolean, whether factory key is included in the manager."""
        return factory_key in self.supported_factories
    # endregion


def extract_instruction_targets(instruction: stim.CircuitInstruction) -> List[int]:
    """:return: Hacky approach to obtaining targets from operation by processing the string representation."""
    if instruction.name in ['DETECTOR', 'OBSERVABLE_INCLUDE', 'SHIFT_COORDS']:
        return []
    targets: List[str] = str(instruction).split()[1:]
    return [int(target) for target in targets]


def extract_all_targets(circuit: stim.Circuit) -> List[int]:
    """:return: Approach to obtaining targets from all operations in a circuit."""
    # Set to store all unique qubit indices
    qubit_indices = set()

    # Iterate through each operation in the circuit
    for instruction in circuit:
        # The targets of an instruction include the qubits it operates on
        for target in extract_instruction_targets(instruction):
            # Add the qubit index to the set
            qubit_indices.add(target)

    # Convert the set to a sorted list to have a consistent order
    return sorted(list(qubit_indices))
