# -------------------------------------------
# Module containing Stim operation factories for basic operations.
# -------------------------------------------
import stim
from qce_circuit.addon_stim.intrf_stim_factory import (
    IStimOperationFactory,
)
from qce_circuit.addon_stim.circuit_operations import (
    CoordinateShiftOperation,
    DetectorOperation,
    LogicalObservableOperation,
)


class CoordinateShiftOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on specific operation.
    """

    # region Interface Methods
    def construct(self, operation: CoordinateShiftOperation) -> stim.CircuitInstruction:
        """:return: Stim operation based on operation type."""
        return operation.to_stim_instruction()
    # endregion


class DetectorOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on specific operation.
    """

    # region Interface Methods
    def construct(self, operation: DetectorOperation) -> stim.CircuitInstruction:
        """:return: Stim operation based on operation type."""
        return operation.to_stim_instruction()
    # endregion


class LogicalObservableOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on specific operation.
    """

    # region Interface Methods
    def construct(self, operation: LogicalObservableOperation) -> stim.CircuitInstruction:
        """:return: Stim operation based on operation type."""
        return operation.to_stim_instruction()
    # endregion
