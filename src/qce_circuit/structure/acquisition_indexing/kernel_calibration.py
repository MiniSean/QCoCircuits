# -------------------------------------------
# Module describing implementation of indexing kernel.
# Specializes in calibration point kernel implementations.
# -------------------------------------------
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import List
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.structure.acquisition_indexing.intrf_index_kernel import IIndexingKernel
from qce_circuit.structure.acquisition_indexing.intrf_index_strategy import IIndexStrategy
from qce_circuit.structure.acquisition_indexing.intrf_stabilizer_index_kernel import StateKey
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID


@dataclass(frozen=True)
class QutritCalibrationIndexKernel(IIndexingKernel):
    """Data class, containing information about qutrit calibration-points (measurement acquisition) indexing."""
    heralded_initialization: bool
    """Boolean whether heralded initialization is performed at the start of the kernel."""
    index_offset_strategy: IIndexStrategy = field(repr=False)
    """Determines reference index by which internal indices are offset."""
    involved_qubit_ids: List[IQubitID] = field(repr=False)

    # region Interface Properties
    @property
    def start_index(self) -> int:
        """:return: Starting index."""
        return self.index_offset_strategy.get_index(self)  # Starts counting after previous index

    @property
    def _exclusive_start_index(self) -> int:
        """:return: Exclusive start index, used for counting Inclusive indices."""
        return self.start_index - 1  # -1 used to make sure all other indices are INCLUSIVE.

    @property
    def index_delta_heralded_initialization(self) -> int:
        """:return: Number of measurements performed during heralded initialization."""
        return 1 if self.heralded_initialization else 0

    @property
    def index_delta_state_0(self) -> int:
        """:return: Number of measurements performed during State-0 measurement."""
        return 1

    @property
    def index_delta_state_1(self) -> int:
        """:return: Number of measurements performed during State-1 measurement."""
        return 1

    @property
    def index_delta_state_2(self) -> int:
        """:return: Number of measurements performed during State-2 measurement."""
        return 1

    @property
    def stop_index(self) -> int:
        """:return: End index."""
        total_index_delta: int = 3 * self.index_delta_heralded_initialization + self.index_delta_state_0 + self.index_delta_state_1 + self.index_delta_state_2
        return self._exclusive_start_index + total_index_delta
    # endregion

    # region Interface Methods
    def contains(self, element: IQubitID) -> List[int]:
        """:return: Array-like of measurement indices corresponding to element within this indexing kernel."""
        heralded_0_measurement_indices: List[int] = self.get_heralded_state_0_measurement_index(element)
        heralded_1_measurement_indices: List[int] = self.get_heralded_state_1_measurement_index(element)
        heralded_2_measurement_indices: List[int] = self.get_heralded_state_2_measurement_index(element)
        state_0_measurement_indices: List[int] = self.get_state_0_measurement_index(element)
        state_1_measurement_indices: List[int] = self.get_state_1_measurement_index(element)
        state_2_measurement_indices: List[int] = self.get_state_2_measurement_index(element)
        return sorted(heralded_0_measurement_indices + heralded_1_measurement_indices + heralded_2_measurement_indices + state_0_measurement_indices + state_1_measurement_indices + state_2_measurement_indices)

    def get_heralded_state_0_measurement_index(self, element: IQubitID) -> List[int]:
        """
        If element not part of this kernel, return None.
        If no heralded initialization is performed, return None.
        :return: (Optional) index corresponding to heralded measurement.
        """
        if element not in self.involved_qubit_ids:
            return []
        if not self.heralded_initialization:
            return []
        return [self._exclusive_start_index + self.index_delta_heralded_initialization]

    def get_heralded_state_1_measurement_index(self, element: IQubitID) -> List[int]:
        """
        If element not part of this kernel, return None.
        If no heralded initialization is performed, return None.
        :return: (Optional) index corresponding to heralded measurement.
        """
        if element not in self.involved_qubit_ids:
            return []
        if not self.heralded_initialization:
            return []
        return [self._exclusive_start_index + 2 * self.index_delta_heralded_initialization + self.index_delta_state_0]

    def get_heralded_state_2_measurement_index(self, element: IQubitID) -> List[int]:
        """
        If element not part of this kernel, return None.
        If no heralded initialization is performed, return None.
        :return: (Optional) index corresponding to heralded measurement.
        """
        if element not in self.involved_qubit_ids:
            return []
        if not self.heralded_initialization:
            return []
        return [self._exclusive_start_index + 3 * self.index_delta_heralded_initialization + self.index_delta_state_0 + self.index_delta_state_1]

    def get_state_0_measurement_index(self, element: IQubitID) -> List[int]:
        """
        If element not part of this kernel, return None.
        :return: (Optional) index corresponding to State-0 measurement.
        """
        if element not in self.involved_qubit_ids:
            return []
        return [self._exclusive_start_index + self.index_delta_heralded_initialization + self.index_delta_state_0]

    def get_state_1_measurement_index(self, element: IQubitID) -> List[int]:
        """
        If element not part of this kernel, return None.
        :return: (Optional) index corresponding to State-1 measurement.
        """
        if element not in self.involved_qubit_ids:
            return []
        return [self._exclusive_start_index + 2 * self.index_delta_heralded_initialization + self.index_delta_state_0 + self.index_delta_state_1]

    def get_state_2_measurement_index(self, element: IQubitID) -> List[int]:
        """
        If element not part of this kernel, return None.
        :return: (Optional) index corresponding to State-2 measurement.
        """
        if element not in self.involved_qubit_ids:
            return []
        return [self._exclusive_start_index + 3 * self.index_delta_heralded_initialization + self.index_delta_state_0 + self.index_delta_state_1 + self.index_delta_state_2]
    # endregion


class IGeneralCalibrationIndexKernel(IIndexingKernel, metaclass=ABCMeta):
    """
    Interface class, describing index kernel for general calibration acquisition.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def heralded_calibration(self) -> bool:
        """:return: Whether calibration contains heralded initialization."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def contained_states(self) -> List[StateKey]:
        """:return: Array-like of contained state keys."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_heralded_state_measurement_index(self, state: StateKey) -> List[int]:
        """
        If no heralded initialization is performed, return empty list.
        If state is not included, return empty list.
        :return: (Optional) index corresponding to heralded measurement.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_calibration_state_measurement_index(self, state: StateKey) -> List[int]:
        """
        If state is not included, return empty list.
        :return: (Optional) index corresponding to calibration measurement.
        """
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class GeneralCalibrationIndexKernel(IGeneralCalibrationIndexKernel):
    """
    Data class, containing information about qubit/qutrit calibration-points (measurement acquisition) indexing.
    """
    index_offset_strategy: IIndexStrategy = field(repr=False)
    """Determines reference index by which internal indices are offset."""
    heralded_initialization: bool = field(default=False)
    """Boolean whether heralded initialization is performed at the start of the kernel."""
    f_state: bool = field(default=False)
    """Whether to include second-excited (f) state resulting in qutrit calibration. Default False (qubit)."""
    repetitions: int = field(default=1)
    """Index kernel repetition."""

    # region Interface Properties
    @property
    def start_index(self) -> int:
        """:return: Starting index."""
        return self.index_offset_strategy.get_index(self)  # Starts counting after previous index

    @property
    def _exclusive_start_index(self) -> int:
        """:return: Exclusive start index, used for counting Inclusive indices."""
        return self.start_index - 1  # -1 used to make sure all other indices are INCLUSIVE.

    @property
    def stop_index(self) -> int:
        """:return: End index."""
        return self._exclusive_start_index + self.cycle_length * self.repetitions

    @property
    def heralded_calibration(self) -> bool:
        """:return: Whether calibration contains heralded initialization."""
        return self.heralded_initialization

    @property
    def contained_states(self) -> List[StateKey]:
        """:return: Array-like of contained state keys."""
        if self.f_state:
            return [
                StateKey.STATE_0,
                StateKey.STATE_1,
                StateKey.STATE_2,
            ]
        return [
            StateKey.STATE_0,
            StateKey.STATE_1
        ]
    # endregion

    # region Class Properties
    @property
    def cycle_length(self) -> int:
        """:return: Length of single cycle."""
        return 2**self.heralded_initialization * (2 + self.f_state)
    # endregion

    # region Interface Methods
    def contains(self, element: IQubitID) -> List[int]:
        """:return: Array-like of measurement indices corresponding to element within this indexing kernel."""
        return list(range(self.start_index, self.stop_index + 1))

    def get_heralded_state_measurement_index(self, state: StateKey) -> List[int]:
        """
        If no heralded initialization is performed, return empty list.
        If state is not included, return empty list.
        :return: (Optional) index corresponding to heralded measurement.
        """
        if not self.heralded_initialization:
            return []
        if state not in self.contained_states:
            return []

        all_indices: List[int] = list(range(self.start_index, self.stop_index + 1))
        cycle_length: int = self.cycle_length
        if state == StateKey.STATE_0:
            return all_indices[0::cycle_length]
        if state == StateKey.STATE_1:
            return all_indices[2::cycle_length]
        if state == StateKey.STATE_2:
            return all_indices[4::cycle_length]
        return []

    def get_calibration_state_measurement_index(self, state: StateKey) -> List[int]:
        """
        If state is not included, return empty list.
        :return: (Optional) index corresponding to calibration measurement.
        """
        if state not in self.contained_states:
            return []

        all_indices: List[int] = list(range(self.start_index, self.stop_index + 1))
        cycle_length: int = self.cycle_length
        if state == StateKey.STATE_0:
            return all_indices[1::cycle_length]
        if state == StateKey.STATE_1:
            return all_indices[3::cycle_length]
        if state == StateKey.STATE_2:
            return all_indices[5::cycle_length]
        return []
    # endregion
