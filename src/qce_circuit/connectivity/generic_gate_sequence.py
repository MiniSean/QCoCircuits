# -------------------------------------------
# Module containing interface and implementation of generic (Surface17) gate sequences.
# -------------------------------------------
import warnings
import math
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Union, Optional, Dict
from qce_circuit.utilities.custom_exceptions import (
    ElementNotIncludedException,
    InterfaceMethodException,
    LayoutTranslationException,
)
from qce_circuit.utilities.array_manipulation import unique_in_order
from qce_circuit.connectivity.intrf_channel_identifier import (
    IQubitID,
    IEdgeID,
    IFeedlineID,
    EdgeIDObj,
)
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    IParityGroup,
    FrequencyGroupIdentifier,
    StabilizerType,
)
from qce_circuit.connectivity.intrf_connectivity_gate_sequence import (
    IGateSequenceLayer,
    GateSequenceLayer,
    Operation,
    OperationType,
)
from qce_circuit.connectivity.connectivity_surface_code import (
    Surface17Layer,
    ParityGroup,
)
from qce_circuit.utilities.geometric_definitions.vector_elements import Vec2D


class ILogicalObservable(ABC):
    """
    Interface class, describing logical observable.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def observable_basis(self) -> StabilizerType:
        """:return: (StabilizerType) basis of logical observable."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def involved_data_qubit_ids(self) -> List[IQubitID]:
        """:return: Array-like of data-qubit ID's involved in observable."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def concordant_stabilizer_qubit_ids(self) -> List[IQubitID]:
        """
        :return: Array-like of ancilla-qubit ID's that describe the stabilizers which are concordant with the observable.
        """
        raise InterfaceMethodException

    @property
    @abstractmethod
    def default_projection_basis(self) -> StabilizerType:
        """:return: Default projection type"""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def contains(self, element: IQubitID) -> bool:
        """:return: True if element is contained in logical observable, else False."""
        raise InterfaceMethodException

    @abstractmethod
    def get_projection_basis(self, qubit_id: IQubitID) -> StabilizerType:
        """:return: Projection basis per qubit in observable."""
        raise InterfaceMethodException
    # endregion


class IGenericSurfaceCodeLayer(ISurfaceCodeLayer, IGateSequenceLayer, metaclass=ABCMeta):
    """
    Interface class, combining ISurfaceCodeLayer and IGateSequenceLayer.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def background_surface_layer(self) -> ISurfaceCodeLayer:
        """:return: The underlying master surface code layer."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_gate_sequence_indices(self, parity_group: IParityGroup) -> List[int]:
        """
        :return: Array-like of gate-sequence indices corresponding to parity-group edge-ID's.
        Returns an empty list if parity-group is not present.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_logical_observable(self, basis: StabilizerType) -> ILogicalObservable:
        """:return: Logical observable corresponding to basis."""
        raise InterfaceMethodException
    # endregion


class LogicalObservable(ILogicalObservable):
    """
    Data class, implementing ILogicalObservable interface.
    """

    # region Interface Properties
    @property
    def observable_basis(self) -> StabilizerType:
        """:return: (StabilizerType) basis of logical observable."""
        return self._observable_basis

    @property
    def involved_data_qubit_ids(self) -> List[IQubitID]:
        """:return: Array-like of data-qubit ID's involved in observable."""
        return self._supporting_logical

    @property
    def concordant_stabilizer_qubit_ids(self) -> List[IQubitID]:
        """
        :return: Array-like of ancilla-qubit ID's that describe the stabilizers which are concordant with the observable.
        """
        return self._supporting_stabilizers

    @property
    def default_projection_basis(self) -> StabilizerType:
        """:return: Default projection type"""
        return self._default_projections
    # endregion

    # region Class Constructor
    def __init__(
            self,
            observable_basis: StabilizerType,
            data_qubit_projections: Dict[IQubitID, StabilizerType],
            supporting_stabilizers: List[IQubitID],
            supporting_logical: Optional[List[IQubitID]] = None,  # Defaults to data_qubit_projections
            default_projections: StabilizerType = StabilizerType.STABILIZER_Z,
    ):
        self._observable_basis: StabilizerType = observable_basis
        self._data_qubit_projections: Dict[IQubitID, StabilizerType] = data_qubit_projections
        self._supporting_stabilizers: List[IQubitID] = supporting_stabilizers
        self._supporting_logical: List[IQubitID] = supporting_logical if supporting_logical is not None else list(data_qubit_projections.keys())
        self._default_projections: StabilizerType = default_projections
    # endregion

    # region Interface Methods
    def contains(self, element: IQubitID) -> bool:
        """:return: True if element is contained in logical observable, else False."""
        return element in self._data_qubit_projections

    def get_projection_basis(self, qubit_id: IQubitID) -> StabilizerType:
        """:return: Projection basis per qubit in observable."""
        if qubit_id not in self._data_qubit_projections:
            # raise ObservableElementNotIncludedException(f"{qubit_id} is not in logical observable. Use one of self.involved_data_qubit_ids.")
            return self._default_projections
        return self._data_qubit_projections[qubit_id]
    # endregion


class GenericSurfaceCode(IGenericSurfaceCodeLayer):

    # region IGenericSurfaceCodeLayer Properties
    @property
    def background_surface_layer(self) -> ISurfaceCodeLayer:
        """:return: The underlying master surface code layer."""
        return self._surface_code_layer
    # endregion

    # region IGateSequenceLayer Interface Properties
    @property
    def gate_sequence_count(self) -> int:
        """:return: Number of gate-sequences in layer."""
        return len(self._gate_sequences)

    @property
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of gate sequences."""
        return self._gate_sequences

    @property
    def involved_qubit_ids(self) -> List[IQubitID]:
        """:return: (Only) involved qubit-ID's in gate sequence."""
        gate_sequence_layers: List[GateSequenceLayer] = [self.get_gate_sequence_at_index(layer_index) for layer_index in range(self.gate_sequence_count)]
        return unique_in_order([qubit_id for gate_sequence_layer in gate_sequence_layers for qubit_id in gate_sequence_layer.qubit_ids])

    @property
    def involved_edge_ids(self) -> List[IEdgeID]:
        """:return: (Only) involved edge-ID's in gate sequence."""
        gate_sequence_layers: List[GateSequenceLayer] = [self.get_gate_sequence_at_index(layer_index) for layer_index in range(self.gate_sequence_count)]
        return unique_in_order([edge_ids for gate_sequence_layer in gate_sequence_layers for edge_ids in gate_sequence_layer.edge_ids])
    # endregion

    # region ISurfaceCodeLayer Interface Properties
    @property
    def parity_group_x(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of X-stabilizers."""
        return self._parity_group_x

    @property
    def parity_group_z(self) -> List[IParityGroup]:
        """:return: (All) parity groups part of Z-stabilizers."""
        return self._parity_group_z

    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: (Data) qubit-ID's in device layer."""
        return unique_in_order([data_id for parity_group in self.parity_group_x + self.parity_group_z for data_id in parity_group.data_ids])

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        return unique_in_order([parity_group.ancilla_id for parity_group in self.parity_group_x + self.parity_group_z])
    # endregion

    # region IDeviceLayer Interface Properties
    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's in device layer."""
        return self._surface_code_layer.feedline_ids
    # endregion

    # region IConnectivityLayer Interface Properties
    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        return self._surface_code_layer.qubit_ids

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        return self._surface_code_layer.edge_ids
    # endregion

    # region Class Constructor
    def __init__(self, gate_sequences: List[GateSequenceLayer], parity_group_z: List[IParityGroup], parity_group_x: List[IParityGroup], logical_observables: Optional[List[ILogicalObservable]] = None, surface_code_layer: ISurfaceCodeLayer = Surface17Layer()):
        self._gate_sequences: List[GateSequenceLayer] = gate_sequences
        self._parity_group_z: List[IParityGroup] = parity_group_z
        self._parity_group_x: List[IParityGroup] = parity_group_x
        if logical_observables is None:
            logical_observables = []
        self._logical_observables: Dict[StabilizerType, ILogicalObservable] = {
            logical_observable.observable_basis: logical_observable
            for logical_observable in logical_observables
        }
        self._surface_code_layer: ISurfaceCodeLayer = surface_code_layer
    # endregion

    # region IGenericSurfaceCodeLayer Methods
    def get_gate_sequence_indices(self, parity_group: IParityGroup) -> List[int]:
        """
        :return: Array-like of gate-sequence indices corresponding to parity-group edge-ID's.
        Returns an empty list if parity-group is not present.
        """
        # Guard clause, if parity-group is not present, return empty list
        if parity_group not in self.parity_group_x + self.parity_group_z:
            return []
        edge_ids: List[IEdgeID] = parity_group.edge_ids
        result: List[int] = []
        for gate_sequence_index, gate_sequence in enumerate(self.gate_sequences):
            contains_any_edge: bool = any([edge_id in gate_sequence.edge_ids for edge_id in edge_ids])
            if contains_any_edge:
                result.append(gate_sequence_index)
                continue

        return result

    def get_logical_observable(self, basis: StabilizerType) -> ILogicalObservable:
        """:return: Logical observable corresponding to basis."""
        default_fallback: bool = basis not in self._logical_observables
        if default_fallback:
            warnings.warn(f"Logical observable for basis {basis.name} is not defined in GenericSurfaceCode. Defaulting to {StabilizerType.STABILIZER_Z.name} for all data qubit ID's.")
            return LogicalObservable(
                observable_basis=StabilizerType.STABILIZER_Z,
                data_qubit_projections={
                    data_qubit_id: StabilizerType.STABILIZER_Z
                    for data_qubit_id in self.data_qubit_ids
                },
                supporting_stabilizers=StabilizerType.STABILIZER_Z,
            )
        return self._logical_observables[basis]
    # endregion

    # region IGateSequenceLayer Interface Methods
    def get_gate_sequence_at_index(self, index: int) -> GateSequenceLayer:
        """:return: Gate-sequence object based on round index."""
        gate_sequences: List[GateSequenceLayer] = self._gate_sequences
        try:
            gate_sequence: GateSequenceLayer = gate_sequences[index]
            return gate_sequence
        except IndexError:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for gate-sequence of length: {len(gate_sequences)}.")

    def get_gate_sequence_from_element(self, element: IEdgeID) -> GateSequenceLayer:
        """:return: Gate-sequence layer of which edge element is part of."""
        gate_sequences: List[GateSequenceLayer] = self._gate_sequences
        # Assumes element is part of only a single flux-dance layer
        for gate_sequence in gate_sequences:
            if gate_sequence.contains(element=element):
                return gate_sequence
        raise ElementNotIncludedException(f"Element: {element} is not included in any gate-sequence layer.")
    # endregion

    # region ISurfaceCodeLayer Interface Methods
    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> List[IParityGroup]:
        """:return: Parity group(s) of which element (edge- or qubit-ID) is part of."""
        result: List[IParityGroup] = []
        # Assumes element is part of only a single parity group
        for parity_group in self.parity_group_x + self.parity_group_z:
            if parity_group.contains(element=element):
                result.append(parity_group)
        return result

    def get_frequency_group_identifier(self, element: IQubitID) -> FrequencyGroupIdentifier:
        """:return: Frequency group identifier based on qubit-ID."""
        return self._surface_code_layer.get_frequency_group_identifier(element=element)
    # endregion

    # region IDeviceLayer Interface Methods
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """:return: Qubit-ID's connected to feedline-ID."""
        return self._surface_code_layer.get_connected_qubits(feedline=feedline)

    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """:return: Feedline-ID's connected to qubit-ID."""
        return self._surface_code_layer.get_connected_feedline(qubit=qubit)

    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        return self._surface_code_layer.contains(element=element)
    # endregion

    # region IConnectivityLayer Interface Methods
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        return self._surface_code_layer.get_neighbors(qubit=qubit, order=order)

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        return self._surface_code_layer.get_edges(qubit=qubit)

    def get_qubit_coordinates(self, qubit_id: IQubitID) -> Vec2D:
        """:return: The geometric coordinates for the given qubit ID."""
        return self._surface_code_layer.get_qubit_coordinates(qubit_id)
    # endregion


class TranslatedGenericSurfaceCodeLayer(IGenericSurfaceCodeLayer):
    """
    Decorator class that translates a generic surface code experiment across the quantum plane
    based on a geometric translation from a base_anchor to a target_anchor.
    """

    # region Interface Properties
    @property
    def gate_sequences(self) -> List[GateSequenceLayer]:
        """:return: Array-like of translated gate sequences."""
        return self._translated_gate_sequences

    @property
    def parity_group_x(self) -> List[IParityGroup]:
        """:return: Array-like of translated X-type parity groups."""
        return self._translated_parity_group_x

    @property
    def parity_group_z(self) -> List[IParityGroup]:
        """:return: Array-like of translated Z-type parity groups."""
        return self._translated_parity_group_z

    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: All mapped qubit-ID's in the translated device layer."""
        return self.background_surface_layer.qubit_ids

    @property
    def data_qubit_ids(self) -> List[IQubitID]:
        """:return: Data qubit-ID's in the translated device layer."""
        return self.background_surface_layer.data_qubit_ids

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: Ancilla qubit-ID's in the translated device layer."""
        return self.background_surface_layer.ancilla_qubit_ids

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: All mapped edge-ID's in the translated device layer."""
        return self.background_surface_layer.edge_ids

    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's connected to mapped qubits in the target device layer."""
        return self.background_surface_layer.feedline_ids

    @property
    def gate_sequence_count(self) -> int:
        """:return: Number of gate-sequences in layer."""
        return self._base_layer.gate_sequence_count

    @property
    def involved_qubit_ids(self) -> List[IQubitID]:
        """:return: Only involved qubit-ID's in gate sequence."""
        return [self._translate_qubit(qubit=qubit) for qubit in self._base_layer.involved_qubit_ids]

    @property
    def involved_edge_ids(self) -> List[IEdgeID]:
        """:return: Only involved edge-ID's in gate sequence."""
        return [self._translate_edge(edge=edge) for edge in self._base_layer.involved_edge_ids]

    @property
    def background_surface_layer(self) -> ISurfaceCodeLayer:
        """:return: The underlying master surface code layer."""
        return self._target_layer
    # endregion

    # region Class Constructor
    def __init__(self, base_layer: IGenericSurfaceCodeLayer, target_layer: ISurfaceCodeLayer, base_anchor: IQubitID, target_anchor: IQubitID):
        self._base_layer: IGenericSurfaceCodeLayer = base_layer
        self._target_layer: ISurfaceCodeLayer = target_layer
        
        # Calculate translation vector
        if not hasattr(self._base_layer, 'get_qubit_coordinates'):
            raise LayoutTranslationException("Base layer does not support get_qubit_coordinates.")
        if not hasattr(self._target_layer, 'get_qubit_coordinates'):
            raise LayoutTranslationException("Target layer does not support get_qubit_coordinates.")
            
        base_coordinate: Vec2D = self._base_layer.get_qubit_coordinates(qubit_id=base_anchor)
        target_coordinate: Vec2D = self._target_layer.get_qubit_coordinates(qubit_id=target_anchor)
        translation_vector: Vec2D = target_coordinate - base_coordinate
        
        self._qubit_mapping: Dict[IQubitID, IQubitID] = {}
        for base_qubit in self._base_layer.involved_qubit_ids:
            mapped_coordinate: Vec2D = self._base_layer.get_qubit_coordinates(qubit_id=base_qubit) + translation_vector
            
            # Find matching target qubit
            match_found: bool = False
            for target_qubit in self._target_layer.qubit_ids:
                target_qubit_coordinate: Vec2D = self._target_layer.get_qubit_coordinates(qubit_id=target_qubit)
                if math.isclose(target_qubit_coordinate.x, mapped_coordinate.x, abs_tol=1e-5) and math.isclose(target_qubit_coordinate.y, mapped_coordinate.y, abs_tol=1e-5):
                    self._qubit_mapping[base_qubit] = target_qubit
                    match_found = True
                    break
            if not match_found:
                raise LayoutTranslationException(f"Translation failed: Base qubit {base_qubit.id} mapped to {mapped_coordinate} falls outside target layer bounds.")
                
        # Cache translated sequences and parity groups
        self._translated_gate_sequences: List[GateSequenceLayer] = [self._translate_gate_sequence(sequence=sequence) for sequence in self._base_layer.gate_sequences]
        self._translated_parity_group_x: List[IParityGroup] = [self._translate_parity_group(parity_group=parity_group) for parity_group in self._base_layer.parity_group_x]
        self._translated_parity_group_z: List[IParityGroup] = [self._translate_parity_group(parity_group=parity_group) for parity_group in self._base_layer.parity_group_z]
    # endregion

    # region Class Methods
    def _translate_qubit(self, qubit: IQubitID) -> IQubitID:
        """
        :param qubit: Qubit ID in the base layer.
        :return: Translated qubit ID in the target layer.
        """
        if qubit not in self._qubit_mapping:
            raise LayoutTranslationException(f"Qubit {qubit.id} not found in translation mapping.")
        return self._qubit_mapping[qubit]
        
    def _translate_edge(self, edge: IEdgeID) -> IEdgeID:
        """
        :param edge: Edge ID in the base layer.
        :return: Translated edge ID in the target layer.
        """
        return EdgeIDObj(
            qubit_id0=self._translate_qubit(qubit=edge.qubit_ids[0]),
            qubit_id1=self._translate_qubit(qubit=edge.qubit_ids[1]),
        )
        
    def _translate_operation(self, operation: Operation) -> Operation:
        """
        :param operation: Operation in the base layer.
        :return: Translated operation in the target layer.
        """
        if operation.type == OperationType.IDLE:
            return Operation.type_idle(qubit_id=self._translate_qubit(qubit=operation.identifier))
        elif operation.type == OperationType.PARK:
            return Operation.type_park(qubit_id=self._translate_qubit(qubit=operation.identifier))
        elif operation.type == OperationType.GATE:
            return Operation.type_gate(edge_id=self._translate_edge(edge=operation.identifier))
        raise NotImplementedError(f"Operation type {operation.type} not supported for translation.")
        
    def _translate_gate_sequence(self, sequence: GateSequenceLayer) -> GateSequenceLayer:
        """
        :param sequence: Gate sequence layer in the base layer.
        :return: Translated gate sequence layer in the target layer.
        """
        return GateSequenceLayer(
            _park_operations=[self._translate_operation(operation=operation) for operation in sequence.park_operations],
            _gate_operations=[self._translate_operation(operation=operation) for operation in sequence.gate_operations],
        )
        
    def _translate_parity_group(self, parity_group: IParityGroup) -> IParityGroup:
        """
        :param parity_group: Parity group in the base layer.
        :return: Translated parity group in the target layer.
        """
        translated_data_qubits: List[Union[IQubitID, Tuple[IQubitID, StabilizerType]]] = []
        # Accessing the private member if it is an instance of ParityGroup
        if hasattr(parity_group, '_data_qubits'):
            for data_qubit in parity_group._data_qubits:
                if isinstance(data_qubit, tuple):
                    translated_data_qubits.append((self._translate_qubit(qubit=data_qubit[0]), data_qubit[1]))
                else:
                    translated_data_qubits.append(self._translate_qubit(qubit=data_qubit))
        else:
            # Fallback for other IParityGroup implementations if any
            for data_qubit_id in parity_group.data_ids:
                translated_data_qubits.append(self._translate_qubit(qubit=data_qubit_id))
                
        return ParityGroup(
            _parity_type=parity_group.parity_type,
            _ancilla_qubit=self._translate_qubit(qubit=parity_group.ancilla_id),
            _data_qubits=translated_data_qubits
        )
    # endregion

    def get_gate_sequence_at_index(self, index: int) -> GateSequenceLayer:
        """
        :param index: Index of the gate sequence.
        :return: Translated gate-sequence object based on round index.
        """
        gate_sequences: List[GateSequenceLayer] = self.gate_sequences
        try:
            return gate_sequences[index]
        except IndexError:
            raise ElementNotIncludedException(f"Index: {index} is out of bounds for gate-sequence of length: {len(gate_sequences)}.")
        
    def get_gate_sequence_from_element(self, element: IEdgeID) -> GateSequenceLayer:
        """
        :param element: Edge element to look for.
        :return: Translated gate-sequence layer of which edge element is part of.
        """
        for sequence in self.gate_sequences:
            if element in sequence.edge_ids:
                return sequence
        raise ElementNotIncludedException(f"Edge {element} not part of any sequence.")
        
    def get_gate_sequence_indices(self, parity_group: IParityGroup) -> List[int]:
        """
        :param parity_group: Parity group to find sequences for.
        :return: Array-like of gate-sequence indices corresponding to parity-group edge-ID's.
        """
        parity_groups: List[IParityGroup] = self.parity_group_x + self.parity_group_z
        if parity_group not in parity_groups:
            return []
        
        edge_ids: List[IEdgeID] = parity_group.edge_ids
        result: List[int] = []
        for index, sequence in enumerate(self.gate_sequences):
            if any([edge in sequence.edge_ids for edge in edge_ids]):
                result.append(index)
        return result
        
    def get_logical_observable(self, basis: StabilizerType) -> ILogicalObservable:
        """
        :param basis: Basis of the logical observable.
        :return: Translated logical observable corresponding to basis.
        """
        base_observable: ILogicalObservable = self._base_layer.get_logical_observable(basis=basis)
        translated_data_qubit_projections: Dict[IQubitID, StabilizerType] = {
            self._translate_qubit(qubit=qubit_id): base_observable.get_projection_basis(qubit_id=qubit_id)
            for qubit_id in base_observable.involved_data_qubit_ids
        }
        translated_supporting_stabilizers: List[IQubitID] = [
            self._translate_qubit(qubit=qubit_id)
            for qubit_id in base_observable.concordant_stabilizer_qubit_ids
        ]
        translated_supporting_logical: List[IQubitID] = [
            self._translate_qubit(qubit=qubit_id)
            for qubit_id in base_observable.involved_data_qubit_ids
        ]
        result = LogicalObservable(
            observable_basis=base_observable.observable_basis,
            data_qubit_projections=translated_data_qubit_projections,
            supporting_stabilizers=translated_supporting_stabilizers,
            supporting_logical=translated_supporting_logical,
            default_projections=base_observable.default_projection_basis,
        )
        return result

    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> List[IParityGroup]:
        """
        :param element: Qubit or edge ID.
        :return: Parity group(s) of which element (edge- or qubit-ID) is part of.
        """
        result: List[IParityGroup] = []
        for parity_group in self.parity_group_x + self.parity_group_z:
            if parity_group.contains(element=element):
                result.append(parity_group)
        return result

    def get_frequency_group_identifier(self, element: IQubitID) -> FrequencyGroupIdentifier:
        """
        :param element: Qubit ID.
        :return: Frequency group identifier.
        """
        return self._target_layer.get_frequency_group_identifier(element=element)
        
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """
        :param feedline: Feedline ID.
        :return: Array-like of qubit-ID's connected to feedline-ID.
        """
        target_qubits: List[IQubitID] = self._target_layer.get_connected_qubits(feedline=feedline)
        return [qubit for qubit in target_qubits if qubit in self.qubit_ids]
        
    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """
        :param qubit: Qubit ID.
        :return: Feedline-ID connected to qubit-ID.
        """
        return self._target_layer.get_connected_feedline(qubit=qubit)
        
    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """
        :param element: Element to check.
        :return: Boolean, whether element is part of device layer or not.
        """
        if isinstance(element, IQubitID):
            return element in self.qubit_ids
        if isinstance(element, IEdgeID):
            return element in self.edge_ids
        if isinstance(element, IFeedlineID):
            return element in self.feedline_ids
        return False
        
    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        :param qubit: Qubit ID to find neighbors for.
        :param order: Distance order of neighbors.
        :return: Array-like of qubit neighbors separated by order.
        """
        target_neighbors: List[IQubitID] = self._target_layer.get_neighbors(qubit=qubit, order=order)
        return [neighbor for neighbor in target_neighbors if neighbor in self.qubit_ids]
        
    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """
        :param qubit: Qubit ID.
        :return: All qubit-to-qubit edges from qubit-ID.
        """
        return [edge for edge in self.edge_ids if edge.contains(element=qubit)]
        
    def get_qubit_coordinates(self, qubit_id: IQubitID) -> Vec2D:
        """
        :param qubit_id: Qubit ID.
        :return: The geometric coordinates for the given qubit ID.
        """
        return self._target_layer.get_qubit_coordinates(qubit_id=qubit_id)
