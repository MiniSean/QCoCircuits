# -------------------------------------------
# Module containing Stim operation factories for basic operations.
# -------------------------------------------
from typing import List
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.addon_stim.intrf_stim_factory import (
    IStimOperationFactory,
    StimOperationConstructor,
)
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.addon_stim.circuit_operations import (
    CoordinateShiftOperation,
    DetectorOperation,
    LogicalObservableOperation,
)
from qce_circuit.addon_stim.operation_factories.factory_basic_operations import get_qubit_index


class CoordinateShiftOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on specific operation.
    """

    # region Interface Methods
    def construct(self, operation: CoordinateShiftOperation) -> StimOperationConstructor:
        """:return: Stim operation based on operation type."""
        return StimOperationConstructor(
            _kwargs=dict(
                name='SHIFT_COORDS',
                targets=[],
                arg=(
                    float(operation.space_shift),
                    float(operation.time_shift)
                ),
            )
        )
    # endregion


class DetectorOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on specific operation.
    """

    # region Interface Methods
    def construct(self, operation: DetectorOperation) -> StimOperationConstructor:
        """:return: Stim operation based on operation type."""
        if operation.get_stim_arguments() is None:
            print('Detector kwargs are None, expected to fail.')
        return StimOperationConstructor(
            _args=(
                'DETECTOR',
            ),
            _kwargs=operation.get_stim_arguments(),
        )
    # endregion


class LogicalObservableOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on specific operation.
    """

    # region Interface Methods
    def construct(self, operation: LogicalObservableOperation) -> StimOperationConstructor:
        """:return: Stim operation based on operation type."""
        # Guard clause, if operation not p
        return StimOperationConstructor(
            _args=(
                'OBSERVABLE_INCLUDE',
            ),
            _kwargs=operation.get_stim_arguments(),
        )
    # endregion
