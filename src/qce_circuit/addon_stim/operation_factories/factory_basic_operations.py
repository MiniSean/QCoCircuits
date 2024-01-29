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


def get_qubit_index(operation: ICircuitOperation) -> List[int]:
    channels = operation.channel_identifiers
    qubit_indices: List[int] = unique_in_order([channel.id for channel in channels])
    return qubit_indices


class NameBasedOperationsFactory(IStimOperationFactory):
    """
    Behaviour class, describing Stim-operation factory based on name description.
    """

    # region Class Constructor
    def __init__(self, operation_name: str):
        self._operation_name: str = operation_name
    # endregion

    # region Interface Methods
    def construct(self, operation: ICircuitOperation) -> StimOperationConstructor:
        """:return: Stim operation based on operation type."""
        return StimOperationConstructor(
            _kwargs=dict(
                name=self._operation_name,
                targets=get_qubit_index(operation),
            )
        )
    # endregion
