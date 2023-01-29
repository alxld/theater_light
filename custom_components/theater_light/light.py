"""Platform for light integration"""
from __future__ import annotations
import sys
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

sys.path.append("custom_components/new_light")
from new_light import NewLight


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the light platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    ent = TheaterLight()
    add_entities([ent])


class TheaterLight(NewLight):
    """Theater Light."""

    def __init__(self) -> None:
        """Initialize Theater Light."""
        super(TheaterLight, self).__init__(
            "Theater", domain=DOMAIN, debug=False, debug_rl=False
        )

        self._dartboard = "light.theater_dart_board"
        self._arcade = "light.theater_arcade"
        self.entities["light.theater_group"] = None
        self.switch = "Theater Switch"
        self.motion_sensors.append("Theater Motion Sensor")
        self.motion_disable_entities.append("remote.theater_harmony_hub")
        self.turn_off_other_lights = True

        self.other_light_trackers["light.harmony_button_1"] = 175
        self.other_light_trackers["light.harmony_button_2"] = 100
        self.other_light_trackers["light.harmony_button_3"] = 50
        self.other_light_trackers["light.harmony_button_4"] = 0
