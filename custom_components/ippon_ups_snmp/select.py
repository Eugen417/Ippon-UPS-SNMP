import logging
import asyncio
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN, OID_CONTROL_ACTION, MAPS
from .snmp_helper import async_set_snmp_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]

    coordinator = None
    for _ in range(20):
        coordinator = hass.data[DOMAIN].get(f"coordinator_{host}")
        if coordinator: break
        await asyncio.sleep(0.5)

    if coordinator:
        async_add_entities([
            IpponActionSelect(coordinator, hass, host, port, user, key, OID_CONTROL_ACTION, "control_action", "mdi:power-settings", None)
        ])

class IpponActionSelect(SelectEntity):
    def __init__(self, coordinator, hass_obj, host, port, user, key, oid, trans_key, icon, category):
        self.coordinator = coordinator
        self.hass_obj = hass_obj
        self.host = host
        self.port = port
        self.user = user
        self.key = key
        self.oid = oid
        self.trans_key = trans_key
        
        self._attr_has_entity_name = True
        self._attr_translation_key = trans_key
        self._attr_unique_id = f"ippon_snmp_{host}_{trans_key}"
        self._attr_icon = icon
        self._attr_options = list(MAPS[trans_key].keys())
        self._attr_entity_category = category
        self._attr_device_info = {"identifiers": {(DOMAIN, host)}}

    @property
    def current_option(self):
        if not self.coordinator.data: return None
        raw_val = self.coordinator.data.get(self.oid, "4")
        for label, value in MAPS[self.trans_key].items():
            if str(value) == str(raw_val): return label
        return "none"

    async def async_select_option(self, option: str) -> None:
        cmd_value = MAPS[self.trans_key].get(option, 4)
        if await async_set_snmp_data(self.hass_obj, self.host, self.port, self.user, self.key, self.oid, cmd_value):
            await self.coordinator.async_request_refresh()
