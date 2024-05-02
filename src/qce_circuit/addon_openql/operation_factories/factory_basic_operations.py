# -------------------------------------------
# Module containing OpenQL operation factories for basic operations.
# -------------------------------------------
from typing import List
import openql as ql
from qce_circuit.addon_openql.intrf_openql_factory import (
    IOpenQLOperationFactory,
)
from qce_circuit.addon_stim.operation_factories.factory_basic_operations import get_qubit_index
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


class NameBasedOperationsFactory(IOpenQLOperationFactory):
    """
    Behaviour class, describing OpenQL-operation factory based on name description.
    """

    # region Class Constructor
    def __init__(self, operation_name: str):
        self._operation_name: str = operation_name
    # endregion

    # region Interface Methods
    def construct(self, operation: ICircuitOperation, kernel: ql.Kernel) -> ql.Kernel:
        """:return: Updated OpenQL Kernel based on operation type."""
        kernel.gate(
            self._operation_name,
            get_qubit_index(operation),
        )
        return kernel
    # endregion
