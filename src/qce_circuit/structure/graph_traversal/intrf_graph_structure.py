# -------------------------------------------
# A module describing the underlying graph structure.
# This framework describes how nodes relate to each other.
# -------------------------------------------
from abc import ABC, abstractmethod, ABCMeta
from dataclasses import dataclass, field
from typing import List, TypeVar, Iterable, Any, Iterator, Generic
from functools import reduce
from qce_circuit.utilities.custom_exceptions import InterfaceMethodException
from qce_circuit.utilities.custom_context_managers import WhileLoopSafety
from qce_circuit.utilities.array_manipulation import unique_in_order


class IGraphEvaluation(ABC):
    """
    Interface class, exposing method for evaluating circuit topology to an ordered list of nodes.
    """

    # region Interface Methods
    @abstractmethod
    def evaluate(self) -> List[List['IGraphNode']]:
        """:return: Iterable of IGraphNode instances."""
        raise InterfaceMethodException
    # endregion


class IEndpoint(ABC):
    """
    Interface class, describing multi-endpoint connection.
    End point is by default not connected (None) but can be connected to an entrypoint or another endpoint.
    The endpoint interface inherits from the IGraphEvaluation interface because it can back-propagate the information.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def outgoing_pointers(self) -> List['IEntrypoint']:
        """:return: Array-like of entrypoints to which this endpoint points."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def point_towards(self, pointer: 'IEntrypoint'):
        """:return: Void. Sets pointer to entrypoint."""
        raise InterfaceMethodException

    @abstractmethod
    def release_pointer(self, pointer: 'IEntrypoint'):
        """:return: Void. Removes entrypoint pointer."""
        raise InterfaceMethodException
    # endregion


class IEntrypoint(IGraphEvaluation, metaclass=ABCMeta):
    """
    Interface class, describing multi-entrypoint connection.
    Entry point is always connected to an endpoint, or to another entry point
    """

    # region Interface Properties
    @property
    @abstractmethod
    def incoming_pointers(self) -> List[IEndpoint]:
        """:return: Array-like of endpoints pointing to this entrypoint."""
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def update_set_incoming_pointer(self, pointer: IEndpoint):
        """:return: Void. Called when pointer is set to this endpoint."""
        raise InterfaceMethodException

    @abstractmethod
    def update_release_incoming_pointer(self, pointer: IEndpoint):
        """:return: Void. Called when pointer is released to this endpoint."""
        raise InterfaceMethodException
    # endregion


class IGraphNode(IEntrypoint, IEndpoint, metaclass=ABCMeta):
    """
    Interface class, describing entry- and end-point properties.
    A graph node maintains constant entry-endpoint to enable chaining.
    A graph node is its own entry point.
    Implements default behaviour for IEntrypoint and IEndpoint interface.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def incoming_pointers(self) -> List['IGraphNode']:
        """:return: Array-like of endpoints pointing to this entrypoint."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def outgoing_pointers(self) -> List['IGraphNode']:
        """:return: Array-like of entrypoints to which this endpoint points."""
        raise InterfaceMethodException

    @property
    def is_root(self) -> bool:
        """:return: Boolean, whether node is considered a root node."""
        return len(self.incoming_pointers) == 0

    @property
    def is_leaf(self) -> bool:
        """:return: Boolean, whether node is considered a leaf node."""
        return len(self.outgoing_pointers) == 0
    # endregion

    # region Interface Methods
    @abstractmethod
    def point_towards(self, pointer: 'IGraphNode'):
        """:return: Void. Sets pointer to entrypoint."""
        raise InterfaceMethodException

    @abstractmethod
    def release_pointer(self, pointer: 'IGraphNode'):
        """:return: Void. Removes entrypoint pointer."""
        raise InterfaceMethodException

    @abstractmethod
    def update_set_incoming_pointer(self, pointer: 'IGraphNode'):
        """:return: Void. Called when pointer is set to this endpoint."""
        raise InterfaceMethodException

    @abstractmethod
    def update_release_incoming_pointer(self, pointer: 'IGraphNode'):
        """:return: Void. Called when pointer is released to this endpoint."""
        raise InterfaceMethodException

    @abstractmethod
    def get_next_pointers(self) -> List['IGraphNode']:
        """:return: Array-like of (next) pointer(s) to which this pointer refers."""
        raise InterfaceMethodException

    # @abstractmethod
    # def insert_between(self, incoming_pointer: IEntryEndPointMaintainer, outgoing_pointer: IEntryEndPointMaintainer):
    #     """:return: Void. Inserts self between incoming- and outgoing-pointer."""
    #     raise InterfaceMethodException
    #
    # @abstractmethod
    # def insert_after(self, pointer: IEntryEndPointMaintainer):
    #     """:return: Void. Inserts maintainer after self and before all outgoing pointers."""
    #     raise InterfaceMethodException
    #
    # @abstractmethod
    # def insert_before(self, pointer: IEntryEndPointMaintainer):
    #     """:return: Void. Inserts maintainer after all incoming pointers and before self."""
    #     raise InterfaceMethodException
    # endregion


TGraphNode = TypeVar('TGraphNode', bound=IGraphNode)


class IGraphNavigation(ABC, Generic[TGraphNode]):
    """
    Interface class, describing navigation methods for a graph-like structure.
    Based on a type variable, bounded by IGraphNode.
    """

    # region Interface Properties
    @property
    @abstractmethod
    def root_node(self) -> TGraphNode:
        """:return: (single) root node."""
        raise InterfaceMethodException

    @property
    @abstractmethod
    def leaf_nodes(self) -> List[TGraphNode]:
        """
        Iterates through child nodes from root (entry-point).
        Collects all nodes that are not pointing to any other node (or pointing to end-point).
        :return: Array-like of TGraphNode (leaf nodes).
        """
        raise InterfaceMethodException
    # endregion

    # region Interface Methods
    @abstractmethod
    def get_branch_iterator(self) -> Iterator[List[TGraphNode]]:
        """
        :return: Iterator, going through layers of child nodes from root (entry-point) to end-point.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_node_iterator(self) -> Iterator[TGraphNode]:
        """
        :return: Iterator, going through nodes from root (entry-point) to end-point.
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_branch_depth(self) -> int:
        """
        Iterate through child nodes from root (entry-point).
        :return: Number of child node steps until 'lowest' leaf. (At the root, the depth is 0).
        """
        raise InterfaceMethodException

    @abstractmethod
    def get_nodes_at(self, depth: int) -> List[TGraphNode]:
        """
        :param depth: Branch depth at which to collect nodes.
        :return: Array-like of TGraphNodes at specific branch depth.
        """
        raise InterfaceMethodException
    # endregion


class IGraphBranch(IGraphNode, IGraphNavigation[TGraphNode], Generic[TGraphNode], metaclass=ABCMeta):
    """
    Interface class, exposing properties and methods for a single graph branch.
    A graph branch maintains constant entry-endpoint to enable chaining.
    A graph branch can be evaluated to collect all IGraphNodes between entry and endpoint.
    """

    # region Interface Methods
    @abstractmethod
    def append(self, pointer: TGraphNode) -> 'IGraphBranch[TGraphNode]':
        """:return: Appends self with another entry/end point maintainer."""
        raise InterfaceMethodException

    @abstractmethod
    def extend(self, pointers: Iterable[TGraphNode]) -> 'IGraphBranch[TGraphNode]':
        """:return: Extends self with an array-like of entry/end point maintainers."""
        raise InterfaceMethodException

    @abstractmethod
    def contains(self, node: TGraphNode) -> bool:
        """:return: Boolean whether self contains node."""
        raise InterfaceMethodException

    @abstractmethod
    def update_point_leafs_to_endpoint(self):
        """
        Traverses branch from 'root' to all 'leafs'.
        Updates pointers from all 'leaf' nodes to branch endpoint.
        Ensures all nodes part of the branch are contained withing graph-branch.
        :return: Void.
        """
        raise InterfaceMethodException

    @classmethod
    @abstractmethod
    def from_node(cls, node: TGraphNode) -> 'IGraphBranch[TGraphNode]':
        """:return: Class-method constructor based on (basic) node."""
        raise InterfaceMethodException
    # endregion


@dataclass(frozen=False)
class Endpoint(IEndpoint):
    """
    Data class, implementing IEndpoint
    """
    _outgoing_pointers: List[IEntrypoint] = field(init=False, default_factory=list)
    """Outgoing pointers."""

    # region Interface Properties
    @property
    def outgoing_pointers(self) -> List[IEntrypoint]:
        """:return: Array-like of entrypoints to which this endpoint points."""
        return self._outgoing_pointers
    # endregion

    # region Interface Methods
    def point_towards(self, pointer: 'IEntrypoint'):
        """:return: Void. Sets pointer to entrypoint."""
        self._outgoing_pointers.append(pointer)
        pointer.update_set_incoming_pointer(pointer=self)

    def release_pointer(self, pointer: 'IEntrypoint'):
        """:return: Void. Removes entrypoint pointer."""
        if pointer in self._outgoing_pointers:
            pointer.update_release_incoming_pointer(pointer=self)
            self._outgoing_pointers.remove(pointer)
    # endregion

    # region Class Methods
    def __repr__(self):
        result: str = f"Points towards: {[pointer.__class__.__name__ for pointer in self._outgoing_pointers]}"
        return result
    # endregion


def multipath(x: List[List[Any]], y: List[Any]) -> List[List[Any]]:
    """
    Method that merges two lists (of lists) together to obtain all possible perturbations.
    Example:
        a = []
        b = [0]
        c = [1, 2]
        d = [3]
        e = []
        ab = multipath(a, b)  # ab = [[0]]
        abc = multipath(ab, c) # abc = [[0, 1], [0, 2]]
        abcd = multipath(abc, d) # abcd = [[0, 1, 3], [0, 2, 3]]
        abcde = f(abcd, e) # abcde = [[0, 1, 3], [0, 2, 3]]
    """
    if not y:
        return x
    if not x:
        return [[item] for item in y]
    return [sublist + [item] for sublist in x for item in y]


@dataclass(frozen=False)
class Entrypoint(IEntrypoint):
    """
    Data class, implementing IEntrypoint.
    The pointer for an entry point should always be specified.
    """
    _pointer: IEndpoint = field(init=True, repr=False)
    """Required endpoint attribute."""
    _incoming_pointers: List[IEndpoint] = field(init=False, repr=False, default_factory=list)
    """Incoming pointers."""

    # region Interface Properties
    @property
    def incoming_pointers(self) -> List[IEndpoint]:
        """:return: Array-like of endpoints pointing to this entrypoint."""
        return self._incoming_pointers
    # endregion

    # region Interface Methods
    def update_set_incoming_pointer(self, pointer: IEndpoint):
        """:return: Void. Called when pointer is set to this endpoint."""
        self._incoming_pointers.append(pointer)

    def update_release_incoming_pointer(self, pointer: IEndpoint):
        """:return: Void. Called when pointer is released to this endpoint."""
        if pointer in self._incoming_pointers:
            self._incoming_pointers.remove(pointer)

    def evaluate(self) -> List[List[IGraphNode]]:
        """:return: Iterable of IGraphNode instances."""
        return reduce(multipath, [pointer.evaluate() for pointer in self._pointer.outgoing_pointers], [])
    # endregion

    # region Class Methods
    def __repr__(self):
        result: str = f"Points towards: {[self._pointer.__class__.__name__]}. Incoming: {[pointer.__class__.__name__ for pointer in self._incoming_pointers]}"
        return result
    # endregion


@dataclass(frozen=True)
class GraphNode(IGraphNode, Generic[TGraphNode]):
    """
    Data class, implementing IGraphNode interface.
    A single node is its own entry point.
    """
    _outgoing_pointers: List[TGraphNode] = field(init=False, repr=False, compare=False, default_factory=list)
    """Outgoing pointers."""
    _incoming_pointers: List[TGraphNode] = field(init=False, repr=False, compare=False, default_factory=list)
    """Incoming pointers."""
    identifier: int = field(init=False, repr=True, compare=True, default_factory=lambda: GraphNode._id_counter)
    """Automatically populated (instance) identifier."""
    _id_counter: int = field(init=False, repr=False, compare=False, default=0)
    """Class level counter. Used to populate unique identifier."""

    # region Interface Properties
    @property
    def incoming_pointers(self) -> List[TGraphNode]:
        """:return: Array-like of endpoints pointing to this entrypoint."""
        return self._incoming_pointers

    @property
    def outgoing_pointers(self) -> List[TGraphNode]:
        """:return: Array-like of entrypoints to which this endpoint points."""
        return self._outgoing_pointers
    # endregion

    # region Interface Methods
    def point_towards(self, pointer: TGraphNode):
        """:return: Void. Sets pointer to entrypoint."""
        self._outgoing_pointers.append(pointer)
        pointer.update_set_incoming_pointer(pointer=self)

    def release_pointer(self, pointer: TGraphNode):
        """:return: Void. Removes entrypoint pointer."""
        if pointer in self._outgoing_pointers:
            pointer.update_release_incoming_pointer(pointer=self)
            self._outgoing_pointers.remove(pointer)

    def update_set_incoming_pointer(self, pointer: TGraphNode):
        """:return: Void. Called when pointer is set to this endpoint."""
        self._incoming_pointers.append(pointer)

    def update_release_incoming_pointer(self, pointer: TGraphNode):
        """:return: Void. Called when pointer is released to this endpoint."""
        if pointer in self._incoming_pointers:
            self._incoming_pointers.remove(pointer)

    def get_next_pointers(self) -> List[TGraphNode]:
        """:return: Array-like of (next) pointer(s) to which this pointer refers."""
        return self.outgoing_pointers

    def evaluate(self) -> List[List[TGraphNode]]:
        """:return: Iterable of IGraphNode instances."""
        return reduce(multipath, [pointer.evaluate() for pointer in self.outgoing_pointers], [])
    # endregion

    # region Class Methods
    def __post_init__(self):
        GraphNode._id_counter += 1

    def __repr__(self):
        return f"{self.__class__.__name__}(#{str(self.identifier).zfill(3)})"
    # endregion


@dataclass(frozen=True)
class GraphBranch(IGraphBranch[TGraphNode], Generic[TGraphNode]):
    """
    Data class, implementing IGraphBranch interface.
    A single graph branch.
    """
    _entrypoint_node: TGraphNode = field(init=False, repr=False, compare=False)
    """Fixed entrypoint (node) for branch."""
    _endpoint_node: TGraphNode = field(init=False, repr=False, compare=False)
    """Fixed endpoint (node) for branch."""

    # region Interface Properties
    @property
    def incoming_pointers(self) -> List[IEndpoint]:
        """:return: Array-like of endpoints pointing to this entrypoint."""
        return self._entrypoint_node.incoming_pointers

    @property
    def outgoing_pointers(self) -> List[IEntrypoint]:
        """:return: Array-like of entrypoints to which this endpoint points."""
        return self._endpoint_node.outgoing_pointers

    @property
    def root_node(self) -> TGraphNode:
        """:return: (single) root node."""
        return self._entrypoint_node

    # TODO: Write unit test for following method
    @property
    def leaf_nodes(self) -> List[TGraphNode]:
        """
        Iterates through child nodes from root (self._entrypoint_node).
        Collects all nodes that are not pointing to any other node (or pointing to self._endpoint_node).
        :return: Array-like of IGraphNodes (leaf nodes).
        """
        # Data allocation
        leaf_nodes: List[TGraphNode] = []
        for _depth, branch_layer in enumerate(self.get_branch_iterator()):
            for potential_leaf_node in branch_layer:
                # Check next pointers of potential leaf node (excluding endpoint)
                potential_next_pointers: List[TGraphNode] = potential_leaf_node.get_next_pointers()
                excluding_endpoint: List[TGraphNode] = [node for node in potential_next_pointers if node is not self._endpoint_node]

                # Decide if node is a leaf node
                is_leaf: bool = len(excluding_endpoint) == 0
                if is_leaf:
                    leaf_nodes.append(potential_leaf_node)

        return unique_in_order(leaf_nodes)  # Filter duplicate nodes
    # endregion

    # region Interface Methods
    def point_towards(self, pointer: TGraphNode):
        """:return: Void. Sets pointer to entrypoint."""
        self._endpoint_node.point_towards(pointer=pointer)

    def release_pointer(self, pointer: TGraphNode):
        """:return: Void. Removes entrypoint pointer."""
        self._endpoint_node.release_pointer(pointer=pointer)

    def get_next_pointers(self) -> List[TGraphNode]:
        """:return: Array-like of (next) pointer(s) to which this pointer refers."""
        return self._entrypoint_node.get_next_pointers()

    def update_set_incoming_pointer(self, pointer: TGraphNode):
        """:return: Void. Called when pointer is set to this endpoint."""
        self._entrypoint_node.update_set_incoming_pointer(pointer=pointer)

    def update_release_incoming_pointer(self, pointer: TGraphNode):
        """:return: Void. Called when pointer is released to this endpoint."""
        self._entrypoint_node.update_release_incoming_pointer(pointer=pointer)

    def evaluate(self) -> List[List[TGraphNode]]:
        """:return: Iterable of IGraphNode instances."""
        return self._entrypoint_node.evaluate()
    # endregion

    # region Interface IGraphBranch Methods
    def append(self, pointer: TGraphNode) -> 'GraphBranch[TGraphNode]':
        """:return: Appends self with another entry/end point maintainer."""
        # Append before endpoint
        incoming_pointers: List[IEndpoint] = self._endpoint_node.incoming_pointers
        for incoming_pointer in incoming_pointers:
            incoming_pointer.point_towards(pointer=pointer)
            incoming_pointer.release_pointer(pointer=self._endpoint_node)
        # Update branch pointers
        self.update_point_leafs_to_endpoint()  # Points all leaf nodes to endpoint
        return self

    def extend(self, pointers: Iterable[TGraphNode]) -> 'GraphBranch[TGraphNode]':
        """:return: Extends self with an array-like of entry/end point maintainers."""
        for pointer in pointers:
            self.append(pointer)
        return self

    def contains(self, node: TGraphNode) -> bool:
        """:return: Boolean whether self contains node."""
        raise InterfaceMethodException

    def update_point_leafs_to_endpoint(self):
        """
        Traverses branch from 'root' to all 'leafs'.
        Updates pointers from all 'leaf' nodes to point to (branch) endpoint.
        Ensures all nodes part of the branch are contained withing graph-branch.
        :return: Void.
        """
        # Data allocation
        leaf_nodes: List[TGraphNode] = self.leaf_nodes
        # Set pointer only to self endpoint
        for node in leaf_nodes:
            for outgoing_pointer in node.outgoing_pointers:
                node.release_pointer(pointer=outgoing_pointer)
            # Point towards self endpoint
            node.point_towards(pointer=self._endpoint_node)

    @classmethod
    def from_node(cls, node: TGraphNode) -> 'GraphBranch[TGraphNode]':
        """:return: Class-method constructor based on (basic) node."""
        return GraphBranch().append(node)
    # endregion

    # region Interface IGraphNavigation Methods
    # TODO: Write unit test for following method
    def get_branch_iterator(self) -> Iterator[List[TGraphNode]]:
        """
        :return: Iterator, going through layers of child nodes from root (self._entrypoint_node) to self._endpoint_node.
        """
        # Data allocation
        iteration_nodes: List[TGraphNode] = [self._entrypoint_node]  # Root
        next_iteration_nodes: List[TGraphNode] = []

        with WhileLoopSafety(max_iterations=100) as loop:
            while len(iteration_nodes) > 0 and loop.safety_condition():
                yield iteration_nodes

                # Iterate through nodes
                for potential_leaf_node in iteration_nodes:
                    # Check next pointers of potential leaf node (excluding endpoint)
                    potential_next_pointers: List[TGraphNode] = potential_leaf_node.get_next_pointers()
                    excluding_endpoint: List[TGraphNode] = [node for node in potential_next_pointers if node is not self._endpoint_node]
                    # Collect next iteration
                    next_iteration_nodes.extend(excluding_endpoint)
                # Prepare for next round
                iteration_nodes = unique_in_order(next_iteration_nodes)  # Filter duplicate nodes
                next_iteration_nodes = []

    # TODO: Write unit test for following method
    def get_node_iterator(self) -> Iterator[TGraphNode]:
        """
        :return: Iterator, going through nodes from root (entry-point) to end-point.
        """
        for branch in self.get_branch_iterator():
            for node in branch:
                yield node

    # TODO: Write unit test for following method
    def get_branch_depth(self) -> int:
        """
        Iterate through child nodes from root (self._entrypoint_node).
        :return: Number of child node steps until 'lowest' leaf. (At the root, the depth is 0).
        """
        # Data allocation
        depth: int = 0

        for _depth, branch_layer in enumerate(self.get_branch_iterator()):
            depth = _depth
        return depth

    # TODO: Write unit test for following method
    def get_nodes_at(self, depth: int) -> List[TGraphNode]:
        """
        :param depth: Branch depth at which to collect nodes.
        :return: Array-like of IGraphNodes at specific branch depth.
        """
        # Guard clause, if depth is negative, return empty list
        if depth < 0:
            return []
        # Iterate through branch until specified depth has been reached.
        for _depth, branch_layer in enumerate(self.get_branch_iterator()):
            if _depth == depth:
                return branch_layer
        return []
    # endregion

    # region Class Methods
    def __post_init__(self):
        object.__setattr__(self, '_entrypoint_node', GraphNode())
        object.__setattr__(self, '_endpoint_node', GraphNode())
        self._entrypoint_node.point_towards(self._endpoint_node)

    def __repr__(self):
        internal_nodes: str = ""
        iteration_nodes: List[TGraphNode] = [self._entrypoint_node]
        next_iteration_nodes: List[TGraphNode] = []

        graph_depth: int = 100
        with WhileLoopSafety(max_iterations=graph_depth) as loop:
            # Execute while loop in safety environment
            while len(iteration_nodes) > 0 and loop.safety_condition():
                for iteration_node in iteration_nodes:
                    x = iteration_node.get_next_pointers()
                    next_iteration_nodes.extend(iteration_node.get_next_pointers())
                if len(next_iteration_nodes) == 0:
                    break

                # Perform metric
                internal_nodes += f"{[pointer.__repr__() for pointer in set(next_iteration_nodes)]}\n"

                # Prepare for next round
                iteration_nodes = next_iteration_nodes
                next_iteration_nodes = []

        result: str = f"Graph Branch:\n" \
                      f"EntryPoint: {self._entrypoint_node.__repr__()}\n" \
                      f"{internal_nodes}" \
                      f"EndPoint: {self._endpoint_node.__repr__()}\n"
        return result
    # endregion


if __name__ == '__main__':
    graph = GraphBranch()
    node_a = GraphNode()
    node_b = GraphNode()
    node_c = GraphNode()
    node_d = GraphNode()
    node_e = GraphNode()
    node_f = GraphNode()

    print(graph.get_branch_depth())  # 0

    # Create node dependencies
    #          B - D - End
    #         /   /
    # Entry- A   /
    #         \ /
    #          C
    node_a.point_towards(node_b)
    node_a.point_towards(node_c)
    node_b.point_towards(node_d)
    node_c.point_towards(node_d)
    graph.append(node_a)
    print(graph)
    print(graph.leaf_nodes)
    print(graph.get_branch_depth())  # 3

    # Create node dependencies
    #          B - D - E - F - End
    #         /   /       /
    # Entry- A   /       /
    #         \ /       /
    #          C ------
    node_e.point_towards(node_f)
    node_c.point_towards(node_f)
    graph.append(node_e)
    print(graph)
    print(graph.leaf_nodes)
    print(graph.get_branch_depth())  # 5
    print(graph.get_nodes_at(depth=2))  # C and B
