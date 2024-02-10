# -------------------------------------------
# Module containing arbitrary length repetition-code circuit.
# -------------------------------------------
from typing import List
from qce_circuit.library.repetition_code.circuit_components import (
    IRepetitionCodeDescription,
    RepetitionCodeDescription,
    get_last_acquisition_operation,
    get_repetition_code_connectivity,
    get_circuit_initialize, get_circuit_initialize_with_heralded,
    get_circuit_final_measurement,
    get_circuit_qec_round_with_dynamical_decoupling,
    get_circuit_qec_with_detectors,
)
from qce_circuit.library.repetition_code.repetition_code_connectivity import Repetition9Code
from qce_circuit.connectivity import (
    IQubitID,
    IEdgeID,
)
from qce_circuit.structure.registry_acquisition import (
    AcquisitionRegistry,
)
from qce_circuit.structure.registry_repetition import FixedRepetitionStrategy
from qce_circuit.language import (
    DeclarativeCircuit,
    InitialStateEnum,
    InitialStateContainer
)
from qce_circuit.addon_stim.circuit_operations import (
    DetectorOperation,
    LogicalObservableOperation,
)


def construct_repetition_code_circuit(description: IRepetitionCodeDescription, qec_cycles: int, initial_state: InitialStateContainer = InitialStateContainer.empty()) -> DeclarativeCircuit:
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

    # # Add detector operations
    # for ancilla in description.ancilla_qubit_indices:
    #     ancilla_element: IQubitID = description.get_element(index=ancilla)
    #     involved_edges: List[IEdgeID] = description.get_edges(qubit=ancilla_element)
    #     neighbor_a: IQubitID = involved_edges[0].get_connected_qubit_id(element=ancilla_element)
    #     neighbor_b: IQubitID = involved_edges[1].get_connected_qubit_id(element=ancilla_element)
    #     if qec_cycles > 0:
    #         ancilla_reference_offset: int = (get_last_acquisition_operation(
    #             circuit_qec_with_detectors).circuit_level_acquisition_index + 1) - get_last_acquisition_operation(
    #             circuit_qec_with_detectors, qubit_index=ancilla).circuit_level_acquisition_index
    #     else:
    #         ancilla_reference_offset = (get_last_acquisition_operation(
    #             result).circuit_level_acquisition_index + 1) - get_last_acquisition_operation(result, qubit_index=ancilla).circuit_level_acquisition_index
    #
    #     result.add(DetectorOperation(
    #         qubit_index=ancilla,
    #         last_acquisition_index=get_last_acquisition_operation(result).circuit_level_acquisition_index,
    #         main_target=get_last_acquisition_operation(result, qubit_index=description.get_index(neighbor_a)).circuit_level_acquisition_index,
    #         secondary_target=get_last_acquisition_operation(result, qubit_index=description.get_index(neighbor_b)).circuit_level_acquisition_index,
    #         reference_offset=ancilla_reference_offset + len(description.data_qubit_indices) if qec_cycles > 0 else ancilla_reference_offset,
    #         secondary_offset=len(description.ancilla_qubit_indices) if qec_cycles > 1 else None,
    #     ))
    # for data in description.data_qubit_indices:
    #     result.add(LogicalObservableOperation(
    #         qubit_index=data,
    #         last_acquisition_index=get_last_acquisition_operation(result).circuit_level_acquisition_index,
    #         main_target=get_last_acquisition_operation(result, qubit_index=data).circuit_level_acquisition_index
    #     ))
    return result


def construct_repetition_code_circuit_simplified(description: IRepetitionCodeDescription, qec_cycles: int, initial_state: InitialStateContainer = InitialStateContainer.empty()) -> DeclarativeCircuit:
    result: DeclarativeCircuit = DeclarativeCircuit()
    registry: AcquisitionRegistry = result.acquisition_registry
    result.add(get_circuit_initialize(
        connectivity=description,
        initial_state=initial_state,
    ))
    cycle_circuit: DeclarativeCircuit = DeclarativeCircuit(
        repetition_strategy=FixedRepetitionStrategy(repetitions=qec_cycles)
    )
    cycle_circuit.add(get_circuit_qec_round_with_dynamical_decoupling(
        connectivity=description,
        registry=registry
    ))

    result.add(cycle_circuit)
    result.add(get_circuit_final_measurement(
        connectivity=description,
        registry=registry,
    ))
    return result


if __name__ == '__main__':
    from qce_circuit.visualization.visualize_circuit.display_circuit import plot_circuit
    from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj
    import matplotlib.pyplot as plt
    from qce_circuit.addon_stim import to_stim

    initial_state: InitialStateContainer = InitialStateContainer.from_ordered_list([
        InitialStateEnum.ZERO,
        InitialStateEnum.ZERO,
        InitialStateEnum.ZERO,
        InitialStateEnum.ZERO,
        InitialStateEnum.ZERO,
    ])
    circuit_description: RepetitionCodeDescription = RepetitionCodeDescription.from_connectivity(
        involved_qubit_ids=[
            QubitIDObj('D7'),
            QubitIDObj('Z3'),
            QubitIDObj('D4'),
            QubitIDObj('Z1'),
            QubitIDObj('D5'),
            QubitIDObj('Z4'),
            QubitIDObj('D6'),
            QubitIDObj('Z2'),
            QubitIDObj('D3'),
        ],
        connectivity=Repetition9Code(),
    )
    circuit = construct_repetition_code_circuit(
        description=circuit_description,
        qec_cycles=7,
        initial_state=initial_state,
    )
    plot_circuit(circuit, channel_map=circuit_description.circuit_channel_map)
    plt.show()

    stim_circuit = to_stim(circuit)
    print(stim_circuit.diagram())

