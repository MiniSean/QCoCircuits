# -------------------------------------------
# Module containing OpenQL operation factories for wait operations.
# -------------------------------------------
import openql as ql
from qce_circuit.addon_openql.intrf_openql_factory import (
    IOpenQLOperationFactory,
)
from qce_circuit.addon_stim.operation_factories.factory_basic_operations import get_qubit_index
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


class WaitOperationsFactory(IOpenQLOperationFactory):
    """
    Behaviour class, describing OpenQL-operation factory based on name description.
    """

    # region Interface Methods
    def construct(self, operation: ICircuitOperation, kernel: ql.Kernel) -> ql.Kernel:
        """:return: Updated OpenQL Kernel based on operation type."""
        kernel.wait(
            qubits=get_qubit_index(operation),
            duration=operation.duration,
        )
        return kernel
    # endregion
