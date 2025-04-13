from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_RGB_COLOR,
    ATTR_BRIGHTNESS,
)
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_HOST
import aiohttp

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    async_add_entities([WortuhrRGBLight(config_entry.data[CONF_HOST], hass)])

class WortuhrRGBLight(LightEntity):
    def __init__(self, host, hass):
        self._host = host
        self._hass = hass
        self._is_on = False
        self._rgb = (255, 255, 255)
        self._brightness = 255
        self._attr_name = "Wortuhr RGB"
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._attr_unique_id = "wortuhr_rgb_light"
        self._attr_supported_features = 0

    @property
    def is_on(self):
        return self._is_on

    @property
    def rgb_color(self):
        return self._rgb

    @property
    def brightness(self):
        return self._brightness

    def _get_url(self):
        return f"{self._host}/color"

    def _scale_to_api(self, brightness_255):
        return round(brightness_255 / 255 * 100)

    def _scale_from_api(self, brightness_100):
        return round(brightness_100 / 100 * 255)

    async def async_turn_on(self, **kwargs):
        if ATTR_RGB_COLOR in kwargs:
            self._rgb = kwargs[ATTR_RGB_COLOR]
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = kwargs[ATTR_BRIGHTNESS]
        self._is_on = True
        r, g, b = self._rgb
        brightness_100 = self._scale_to_api(self._brightness)
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self._get_url(), json={
                    "red": r,
                    "green": g,
                    "blue": b,
                    "brightness": brightness_100
                })
            await self.async_update()
        except Exception as e:
            self._is_on = False
            raise e

    async def async_turn_off(self, **kwargs):
        r, g, b = self._rgb
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(self._get_url(), json={
                    "red": r,
                    "green": g,
                    "blue": b,
                    "brightness": 0
                })
            await self.async_update()
        except Exception as e:
            raise e
        self._is_on = False

    async def async_update(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._get_url()) as response:
                    data = await response.json()
                    r = data.get("red", 0)
                    g = data.get("green", 0)
                    b = data.get("blue", 0)
                    brightness_100 = data.get("brightness", 100)
                    self._rgb = (r, g, b)
                    self._is_on = brightness_100 > 0
                    if self._is_on:
                        self._brightness = self._scale_from_api(brightness_100)
        except Exception:
            self._is_on = False
