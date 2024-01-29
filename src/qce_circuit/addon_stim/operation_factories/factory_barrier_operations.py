# -------------------------------------------
# Module containing Stim operation factories for basic operations.
# -------------------------------------------
from qce_circuit.addon_stim.intrf_stim_factory import (
    IStimOperationFactory,
    StimOperationConstructor,
)
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


class TickOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on name description.
    """

    # region Interface Methods
    def construct(self, operation: ICircuitOperation) -> StimOperationConstructor:
        """:return: Stim operation based on operation type."""
        return StimOperationConstructor(
            _kwargs=dict(
                name='TICK',
            )
        )
    # endregion
