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
harmony_entity = "remote.theater_harmony_hub"
harmony_button_1 = "light.harmony_button_1"
harmony_button_2 = "light.harmony_button_2"
harmony_button_3 = "light.harmony_button_3"
harmony_button_4 = "light.harmony_button_4"
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
        self._dartboard = dartboard_entity
        self._arcade = arcade_entity
        self.entities["light.theater_gorup"] = None
        self.switch = "Theater Switch"
        self.has_json = True
        self.motion_sensors.append("Theater Motion Sensor")
        self._name = "Theater"
        # self.has_harmony = True
        self.harmony_entity = "remote.theater_harmony_hub"

        self.other_light_trackers["light.harmony_button_1"] = 175
        self.other_light_trackers["light.harmony_button_2"] = 100
        self.other_light_trackers["light.harmony_button_3"] = 50
        self.other_light_trackers["light.harmony_button_4"] = 0

    async def async_added_to_hass(self) -> None:
        # Track harmony button template lights
        event.async_track_state_change_event(
            self.hass, harmony_button_1, self.harmony_button_1_update
        )
        event.async_track_state_change_event(
            self.hass, harmony_button_2, self.harmony_button_2_update
        )
        event.async_track_state_change_event(
            self.hass, harmony_button_3, self.harmony_button_3_update
        )
        event.async_track_state_change_event(
            self.hass, harmony_button_4, self.harmony_button_4_update
        )


#    @callback
#    async def harmony_button_1_update(self, this_event):
#        """Handle Harmony button 1 press"""
#        ev = this_event.as_dict()
#        ns = ev["data"]["new_state"].state
#        if ns == "on":
#            await self.async_turn_on(brightness=175)
#            await self.hass.services.async_call(
#                "light", "turn_off", {"entity_id": harmony_button_1}
#            )

#    @callback
#    async def harmony_button_2_update(self, this_event):
#        """Handle Harmony button 2 press"""
#        ev = this_event.as_dict()
#        ns = ev["data"]["new_state"].state
#        if ns == "on":
#            await self.async_turn_on(brightness=100)
#            await self.hass.services.async_call(
#                "light", "turn_off", {"entity_id": harmony_button_2}
#            )

#    @callback
#    async def harmony_button_3_update(self, this_event):
#        """Handle Harmony button 3 press"""
#        ev = this_event.as_dict()
#        ns = ev["data"]["new_state"].state
#        if ns == "on":
#            await self.async_turn_on(brightness=50)
#            await self.hass.services.async_call(
#                "light", "turn_off", {"entity_id": harmony_button_3}
#            )

#    @callback
#    async def harmony_button_4_update(self, this_event):
#        """Handle Harmony button 4 press"""
#        ev = this_event.as_dict()
#        ns = ev["data"]["new_state"].state
#        if ns == "on":
#            await self.async_turn_off()
#
#            await self.hass.services.async_call(
#                "light", "turn_off", {"entity_id": outside_near_group}
#            )
#            await self.hass.services.async_call(
#                "light", "turn_off", {"entity_id": harmony_button_4}
#            )

#    async def switch_message_received(self, topic: str, payload: str, qos: int) -> None:
#        """A new MQTT message has been received."""
#        # self.hass.states.async_set(f"light.{self._name}", f"ENT: {payload}")
#        self._updateState(f"{payload}")
#
#        self.switched_on = True
#        if payload == "on-press":
#            self._brightness_override = 0
#            await self.async_turn_on(source="Switch", brightness=255)
#        elif payload == "on-hold":
#            await self.async_turn_on_mode(mode="Vivid", source="Switch")
#        elif payload == "off-press":
#            self.switched_on = False
#            await self.async_turn_off(source="Switch")
#        elif payload == "up-press":
#            await self.up_brightness(source="Switch")
#        elif payload == "up-hold":
#            await self.async_turn_on_mode(mode="Bright", source="Switch")
#        elif payload == "down-press":
#            await self.down_brightness(source="Switch")
#        else:
#            self._updateState(f"Fail: {payload}")

#    async def aqara_message_received(self, topic: str, payload: str, qos: int) -> None:
#        """A new MQTT aqara message has been received."""
#
#        # _LOGGER.error(f"{self._name} aqara action: Topic: {topic}, Payload: {payload}")
#        if payload == "flip90":
#            state = self.hass.states.get(self._dartboard).state
#            # _LOGGER.error(f"{self._name} aqara action: state: {state}")
#
#            if state == "on":
#                await self._rightlight_db.disable_and_turn_off()
#                await self._rightlight_ar.disable_and_turn_off()
#            else:
#                await self._rightlight_db.turn_on(mode="Vivid")
#                await self._rightlight_ar.turn_on(mode="Vivid")
#        elif payload == "flip180":
#            pass
#        elif payload == "rotate_right":
#            pass
#        elif payload == "rotate_left":
#            pass
#        elif payload == "tap":
#            pass
