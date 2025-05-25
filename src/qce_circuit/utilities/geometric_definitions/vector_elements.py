# -------------------------------------------
# Module containing vector definitions.
# -------------------------------------------
from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass(frozen=True)
class Vec2D:
    """
    Data class, containing x- and y-coordinate vector.
    """
    x: float
    y: float

    # region Class Methods
    def to_vector(self) -> np.ndarray:
        return np.asarray([self.x, self.y])

    def to_tuple(self) -> Tuple[float, float]:
        return self.x, self.y

    def rotate(self, radian_angle: float, origin: Tuple[float, float] = (0, 0)) -> 'Vec2D':
        """Rotate a point (x, y) around the origin (0, 0) by a given angle in radians."""
        # Translate point to origin
        x_translated = self.x - origin[0]
        y_translated = self.y - origin[1]

        # Apply rotation
        cos_phi = np.cos(radian_angle)
        sin_phi = np.sin(radian_angle)
        x_rotated = x_translated * cos_phi - y_translated * sin_phi
        y_rotated = x_translated * sin_phi + y_translated * cos_phi

        # Translate point back
        x_new = x_rotated + origin[0]
        y_new = y_rotated + origin[1]
        return Vec2D(x_new, y_new)

    @classmethod
    def from_vector(cls, vector: np.ndarray) -> 'Vec2D':
        return Vec2D(
            x=vector[0],
            y=vector[1],
        )

    def __add__(self, other):
        if isinstance(other, Vec2D):
            return Vec2D(x=self.x + other.x, y=self.y + other.y)
        raise NotImplementedError(f"Addition with anything other than {Vec2D} is not implemented.")

    def __sub__(self, other):
        if isinstance(other, Vec2D):
            return Vec2D(x=self.x - other.x, y=self.y - other.y)
        raise NotImplementedError(f"Subtraction with anything other than {Vec2D} is not implemented.")

    def __mul__(self, other):
        return Vec2D(
            x=self.x * other,
            y=self.y * other,
        )
    # endregion


@dataclass(frozen=True)
class Line2D:
    """
    Data class, containing 2 vectors indicating start and end of line.
    """
    start: Vec2D
    end: Vec2D
