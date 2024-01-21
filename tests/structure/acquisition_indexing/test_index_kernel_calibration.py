import unittest
from numpy.testing import assert_array_equal
from qce_utils.control_interfaces.circuit_definitions.structure.acquisition_indexing.kernel_calibration import (
    QutritCalibrationIndexKernel,
)
from qce_utils.control_interfaces.circuit_definitions.structure.acquisition_indexing.intrf_index_strategy import (
    FixedIndexStrategy,
    RelativeIndexStrategy,
)
from qce_utils.control_interfaces.intrf_channel_identifier import IQubitID, QubitIDObj


class QutritCalibrationKernelTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.start_index: int = 0
        cls.qubit_id: IQubitID = QubitIDObj('Q')
        cls.index_kernel = QutritCalibrationIndexKernel(
            heralded_initialization=False,
            index_offset_strategy=FixedIndexStrategy(index=cls.start_index),
            involved_qubit_ids=[cls.qubit_id]
        )

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_start_and_end_indices(self):
        """Tests start and end indices without heralded initialization."""
        self.assertEqual(
            self.index_kernel.start_index,
            self.start_index,
        )
        self.assertEqual(
            self.index_kernel.stop_index,
            self.start_index + 2,
            msg="Included indices are i, i+1 and i+2 because of the 3 state calibration."
        )

    def test_start_and_end_indices_with_heralded_init(self):
        """Tests start and end indices with heralded initialization."""
        index_kernel = QutritCalibrationIndexKernel(
            heralded_initialization=True,
            index_offset_strategy=FixedIndexStrategy(index=self.start_index),
            involved_qubit_ids=[self.qubit_id]
        )

        self.assertEqual(
            index_kernel.start_index,
            self.start_index,
        )
        self.assertEqual(
            index_kernel.stop_index,
            self.start_index + 2 + 3,
            msg="Included indices are i, ..., i+5 because of heralded acquisition is performed at i, i+2 and i+4."
        )

    def test_relative_indices(self):
        """Tests relative indexing."""
        relative_strategy: RelativeIndexStrategy = RelativeIndexStrategy(self.index_kernel)
        index_kernel = QutritCalibrationIndexKernel(
            heralded_initialization=False,
            index_offset_strategy=relative_strategy,
            involved_qubit_ids=[self.qubit_id]
        )

        self.assertEqual(
            self.index_kernel.start_index,
            self.start_index,
        )
        self.assertEqual(
            index_kernel.start_index,
            self.index_kernel.stop_index + 1,
            msg="Index kernel will start relative to other kernel."
        )

    def test_index_inclusion(self):
        """Tests arbitrary index retrieval."""
        assert_array_equal(
            self.index_kernel.contains(element=self.qubit_id),
            [0, 1, 2],
        )
        non_included_qubit = QubitIDObj('DummyID')
        assert_array_equal(
            self.index_kernel.contains(element=non_included_qubit),
            [],
            err_msg="If qubit ID is not included in indexing kernel, return empty array."
        )

    def test_specific_index_retrieval(self):
        """Tests specific index retrieval."""
        index_kernel = QutritCalibrationIndexKernel(
            heralded_initialization=True,
            index_offset_strategy=FixedIndexStrategy(index=self.start_index),
            involved_qubit_ids=[self.qubit_id]
        )

        assert_array_equal(
            index_kernel.get_heralded_state_0_measurement_index(element=self.qubit_id),
            [0],
        )
        assert_array_equal(
            index_kernel.get_state_0_measurement_index(element=self.qubit_id),
            [1],
        )
        assert_array_equal(
            index_kernel.get_heralded_state_1_measurement_index(element=self.qubit_id),
            [2],
        )
        assert_array_equal(
            index_kernel.get_state_1_measurement_index(element=self.qubit_id),
            [3],
        )
        assert_array_equal(
            index_kernel.get_heralded_state_2_measurement_index(element=self.qubit_id),
            [4],
        )
        assert_array_equal(
            index_kernel.get_state_2_measurement_index(element=self.qubit_id),
            [5],
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
