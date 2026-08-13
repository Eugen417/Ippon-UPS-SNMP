import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, OID_BATTERY_TEST_CMD
from .snmp_helper import async_set_snmp_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]

    async_add_entities([
        IpponTestButton(hass, host, port, user, key, "test_10sec", 2, "mdi:battery-sync"),
        IpponTestButton(hass, host, port, user, key, "test_until_low", 3, "mdi:battery-minus-outline"),
        IpponTestButton(hass, host, port, user, key, "test_by_time", 4, "mdi:timer-play-outline"),
        IpponTestButton(hass, host, port, user, key, "test_cancel", 5, "mdi:battery-off-outline"),
        IpponTestButton(hass, host, port, user, key, "clear_info", 6, "mdi:delete-restore")
    ])

class IpponTestButton(ButtonEntity):
    def __init__(self, hass_obj, host, port, user, key, trans_key, cmd_value, icon):
        self.hass_obj = hass_obj
        self.host = host
        self.port = port
        self.user = user
        self.key = key
        self.cmd_value = cmd_value
        
        self._attr_has_entity_name = True
        self._attr_translation_key = trans_key
        self._attr_unique_id = f"ippon_snmp_{host}_test_btn_{trans_key}"
        self._attr_icon = icon
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {"identifiers": {(DOMAIN, host)}}

    async def async_press(self) -> None:
        await async_set_snmp_data(self.hass_obj, self.host, self.port, self.user, self.key, OID_BATTERY_TEST_CMD, self.cmd_value)
