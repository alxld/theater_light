"""Platform for light integration"""
from __future__ import annotations
import sys
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

sys.path.append("custom_components/new_light")
from new_light import NewLight

# light_entity = "light.theater_group"
dartboard_entity = "light.dart_board"
arcade_entity = "light.arcade"
outside_near_group = "light.outside_near_group"
# switch_action = "zigbee2mqtt/Theater Switch/action"
# motion_sensor_action = "zigbee2mqtt/Theater Motion Sensor"
aqara_action = "zigbee2mqtt/AqaraTest/action"
# brightness_step = 43
# motion_sensor_brightness = 192
# has_harmony = True
# has_motion_sensor = True
# has_switch = True
has_aqara = True


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

        self._dartboard = dartboard_entity
        self._arcade = arcade_entity
        self.entities["light.theater_group"] = None
        self.switch = "Theater Switch"
        self.motion_sensors.append("Theater Motion Sensor")
        self.motion_disable_entities.append("remote.theater_harmony_hub")
        self.turn_off_other_lights = True

        self.other_light_trackers["light.harmony_button_1"] = 175
        self.other_light_trackers["light.harmony_button_2"] = 100
        self.other_light_trackers["light.harmony_button_3"] = 50
        self.other_light_trackers["light.harmony_button_4"] = 0
