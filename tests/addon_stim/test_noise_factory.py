import unittest
import stim
from qce_circuit.language.intrf_declarative_circuit import (
    IDeclarativeCircuit,
    InitialStateEnum,
)
from qce_circuit.library.repetition_code_circuit import (
    construct_repetition_code_circuit,
    InitialStateContainer,
)
from qce_circuit.addon_stim import to_stim
from qce_circuit.addon_stim.noise_factory_manager import apply_noise
from qce_circuit.addon_stim.noise_settings_manager import (
    NoiseSettingManager,
    IndexedNoiseSettings,
    NoiseSettings,
    QubitNoiseModelParameters,
)
from qce_circuit.connectivity.intrf_channel_identifier import QubitIDObj


class StimNoiseSettingsManagerTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        cls.settings = NoiseSettingManager.read_config()

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_import_noise_settings(self):
        """Tests import of noise settings."""
        self.assertIsInstance(
            self.settings,
            NoiseSettings,
        )
        self.assertIsInstance(
            self.settings.individual_noise,
            dict
        )

    def test_obtain_default_noise_settings(self):
        """Tests import of default (qubit) noise settings."""
        default_settings = self.settings.get_default_noise_settings()
        self.assertIsInstance(
            default_settings,
            QubitNoiseModelParameters,
        )
        self.assertTrue(
            0 <= default_settings.t1,
        )
        self.assertTrue(
            0 <= default_settings.t2,
        )
        self.assertTrue(
            0 <= default_settings.assignment_error <= 1,
        )
        self.assertTrue(
            0 <= default_settings.single_qubit_gate_error <= 1,
        )

    def test_construct_indexed_noise_settings(self):
        """Tests construction of indexed noise settings."""
        qubit_index_lookup = {
            0: QubitIDObj('Dummy0'),
            1: QubitIDObj('Dummy1'),
            2: QubitIDObj('Dummy2'),
        }
        indexed_settings = IndexedNoiseSettings(
            noise_settings=self.settings,
            qubit_index_lookup=qubit_index_lookup
        )
        self.assertTrue(
            indexed_settings.contains(0)
        )
        self.assertFalse(
            indexed_settings.contains(3)
        )
        self.assertEqual(
            indexed_settings.get_noise_settings(3),
            self.settings.get_default_noise_settings(),
            msg="Expects default noise settings to be returned if index is not present in lookup"
        )

    def test_specific_noise_settings(self):
        """Tests construction of indexed noise settings."""
        specific_qubit_id = QubitIDObj('D3')
        specific_parameters = QubitNoiseModelParameters(
            t1=20e-6,
            t2=40e-6,
            assignment_error=0.02,
            single_qubit_gate_error=0.01,
        )
        settings = NoiseSettings(
            individual_noise={
                specific_qubit_id: specific_parameters
            }
        )
        indexed_settings = IndexedNoiseSettings(
            noise_settings=settings,
            qubit_index_lookup={0: specific_qubit_id}
        )
        self.assertEqual(
            indexed_settings.get_noise_settings(0),
            specific_parameters,
            msg="Expects specific noise settings to be returned if index is present in lookup"
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion


class StimNoiseFactoryTestCase(unittest.TestCase):

    # region Setup
    @classmethod
    def setUpClass(cls) -> None:
        """Set up for all test cases"""
        initial_state = InitialStateContainer.from_ordered_list([
            InitialStateEnum.ZERO,
            InitialStateEnum.ONE,
            InitialStateEnum.ZERO,
        ])
        cls.circuit_with_detectors: IDeclarativeCircuit = construct_repetition_code_circuit(
            initial_state=initial_state,
            qec_cycles=1,
        )

    def setUp(self) -> None:
        """Set up for every test case"""
        pass
    # endregion

    # region Test Cases
    def test_to_stim_operation(self):
        """Tests construction of stim circuit from declarative circuit."""
        stim_circuit: stim.Circuit = to_stim(self.circuit_with_detectors)
        self.assertIsInstance(
            stim_circuit,
            stim.Circuit,
        )

    def test_apply_noise_operation(self):
        """Tests application of noise operations from stim circuit."""
        stim_circuit: stim.Circuit = to_stim(self.circuit_with_detectors)
        noisy_stim_circuit: stim.Circuit = apply_noise(
            circuit=stim_circuit,
            qubit_index_map=dict()  # All qubits are treated with default noise model/parameters
        )
        self.assertIsInstance(
            noisy_stim_circuit,
            stim.Circuit,
        )
        self.assertGreaterEqual(
            len(noisy_stim_circuit.flattened()),
            len(stim_circuit.flattened()),
            msg="Expects noise application to be an additive process"
        )
        # Note: requires flatten to implement coordinate shifts
        self.assertEqual(
            noisy_stim_circuit.without_noise(),
            stim_circuit.flattened(),
            msg="Expects (flattened) circuit to be equal to noiseless noisy-circuit."
        )
    # endregion

    # region Teardown
    @classmethod
    def tearDownClass(cls) -> None:
        """Closes any left over processes after testing"""
        pass
    # endregion
