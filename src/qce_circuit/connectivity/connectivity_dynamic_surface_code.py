# -------------------------------------------
# Module containing dynamic implementation of surface-code connectivity structure.
# -------------------------------------------
from typing import List, Union, Dict
from qce_circuit.utilities.custom_exceptions import ElementNotIncludedException
from qce_circuit.connectivity.intrf_channel_identifier import (
    IFeedlineID,
    IQubitID,
    IEdgeID,
    FeedlineIDObj,
    QubitIDObj,
    EdgeIDObj,
)
from qce_circuit.connectivity.intrf_connectivity_surface_code import (
    ISurfaceCodeLayer,
    IParityGroup,
    StabilizerType,
    FrequencyGroup,
    FrequencyGroupIdentifier,
)
from qce_circuit.connectivity.connectivity_surface_code import ParityGroup
from qce_circuit.utilities.geometric_definitions.vector_elements import Vec2D


class DynamicSurfaceCodeLayer(ISurfaceCodeLayer):
    """
    Class implementing ISurfaceCodeLayer interface to describe a dynamically generated 
    rotated surface-code layout with arbitrary dimensions.
    """

    # region Class Constructor
    def __init__(self, width: int, height: int):
        """Initializes the dynamic surface code layer with the specified dimensions."""
        self._width: int = width
        self._height: int = height
        
        self._parity_group_x: List[IParityGroup] = []
        self._parity_group_z: List[IParityGroup] = []
        self._qubit_edges: List[IEdgeID] = []
        self._feedline_qubit_lookup: Dict[IFeedlineID, List[IQubitID]] = {}
        self._frequency_group_lookup: Dict[IQubitID, FrequencyGroupIdentifier] = {}
        self._qubit_coordinates_lookup: Dict[IQubitID, Vec2D] = {}
        
        self._generate_layout()
    # endregion

    # region Class Methods
    def _generate_layout(self) -> None:
        """Generates the parity groups, edges, feedlines, and frequency groups based on the width and height."""
        grid_width = self._width
        grid_height = self._height
        
        x_ancilla_count = 0
        z_ancilla_count = 0
        
        x_offset = (grid_width - grid_height) / 2.0
        y_offset = (grid_width + grid_height - 2) / 2.0
        
        def get_coord(row_eff: float, col_eff: float) -> Vec2D:
            return Vec2D(col_eff - row_eff - x_offset, col_eff + row_eff - y_offset)

        for row in range(grid_height):
            for col in range(grid_width):
                qubit_id = QubitIDObj(f'D{row * grid_width + col}')
                self._qubit_coordinates_lookup[qubit_id] = get_coord(row, col)
        
        for row in range(grid_height - 1):
            for col in range(grid_width - 1):
                data_ids = [
                    QubitIDObj(f'D{row * grid_width + col}'),
                    QubitIDObj(f'D{row * grid_width + col + 1}'),
                    QubitIDObj(f'D{(row + 1) * grid_width + col}'),
                    QubitIDObj(f'D{(row + 1) * grid_width + col + 1}'),
                ]
                if (row + col) % 2 == 1:
                    ancilla_id = QubitIDObj(f'X{x_ancilla_count}')
                    self._qubit_coordinates_lookup[ancilla_id] = get_coord(row + 0.5, col + 0.5)
                    self._parity_group_x.append(ParityGroup(
                        _parity_type=StabilizerType.STABILIZER_X, 
                        _ancilla_qubit=ancilla_id, 
                        _data_qubits=data_ids
                    ))
                    x_ancilla_count += 1
                else:
                    ancilla_id = QubitIDObj(f'Z{z_ancilla_count}')
                    self._qubit_coordinates_lookup[ancilla_id] = get_coord(row + 0.5, col + 0.5)
                    self._parity_group_z.append(ParityGroup(
                        _parity_type=StabilizerType.STABILIZER_Z, 
                        _ancilla_qubit=ancilla_id, 
                        _data_qubits=data_ids
                    ))
                    z_ancilla_count += 1
        
        for col in range(grid_width - 1):
            if col % 2 == 0:
                data_ids = [QubitIDObj(f'D{col}'), QubitIDObj(f'D{col + 1}')]
                ancilla_id = QubitIDObj(f'X{x_ancilla_count}')
                self._qubit_coordinates_lookup[ancilla_id] = get_coord(-0.5, col + 0.5)
                self._parity_group_x.append(ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_X, 
                    _ancilla_qubit=ancilla_id, 
                    _data_qubits=data_ids
                ))
                x_ancilla_count += 1
                
        for col in range(grid_width - 1):
            if (grid_height + col) % 2 == 0:
                data_ids = [QubitIDObj(f'D{(grid_height - 1) * grid_width + col}'), QubitIDObj(f'D{(grid_height - 1) * grid_width + col + 1}')]
                ancilla_id = QubitIDObj(f'X{x_ancilla_count}')
                self._qubit_coordinates_lookup[ancilla_id] = get_coord(grid_height - 0.5, col + 0.5)
                self._parity_group_x.append(ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_X, 
                    _ancilla_qubit=ancilla_id, 
                    _data_qubits=data_ids
                ))
                x_ancilla_count += 1
                
        for row in range(grid_height - 1):
            if row % 2 == 1:
                data_ids = [QubitIDObj(f'D{row * grid_width}'), QubitIDObj(f'D{(row + 1) * grid_width}')]
                ancilla_id = QubitIDObj(f'Z{z_ancilla_count}')
                self._qubit_coordinates_lookup[ancilla_id] = get_coord(row + 0.5, -0.5)
                self._parity_group_z.append(ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z, 
                    _ancilla_qubit=ancilla_id, 
                    _data_qubits=data_ids
                ))
                z_ancilla_count += 1
                
        for row in range(grid_height - 1):
            if (row + grid_width) % 2 == 1:
                data_ids = [QubitIDObj(f'D{row * grid_width + (grid_width - 1)}'), QubitIDObj(f'D{(row + 1) * grid_width + (grid_width - 1)}')]
                ancilla_id = QubitIDObj(f'Z{z_ancilla_count}')
                self._qubit_coordinates_lookup[ancilla_id] = get_coord(row + 0.5, grid_width - 0.5)
                self._parity_group_z.append(ParityGroup(
                    _parity_type=StabilizerType.STABILIZER_Z, 
                    _ancilla_qubit=ancilla_id, 
                    _data_qubits=data_ids
                ))
                z_ancilla_count += 1

        for group in self._parity_group_x + self._parity_group_z:
            for data_id in group.data_ids:
                edge = EdgeIDObj(qubit_id0=data_id, qubit_id1=group.ancilla_id)
                if edge not in self._qubit_edges:
                    self._qubit_edges.append(edge)

        all_qubits = [QubitIDObj(f'D{index}') for index in range(grid_width * grid_height)]
        all_qubits.extend([QubitIDObj(f'X{index}') for index in range(x_ancilla_count)])
        all_qubits.extend([QubitIDObj(f'Z{index}') for index in range(z_ancilla_count)])
        
        self._feedline_qubit_lookup = {
            FeedlineIDObj('FL_global'): all_qubits
        }
        
        self._frequency_group_lookup = {
            qubit: FrequencyGroupIdentifier(_id=FrequencyGroup.MID)
            for qubit in all_qubits
        }
    # endregion

    # region IDeviceLayer Interface Properties
    @property
    def feedline_ids(self) -> List[IFeedlineID]:
        """:return: All feedline-ID's in device layer."""
        return list(self._feedline_qubit_lookup.keys())

    @property
    def qubit_ids(self) -> List[IQubitID]:
        """:return: (All) qubit-ID's in device layer."""
        return [qubit_id for qubit_ids in self._feedline_qubit_lookup.values() for qubit_id in qubit_ids]

    @property
    def edge_ids(self) -> List[IEdgeID]:
        """:return: (All) edge-ID's in device layer."""
        return self._qubit_edges
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
        all_qubit_ids: List[IQubitID] = self.qubit_ids
        ancilla_qubit_ids: List[IQubitID] = self.ancilla_qubit_ids
        return [qubit_id for qubit_id in all_qubit_ids if qubit_id not in ancilla_qubit_ids]

    @property
    def ancilla_qubit_ids(self) -> List[IQubitID]:
        """:return: (Ancilla) qubit-ID's in device layer."""
        return [parity_group.ancilla_id for parity_group in self.parity_group_x + self.parity_group_z]
    # endregion

    # region ISurfaceCodeLayer Interface Methods
    def get_parity_group(self, element: Union[IQubitID, IEdgeID]) -> List[IParityGroup]:
        """:return: Parity group(s) of which element (edge- or qubit-ID) is part of."""
        result: List[IParityGroup] = []
        for parity_group in self.parity_group_x + self.parity_group_z:
            if parity_group.contains(element=element):
                result.append(parity_group)
        return result
    
    def get_frequency_group_identifier(self, element: IQubitID) -> FrequencyGroupIdentifier:
        """:return: Frequency group identifier based on qubit-ID."""
        return self._frequency_group_lookup[element]
        
    def get_qubit_coordinates(self, qubit_id: IQubitID) -> Vec2D:
        """:return: The geometric coordinates for the given qubit ID."""
        if qubit_id not in self._qubit_coordinates_lookup:
            raise ElementNotIncludedException(f"Element: {qubit_id} has no coordinates defined.")
        return self._qubit_coordinates_lookup[qubit_id]
    # endregion

    # region IDeviceLayer Interface Methods
    def get_connected_qubits(self, feedline: IFeedlineID) -> List[IQubitID]:
        """:return: Qubit-ID's connected to feedline-ID."""
        if feedline not in self._feedline_qubit_lookup:
            raise ElementNotIncludedException(f"Element: {feedline} is not included in any feedline group.")
        return self._feedline_qubit_lookup[feedline]

    def get_connected_feedline(self, qubit: IQubitID) -> IFeedlineID:
        """:return: Feedline-ID's connected to qubit-ID."""
        for feedline_id in self.feedline_ids:
            if qubit in self.get_connected_qubits(feedline=feedline_id):
                return feedline_id
        raise ElementNotIncludedException(f"Element: {qubit} is not included in any feedline.")

    def get_neighbors(self, qubit: IQubitID, order: int = 1) -> List[IQubitID]:
        """
        Requires :param order: to be higher or equal to 1.
        :return: qubit neighbors separated by order. (order=1, nearest neighbors).
        """
        if order > 1:
            raise NotImplementedError("Apologies, so far there has not been a use for. But feel free to implement.")
        edges: List[IEdgeID] = self.get_edges(qubit=qubit)
        result: List[IQubitID] = []
        for edge in edges:
            result.append(edge.get_connected_qubit_id(element=qubit))
        return result

    def get_edges(self, qubit: IQubitID) -> List[IEdgeID]:
        """:return: All qubit-to-qubit edges from qubit-ID."""
        result: List[IEdgeID] = []
        for edge in self.edge_ids:
            if edge.contains(element=qubit):
                result.append(edge)
        return result

    def contains(self, element: Union[IFeedlineID, IQubitID, IEdgeID]) -> bool:
        """:return: Boolean, whether element is part of device layer or not."""
        if element in self.feedline_ids:
            return True
        if element in self.qubit_ids:
            return True
        if element in self.edge_ids:
            return True
        return False
    # endregion


if __name__ == '__main__':
    from qce_circuit.visualization.visualize_layout.display_connectivity import plot_layout_description, VisualConnectivityDescription
    from qce_circuit.connectivity.connectivity_surface_code import Surface17Layer
    import matplotlib.pyplot as plt

    # Initialize an arbitrary HxW surface code:
    layer = DynamicSurfaceCodeLayer(width=5, height=5)
    print(layer)
    # layer = Surface17Layer()

    plot_layout_description(description=VisualConnectivityDescription(layer))
    plt.show()
