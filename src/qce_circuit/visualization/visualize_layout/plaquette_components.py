# -------------------------------------------
# Module containing rectilinear/draw components that represent layout plaquettes.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List
from enum import unique, Enum, auto
import numpy as np
from matplotlib import pyplot as plt, patches as patches
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    TransformAlignment,
    IRectTransform,
    RectTransform,
    FixedPivot,
    FixedLength,
    Vec2D,
)
from qce_circuit.visualization.visualize_layout.style_manager import (
    StyleManager,
    PlaquetteStyleSettings,
)


@unique
class BackgroundType(Enum):
    Z = auto()
    X = auto()


@dataclass(frozen=True)
class RectanglePlaquette(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing plaquette rectangle.
    """
    pivot: Vec2D
    width: float
    height: float
    rotation: float = field(default=0)
    background_type: BackgroundType = field(default=BackgroundType.X)
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: PlaquetteStyleSettings = field(default_factory=lambda: StyleManager.read_config().plaquette_style_x)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        rectangle = patches.Rectangle(
            xy=self.rectilinear_transform.origin_pivot.to_tuple(),
            width=self.rectilinear_transform.width,
            height=self.rectilinear_transform.height,
            rotation_point=self.rectilinear_transform.pivot.to_tuple(),
            angle=self.rotation,
            edgecolor='none',
            facecolor=self.style_settings.background_color,  # Depends on background type
            zorder=self.style_settings.zorder,
        )
        axes.add_patch(rectangle)
        return axes
    # endregion


@dataclass(frozen=True)
class TrianglePlaquette(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing plaquette triangle.
    """
    pivot: Vec2D
    width: float
    height: float
    rotation: float = field(default=0)
    background_type: BackgroundType = field(default=BackgroundType.X)
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: PlaquetteStyleSettings = field(default_factory=lambda: StyleManager.read_config().plaquette_style_x)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Properties
    @property
    def polygon_vertices(self) -> List[Vec2D]:
        transform: IRectTransform = self.rectilinear_transform
        vertices: List[Vec2D] = [Vec2D(0, 0), Vec2D(-self.width/2, +self.height/2), Vec2D(+self.width/2, +self.height/2)]
        vertices = [transform.pivot + vertex for vertex in vertices]
        # Apply rotation
        rotation_pivot: Vec2D = transform.pivot
        vertices = [vertex.rotate(np.deg2rad(self.rotation), rotation_pivot.to_tuple()) for vertex in vertices]
        return vertices
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        rectangle = patches.Polygon(
            [vertex.to_tuple() for vertex in self.polygon_vertices],
            closed=True,
            edgecolor='none',
            facecolor=self.style_settings.background_color,  # Depends on background type
            zorder=self.style_settings.zorder,
        )
        axes.add_patch(rectangle)
        return axes
    # endregion


@dataclass(frozen=True)
class DiagonalPlaquette(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing dimension data for drawing plaquette triangle.
    """
    pivot: Vec2D
    width: float
    height: float
    rotation: float = field(default=0)
    background_type: BackgroundType = field(default=BackgroundType.X)
    alignment: TransformAlignment = field(default=TransformAlignment.MID_LEFT)
    style_settings: PlaquetteStyleSettings = field(default_factory=lambda: StyleManager.read_config().plaquette_style_x)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return RectTransform(
            _pivot_strategy=FixedPivot(self.pivot),
            _width_strategy=FixedLength(self.width),
            _height_strategy=FixedLength(self.height),
            _parent_alignment=self.alignment,
        )
    # endregion

    # region Class Properties
    @property
    def polygon_vertices(self) -> List[Vec2D]:
        transform: IRectTransform = self.rectilinear_transform
        vertices: List[Vec2D] = [
            Vec2D(-self.width/2, +self.height/2),
            Vec2D(+self.width/3.5, +self.height/3.5),
            Vec2D(+self.width/2, -self.height/2),
            Vec2D(-self.width/3.5, -self.height/3.5),
        ]
        vertices = [transform.pivot + vertex for vertex in vertices]
        # Apply rotation
        rotation_pivot: Vec2D = transform.pivot
        vertices = [vertex.rotate(np.deg2rad(self.rotation), rotation_pivot.to_tuple()) for vertex in vertices]
        return vertices
    # endregion

    # region Class Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        rectangle = patches.Polygon(
            [vertex.to_tuple() for vertex in self.polygon_vertices],
            closed=True,
            edgecolor='none',
            facecolor=self.style_settings.background_color,  # Depends on background type
            zorder=self.style_settings.zorder,
        )
        axes.add_patch(rectangle)
        return axes
    # endregion

