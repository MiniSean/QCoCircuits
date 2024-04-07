# -------------------------------------------
# Module containing functionality for constructing multiple draw components from multiple operation class types.
# Mainly intended to deal with (two-qubit gate) overlapping draw components.
# -------------------------------------------
from typing import List
from qce_circuit import CPhase
from qce_circuit.visualization.visualize_circuit.draw_components.factory_draw_components import TwoQubitBlockFactory
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_circuit.intrf_factory_draw_components import (
    IOperationBulkDrawComponentFactory,
    ITransformConstructor,
)


class MultiTwoQubitBlockFactory(IOperationBulkDrawComponentFactory):

    # region Interface Methods
    def construct(self, operations: List[CPhase], transform_constructor: ITransformConstructor) -> List[IDrawComponent]:
        """:return: Draw components based on array-like of operations."""
        individual_factory: TwoQubitBlockFactory = TwoQubitBlockFactory()
        result: List[IDrawComponent] = []

        for operation in operations:
            result.append(individual_factory.construct(operation=operation, transform_constructor=transform_constructor))

        return result
    # endregion
