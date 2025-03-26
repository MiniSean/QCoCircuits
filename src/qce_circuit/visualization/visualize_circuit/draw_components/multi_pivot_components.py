# -------------------------------------------
# Module containing components that represent operations using multi-pivots.
# -------------------------------------------
from dataclasses import dataclass, field
from typing import List
from matplotlib import pyplot as plt, patches as patches
from qce_circuit.visualization.visualize_circuit.intrf_draw_component import IDrawComponent
from qce_circuit.visualization.visualize_circuit.intrf_factory_draw_components import ITransformConstructor
from qce_circuit.utilities.geometric_definitions import (
    IRectTransformComponent,
    TransformAlignment,
    IRectTransform,
    RectTransform,
    IPivotStrategy,
    ILengthStrategy,
    DynamicPivot,
    DynamicLength,
    Vec2D,
    Line2D,
)
from qce_circuit.visualization.visualize_circuit.draw_components.operation_components import (
    RotationAngle,
    RotationAxis,
    BlockRotation,
)
from qce_circuit.visualization.visualize_circuit.style_manager import (
    StyleManager,
    OperationStyleSettings,
    IndicatorStyleSettings,
)

TransformAlignmentSubset = {TransformAlignment.MID_LEFT, TransformAlignment.MID_CENTER, TransformAlignment.MID_RIGHT}


@dataclass(frozen=True)
class DotComponent(IDrawComponent):
    base_transform: IRectTransform
    style_settings: OperationStyleSettings = field(default_factory=lambda: StyleManager.read_config().operation_style)

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        dot = patches.Circle(
            xy=self.base_transform.center_pivot.to_tuple(),
            radius=self.style_settings.dot_radius,
            color=self.style_settings.border_color,
        )
        # Apply patches
        axes.add_patch(dot)
        return axes
    # endregion


@dataclass(frozen=True)
class CrossComponent(IDrawComponent):
    base_transform: IRectTransform
    style_settings: OperationStyleSettings = field(default_factory=lambda: StyleManager.read_config().operation_style)

    # region Class Properties
    @property
    def cross_line_width(self) -> float:
        return self.style_settings.line_width * 1.0

    @property
    def dot_radius(self) -> float:
        return self.style_settings.dot_radius

    @property
    def cross_line_horizontal(self) -> Line2D:
        return Line2D(
            start=self.base_transform.center_pivot + Vec2D(x=-self.dot_radius, y=0),
            end=self.base_transform.center_pivot + Vec2D(x=+self.dot_radius, y=0),
        )

    @property
    def cross_line_vertical(self) -> Line2D:
        return Line2D(
            start=self.base_transform.center_pivot + Vec2D(x=0, y=-self.dot_radius),
            end=self.base_transform.center_pivot + Vec2D(x=0, y=+self.dot_radius),
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        dot = patches.Circle(
            xy=self.base_transform.center_pivot.to_tuple(),
            radius=self.style_settings.dot_radius,
            facecolor=self.style_settings.background_color,
            edgecolor=self.style_settings.border_color,
            linewidth=self.cross_line_width,
        )
        axes.plot(
            [self.cross_line_horizontal.start.x, self.cross_line_horizontal.end.x],
            [self.cross_line_horizontal.start.y, self.cross_line_horizontal.end.y],
            linestyle='-',
            linewidth=self.cross_line_width,
            color=self.style_settings.border_color,
        )
        axes.plot(
            [self.cross_line_vertical.start.x, self.cross_line_vertical.end.x],
            [self.cross_line_vertical.start.y, self.cross_line_vertical.end.y],
            linestyle='-',
            linewidth=self.cross_line_width,
            color=self.style_settings.border_color,
        )
        # Apply patches
        axes.add_patch(dot)
        return axes
    # endregion


@dataclass(frozen=True)
class BlockRotationComponent(IDrawComponent):
    """
    Data class, specializes in drawing rotation block
    """
    base_transform: IRectTransform
    rotation_angle: RotationAngle = field(default=RotationAngle.THETA)
    style_settings: OperationStyleSettings = field(default_factory=lambda: StyleManager.read_config().operation_style)

    # region Class Properties
    @property
    def rotation_block(self) -> BlockRotation:
        return BlockRotation(
            pivot=self.base_transform.center_pivot,
            height=self.base_transform.height,
            alignment=TransformAlignment.MID_CENTER,
            rotation_axes=RotationAxis.Z,
            rotation_angle=self.rotation_angle,
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        return self.rotation_block.draw(axes=axes)
    # endregion


@dataclass(frozen=True)
class BlockTwoQubitGate(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing information to draw a two-qubit gate block
    that uses two pivots to comply with vertical alignment.
    """
    main_pivot: IPivotStrategy
    vertical_pivot: IPivotStrategy
    """Second pivot. Only y-value is used."""
    single_block_height: ILengthStrategy
    single_block_width: ILengthStrategy
    alignment: TransformAlignmentSubset = field(default=TransformAlignment.MID_LEFT)
    style_settings: OperationStyleSettings = field(default_factory=lambda: StyleManager.read_config().operation_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        origin_pivot: Vec2D = self.combined_origin_pivot
        opposite_origin_pivot: Vec2D = self.combined_opposite_origin_pivot
        return RectTransform(
            _pivot_strategy=DynamicPivot(lambda: origin_pivot),
            _width_strategy=DynamicLength(lambda: abs(origin_pivot.x - opposite_origin_pivot.x)),
            _height_strategy=DynamicLength(lambda: abs(origin_pivot.y - opposite_origin_pivot.y)),
            _parent_alignment=TransformAlignment.BOT_LEFT,
        )
    # endregion

    # region Class Properties
    @property
    def main_transform_block(self) -> IRectTransform:
        """:return: Transform block around main pivot."""
        return RectTransform(
            _pivot_strategy=self.main_pivot,
            _width_strategy=self.single_block_width,
            _height_strategy=self.single_block_height,
            _parent_alignment=self.alignment,
        )

    @property
    def second_transform_block(self) -> IRectTransform:
        """:return: Transform block around second (vertical) pivot."""
        return RectTransform(
            _pivot_strategy=self.vertical_pivot,
            _width_strategy=self.single_block_width,
            _height_strategy=self.single_block_height,
            _parent_alignment=self.alignment,
        )

    @property
    def combined_origin_pivot(self) -> Vec2D:
        """:return: Origin (bot-left) pivot of the combined main- and secondary transform block."""
        main_origin: Vec2D = self.main_transform_block.origin_pivot
        second_origin: Vec2D = self.second_transform_block.origin_pivot
        return Vec2D(
            x=min(main_origin.x, second_origin.x),
            y=min(main_origin.y, second_origin.y),
        )

    @property
    def combined_opposite_origin_pivot(self) -> Vec2D:
        """:return: Origin (top-right) pivot of the combined main- and secondary transform block."""
        main_origin_opposite: Vec2D = self.main_transform_block.origin_opposite_pivot
        second_origin_opposite: Vec2D = self.second_transform_block.origin_opposite_pivot
        return Vec2D(
            x=max(main_origin_opposite.x, second_origin_opposite.x),
            y=max(main_origin_opposite.y, second_origin_opposite.y),
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        # TODO: Add logic based on attributes
        DotComponent(
            base_transform=self.main_transform_block,
        ).draw(axes=axes)
        DotComponent(
            base_transform=self.second_transform_block,
        ).draw(axes=axes)
        # CrossComponent(
        #     base_transform=self.second_transform_block,
        # ).draw(axes=axes)
        # BlockRotationComponent(
        #     base_transform=self.second_transform_block,
        #     rotation_angle=RotationAngle.THETA,
        # ).draw(axes=axes)

        axes.plot(
            [self.main_transform_block.center_pivot.x, self.second_transform_block.center_pivot.x],
            [self.main_transform_block.center_pivot.y, self.second_transform_block.center_pivot.y],
            linestyle='-',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.border_color,
            zorder=-10,
        )
        return axes
    # endregion


@dataclass(frozen=True)
class BlockTwoQubitVacant(BlockTwoQubitGate, IRectTransformComponent, IDrawComponent):
    """
    Data class, containing information to draw a two-qubit gate block
    that uses two pivots to comply with vertical alignment.
    """
    style_settings: OperationStyleSettings = field(default_factory=lambda: StyleManager.read_config().vacant_operation_style)

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""
        DotComponent(
            base_transform=self.main_transform_block,
            style_settings=self.style_settings,
        ).draw(axes=axes)
        DotComponent(
            base_transform=self.second_transform_block,
            style_settings=self.style_settings,
        ).draw(axes=axes)
        axes.plot(
            [self.main_transform_block.center_pivot.x, self.second_transform_block.center_pivot.x],
            [self.main_transform_block.center_pivot.y, self.second_transform_block.center_pivot.y],
            linestyle='--',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.border_color,
            zorder=-10,
        )
        return axes
    # endregion


@dataclass(frozen=True)
class BlockVerticalBarrier(IRectTransformComponent, IDrawComponent):
    """
    Data class, containing information to draw a vertical barrier block
    that uses multiple pivots to comply with vertical alignment.
    """
    multiple_transforms: List[IRectTransform]
    style_settings: IndicatorStyleSettings = field(default_factory=lambda: StyleManager.read_config().indicator_style)

    # region Interface Properties
    @property
    def rectilinear_transform(self) -> IRectTransform:
        """:return: 'Hard' rectilinear transform boundary. Should be treated as 'personal zone'."""
        return ITransformConstructor.combine_transforms(self.rectilinear_transforms)
    # endregion

    # region Class Properties
    @property
    def rectilinear_transforms(self) -> List[IRectTransform]:
        return self.multiple_transforms

    @property
    def top_pivot(self) -> Vec2D:
        """:return: Combine multiple pivot by taking maximum x-value, and maximum y-value."""
        transforms: List[IRectTransform] = self.rectilinear_transforms
        return Vec2D(
            x=max([transform.center_pivot.x for transform in transforms]),
            y=max([transform.top_pivot.y for transform in transforms]),
        )

    @property
    def bot_pivot(self) -> Vec2D:
        """:return: Combine multiple pivot by taking maximum x-value, and minimum y-value."""
        transforms: List[IRectTransform] = self.rectilinear_transforms
        return Vec2D(
            x=max([transform.center_pivot.x for transform in transforms]),
            y=min([transform.bot_pivot.y for transform in transforms]),
        )
    # endregion

    # region Interface Methods
    def draw(self, axes: plt.Axes) -> plt.Axes:
        """Method used for drawing component on Axes."""

        top_pivot: Vec2D = self.top_pivot
        bot_pivot: Vec2D = self.bot_pivot
        axes.plot(
            [top_pivot.x, bot_pivot.x],
            [top_pivot.y, bot_pivot.y],
            linestyle='--',
            linewidth=self.style_settings.line_width,
            color=self.style_settings.line_color,
            zorder=-10,
        )
        return axes
    # endregion
