import unittest
import numpy as np
from numpy.testing import assert_array_equal
from qce_circuit.structure.registry_acquisition import (
    AcquisitionRegistry,
    RegistryAcquisitionStrategy,
)
from qce_circuit.structure.registry_repetition import (
    FixedRepetitionStrategy,
)
from qce_circuit.structure.intrf_acquisition_operation import (
    AcquisitionTag,
)
from qce_circuit.language.declarative_circuit import (
    IDeclarativeCircuit,
    DeclarativeCircuit,
)
from qce_circuit.structure.intrf_circuit_operation_composite import (
    ICircuitCompositeOperation,
    CircuitCompositeOperation,
)
from qce_circuit.structure.circuit_operations import (
    DispersiveMeasure,
)


class AcquisitionIdentifierTestCase(unittest.TestCase):

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
    def test_basic_acquisition_order(self):
        """Tests acquisition index order."""
        qubit_index: int = 0
        circuit: IDeclarativeCircuit = DeclarativeCircuit()
        registry: AcquisitionRegistry = AcquisitionRegistry(circuit=circuit._structure)

        acquisition_0 = DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=registry),
        )
        circuit.add(acquisition_0)
        acquisition_1 = DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=registry),
        )
        circuit.add(acquisition_1)

        self.assertEqual(
            acquisition_0.acquisition_index,
            0,
        )
        self.assertEqual(
            acquisition_1.acquisition_index,
            1,
        )

    def test_acquisition_order_using_tags(self):
        """Tests acquisition index order."""
        qubit_index: int = 0
        tag_heralded: str = 'heralded'
        tag_final: str = 'final'

        circuit: IDeclarativeCircuit = DeclarativeCircuit()

        acquisition_0 = DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
            acquisition_tag=tag_heralded,
        )
        circuit.add(acquisition_0)
        acquisition_1 = DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
            acquisition_tag=tag_final,
        )
        circuit.add(acquisition_1)

        assert_array_equal(
            circuit.get_acquisition_indices(qubit_index),
            np.asarray([0, 1])
        )
        assert_array_equal(
            circuit.get_acquisition_indices(AcquisitionTag(
                qubit_index=qubit_index,
                tag=tag_heralded
            )),
            np.asarray([0])
        )
        assert_array_equal(
            circuit.get_acquisition_indices(AcquisitionTag(
                qubit_index=qubit_index,
                tag=tag_final
            )),
            np.asarray([1])
        )

    def test_acquisition_order_after_repetition_modifier(self):
        """Tests acquisition index order."""
        qubit_index: int = 0
        tag_heralded: str = 'heralded'
        tag_final: str = 'final'

        circuit: IDeclarativeCircuit = DeclarativeCircuit(
            repetition_strategy=FixedRepetitionStrategy(repetitions=3)
        )

        acquisition_0 = DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
            acquisition_tag=tag_heralded,
        )
        circuit.add(acquisition_0)
        acquisition_1 = DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=circuit.get_acquisition_strategy(),
            acquisition_tag=tag_final,
        )
        circuit.add(acquisition_1)

        # Apply modifier
        modified_circuit = circuit.apply_modifiers()

        assert_array_equal(
            modified_circuit.get_acquisition_indices(qubit_index),
            np.asarray([0, 1, 2, 3, 4, 5])
        )
        assert_array_equal(
            modified_circuit.get_acquisition_indices(AcquisitionTag(
                qubit_index=qubit_index,
                tag=tag_heralded
            )),
            np.asarray([0, 2, 4])
        )
        assert_array_equal(
            modified_circuit.get_acquisition_indices(AcquisitionTag(
                qubit_index=qubit_index,
                tag=tag_final
            )),
            np.asarray([1, 3, 5])
        )

    def test_nested_acquisition_order(self):
        """Tests acquisition index order."""
        qubit_index: int = 0
        tag_heralded: str = 'heralded'
        tag_final: str = 'final'

        sub_circuit: IDeclarativeCircuit = DeclarativeCircuit()
        sub_registry: AcquisitionRegistry = AcquisitionRegistry(circuit=sub_circuit.circuit_structure)
        sub_circuit.add(DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=sub_registry),
            acquisition_tag=tag_heralded,
        ))
        sub_circuit.add(DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=sub_registry),
            acquisition_tag=tag_final,
        ))

        circuit: IDeclarativeCircuit = DeclarativeCircuit()
        registry: AcquisitionRegistry = AcquisitionRegistry(circuit=circuit.circuit_structure)
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=registry),
            acquisition_tag=tag_heralded,
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=registry),
            acquisition_tag=tag_final,
        ))
        circuit.add_declarative_circuit(sub_circuit)

        assert_array_equal(
            circuit.get_acquisition_indices(qubit_index),
            np.asarray([0, 1, 2, 3]),
            err_msg="Expects sub circuit to take reference from super circuit."
        )
        assert_array_equal(
            circuit.get_acquisition_indices(AcquisitionTag(
                qubit_index=qubit_index,
                tag=tag_heralded
            )),
            np.asarray([0, 2])
        )
        assert_array_equal(
            circuit.get_acquisition_indices(AcquisitionTag(
                qubit_index=qubit_index,
                tag=tag_final
            )),
            np.asarray([1, 3])
        )

    def test_multi_qubit_acquisition_order(self):
        """Tests acquisition index order."""
        qubit_index_0: int = 0
        qubit_index_1: int = 1

        circuit: IDeclarativeCircuit = DeclarativeCircuit()

        registry: AcquisitionRegistry = AcquisitionRegistry(circuit=circuit._structure)
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_index_0,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=registry),
        ))
        circuit.add(DispersiveMeasure(
            qubit_index=qubit_index_1,
            acquisition_strategy=RegistryAcquisitionStrategy(registry=registry),
        ))

        assert_array_equal(
            circuit.get_acquisition_indices(qubit_index_0),
            np.asarray([0]),
            err_msg="Expects acquisition indices to count individually per qubit-ID."
        )
        assert_array_equal(
            circuit.get_acquisition_indices(qubit_index_1),
            np.asarray([0]),
            err_msg="Expects acquisition indices to count individually per qubit-ID."
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
