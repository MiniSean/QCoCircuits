# -------------------------------------------
# Module containing Stim operation factories for basic operations.
# -------------------------------------------
import stim
from qce_circuit.addon_stim.intrf_stim_factory import (
    IStimOperationFactory,
)
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


class TickOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on name description.
    """

    # region Interface Methods
    def construct(self, operation: ICircuitOperation) -> stim.CircuitInstruction:
        """:return: Stim operation based on operation type."""
        return stim.CircuitInstruction(name='TICK', targets=[], gate_args=[])
    # endregion
