# -------------------------------------------
# Module describing the additional stim-specialized operations.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
import stim
from qce_circuit.structure.intrf_circuit_operation import (
    ICircuitOperation,
    ChannelIdentifier,
    QubitChannel,
)
from qce_circuit.structure.circuit_operations import (
    Barrier,
    SingleQubitOperation
)
from qce_circuit.structure.registry_duration import (
    IDurationStrategy,
    FixedDurationStrategy,
)


@dataclass(frozen=False)
class CoordinateShiftOperation(Barrier, ICircuitOperation):
    """
    Basic channel operation covers all qubit channels.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=FixedDurationStrategy(duration=0.0))
    time_shift: int = field(init=True, default=0)
    space_shift: int = field(init=True, default=0)

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'CoordinateShiftOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return CoordinateShiftOperation(
            qubit_indices=self.qubit_indices,
            time_shift=self.time_shift,
            space_shift=self.space_shift,
        )
    # endregion

    # region Class Methods
    def __hash__(self):
        """Overwrites @dataclass behaviour. Circuit operation requires hash based on instance identity."""
        return id(self)
    # endregion


@dataclass(frozen=False, unsafe_hash=True)
class DetectorOperation(SingleQubitOperation, ICircuitOperation):
    """
    Basic channel operation covers all qubit channels.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=FixedDurationStrategy(duration=0.0))
    last_acquisition_index: Optional[int] = field(init=True, default=None)
    main_target: Optional[int] = field(init=True, default=None)
    secondary_target: Optional[int] = field(init=True, default=None)
    reference_offset: Optional[int] = field(init=True, default=None)
    secondary_offset: Optional[int] = field(init=True, default=None)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.ALL),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'DetectorOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return DetectorOperation(
            qubit_index=self.qubit_index,
            last_acquisition_index=self.last_acquisition_index,
            main_target=self.main_target,
            secondary_target=self.secondary_target,
            reference_offset=self.reference_offset,
            secondary_offset=self.secondary_offset,
        )
    # endregion

    def get_stim_arguments(self) -> Optional[Any]:
        arg_index: int = 0
        # Main target
        if self.main_target is not None and self.secondary_target is None and self.reference_offset is None:
            main_target: int = self.main_target - (self.last_acquisition_index + 1)
            return dict(targets=[stim.target_rec(main_target)], arg=(self.qubit_index, arg_index))
        # Main target and reference target
        if self.main_target is not None and self.secondary_target is None and self.reference_offset is not None:
            main_target: int = self.main_target - (self.last_acquisition_index + 1)
            ref_target: int = main_target - self.reference_offset
            return dict(targets=[stim.target_rec(main_target), stim.target_rec(ref_target)], arg=(self.qubit_index, arg_index))
        # Main target, secondary target and reference target
        if self.main_target is not None and self.secondary_target is not None and self.reference_offset is not None and self.secondary_offset is None:
            main_target: int = self.main_target - (self.last_acquisition_index + 1)
            secondary_target: int = self.secondary_target - (self.last_acquisition_index + 1)
            ref_target: int = -self.reference_offset
            return dict(targets=[stim.target_rec(main_target), stim.target_rec(secondary_target), stim.target_rec(ref_target)], arg=(self.qubit_index, arg_index))
        # Main target, secondary target and reference target
        if self.main_target is not None and self.secondary_target is not None and self.reference_offset is not None and self.secondary_offset is not None:
            main_target: int = self.main_target - (self.last_acquisition_index + 1)
            secondary_target: int = self.secondary_target - (self.last_acquisition_index + 1)
            ref_target: int = -self.reference_offset
            second_ref_target: int = ref_target - self.secondary_offset
            return dict(targets=[stim.target_rec(main_target), stim.target_rec(secondary_target), stim.target_rec(ref_target), stim.target_rec(second_ref_target)], arg=(self.qubit_index, arg_index))
        return None


@dataclass(frozen=False, unsafe_hash=True)
class LogicalObservableOperation(SingleQubitOperation, ICircuitOperation):
    """
    Basic channel operation covers all qubit channels.
    """
    duration_strategy: IDurationStrategy = field(init=False, default=FixedDurationStrategy(duration=0.0))
    last_acquisition_index: Optional[int] = field(init=True, default=None)
    main_target: Optional[int] = field(init=True, default=None)

    # region Interface Properties
    @property
    def channel_identifiers(self) -> List[ChannelIdentifier]:
        """:return: Array-like of channel identifiers to which this operation applies to."""
        return [
            ChannelIdentifier(_id=self.qubit_index, _channel=QubitChannel.ALL),
        ]
    # endregion

    # region Interface Methods
    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'LogicalObservableOperation':
        """
        Creates a copy from self. Excluding any relation details.
        :param relation_transfer_lookup: Lookup table used to transfer relation link.
        :return: Copy of self with updated relation link.
        """
        return LogicalObservableOperation(
            qubit_index=self.qubit_index,
            last_acquisition_index=self.last_acquisition_index,
            main_target=self.main_target,
        )
    # endregion

    def get_stim_arguments(self) -> Optional[Any]:
        arg_index: int = 0
        # Main target
        if self.last_acquisition_index is not None and self.main_target is not None:
            main_target: int = self.main_target - (self.last_acquisition_index + 1)
            return dict(targets=[stim.target_rec(main_target)], arg=(arg_index))
        return None
