# -------------------------------------------
# Module describing interface for circuit annotations.
# -------------------------------------------
from dataclasses import dataclass
from typing import List
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


@dataclass(frozen=True)
class CircuitAnnotation:
    """
    Data class, containing operations to bound and text to display for cosmetic annotation.
    """
    operations: List[ICircuitOperation]
    text_string: str
