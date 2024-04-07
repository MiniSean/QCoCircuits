# -------------------------------------------
# Module containing implementation of transform constructor interface.
# -------------------------------------------
from dataclasses import dataclass
from typing import List

from qce_circuit.structure.intrf_circuit_operation import ChannelIdentifier, IDurationComponent
from qce_circuit.utilities.geometric_definitions import Vec2D
from qce_circuit.visualization.visualize_circuit.intrf_factory_draw_components import ITransformConstructor


@dataclass(frozen=True)
class TransformConstructor(ITransformConstructor):
    """
    Behaviour class, implementing ITransformConstructor interface
    """
    channel_height: float
    channel_spacing: float
    channel_indices: List[int]
    """Array of unique, ordered channel indices."""

    # region Interface Methods
    def identifier_to_pivot(self, identifier: ChannelIdentifier, time_component: IDurationComponent) -> Vec2D:
        """:return: Pivot based on channel identifier and duration component."""
        return Vec2D(
            x=time_component.start_time,
            y=-1 * self.channel_indices.index(identifier.id) * self.channel_spacing
        )

    def identifier_to_width(self, time_component: IDurationComponent) -> float:
        """:return: Rectilinear transform height based on duration component."""
        return time_component.duration

    def identifier_to_height(self, identifier: ChannelIdentifier) -> float:
        """:return: Rectilinear transform height based on channel identifier."""
        return self.channel_height
    # endregion


@dataclass(frozen=True)
class OffsetTransformConstructor(ITransformConstructor):
    """
    Behaviour class, implementing ITransformConstructor interface,
    with an additional off-center x-offset (for artistic purposes).
    """
    default_transform: ITransformConstructor
    pivot_offset_scalar_x: float
    """Scalar that offsets pivot in X-direction. x0 + xoff * time_component.duration."""

    # region Interface Methods
    def identifier_to_pivot(self, identifier: ChannelIdentifier, time_component: IDurationComponent) -> Vec2D:
        """:return: Pivot based on channel identifier and duration component."""
        default_pivot = self.default_transform.identifier_to_pivot(
            identifier=identifier,
            time_component=time_component,
        )
        return Vec2D(
            x=default_pivot.x + self.pivot_offset_scalar_x * time_component.duration,
            y=default_pivot.y
        )

    def identifier_to_width(self, time_component: IDurationComponent) -> float:
        """:return: Rectilinear transform height based on duration component."""
        return self.default_transform.identifier_to_width(time_component=time_component)

    def identifier_to_height(self, identifier: ChannelIdentifier) -> float:
        """:return: Rectilinear transform height based on channel identifier."""
        return self.default_transform.identifier_to_height(identifier=identifier)
    # endregion

