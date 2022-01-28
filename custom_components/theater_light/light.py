"""Platform for light integration"""
from __future__ import annotations
import logging, json
#from enum import Enum
#import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers import event
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_EFFECT,
    ATTR_EFFECT_LIST,
    ATTR_FLASH,
    ATTR_HS_COLOR,
    ATTR_MAX_MIREDS,
    ATTR_MIN_MIREDS,
    ATTR_TRANSITION,
    ATTR_WHITE_VALUE,
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    SUPPORT_EFFECT,
    SUPPORT_FLASH,
    SUPPORT_TRANSITION,
    SUPPORT_WHITE_VALUE,
    LightEntity
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_SUPPORTED_FEATURES,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_OFFSET,
    CONF_UNIQUE_ID,
    EVENT_HOMEASSISTANT_START,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from .right_light import RightLight

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

light_entity = "light.theater_group"
harmony_entity = "remote.theater_harmony_hub"
switch_action = "zigbee2mqtt/Theater Switch/action"
motion_sensor_action = "zigbee2mqtt/Theater Motion Sensor"
brightness_step = 43

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

    @callback
    async def switch_message_received(topic: str, payload: str, qos: int) -> None:
        """A new MQTT message has been received."""
        await ent.switch_message_received(topic, payload, qos)

    @callback
    async def motion_sensor_message_received(topic: str, payload: str, qos: int) -> None:
        """A new motion sensor MQTT message has been received"""
        await ent.motion_sensor_message_received(topic, json.loads(payload), qos)

    await hass.components.mqtt.async_subscribe( switch_action, switch_message_received )
    await hass.components.mqtt.async_subscribe( motion_sensor_action, motion_sensor_message_received )


class TheaterLight(LightEntity):
    """Theater Light."""

    def __init__(self) -> None:
        """Initialize Theater Light."""
        self._light = light_entity
        self._name = "Theater"
        #self._state = 'off'
        self._brightness = 0
        self._brightness_override = 0
        self._hs_color: Optional[Tuple[float, float]] = None
        self._color_temp: Optional[int] = None
        self._rgb_color: Optional[Tuple[int, int, int]] = None
        self._min_mireds: int = 154
        self._max_mireds: int = 500
        self._mode = "Off"
        self._is_on = False
        self._available = True
        self._occupancy = False
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, self._name, [])
        self._white_value: Optional[int] = None
        self._effect_list: Optional[List[str]] = None
        self._effect: Optional[str] = None
        self._supported_features: int = 0

        # Record whether a switch was used to turn on this light
        self.switched_on = False

        # Track if the Theater Harmony is on
        self.harmony_on = False

        # self.hass.states.async_set(f"light.{self._name}", "Initialized")
        _LOGGER.info("TheaterLight initialized")

    async def async_added_to_hass(self) -> None:
        """Instantiate RightLight"""
        self._rightlight = RightLight(self._light, self.hass)

#        #temp = self.hass.states.get(harmony_entity).new_state
#        #_LOGGER.error(f"Harmony state: {temp}")
        event.async_track_state_change_event(self.hass, harmony_entity, self.harmony_update)

        self.async_schedule_update_ha_state(force_refresh=True)

        # Not working.  Light starts up an sends None=>Off, Off=>Off, Off=>On, but not sure if that's always the case
        #event.async_track_state_change_event(self.hass, self._light, self.light_update)

    @callback
    async def harmony_update(self, this_event):
        """Track harmony updates"""
        ev = this_event.as_dict()
        ns = ev["data"]["new_state"].state
        if ns == "on":
            self.harmony_on = True
        else:
            self.harmony_on = False

    #@callback
    #async def light_update(self, this_event):
    #    """Get initial light state"""
    #    ev = this_event.as_dict()
    #    if self._state == None and ev["data"]["old_state"] != None:
    #        _LOGGER.error(f"Light update: {this_event}")

    def _updateState(self, comment = ""):
        pass
        #self.hass.states.async_set(f"light.{self._name}", self._is_on, {"brightness": self._brightness,
        #                                                                "brightness_override": self._brightness_override,
        #                                                                "switched_on": self.switched_on,
        #                                                                "harmony_on": self.harmony_on,
        #                                                                "occupancy": self._occupancy,
        #                                                                "mode": self._mode,
        #                                                                "comment": comment})
#        self.hass.states.async_set(f"light.{self._name}", self._state, {"brightness": self._brightness, "brightness_override": self._brightness_override, "switched_on": self.switched_on, "mode": self._mode, "comment": comment})

    @property
    def should_poll(self):
        """Will update state as needed"""
        return False

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._is_on
        #return self._state == "on"

    @property
    def device_info(self):
        prop = {
            "identifiers": {
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            "name": self._name,
            "manufacturer": "Aaron"
        }
        return prop

    @property
    def unique_id(self):
        """Return the unique id of the light."""
        return self.entity_id

    @property
    def available(self) -> bool:
        """Return whether the light group is available."""
        return self._available

    @property
    def brightness(self) -> Optional[int]:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def hs_color(self) -> Optional[Tuple[float, float]]:
        """Return the hue and saturation color value [float, float]."""
        return self._hs_color

    @property
    def color_temp(self) -> Optional[int]:
        """Return the CT color value in mireds."""
        return self._color_temp

    @property
    def min_mireds(self) -> int:
        """Return the coldest color_temp that this light group supports."""
        return self._min_mireds

    @property
    def max_mireds(self) -> int:
        """Return the warmest color_temp that this light group supports."""
        return self._max_mireds

    @property
    def white_value(self) -> Optional[int]:
        """Return the white value of this light group between 0..255."""
        return self._white_value

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        return self._rgb_color

    @property
    def color_temp(self) -> int | None:
        """Return the CT color value in mireds."""
        return self._attr_color_temp

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features

#    def capability_attributes(self):
#        """Return capability attributes."""
#        data = {}
#        supported_features = self.supported_features
#        supported_color_modes = self._light_internal_supported_color_modes
#
#        if COLOR_MODE_COLOR_TEMP in supported_color_modes:
#            data[ATTR_MIN_MIREDS] = self.min_mireds
#            data[ATTR_MAX_MIREDS] = self.max_mireds
#
#        if supported_features & SUPPORT_EFFECT:
#            data[ATTR_EFFECT_LIST] = self.effect_list
#
#        data[ATTR_SUPPORTED_COLOR_MODES] = sorted(supported_color_modes)
#
#        return data

    async def async_turn_on(self, **kwargs) -> None:
        """Instruct the light to turn on.
        You can skip the brightness part if your light does not support
        brightness control.
        """
        _LOGGER.error(f"THEATER_LIGHT ASYNC_TURN_ON: {kwargs}")
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._is_on = True
        self._mode = "On"

        rl = True
        data = {ATTR_ENTITY_ID: self._light}

        if ATTR_HS_COLOR in kwargs:
            rl = False
            data[ATTR_HS_COLOR] = kwargs[ATTR_HS_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            data[ATTR_BRIGHTNESS] = kwargs[ATTR_BRIGHTNESS]
        if ATTR_COLOR_TEMP in kwargs:
            rl = False
            data[ATTR_COLOR_TEMP] = kwargs[ATTR_COLOR_TEMP]
        if ATTR_WHITE_VALUE in kwargs:
            rl = False
            data[ATTR_WHITE_VALUE] = kwargs[ATTR_WHITE_VALUE]
        if ATTR_TRANSITION in kwargs:
            data[ATTR_TRANSITION] = kwargs[ATTR_TRANSITION]

        if rl:
            await self._rightlight.turn_on(brightness=self._brightness, brightness_override=self._brightness_override)
        else:
            await self._rightlight.disable()
            await self.hass.services.async_call("light", "turn_on", data, blocking=True, limit=2)

        self._updateState()

#        # await self.hass.components.mqtt.async_publish(self.hass, "zigbee2mqtt/Office/set", f"{{\"brightness\": {self._brightness}, \"state\": \"on\"}}")
#        await self.hass.services.async_call(
#            "light",
#            "turn_on",
#            {"entity_id": self._light, "brightness": self._brightness},
#        )
        self.async_schedule_update_ha_state(force_refresh=True)
        #self.async_write_ha_state()

    async def async_turn_on_mode(self, **kwargs: Any) -> None:
        self._mode = kwargs.get("mode", "Vivid")
        self._is_on = True
        self._brightness = 255
        #self._state = "on"
        await self._rightlight.turn_on(mode=self._mode)
        self._updateState()
        self.async_schedule_update_ha_state(force_refresh=True)
        #self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._brightness = 0
        self._brightness_override = 0
        self._is_on = False
        #self._state = "off"
        await self._rightlight.disable_and_turn_off()
        self._updateState()

#        # await self.hass.components.mqtt.async_publish(self.hass, "zigbee2mqtt/Office/set", "OFF"})
#        await self.hass.services.async_call(
#            "light", "turn_off", {"entity_id": self._light}
#        )
        self.async_schedule_update_ha_state(force_refresh=True)
        #self.async_write_ha_state()

    async def up_brightness(self) -> None:
        """Increase brightness by one step"""
        if self._brightness == None:
            self._brightness = brightness_step
        elif self._brightness > (255 - brightness_step):
            self._brightness = 255
            self._brightness_override = self._brightness_override + brightness_step
        else:
            self._brightness = self._brightness + brightness_step

        await self.async_turn_on(brightness=self._brightness)

    async def down_brightness(self) -> None:
        """Decrease brightness by one step"""
        if self._brightness == None:
            await self.async_turn_off()
        elif self._brightness_override > 0:
            self._brightness_override = 0
            await self.async_turn_on(brightness=self._brightness)
        elif self._brightness < brightness_step:
            await self.async_turn_off()
        else:
            self._brightness = self._brightness - brightness_step
            await self.async_turn_on(brightness=self._brightness)

    async def async_update(self):
        """Query light and determine the state."""
        _LOGGER.error("THEATER_LIGHT ASYNC_UPDATE")
        state = self.hass.states.get(self._light)

        self._is_on = (state.state == STATE_ON)
        self._available = (state.state != STATE_UNAVAILABLE)

        self._brightness = state.attributes.get(ATTR_BRIGHTNESS)

        self._hs_color = state.attributes.get(ATTR_HS_COLOR)

        self._white_value = state.attributes.get(ATTR_WHITE_VALUE)

        self._color_temp = state.attributes.get(ATTR_COLOR_TEMP, self._color_temp)
        self._min_mireds = state.attributes.get(ATTR_MIN_MIREDS, 154)
        self._max_mireds = state.attributes.get(ATTR_MAX_MIREDS, 500)

        self._effect_list = state.attributes.get(ATTR_EFFECT_LIST)
        self._effect = state.attributes.get(ATTR_EFFECT)

        self._supported_features = state.attributes.get(ATTR_SUPPORTED_FEATURES)
        # Bitwise-or the supported features with the color temp feature
        self._supported_features |= SUPPORT_COLOR_TEMP

#    def update(self) -> None:
#        """Fetch new state data for this light.
#        This is the only method that should fetch new data for Home Assistant.
#        """
#        # self._light.update()
#        # self._state = self._light.is_on()
#        # self._brightness = self._light.brightness
#        self._updateState()

    async def switch_message_received(self, topic: str, payload: str, qos: int) -> None:
        """A new MQTT message has been received."""
        #self.hass.states.async_set(f"light.{self._name}", f"ENT: {payload}")
        self._updateState(f"{payload}")

        self.switched_on = True
        if payload == "on-press":
            await self.async_turn_on()
        elif payload == "on-hold":
            await self.async_turn_on_mode(mode="Vivid")
        elif payload == "off-press":
            self.switched_on = False
            await self.async_turn_off()
        elif payload == "up-press":
            await self.up_brightness()
        elif payload == "up-hold":
            await self.async_turn_on_mode(mode="Bright")
        elif payload == "down-press":
            await self.down_brightness()
        else:
            self._updateState(f"Fail: {payload}")

    async def motion_sensor_message_received(self, topic: str, payload: str, qos: int) -> None:
        """A new MQTT message has been received."""
        self._occupancy = True if payload["occupancy"] == "True" else False
        self._updateState()

        # Disable motion sensor tracking if the lights are switched on or the harmony is on
        if self.switched_on or self.harmony_on:
            return

        if self._occupancy:
            await self.async_turn_on()
        else:
            await self.async_turn_off()