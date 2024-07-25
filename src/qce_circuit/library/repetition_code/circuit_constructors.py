# -------------------------------------------
# Module containing arbitrary length repetition-code circuit.
# -------------------------------------------
from typing import Optional, List, Dict
from qce_circuit.library.repetition_code.circuit_components import (
    IRepetitionCodeDescription,
    RepetitionCodeDescription,
    get_last_acquisition_operation,
    get_circuit_initialize_simplified,
    get_circuit_initialize_with_heralded,
    get_circuit_final_measurement,
    get_circuit_qec_round_with_dynamical_decoupling_simplified,
    get_circuit_qec_with_detectors,
)
from qce_circuit.library.state_calibration.circuit_components import (
    CalibrationDescription,
    CalibrateType,
)
from qce_circuit.library.state_calibration.circuit_constructors import construct_calibration_circuit
from qce_circuit.connectivity import (
    IQubitID,
    IEdgeID,
)
from qce_circuit.structure.circuit_operations import Barrier
from qce_circuit.structure.registry_acquisition import (
    AcquisitionRegistry,
)
from qce_circuit.structure.registry_repetition import FixedRepetitionStrategy
from qce_circuit.language import (
    DeclarativeCircuit,
    InitialStateContainer
)
from qce_circuit.addon_stim.circuit_operations import (
    DetectorOperation,
    LogicalObservableOperation,
)


def construct_repetition_code_circuit(qec_cycles: int, description: Optional[IRepetitionCodeDescription] = None, initial_state: InitialStateContainer = InitialStateContainer.empty()) -> DeclarativeCircuit:
    # Default implementation
    if description is None:
        description = RepetitionCodeDescription.from_initial_state(initial_state=initial_state)

    result: DeclarativeCircuit = DeclarativeCircuit()
    registry: AcquisitionRegistry = result.acquisition_registry
    result.add(get_circuit_initialize_with_heralded(
        connectivity=description,
        initial_state=initial_state,
        registry=registry,
    ))
    circuit_qec_with_detectors = get_circuit_qec_with_detectors(
        connectivity=description,
        qec_cycles=qec_cycles,
        registry=registry,
    )
    result.add(circuit_qec_with_detectors)
    result.add(get_circuit_final_measurement(
        connectivity=description,
        registry=registry,
    ))

    # Add detector operations
    for ancilla in description.ancilla_qubit_indices:
        ancilla_element: IQubitID = description.get_element(index=ancilla)
        involved_edges: List[IEdgeID] = description.get_edges(qubit=ancilla_element)
        neighbor_a: IQubitID = involved_edges[0].get_connected_qubit_id(element=ancilla_element)
        neighbor_b: IQubitID = involved_edges[1].get_connected_qubit_id(element=ancilla_element)
        if qec_cycles > 0:
            ancilla_reference_offset: int = (get_last_acquisition_operation(
                circuit_qec_with_detectors).circuit_level_acquisition_index + 1) - get_last_acquisition_operation(
                circuit_qec_with_detectors, qubit_index=ancilla).circuit_level_acquisition_index
        else:
            ancilla_reference_offset = None

        result.add(DetectorOperation(
            qubit_index=ancilla,
            last_acquisition_index=get_last_acquisition_operation(result).circuit_level_acquisition_index,
            main_target=get_last_acquisition_operation(result, qubit_index=description.get_index(neighbor_a)).circuit_level_acquisition_index,
            secondary_target=get_last_acquisition_operation(result, qubit_index=description.get_index(neighbor_b)).circuit_level_acquisition_index,
            reference_offset=ancilla_reference_offset + len(description.data_qubit_indices) if qec_cycles > 0 else ancilla_reference_offset,
            secondary_offset=len(description.ancilla_qubit_indices) if qec_cycles > 1 else None,
        ))
    for data in description.data_qubit_indices:
        result.add(LogicalObservableOperation(
            qubit_index=data,
            last_acquisition_index=get_last_acquisition_operation(result).circuit_level_acquisition_index,
            main_target=get_last_acquisition_operation(result, qubit_index=data).circuit_level_acquisition_index
        ))
    return result


def construct_repetition_code_circuit_simplified(qec_cycles: int, description: Optional[IRepetitionCodeDescription] = None, initial_state: InitialStateContainer = InitialStateContainer.empty()) -> DeclarativeCircuit:
    # Default implementation
    if description is None:
        description = RepetitionCodeDescription.from_initial_state(initial_state=initial_state)

    result: DeclarativeCircuit = DeclarativeCircuit()
    registry: AcquisitionRegistry = result.acquisition_registry
    result.add(get_circuit_initialize_simplified(
        connectivity=description,
        initial_state=initial_state,
    ))
    cycle_circuit: DeclarativeCircuit = DeclarativeCircuit(
        repetition_strategy=FixedRepetitionStrategy(repetitions=qec_cycles)
    )
    cycle_circuit.add(get_circuit_qec_round_with_dynamical_decoupling_simplified(
        connectivity=description,
        registry=registry
    ))

    result.add(Barrier(description.qubit_indices))
    result.add(cycle_circuit)
    result.add(get_circuit_final_measurement(
        connectivity=description,
        registry=registry,
    ))
    result.add(Barrier(description.qubit_indices))
    return result


def construct_repetition_code_multi_round_circuit(qec_cycles: List[int], description: IRepetitionCodeDescription, initial_state: InitialStateContainer = InitialStateContainer.empty()) -> DeclarativeCircuit:
    # Data allocation
    result: Optional[DeclarativeCircuit] = DeclarativeCircuit()
    channel_map: Dict[int, IQubitID] = description.circuit_channel_map
    calibration_description = CalibrationDescription(
        _qubit_ids=description.qubit_ids,
        _qubit_index_map={value: key for key, value in channel_map.items()},
        _type=CalibrateType.QUTRIT,
    )

    for qec_cycle in qec_cycles:
        cycle_circuit: DeclarativeCircuit = construct_repetition_code_circuit(
            qec_cycles=qec_cycle,
            description=description,
            initial_state=initial_state,
        )
        cycle_circuit = cycle_circuit.apply_modifiers()
        cycle_circuit = cycle_circuit.flatten()

        result.add(cycle_circuit)
        result.add(Barrier(description.qubit_indices))
    calibration_circuit = construct_calibration_circuit(
        description=calibration_description
    )
    result.add(calibration_circuit)
    return result
