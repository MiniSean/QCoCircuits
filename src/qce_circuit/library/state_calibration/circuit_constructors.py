# -------------------------------------------
# Module containing constructors for state-calibration circuit.
# -------------------------------------------
from typing import List
from qce_circuit.library.state_calibration.circuit_components import (
    ICalibrationDescription,
    get_circuit_calibrate_with_heralded,
)
from qce_circuit.structure.registry_acquisition import AcquisitionRegistry
from qce_circuit.structure.acquisition_indexing.intrf_stabilizer_index_kernel import StateKey
from qce_circuit.language import (
    DeclarativeCircuit,
)


def construct_calibration_circuit(description: ICalibrationDescription) -> DeclarativeCircuit:
    """
    :param description: Contains which qubits and corresponding states to calibrate.
    :return: Declarative circuit containing all-state calibration with Heralded initialization.
    """

    result: DeclarativeCircuit = DeclarativeCircuit()
    registry: AcquisitionRegistry = result.acquisition_registry
    qubit_indices: List[int] = description.qubit_indices

    if description.includes_state_calibration(StateKey.STATE_0):
        result.add(get_circuit_calibrate_with_heralded(
            qubit_indices=qubit_indices,
            state=StateKey.STATE_0,
            registry=registry,
        ))

    if description.includes_state_calibration(StateKey.STATE_1):
        result.add(get_circuit_calibrate_with_heralded(
            qubit_indices=qubit_indices,
            state=StateKey.STATE_1,
            registry=registry,
        ))

    if description.includes_state_calibration(StateKey.STATE_2):
        result.add(get_circuit_calibrate_with_heralded(
            qubit_indices=qubit_indices,
            state=StateKey.STATE_2,
            registry=registry,
        ))

    return result
