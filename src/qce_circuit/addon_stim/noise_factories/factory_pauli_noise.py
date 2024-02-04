# -------------------------------------------
# Module containing Stim noise-dresser factories for measurement operations.
# -------------------------------------------
from typing import List, Tuple, Iterator
import numpy as np
import stim
from qce_circuit.addon_stim.intrf_noise_factory import (
    IStimAdditiveCircuitNoiseFactory,
    extract_all_targets,
)
from qce_circuit.addon_stim.noise_settings_manager import (
    IndexedNoiseSettings,
    QubitNoiseModelParameters,
)


class PauliAdditiveCircuitNoiseFactory(IStimAdditiveCircuitNoiseFactory):
    """
    Behaviour class, describing methods for dressing multiple circuit instruction with Pauli (dephasing) noise.
    """

    # region Class Constructor
    def __init__(self, operation_name: str = "PAULI_CHANNEL_1"):
        self._operation_name: str = operation_name
        self._split_operation: str = "TICK"
    # endregion

    # region Interface Methods
    def construct(self, circuit: stim.Circuit, settings: IndexedNoiseSettings) -> stim.Circuit:
        """:return: Noise dressed Stim circuit."""
        circuit_flattened: stim.Circuit = circuit.flattened()
        result_circuit: stim.Circuit = stim.Circuit()
        qubit_targets: List[int] = extract_all_targets(circuit=circuit)

        for instructions in self.split_instruction_blocks(circuit_flattened, self._split_operation):
            max_duration: float = max([
                settings.get_operation_duration(instruction.name) for instruction in instructions
            ], default=0)

            # For each qubit target in circuit, determine pauli noise channel
            for qubit_target in qubit_targets:
                noise_setting: QubitNoiseModelParameters = settings.get_noise_settings(index=qubit_target)
                # Symmetric pauli errors
                px, py, pz = self.get_pauli_error(
                    t=max_duration * 0.5,
                    t1=noise_setting.t1,
                    t2=noise_setting.t2,
                )
                noise_instruction = stim.CircuitInstruction(
                    name=self._operation_name, targets=[qubit_target], gate_args=[px, py, pz]
                )
                # Symmetrically dress instructions
                instructions = [noise_instruction, *instructions, noise_instruction]

            # Apply instructions to new circuit
            for instruction in instructions:  # + [stim.CircuitInstruction("TICK", [], [])]:
                result_circuit.append(instruction)

        return result_circuit
    # endregion

    # region Static Class Methods
    @staticmethod
    def split_instruction_blocks(circuit_instructions: List[stim.CircuitInstruction], instruction_split: str = 'TICK') -> Iterator[List[stim.CircuitInstruction]]:
        """
        Note Includes split-operation within yielded instruction block.
        :return: Iterator of circuit instructions, split based on requested instruction (default TICK instruction).
        """
        sub_set: List[stim.CircuitInstruction] = []
        for instruction in circuit_instructions:
            sub_set.append(instruction)
            if instruction.name != instruction_split:
                continue

            yield sub_set
            sub_set = []
        yield sub_set

    @staticmethod
    def get_pauli_error(t: float, t1: float, t2: float) -> Tuple[float, float, float]:
        """
        :return: Tuple of Pauli X, Y and Z error probabilities based on T1 and T2 coherence times.
        """
        if t == 0:
            return 0, 0, 0

        px = 0.25 * (1 - np.exp(-t / t1))
        py = px
        pz = 0.5 * (1 - np.exp(-t / t2)) - 0.25 * (1 - np.exp(-t / t1))
        # Clamp values
        px = min(max(px, 0.0), 1.0)
        py = min(max(py, 0.0), 1.0)
        pz = min(max(pz, 0.0), 1.0)
        return px, py, pz
    # endregion
