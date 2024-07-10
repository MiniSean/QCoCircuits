# -------------------------------------------
# Module containing circuit components for constructing state-calibration circuit.
# -------------------------------------------
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum, unique, auto
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.connectivity.intrf_channel_identifier import IQubitID
from qce_circuit.structure.acquisition_indexing.intrf_stabilizer_index_kernel import StateKey
from qce_circuit.language.declarative_circuit import DeclarativeCircuit
from qce_circuit.structure.intrf_circuit_operation import (
    RelationType,
    RelationLink,
)
from qce_circuit.structure.registry_acquisition import (
    AcquisitionRegistry,
    RegistryAcquisitionStrategy,
)
from qce_circuit.structure.circuit_operations import (
    Reset,
    Rx180,
    Rx180ef,
    DispersiveMeasure,
)


@unique
class CalibrateType(Enum):
    QUBIT = auto()
    QUTRIT = auto()
    QUQUAD = auto()


class ICalibrationDescription(ABC):
    """
    Interface class, describes methods and properties for state-calibration circuit construction.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in connectivity."""
        raise InterfaceMethodException

    @property
    def qubit_indices(self) -> List[int]:
        """:return: (All) qubit-indices."""
        return [self.map_qubit_id_to_circuit_index(qubit_id) for qubit_id in self.qubit_ids]

    @property
    def calibration_states(self) -> List[StateKey]:
        """:return: Array-like of calibration states."""
        return [_state for _state in StateKey if self.includes_state_calibration(_state)]
    # endregion

    # region Interface Methods
    @abstractmethod
    def map_qubit_id_to_circuit_index(self, qubit_id: IQubitID) -> int:
        """
        :param qubit_id: Identifier that is mapped to circuit channel index.
        :return: Circuit channel index corresponding to qubit-ID.
        """
        raise InterfaceMethodException

    @abstractmethod
    def includes_state_calibration(self, state: StateKey) -> bool:
        """
        :param state: (Qubit) State enumerator.
        :return: Boolean whether state-key is included in the calibration circuit.
        """
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=True)
class CalibrationDescription(ICalibrationDescription):
    """
    Data class, describing properties, required for calibration.
    """
    _qubit_ids: List[IQubitID]
    _qubit_index_map: Dict[IQubitID, int]
    """Mapping from Qubit-ID to circuit channel index."""
    _type: CalibrateType = field(default=CalibrateType.QUBIT)

    # region Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in connectivity."""
        return self._qubit_ids
    # endregion

    # region Interface Methods
    def map_qubit_id_to_circuit_index(self, qubit_id: IQubitID) -> int:
        """
        :param qubit_id: Identifier that is mapped to circuit channel index.
        :return: Circuit channel index corresponding to qubit-ID.
        """
        return self._qubit_index_map[qubit_id]

    def includes_state_calibration(self, state: StateKey) -> bool:
        """
        :param state: (Qubit) State enumerator.
        :return: Boolean whether state-key is included in the calibration circuit.
        """
        if self._type == CalibrateType.QUBIT:
            return state in [StateKey.STATE_0, StateKey.STATE_1]
        if self._type == CalibrateType.QUTRIT:
            return state in [StateKey.STATE_0, StateKey.STATE_1, StateKey.STATE_2]
        return False
    # endregion


def get_circuit_calibrate_with_heralded(qubit_indices: List[int], state: StateKey, registry: AcquisitionRegistry) -> DeclarativeCircuit:
    """
    Constructs declarative circuit containing sequential Heralded initialization, state-preparation and readout.
    :param qubit_indices: Array-like of which qubits to calibrate.
    :param state: Enumerator which state requires calibration.
    :param registry: Measurement acquisition registry.
    :return: Declarative circuit containing Heralded initialization, state-preparation and readout.
    """
    result: DeclarativeCircuit = DeclarativeCircuit()
    for qubit_index in qubit_indices:
        result.add(Reset(qubit_index))
    for qubit_index in qubit_indices:
        result.add(DispersiveMeasure(
            qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='heralded',
        ))
    relation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
    for qubit_index in qubit_indices:
        if state == StateKey.STATE_0:
            continue
        if state == StateKey.STATE_1:
            result.add(Rx180(
                qubit_index,
                relation=relation,
            ))
            continue
        if state == StateKey.STATE_2:
            result.add(Rx180(
                qubit_index,
                relation=relation,
            ))
            result.add(Rx180ef(
                qubit_index,
            ))
            continue

    relation = RelationLink(result.get_last_entry(), RelationType.FOLLOWED_BY)
    for qubit_index in qubit_indices:
        result.add(DispersiveMeasure(
            qubit_index,
            acquisition_strategy=RegistryAcquisitionStrategy(registry),
            acquisition_tag='final',
            relation=relation,
        ))
    return result
