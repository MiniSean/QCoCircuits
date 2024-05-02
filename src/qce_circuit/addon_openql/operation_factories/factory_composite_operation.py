# -------------------------------------------
# Module containing OpenQL operation factories for composite operations.
# -------------------------------------------
from typing import List
import openql as ql
from qce_circuit.addon_openql.intrf_openql_factory import IOpenQLOperationFactory
from qce_circuit.addon_stim.operation_factories.factory_basic_operations import get_qubit_index
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation
from qce_circuit.structure.circuit_operations import CPhase
from qce_circuit.addon_openql.operation_factories.factory_barrier_operations import BarrierOperationsFactory


class CompositeCPhaseOperationsFactory(IOpenQLOperationFactory):
    """
    Behaviour class, describing OpenQL-operation factory based on composite Controlled-Phase operation description.
    """

    # # region Class Constructor
    # def __init__(self, cardinal_direction_getter):
    #     pass
    # # endregion

    # region Interface Methods
    def construct(self, operation: CPhase, kernel: ql.Kernel) -> ql.Kernel:
        """:return: Updated OpenQL Kernel based on operation type."""
        kernel.cz(
            operation.control_qubit_index,
            operation.target_qubit_index,
        )
        # kernel.gate(
        #     'cz',
        #     operation.target_qubit_index,
        # )
        kernel.barrier(
            get_qubit_index(operation),
        )
        kernel.gate(
            'update_ph',
            operation.control_qubit_index,
        )
        kernel.gate(
            'update_ph',
            operation.target_qubit_index,
        )
        return kernel
    # endregion
