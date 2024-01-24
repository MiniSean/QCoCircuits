import unittest
from typing import List
import numpy as np
from numpy.testing import assert_array_equal
from qce_circuit.structure.acquisition_indexing.kernel_repetition_code import (
    RepetitionIndexKernel,
    RepetitionExperimentKernel,
)
from qce_circuit.structure.acquisition_indexing.intrf_index_strategy import (
    FixedIndexStrategy,
    RelativeIndexStrategy,
)
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID, QubitIDObj


class RepetitionCodeKernelTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.start_index: int = 0
        cls.nr_repeated_parities: int = 5
        cls.data_qubit_ids: List[IQubitID] = [QubitIDObj('D1'), QubitIDObj('D2')]
        cls.ancilla_qubit_ids: List[IQubitID] = [QubitIDObj('X1')]
        cls.index_kernel = RepetitionIndexKernel(
            heralded_initialization=False,
            nr_repeated_parities=cls.nr_repeated_parities,
            index_offset_strategy=FixedIndexStrategy(index=cls.start_index),
            involved_data_qubit_ids=cls.data_qubit_ids,
            involved_ancilla_qubit_ids=cls.ancilla_qubit_ids,
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
            self.start_index + self.nr_repeated_parities - 1,
            msg="Included indices container (optional) heralded measurement the number of repeated parities and a final data qubit measurement during the last parity check round."
        )

    def test_start_and_end_indices_with_heralded_init(self):
        """Tests start and end indices with heralded initialization."""
        index_kernel = RepetitionIndexKernel(
            heralded_initialization=True,
            nr_repeated_parities=self.nr_repeated_parities,
            index_offset_strategy=FixedIndexStrategy(index=self.start_index),
            involved_data_qubit_ids=self.data_qubit_ids,
            involved_ancilla_qubit_ids=self.ancilla_qubit_ids,
        )

        self.assertEqual(
            index_kernel.start_index,
            self.start_index,
        )
        self.assertEqual(
            index_kernel.stop_index,
            self.start_index + self.nr_repeated_parities,
            msg="Included indices contains heralded measurement and parity measurements."
        )

    def test_relative_indices(self):
        """Tests relative indexing."""
        relative_strategy: RelativeIndexStrategy = RelativeIndexStrategy(self.index_kernel)
        index_kernel = RepetitionIndexKernel(
            heralded_initialization=False,
            nr_repeated_parities=self.nr_repeated_parities,
            index_offset_strategy=relative_strategy,
            involved_data_qubit_ids=self.data_qubit_ids,
            involved_ancilla_qubit_ids=self.ancilla_qubit_ids,
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
        data_qubit_id = self.data_qubit_ids[0]
        ancilla_qubit_id = self.ancilla_qubit_ids[0]
        assert_array_equal(
            self.index_kernel.contains(element=data_qubit_id),
            [self.nr_repeated_parities - 1],
            err_msg="Data qubit only contains final measurement round."
        )
        assert_array_equal(
            self.index_kernel.contains(element=ancilla_qubit_id),
            np.arange(self.nr_repeated_parities),
            err_msg="Ancilla qubit only contains final measurement round."
        )
        non_included_qubit = QubitIDObj('DummyID')
        assert_array_equal(
            self.index_kernel.contains(element=non_included_qubit),
            [],
            err_msg="If qubit ID is not included in indexing kernel, return empty array."
        )

    def test_specific_index_retrieval(self):
        """Tests specific index retrieval."""
        data_qubit_id = self.data_qubit_ids[0]
        ancilla_qubit_id = self.ancilla_qubit_ids[0]
        index_kernel = RepetitionIndexKernel(
            heralded_initialization=True,
            nr_repeated_parities=self.nr_repeated_parities,
            index_offset_strategy=FixedIndexStrategy(index=self.start_index),
            involved_data_qubit_ids=self.data_qubit_ids,
            involved_ancilla_qubit_ids=self.ancilla_qubit_ids,
        )

        assert_array_equal(
            index_kernel.get_heralded_measurement_index(element=data_qubit_id),
            [0],
        )
        assert_array_equal(
            index_kernel.get_heralded_measurement_index(element=ancilla_qubit_id),
            [0],
        )
        assert_array_equal(
            index_kernel.get_ordered_stabilizer_measurement_indices(element=data_qubit_id),
            [],
            err_msg="Data qubit are not expected to have stabilizer acquisition indices."
        )
        assert_array_equal(
            index_kernel.get_ordered_stabilizer_measurement_indices(element=ancilla_qubit_id),
            np.arange(1, self.nr_repeated_parities),
        )
        assert_array_equal(
            index_kernel.get_final_measurement_index(element=data_qubit_id),
            [index_kernel.stop_index],
        )
        assert_array_equal(
            index_kernel.get_final_measurement_index(element=ancilla_qubit_id),
            [index_kernel.stop_index],
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion


class RepetitionCodeExperimentKernelTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.start_index: int = 0
        cls.rounds: List[int] = [3, 6, 2]
        cls.use_heralded_initialization: bool = False
        cls.use_qutrit_calibration_points: bool = True
        cls.nr_experiment_repetitions: int = 5
        cls.data_qubit_ids: List[IQubitID] = [QubitIDObj('D1'), QubitIDObj('D2')]
        cls.ancilla_qubit_ids: List[IQubitID] = [QubitIDObj('X1')]
        cls.index_kernel = RepetitionExperimentKernel(
            rounds=cls.rounds,
            heralded_initialization=cls.use_heralded_initialization,
            qutrit_calibration_points=cls.use_qutrit_calibration_points,
            involved_data_qubit_ids=cls.data_qubit_ids,
            involved_ancilla_qubit_ids=cls.ancilla_qubit_ids,
            experiment_repetitions=cls.nr_experiment_repetitions,
        )

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_self_consistency(self):
        """Tests whether total dataset size corresponds with number of experiment repetitions."""
        expected_dataset_size: int = self.index_kernel.experiment_repetitions * self.index_kernel.kernel_cycle_length
        expected_experiment_repetitions: int = RepetitionExperimentKernel.estimate_experiment_repetitions(
            rounds=self.rounds,
            heralded_initialization=self.use_heralded_initialization,
            qutrit_calibration_points=self.use_qutrit_calibration_points,
            dataset_size=expected_dataset_size,
        )
        self.assertEqual(
            expected_experiment_repetitions,
            self.index_kernel.experiment_repetitions,
        )

    def test_start_and_end_indices(self):
        """Tests start and end indices without heralded initialization."""
        self.assertEqual(
            self.index_kernel.start_index,
            self.start_index,
        )
        count_heralded: int = len(self.rounds) * self.use_heralded_initialization
        count_parities: int = sum(self.rounds)
        count_calibration: int = 3 * (1 + self.use_heralded_initialization) * self.use_qutrit_calibration_points
        self.assertEqual(
            self.index_kernel.stop_index,
            self.start_index + (count_heralded + count_parities + count_calibration) * self.nr_experiment_repetitions,
        )

    def test_start_and_end_indices_with_heralded_init(self):
        """Tests start and end indices with heralded initialization."""
        use_heralded_initialization: bool = True
        index_kernel = RepetitionExperimentKernel(
            rounds=self.rounds,
            heralded_initialization=use_heralded_initialization,
            qutrit_calibration_points=self.use_qutrit_calibration_points,
            involved_data_qubit_ids=self.data_qubit_ids,
            involved_ancilla_qubit_ids=self.ancilla_qubit_ids,
            experiment_repetitions=self.nr_experiment_repetitions,
        )

        self.assertEqual(
            index_kernel.start_index,
            self.start_index,
        )
        count_heralded: int = len(self.rounds) * use_heralded_initialization
        count_parities: int = sum(self.rounds)
        count_calibration: int = 3 * (1 + use_heralded_initialization) * self.use_qutrit_calibration_points
        self.assertEqual(
            index_kernel.stop_index,
            self.start_index + (count_heralded + count_parities + count_calibration) * self.nr_experiment_repetitions,
        )
        self.assertNotEqual(
            self.index_kernel.stop_index,
            index_kernel.stop_index,
        )

    def test_specific_index_retrieval(self):
        """Tests specific index retrieval."""
        data_qubit_id = self.data_qubit_ids[0]
        ancilla_qubit_id = self.ancilla_qubit_ids[0]
        use_heralded_initialization: bool = True
        index_kernel = RepetitionExperimentKernel(
            rounds=self.rounds,
            heralded_initialization=use_heralded_initialization,
            qutrit_calibration_points=self.use_qutrit_calibration_points,
            involved_data_qubit_ids=self.data_qubit_ids,
            involved_ancilla_qubit_ids=self.ancilla_qubit_ids,
            experiment_repetitions=self.nr_experiment_repetitions,
        )

        for i, nr_repeated_parities in enumerate(self.rounds):
            cycle_offset: int = i * use_heralded_initialization + sum(self.rounds[:i])
            assert_array_equal(
                index_kernel.get_heralded_cycle_acquisition_indices(qubit_id=data_qubit_id, cycle_stabilizer_count=nr_repeated_parities),
                [
                    [0 * index_kernel.kernel_cycle_length + cycle_offset],
                    [1 * index_kernel.kernel_cycle_length + cycle_offset],
                    [2 * index_kernel.kernel_cycle_length + cycle_offset],
                    [3 * index_kernel.kernel_cycle_length + cycle_offset],
                    [4 * index_kernel.kernel_cycle_length + cycle_offset],
                ],
            )
            assert_array_equal(
                index_kernel.get_heralded_cycle_acquisition_indices(qubit_id=ancilla_qubit_id, cycle_stabilizer_count=nr_repeated_parities),
                [
                    [0 * index_kernel.kernel_cycle_length + cycle_offset],
                    [1 * index_kernel.kernel_cycle_length + cycle_offset],
                    [2 * index_kernel.kernel_cycle_length + cycle_offset],
                    [3 * index_kernel.kernel_cycle_length + cycle_offset],
                    [4 * index_kernel.kernel_cycle_length + cycle_offset],
                ],
            )
            assert_array_equal(
                index_kernel.get_stabilizer_and_projected_cycle_acquisition_indices(qubit_id=data_qubit_id, cycle_stabilizer_count=nr_repeated_parities),
                [
                    [0 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [1 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [2 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [3 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [4 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                ],
                err_msg="Data qubit are not expected to have stabilizer acquisition indices. But they are expected to have a single final projected acquisition index."
            )
            assert_array_equal(
                index_kernel.get_projected_cycle_acquisition_indices(qubit_id=data_qubit_id, cycle_stabilizer_count=nr_repeated_parities),
                [
                    [0 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [1 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [2 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [3 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [4 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                ],
            )
            assert_array_equal(
                index_kernel.get_projected_cycle_acquisition_indices(qubit_id=ancilla_qubit_id, cycle_stabilizer_count=nr_repeated_parities),
                [
                    [0 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [1 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [2 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [3 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                    [4 * index_kernel.kernel_cycle_length + cycle_offset + nr_repeated_parities],
                ],
            )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
