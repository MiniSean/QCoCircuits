# -------------------------------------------
# Module for specific (Quantum device layout visualization) style manager
# -------------------------------------------
import os
from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class ElementStyleSettings:
    """
    Data class, containing (dot) element style settings.
    """
    background_color: str
    dot_radius: float


@dataclass(frozen=True)
class StyleSettings:
    """
    Data class, describing a variety of parameter settings for stylization.
    """
    # Color schemes
    color_background: str = field(default='lightgrey')
    color_text: str = field(default='black')
    color_outline: str = field(default='black')
    color_element: str = field(default='black')

    # Widths
    width_line: float = field(default=2.0)

    # Radius
    radius_dot: float = field(default=0.1)

    # Font sizes
    font_size: float = field(default=12.0)

    # region Class Properties
    @property
    def plaquette_style(self) -> PlaquetteStyleSettings:
        return PlaquetteStyleSettings(
            background_color=self.color_background,
            line_color=self.color_outline,
            line_width=self.width_line,
        )

    @property
    def element_style(self) -> ElementStyleSettings:
        return ElementStyleSettings(
            background_color=self.color_element,
            dot_radius=self.radius_dot,
        )
    # endregion


class StyleManager(metaclass=Singleton):
    """
    Behaviour Class, manages import of (device) layout-visualization style file.
    """
    CONFIG_NAME: str = 'config_layout_style.yaml'

    # region Class Methods
    @classmethod
    def _default_config_object(cls) -> dict:
        """:return: Default config dict."""
        return StyleSettings().__dict__

    @classmethod
    def read_config(cls) -> StyleSettings:
        """:return: File-manager config file."""
        path = get_yaml_file_path(filename=cls.CONFIG_NAME)
        if not os.path.exists(path):
            # Construct config dict
            default_dict: dict = cls._default_config_object()
            write_yaml(
                filename=cls.CONFIG_NAME,
                packable=default_dict,
                make_file=True,
            )
        return StyleSettings(**read_yaml(filename=cls.CONFIG_NAME))
    # endregion
