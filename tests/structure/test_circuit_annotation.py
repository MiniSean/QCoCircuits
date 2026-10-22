import unittest
from typing import List, Dict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
    RelationLink,
    RelationType,
)
from qce_circuit.structure.circuit_operations import (
    Rx180,
    Rx90,
)
from qce_circuit.structure.intrf_circuit_annotation import CircuitAnnotation
from qce_circuit.structure.intrf_circuit_operation_composite import CircuitCompositeOperation
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.visualization.visualize_circuit.display_circuit import plot_circuit


class CircuitAnnotationTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases."""
        pass

    def setUp(self) -> None:
        """Set up for every test case."""
        self.op1: ICircuitOperation = Rx180(qubit_index=0)
        self.op2: ICircuitOperation = Rx180(qubit_index=1, relation=RelationLink(self.op1, RelationType.JOINED_START))
        self.op3: ICircuitOperation = Rx90(qubit_index=0, relation=RelationLink(self.op1, RelationType.FOLLOWED_BY))
    # endregion

    # region Test Cases
    def test_circuit_annotation_dataclass(self) -> None:
        """Tests basic properties and immutability of CircuitAnnotation."""
        annotation = CircuitAnnotation(
            operations=[self.op1, self.op2],
            text_string="Entanglement Layer",
            text_vertical_offset=0.25,
        )

        self.assertEqual(annotation.operations, [self.op1, self.op2])
        self.assertEqual(annotation.text_string, "Entanglement Layer")
        self.assertAlmostEqual(annotation.text_vertical_offset, 0.25)

    def test_circuit_annotation_copy_with_transfer_lookup(self) -> None:
        """Tests copy behavior when remapping operations through a transfer lookup."""
        annotation = CircuitAnnotation(
            operations=[self.op1, self.op2],
            text_string="Original Annotation",
        )

        copied_op1 = self.op1.copy()
        copied_op2 = self.op2.copy()
        lookup: Dict[ICircuitOperation, ICircuitOperation] = {
            self.op1: copied_op1,
            self.op2: copied_op2,
        }

        copied_annotation = annotation.copy(relation_transfer_lookup=lookup)

        self.assertEqual(copied_annotation.text_string, "Original Annotation")
        self.assertEqual(copied_annotation.operations, [copied_op1, copied_op2])
        self.assertIsNot(copied_annotation.operations[0], self.op1)

    def test_declarative_circuit_add_annotation(self) -> None:
        """Tests integrating CircuitAnnotation into a DeclarativeCircuit."""
        circuit = DeclarativeCircuit(nr_qubits=2)
        added_op1 = circuit.add(self.op1)
        added_op2 = circuit.add(self.op2)

        annotation = CircuitAnnotation(
            operations=[added_op1, added_op2],
            text_string="Step 1",
        )
        circuit.add_annotation(annotation)

        self.assertEqual(len(circuit.annotations), 1)
        self.assertEqual(circuit.annotations[0].text_string, "Step 1")
        self.assertEqual(len(circuit.annotations[0].operations), 2)

    def test_composite_circuit_flattened_annotations(self) -> None:
        """Tests hierarchy propagation and flattening of annotations from nested subcircuits."""
        # Root composite
        root_composite = CircuitCompositeOperation()
        root_composite.add(self.op1)

        # Child subcircuit
        child_composite = CircuitCompositeOperation(relation=RelationLink(self.op1, RelationType.FOLLOWED_BY))
        child_op = Rx180(qubit_index=0)
        child_composite.add(child_op)

        child_annotation = CircuitAnnotation(
            operations=[child_op],
            text_string="Child Step",
        )
        child_composite.annotations.append(child_annotation)

        root_composite.add(child_composite)

        # Root annotation
        root_annotation = CircuitAnnotation(
            operations=[self.op1],
            text_string="Root Step",
        )
        root_composite.annotations.append(root_annotation)

        flattened = root_composite.get_flattened_annotations()
        self.assertEqual(len(flattened), 2)
        annotation_labels = [ann.text_string for ann in flattened]
        self.assertIn("Root Step", annotation_labels)
        self.assertIn("Child Step", annotation_labels)

    def test_composite_copy_propagates_annotations(self) -> None:
        """Tests that copying a composite operation copies and remaps its annotations."""
        composite = CircuitCompositeOperation()
        composite.add(self.op1)
        composite.annotations.append(CircuitAnnotation(operations=[self.op1], text_string="Block A"))

        copied = composite.copy()

        self.assertEqual(len(copied.annotations), 1)
        self.assertEqual(copied.annotations[0].text_string, "Block A")
        self.assertIsNot(copied.annotations[0], composite.annotations[0])

    def test_visualize_bracket_annotation_smoke(self) -> None:
        """Smoke test verifying plot_circuit renders bracket annotations without raising exceptions."""
        circuit = DeclarativeCircuit(nr_qubits=2)
        op_a = circuit.add(Rx180(qubit_index=0))
        op_b = circuit.add(Rx180(qubit_index=1, relation=RelationLink(op_a, RelationType.JOINED_START)))
        circuit.add(Rx90(qubit_index=0, relation=RelationLink(op_a, RelationType.FOLLOWED_BY)))

        circuit.add_annotation(CircuitAnnotation(
            operations=[op_a, op_b],
            text_string="State Prep",
            text_vertical_offset=0.1,
        ))

        fig, ax = plot_circuit(circuit=circuit)
        self.assertIsNotNone(fig)
        self.assertIsNotNone(ax)
        plt.close(fig)
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing."""
        plt.close('all')
    # endregion


if __name__ == '__main__':
    unittest.main()
