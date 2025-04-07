# -------------------------------------------
# Module for specific (Quantum device layout visualization) style manager
# -------------------------------------------
import os
from dataclasses import dataclass, field
import threading
from contextlib import contextmanager
from qce_circuit.utilities.singleton_base import Singleton
from qce_circuit.utilities.readwrite_yaml import (
    get_yaml_file_path,
    write_yaml,
    read_yaml,
)


@dataclass(frozen=True)
class PlaquetteStyleSettings:
    """
    Data class, containing (background) plaquette style settings.
    """
    background_color: str
    line_color: str
    line_width: float
    zorder: int


@dataclass(frozen=True)
class ElementStyleSettings:
    """
    Data class, containing (dot) element style settings.
    """
    background_color: str
    line_color: str
    element_radius: float
    zorder: int


@dataclass(frozen=True)
class ElementTextStyleSettings:
    """
    Data class, containing (element) text style settings.
    """
    element_radius: float
    font_size: float
    font_color: str
    zorder: int


@dataclass(frozen=True)
class LineSettings:
    """
    Data class, containing line style settings.
    """
    line_color: str
    line_width: float
    line_style: str
    zorder: int


@dataclass(frozen=True)
class ParkOperationStyleSettings:
    """
    Data class, containing park operation style settings.
    """
    element_radius: float
    line_color: str
    line_width: float
    line_style: str
    zorder: int


@dataclass(frozen=True)
class GateOperationStyleSettings:
    """
    Data class, containing gate operation style settings.
    """
    line_settings: LineSettings
    dot_settings: ElementStyleSettings


@dataclass(frozen=True)
class StyleSettings:
    """
    Data class, describing a variety of parameter settings for stylization.
    """
    # Color schemes
    color_background_x: str = field(default='#7ba3e3')
    color_background_z: str = field(default='#2bab4b')  # '#3870c9'
    color_text: str = field(default='black')
    color_outline: str = field(default='black')
    color_element: str = field(default='#b3c7e8')
    color_element_outline: str = field(default='#1c50a3')
    color_park_operation: str = field(default='black')
    color_gate_operation: str = field(default='black')

    # Widths
    width_line_small: float = field(default=2.0)
    width_line_medium: float = field(default=4.0)
    width_line_large: float = field(default=8.0)
    width_line_thick: float = field(default=12.0)

    # Radius
    radius_dot: float = field(default=0.2)
    radius_hexagon: float = field(default=0.3)
    radius_dot_indicator: float = field(default=0.3)

    # Font sizes
    font_size: float = field(default=16.0)

    # Draw order
    zorder_plaquette: int = field(default=-1)
    zorder_element: int = field(default=3)
    zorder_line: int = field(default=1)
    zorder_operation: int = field(default=2)
    zorder_text: int = field(default=5)

    # region Class Properties
    @property
    def plaquette_style_x(self) -> PlaquetteStyleSettings:
        return PlaquetteStyleSettings(
            background_color=self.color_background_x,
            line_color=self.color_outline,
            line_width=self.width_line_small,
            zorder=self.zorder_plaquette,
        )

    @property
    def plaquette_style_z(self) -> PlaquetteStyleSettings:
        return PlaquetteStyleSettings(
            background_color=self.color_background_z,
            line_color=self.color_outline,
            line_width=self.width_line_small,
            zorder=self.zorder_plaquette,
        )

    @property
    def dot_style(self) -> ElementStyleSettings:
        return ElementStyleSettings(
            background_color=self.color_element,
            line_color=self.color_element,
            element_radius=self.radius_dot,
            zorder=self.zorder_element,
        )

    @property
    def hexagon_style(self) -> ElementStyleSettings:
        return ElementStyleSettings(
            background_color=self.color_element_outline,
            line_color=self.color_element_outline,
            element_radius=self.radius_hexagon,
            zorder=self.zorder_element,
        )

    @property
    def line_style(self) -> LineSettings:
        return LineSettings(
            line_color=self.color_outline,
            line_width=self.width_line_large,
            line_style='-',
            zorder=self.zorder_line,
        )

    @property
    def park_operation_style(self) -> ParkOperationStyleSettings:
        return ParkOperationStyleSettings(
            element_radius=self.radius_dot_indicator,
            line_color=self.color_park_operation,
            line_width=self.width_line_medium,
            line_style='--',
            zorder=self.zorder_operation,
        )

    @property
    def gate_operation_style(self) -> GateOperationStyleSettings:
        return GateOperationStyleSettings(
            line_settings=LineSettings(
                line_color=self.color_gate_operation,
                line_width=self.width_line_thick,
                line_style='-',
                zorder=self.zorder_operation,
            ),
            dot_settings=ElementStyleSettings(
                background_color=self.color_gate_operation,
                line_color=self.color_gate_operation,
                element_radius=self.radius_dot_indicator,
                zorder=self.zorder_operation,
            )
        )

    @property
    def element_text_style(self) -> ElementTextStyleSettings:
        return ElementTextStyleSettings(
            element_radius=self.radius_dot,
            font_size=self.font_size,
            font_color=self.color_text,
            zorder=self.zorder_text,
        )
    # endregion


class StyleManager(metaclass=Singleton):
    """
    Behaviour Class, manages import of (device) layout-visualization style file.
    """
    CONFIG_NAME: str = 'config_layout_style.yaml'
    _override_stack = threading.local()  # Thread-safe storage for overrides

    # region Class Methods
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return StyleSettings().__dict__

    @classmethod
    def read_config(cls) -> StyleSettings:
        """
        Reads the configuration settings, applying any temporary overrides if present.
        It checks if there is a stack of overrides; if so, returns the most recent override.

        :return: The effective StyleSettings, either from file or from temporary overrides.
        """
        if hasattr(cls._override_stack, "stack") and cls._override_stack.stack:
            # Return the latest override if present
            return cls._override_stack.stack[-1]

        path = get_yaml_file_path(filename=cls.CONFIG_NAME)
        if not os.path.exists(path):
            default_dict: dict = cls._default_config_object()
            write_yaml(
                filename=cls.CONFIG_NAME,
                packable=default_dict,
                make_file=True,
            )
        return StyleSettings(**read_yaml(filename=cls.CONFIG_NAME))

    @classmethod
    @contextmanager
    def temporary_override(cls, **overrides):
        """
        Temporarily override specific style settings in memory, supporting nested overrides.
        The new override is based on the current configuration, which may already have been overridden.

        :param overrides: Keyword arguments for the configuration values to override.
        :return: A context manager that yields control with the overridden configuration.
        """
        # Get the current configuration, which is either the top override or the default configuration.
        current_config = cls.read_config()
        new_config_dict = current_config.__dict__.copy()
        new_config_dict.update(overrides)  # Apply new overrides

        new_override = StyleSettings(**new_config_dict)

        # Initialize the override stack if it doesn't exist.
        if not hasattr(cls._override_stack, "stack"):
            cls._override_stack.stack = []
        # Push the new override onto the stack.
        cls._override_stack.stack.append(new_override)

        try:
            yield
        finally:
            # Pop the override from the stack to restore the previous configuration.
            cls._override_stack.stack.pop()
    # endregion
