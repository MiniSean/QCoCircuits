import unittest
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.intrf_circuit_operation import RelationType
from qce_circuit.structure.registry_repetition import FixedRepetitionStrategy
from qce_circuit.visualization.visualize_circuit.display_circuit import plot_circuit
from qce_circuit.structure.circuit_operations import *
from qce_circuit.structure.intrf_circuit_operation_composite import (
    OperationGraphNode,
    CircuitCompositeOperation,
)
import matplotlib.pyplot as plt


class DeclarativeCircuitTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        pass

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_circuit_example_0(self):
        """Tests construction of arbitrary circuit example."""
        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=3)
        circuit.add(Reset(
            qubit_index=8,
        ))
        circuit.add(Reset(
            qubit_index=2,
        ))
        circuit.add(Wait(
            qubit_index=0,
        ))
        circuit.add(Rx90(
            qubit_index=2,
        ))
        circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=2,
        ))
        circuit.add(VirtualPhase(
            qubit_index=2,
        ))
        circuit.add(VirtualPhase(
            qubit_index=8,
        ))
        # Artificial conditional oscillation
        circuit.add(Rphi90(
            qubit_index=8,
        ))

        relation: RelationLink = RelationLink(circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        circuit.add(DispersiveMeasure(
            qubit_index=2,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy()
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=8,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy()
        ))
        plot_circuit(circuit=circuit)

    def test_circuit_example_1(self):
        """Tests construction of arbitrary circuit example."""
        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=3)
        circuit.add(Reset(
            qubit_index=8,
        ))
        circuit.add(Reset(
            qubit_index=2,
        ))
        circuit.add(Reset(
            qubit_index=0,
        ))

        circuit.add(Rx90(
            qubit_index=8,
        ))
        circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=2,
        ))
        # Park
        circuit.add(VirtualPhase(
            qubit_index=2,
        ))
        circuit.add(VirtualPhase(
            qubit_index=8,
        ))

        circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=0,
        ))
        # Park
        circuit.add(VirtualPhase(
            qubit_index=0,
        ))
        circuit.add(VirtualPhase(
            qubit_index=8,
        ))
        # Artificial conditional osillation
        circuit.add(Rphi90(
            qubit_index=8,
        ))

        relation: RelationLink = RelationLink(circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        circuit.add(DispersiveMeasure(
            qubit_index=2,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=8,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=0,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))

    def test_circuit_example_2(self):
        """Tests construction of arbitrary circuit example."""
        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=3)
        circuit.add(Reset(
            qubit_index=8,
        ))
        circuit.add(Reset(
            qubit_index=2,
        ))
        circuit.add(Reset(
            qubit_index=0,
        ))

        circuit.add(Rx90(
            qubit_index=2,
        ))
        circuit.add(Rx90(
            qubit_index=0,
        ))
        circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=2,
        ))
        # Park
        circuit.add(VirtualPhase(
            qubit_index=2,
        ))
        circuit.add(VirtualPhase(
            qubit_index=8,
        ))

        circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=0,
        ))
        # Park
        circuit.add(VirtualPhase(
            qubit_index=0,
        ))
        circuit.add(VirtualPhase(
            qubit_index=8,
        ))
        # Artificial conditional osillation
        relation: RelationLink = RelationLink(circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        circuit.add(Rphi90(
            qubit_index=2,
            relation=relation,
        ))
        circuit.add(Rphi90(
            qubit_index=0,
            relation=relation,
        ))

        relation: RelationLink = RelationLink(circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        circuit.add(DispersiveMeasure(
            qubit_index=2,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=8,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=0,
            relation=relation,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))

    def test_circuit_example_3(self):
        """Tests construction of arbitrary circuit example."""
        sub_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=3,
            repetition_strategy=FixedRepetitionStrategy(repetitions=1)
        )
        sub_circuit.add(Ry90(
            qubit_index=8,
        ))
        sub_circuit.add(Ry90(
            qubit_index=2,
        ))
        sub_circuit.add(Ry90(
            qubit_index=0,
        ))
        sub_circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=2,
        ))
        # Park
        sub_circuit.add(VirtualPhase(
            qubit_index=2,
        ))
        sub_circuit.add(VirtualPhase(
            qubit_index=8,
        ))

        sub_circuit.add(CPhase(
            _control_qubit_index=8,
            _target_qubit_index=0,
        ))
        # Park
        sub_circuit.add(VirtualPhase(
            qubit_index=0,
        ))
        sub_circuit.add(VirtualPhase(
            qubit_index=8,
        ))
        relation: RelationLink = RelationLink(sub_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        sub_circuit.add(Rym90(
            qubit_index=8,
            relation=relation,
        ))
        sub_circuit.add(Rym90(
            qubit_index=2,
            relation=relation,
        ))
        sub_circuit.add(Rym90(
            qubit_index=0,
            relation=relation,
        ))

        dynamic_decoupled_measure_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=3,
            repetition_strategy=FixedRepetitionStrategy(repetitions=1)
        )
        dynamical_decoupling_wait = FixedDurationStrategy(duration=0.5)
        dynamic_decoupled_measure_circuit.add(DispersiveMeasure(
            qubit_index=8,
            acquisition_strategy=dynamic_decoupled_measure_circuit.get_acquisition_strategy()
        ))
        dynamic_decoupled_measure_circuit.add(Wait(
            qubit_index=2,
            duration_strategy=dynamical_decoupling_wait,
        ))
        dynamic_decoupled_measure_circuit.add(Wait(
            qubit_index=0,
            duration_strategy=dynamical_decoupling_wait,
        ))
        dynamic_decoupled_measure_circuit.add(Rx180(
            qubit_index=2,
        ))
        dynamic_decoupled_measure_circuit.add(Rx180(
            qubit_index=0,
        ))
        dynamic_decoupled_measure_circuit.add(Wait(
            qubit_index=2,
            duration_strategy=dynamical_decoupling_wait,
        ))
        dynamic_decoupled_measure_circuit.add(Wait(
            qubit_index=0,
            duration_strategy=dynamical_decoupling_wait,
        ))

        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=3)
        circuit.add(Reset(
            qubit_index=8,
        ))
        circuit.add(Reset(
            qubit_index=2,
        ))
        circuit.add(Reset(
            qubit_index=0,
        ))
        circuit.add(sub_circuit._structure)
        circuit.add(dynamic_decoupled_measure_circuit._structure)
        circuit.add(sub_circuit._structure.copy())
        circuit.add(DispersiveMeasure(
            qubit_index=8,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=2,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=0,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))

    def test_circuit_example_4(self):
        """Tests construction of arbitrary circuit example."""
        # Bit-flip repetition code
        qubit_ancilla_index: int = 12
        qubit_data1_index: int = 1
        qubit_data2_index: int = 15

        individual_parity_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=3,
            repetition_strategy=FixedRepetitionStrategy(repetitions=1)
        )
        individual_parity_circuit.add(Ry90(
            qubit_index=qubit_ancilla_index,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla_index,
            _target_qubit_index=qubit_data1_index,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla_index,
            _target_qubit_index=qubit_data2_index,
        ))
        relation: RelationLink = RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        individual_parity_circuit.add(Rym90(
            qubit_index=qubit_ancilla_index,
            relation=relation,
        ))

        repeated_parity_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=3,
            repetition_strategy=FixedRepetitionStrategy(repetitions=10)
        )
        repeated_parity_circuit.add(individual_parity_circuit._structure.copy())
        relation: RelationLink = RelationLink(repeated_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        # Dynaical decoupling
        dynamical_decoupling_wait = FixedDurationStrategy(duration=0.5)
        repeated_parity_circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla_index,
            acquisition_strategy=repeated_parity_circuit.get_acquisition_strategy()
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data1_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data2_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Rx180(
            qubit_index=qubit_data1_index,
        ))
        repeated_parity_circuit.add(Rx180(
            qubit_index=qubit_data2_index,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data1_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data2_index,
            duration_strategy=dynamical_decoupling_wait,
        ))

        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=3)
        circuit.add(repeated_parity_circuit._structure)
        circuit.add(individual_parity_circuit._structure)
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data1_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data2_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))

    def test_circuit_example_5(self):
        """Tests construction of arbitrary circuit example."""
        # Bit-flip repetition distance-3 code
        qubit_ancilla1_index: int = 'Z1'  # 7   # Z1
        qubit_ancilla2_index: int = 'Z3'  # 12  # Z3
        qubit_data1_index: int = 'D5'  # 13     # D5
        qubit_data2_index: int = 'D4'  # 15     # D4
        qubit_data3_index: int = 'D7'  # 1      # D7

        individual_parity_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=5,
            repetition_strategy=FixedRepetitionStrategy(repetitions=1)
        )
        individual_parity_circuit.add(Ry90(
            qubit_index=qubit_ancilla1_index,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla1_index,
            _target_qubit_index=qubit_data2_index,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla1_index,
            _target_qubit_index=qubit_data1_index,
        ))
        individual_parity_circuit.add(Rym90(
            qubit_index=qubit_ancilla1_index,
        ))
        relation: RelationLink = RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla2_index,
            _target_qubit_index=qubit_data3_index,
            relation=relation,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla2_index,
            _target_qubit_index=qubit_data2_index,
        ))

        repeated_parity_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=5,
            repetition_strategy=FixedRepetitionStrategy(repetitions=9)
        )
        repeated_parity_circuit.add(individual_parity_circuit._structure.copy())
        # Dynamical decoupling
        dynamical_decoupling_wait = FixedDurationStrategy(duration=0.5)
        repeated_parity_circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla1_index,
            acquisition_strategy=repeated_parity_circuit.get_acquisition_strategy(),
        ))
        repeated_parity_circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla2_index,
            acquisition_strategy=repeated_parity_circuit.get_acquisition_strategy(),
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data1_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data2_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data3_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Rx180(
            qubit_index=qubit_data1_index,
        ))
        repeated_parity_circuit.add(Rx180(
            qubit_index=qubit_data2_index,
        ))
        repeated_parity_circuit.add(Rx180(
            qubit_index=qubit_data3_index,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data1_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data2_index,
            duration_strategy=dynamical_decoupling_wait,
        ))
        repeated_parity_circuit.add(Wait(
            qubit_index=qubit_data3_index,
            duration_strategy=dynamical_decoupling_wait,
        ))

        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=5)
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data3_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data2_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data1_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla1_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla2_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(repeated_parity_circuit._structure)
        circuit.add(individual_parity_circuit._structure)
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla1_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_ancilla2_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data1_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data2_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_data3_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
        ))

    def test_apply_simple_one_channel_repetition_modifier(self):
        """Tests nested composite operation with repetition modifier."""
        # Bit-flip repetition distance-5 code
        qubit1_index: int = 0
        repetitions: int = 3

        repeated_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=1,
            repetition_strategy=FixedRepetitionStrategy(repetitions=repetitions)
        )
        repeated_circuit.add(Ry90(
            qubit_index=qubit1_index,
        ))

        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=1)
        circuit.add(repeated_circuit)
        circuit.add(Rx90(
            qubit_index=qubit1_index,
        ))

        expected_operation_length: int = 1 + 1
        expected_modified_operation_length: int = 1 * repetitions + 1
        self.assertEqual(
            len(circuit.operations),
            expected_operation_length,
        )
        # Apply modifier
        modified_circuit = circuit.apply_modifiers()
        self.assertEqual(
            len(circuit.operations),
            expected_modified_operation_length,
            msg="Expects original circuit to be affected by applying the modifiers."
        )
        self.assertEqual(
            len(modified_circuit.operations),
            expected_modified_operation_length,
        )

        fig, ax = plot_circuit(circuit=circuit)
        fig, ax = plot_circuit(circuit=modified_circuit)

    def test_apply_simple_two_channel_repetition_modifier(self):
        """Tests nested composite operation with repetition modifier."""
        # Bit-flip repetition distance-5 code
        qubit1_index: int = 0
        qubit2_index: int = 1
        repetitions: int = 3

        repeated_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=1,
            repetition_strategy=FixedRepetitionStrategy(repetitions=repetitions)
        )
        repeated_circuit.add(Ry90(
            qubit_index=qubit1_index,
        ))

        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=1)
        circuit.add(repeated_circuit._structure.copy())
        circuit.add(Rx90(
            qubit_index=qubit2_index,
            relation=RelationLink(circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))

        expected_operation_length: int = 1 + 1
        expected_modified_operation_length: int = 1 * repetitions + 1
        self.assertEqual(
            len(circuit.operations),
            expected_operation_length,
        )
        # Apply modifier
        modified_circuit = circuit.apply_modifiers()
        self.assertEqual(
            len(circuit.operations),
            expected_modified_operation_length,
            msg="Expects original circuit to be affected by applying the modifiers."
        )
        self.assertEqual(
            len(modified_circuit.operations),
            expected_modified_operation_length,
        )

        fig, ax = plot_circuit(circuit=circuit)
        fig, ax = plot_circuit(circuit=modified_circuit)

    def test_apply_parallel_repetition_modifier(self):
        """Tests nested composite operation with repetition modifier."""
        # Bit-flip repetition distance-5 code
        qubit1_index: int = 0
        inner_repetitions: int = 3
        outer_repetitions: int = 2

        repeated_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=1,
            repetition_strategy=FixedRepetitionStrategy(repetitions=inner_repetitions)
        )
        repeated_circuit.add(Ry90(
            qubit_index=qubit1_index,
        ))

        # Parallel repeated circuit in single circuit
        parallel_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=1,
            repetition_strategy=FixedRepetitionStrategy(repetitions=outer_repetitions)
        )
        parallel_circuit.add(Identity(
            qubit_index=qubit1_index,
        ))

        # Nest single circuit in main circuit
        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=1)
        added_repeated_circuit: ICircuitOperation = circuit.add(repeated_circuit)
        added_parallel_circuit: ICircuitOperation = circuit.add(parallel_circuit)

        self.assertEqual(
            added_parallel_circuit.relation_link.reference_node,
            added_repeated_circuit,
            msg=f"Expects relation to be established and not be none. Instead: {added_parallel_circuit.relation_link.reference_node}."
        )

        high_level_nodes: List[OperationGraphNode] = list(circuit._structure._circuit_graph.get_node_iterator())
        # Apply modifier
        modified_circuit = circuit.apply_modifiers()
        modified_high_level_nodes: List[OperationGraphNode] = list(modified_circuit._structure._circuit_graph.get_node_iterator())
        self.assertEqual(
            len(high_level_nodes),
            len(modified_high_level_nodes),
            msg="Expects number of high level nodes to be identical after modifiers are applied."
        )
        for i in range(len(high_level_nodes)):
            with self.subTest(i):
                self.assertEqual(
                    high_level_nodes[i],
                    modified_high_level_nodes[i],
                    msg="Modified nodes are equal."
                )

        self.assertEqual(
            modified_high_level_nodes[1].operation.relation_link.reference_node,
            modified_high_level_nodes[0].operation,
            msg=f"Expects relation to be re-established after modification and not be none. Instead: {modified_high_level_nodes[1].operation.relation_link.reference_node}."
        )

        fig, ax = plot_circuit(circuit=circuit)
        fig, ax = plot_circuit(circuit=modified_circuit)

    def test_apply_nested_one_channel_repetition_modifier(self):
        """Tests nested composite operation with repetition modifier."""
        # Bit-flip repetition distance-5 code
        qubit1_index: int = 0
        qubit2_index: int = 1
        inner_repetitions: int = 3
        outer_repetitions: int = 2

        repeated_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=1,
            repetition_strategy=FixedRepetitionStrategy(repetitions=inner_repetitions)
        )
        input_operation = Ry90(
            qubit_index=qubit1_index,
        )
        repeated_circuit.add(input_operation)

        # Nest repeated circuit in single circuit
        single_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=1,
            repetition_strategy=FixedRepetitionStrategy(repetitions=outer_repetitions)
        )
        single_circuit.add(repeated_circuit._structure)
        single_circuit.add(Identity(
            qubit_index=qubit2_index,
            relation=RelationLink(single_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))

        # Nest single circuit in main circuit
        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=1)
        circuit.add(single_circuit._structure)

        circuit_structure: CircuitCompositeOperation = circuit._structure
        self.assertEqual(
            len(list(circuit_structure._circuit_graph.get_node_iterator())),
            len(list(circuit_structure.copy()._circuit_graph.get_node_iterator())),
            msg="Expects copied structure to have the same number of high level nodes"
        )

        self.assertEqual(
            len(list(circuit_structure.decomposed_operations())),
            len(list(circuit_structure.copy().decomposed_operations())),
            msg="Expects copied structure to have the same number of decomposed nodes"
        )

        # Apply modifier
        modified_circuit = circuit.apply_modifiers()

        fig, ax = plot_circuit(circuit=circuit)
        fig, ax = plot_circuit(circuit=modified_circuit)

    def test_circuit_example_6(self):
        """Tests construction of arbitrary circuit example."""
        # Bit-flip repetition distance-5 code
        qubit_ancilla1_index: int = 'Z1'  # 7   # Z1
        qubit_ancilla2_index: int = 'Z3'  # 12  # Z3
        qubit_ancilla3_index: int = 'Z2'  # 14  # Z2
        qubit_ancilla4_index: int = 'Z4'  # 10  # Z4
        qubit_data1_index: int = 'D5'  # 13     # D5
        qubit_data2_index: int = 'D4'  # 15     # D4
        qubit_data3_index: int = 'D7'  # 1      # D7
        qubit_data4_index: int = 'D6'  # 16     # D6
        qubit_data5_index: int = 'D3'  # 0      # D3
        # Qubit index groups
        ancilla_indices: List[int] = [qubit_ancilla1_index, qubit_ancilla2_index, qubit_ancilla3_index,
                                      qubit_ancilla4_index]
        data_indices: List[int] = [qubit_data1_index, qubit_data2_index, qubit_data3_index, qubit_data4_index,
                                   qubit_data5_index]
        all_indices: List[int] = data_indices + ancilla_indices

        individual_parity_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=5,
            repetition_strategy=FixedRepetitionStrategy(repetitions=1)
        )
        individual_parity_circuit.add(Ry90(
            qubit_index=qubit_ancilla1_index,
        ))
        individual_parity_circuit.add(Ry90(
            qubit_index=qubit_ancilla3_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.JOINED_START)
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla1_index,
            _target_qubit_index=qubit_data2_index,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla3_index,
            _target_qubit_index=qubit_data4_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla1_index,
            _target_qubit_index=qubit_data1_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla3_index,
            _target_qubit_index=qubit_data5_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(Rym90(
            qubit_index=qubit_ancilla1_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        relation: RelationLink = RelationLink(individual_parity_circuit.get_last_entry(), RelationType.JOINED_START)
        individual_parity_circuit.add(Rym90(
            qubit_index=qubit_ancilla3_index,
            relation=relation,
        ))
        individual_parity_circuit.add(Ry90(
            qubit_index=qubit_ancilla2_index,
            relation=relation,
        ))
        individual_parity_circuit.add(Ry90(
            qubit_index=qubit_ancilla4_index,
            relation=relation
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla2_index,
            _target_qubit_index=qubit_data3_index,
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla4_index,
            _target_qubit_index=qubit_data1_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla2_index,
            _target_qubit_index=qubit_data2_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(CPhase(
            _control_qubit_index=qubit_ancilla4_index,
            _target_qubit_index=qubit_data4_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(Rym90(
            qubit_index=qubit_ancilla2_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        ))
        individual_parity_circuit.add(Rym90(
            qubit_index=qubit_ancilla4_index,
            relation=RelationLink(individual_parity_circuit.get_last_entry(), RelationType.JOINED_START)
        ))

        repeated_parity_circuit: DeclarativeCircuit = DeclarativeCircuit(
            nr_qubits=5,
            repetition_strategy=FixedRepetitionStrategy(repetitions=2)
        )
        repeated_parity_circuit.add(individual_parity_circuit._structure.copy())
        relation: RelationLink = RelationLink(repeated_parity_circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        # Dynamical decoupling
        dynamical_decoupling_wait = FixedDurationStrategy(duration=0.5)
        for ancilla_index in ancilla_indices:
            repeated_parity_circuit.add(DispersiveMeasure(
                qubit_index=ancilla_index,
                relation=relation,
                acquisition_strategy=repeated_parity_circuit.get_acquisition_strategy(),
            ))
        for data_index in data_indices:
            repeated_parity_circuit.add(Wait(
                qubit_index=data_index,
                duration_strategy=dynamical_decoupling_wait,
            ))
            repeated_parity_circuit.add(Rx180(
                qubit_index=data_index,
            ))
            repeated_parity_circuit.add(Wait(
                qubit_index=data_index,
                duration_strategy=dynamical_decoupling_wait,
            ))

        circuit: DeclarativeCircuit = DeclarativeCircuit(nr_qubits=5)
        circuit.add(repeated_parity_circuit._structure)
        # circuit.add(individual_parity_circuit._structure)
        relation: RelationLink = RelationLink(circuit.get_last_entry(), RelationType.FOLLOWED_BY)
        for qubit_index in data_indices:
            circuit.add(DispersiveMeasure(
                qubit_index=qubit_index,
                relation=relation,
                acquisition_strategy=circuit.get_acquisition_strategy(),
            ))

        # Apply modifier
        modified_circuit = circuit.apply_modifiers()

        channel_order = ['D3', 'D4', 'D5', 'D6', 'D7', 'Z1', 'Z2', 'Z3', 'Z4']
        fig, ax = plot_circuit(circuit=circuit, channel_order=channel_order)
        fig, ax = plot_circuit(circuit=modified_circuit, channel_order=channel_order)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        plt.close('all')
    # endregion
