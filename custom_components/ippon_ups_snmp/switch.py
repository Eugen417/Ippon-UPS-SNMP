import logging
import asyncio
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, OID_BUZZER
from .snmp_helper import async_set_snmp_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]

    coordinator = None
    # Ждем инициализации координатора из sensor.py
    for _ in range(20):
        coordinator = hass.data[DOMAIN].get(f"coordinator_{host}")
        if coordinator: break
        await asyncio.sleep(0.5)

    if coordinator:
        async_add_entities([IpponBuzzerSwitch(coordinator, hass, host, port, user, key)])

class IpponBuzzerSwitch(SwitchEntity):
    def __init__(self, coordinator, hass_obj, host, port, user, key):
        self.coordinator = coordinator
        self.hass_obj = hass_obj
        self.host = host
        self.port = port
        self.user = user
        self.key = key
        
        self._attr_has_entity_name = True
        self._attr_translation_key = "buzzer"
        self._attr_unique_id = f"ippon_snmp_{host}_buzzer"
        self._attr_icon = "mdi:volume-high"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = {"identifiers": {(DOMAIN, host)}}

    @property
    def is_on(self):
        if not self.coordinator.data: return None
        val = self.coordinator.data.get(OID_BUZZER)
        return str(val) == "2"

    async def async_turn_on(self, **kwargs):
        success = await async_set_snmp_data(self.hass_obj, self.host, self.port, self.user, self.key, OID_BUZZER, 2)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        success = await async_set_snmp_data(self.hass_obj, self.host, self.port, self.user, self.key, OID_BUZZER, 1)
        if success:
            await self.coordinator.async_request_refresh()
