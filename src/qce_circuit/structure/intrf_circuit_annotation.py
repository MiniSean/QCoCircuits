# -------------------------------------------
# Module describing interface for circuit annotations.
# -------------------------------------------
from dataclasses import dataclass
from typing import List, Dict, Optional
from qce_circuit.structure.intrf_circuit_operation import ICircuitOperation


@dataclass(frozen=True)
class CircuitAnnotation:
    """
    Data class, containing operations to bound and text to display for cosmetic annotation.
    """
    operations: List[ICircuitOperation]
    text_string: str
    text_vertical_offset: float = 0.0

    def copy(self, relation_transfer_lookup: Optional[Dict[ICircuitOperation, ICircuitOperation]] = None) -> 'CircuitAnnotation':
        """
        :param relation_transfer_lookup: Lookup table used to transfer relations and operations.
        :return: Copy of self with updated operations.
        """
        if relation_transfer_lookup is None:
            relation_transfer_lookup = {}
        
        copied_operations = [
            relation_transfer_lookup.get(op, op)
            for op in self.operations
        ]
        
        return CircuitAnnotation(
            operations=copied_operations,
            text_string=self.text_string,
            text_vertical_offset=self.text_vertical_offset,
        )
