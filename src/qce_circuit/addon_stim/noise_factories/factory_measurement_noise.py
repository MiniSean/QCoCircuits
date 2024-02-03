# -------------------------------------------
# Module containing Stim noise-dresser factories for measurement operations.
# -------------------------------------------
from typing import List
import stim
from qce_circuit.addon_stim.intrf_noise_factory import (
    IStimNoiseDresserComponentFactory,
    extract_instruction_targets,
)
from qce_circuit.addon_stim.noise_settings_manager import IndexedNoiseSettings


class MeasurementNoiseDresserFactory(IStimNoiseDresserComponentFactory):
    """
    Behaviour class, describing Stim-operation factory based on name description.
    """

    # region Class Constructor
    def __init__(self, operation_name: str = "MZ"):
        self._operation_name: str = operation_name
    # endregion

    # region Interface Methods
    def construct(self, instruction: stim.CircuitInstruction, settings: IndexedNoiseSettings) -> List[stim.CircuitInstruction]:
        """:return: Noise dressed Stim measurement operation."""
        result: List[stim.CircuitInstruction] = []
        qubit_targets: List[int] = extract_instruction_targets(instruction=instruction)

        for target_index in qubit_targets:  # operation. target indices
            result.append(stim.CircuitInstruction(
                self._operation_name,
                [target_index],
                [settings.get_noise_settings(target_index).assignment_error],
            ))
        return result
    # endregion
