# -------------------------------------------
# Module describing interface for stabilizer (error detection/correction) indexing.
# -------------------------------------------
from abc import abstractmethod, ABCMeta
import numpy as np
from numpy.typing import NDArray
from qce_utils.custom_exceptions import InterfaceMethodException
from qce_utils.control_interfaces.circuit_definitions.structure.acquisition_indexing.intrf_index_kernel import IIndexingKernel
from qce_utils.control_interfaces.intrf_channel_identifier import IQubitID
from qce_utils.qed_error_correction.state_classification.intrf_state_classification import StateKey


class IStabilizerIndexingKernel(IIndexingKernel, metaclass=ABCMeta):
    """
    Interface class, describing qubit acquisition indexing.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def kernel_cycle_length(self) -> int:
        """:return: Integer length of indexing kernel cycle."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def experiment_repetitions(self) -> int:
        """Number of repetitions for this experiment."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_heralded_cycle_acquisition_indices(self, qubit_id: IQubitID, cycle_stabilizer_count: int) -> NDArray[np.int_]:
        """
        :param qubit_id: Identifier to which these acquisition indices correspond to.
        :param cycle_stabilizer_count: Identifies the indices to only include cycles with this number of stabilizers.
        :return: Tensor of indices pointing at all heralded acquisition before stabilizer cycles.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_stabilizer_acquisition_indices(self, qubit_id: IQubitID, cycle_stabilizer_count: int) -> NDArray[np.int_]:
        """
        :param qubit_id: Identifier to which these acquisition indices correspond to.
        :param cycle_stabilizer_count: Identifies the indices to only include cycles with this number of stabilizers.
        :return: Tensor of indices pointing at all stabilizer acquisition within stabilizer cycles.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_projected_cycle_acquisition_indices(self, qubit_id: IQubitID, cycle_stabilizer_count: int) -> NDArray[np.int_]:
        """
        :param qubit_id: Identifier to which these acquisition indices correspond to.
        :param cycle_stabilizer_count: Identifies the indices to only include cycles with this number of stabilizers.
        :return: Tensor of indices pointing at all projection acquisition after stabilizer cycles.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_heralded_calibration_acquisition_indices(self, qubit_id: IQubitID, state: StateKey) -> NDArray[np.int_]:
        """
        :param qubit_id: Identifier to which these acquisition indices correspond to.
        :param state: Identifier for state specific selectivity.
        :return: Tensor of indices pointing at all heralded acquisition before calibration points.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_projected_calibration_acquisition_indices(self, qubit_id: IQubitID, state: StateKey) -> NDArray[np.int_]:
        """
        :param qubit_id: Identifier to which these acquisition indices correspond to.
        :param state: Identifier for state specific selectivity.
        :return: Tensor of indices pointing at all projection acquisition within calibration points.
        """
        raise InterfaceMethodException
    # endregion
