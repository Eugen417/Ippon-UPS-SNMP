import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, OID_BATTERY_TEST_CMD
from .snmp_helper import set_snmp_data

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]
    engine = hass.data[DOMAIN]["engine"]

    # Кнопки со всеми вариантами тестов (из MIB)
    async_add_entities([
        IpponTestButton(engine, host, port, user, key, "test_10sec", 2, "mdi:battery-sync"),
        IpponTestButton(engine, host, port, user, key, "test_until_low", 3, "mdi:battery-minus-outline"),
        IpponTestButton(engine, host, port, user, key, "test_by_time", 4, "mdi:timer-play-outline"),
        IpponTestButton(engine, host, port, user, key, "test_cancel", 5, "mdi:battery-off-outline"),
        IpponTestButton(engine, host, port, user, key, "clear_info", 6, "mdi:delete-restore")
    ])

class IpponTestButton(ButtonEntity):
    def __init__(self, engine, host, port, user, key, trans_key, cmd_value, icon):
        self.engine = engine
        self.host = host
        self.port = port
        self.user = user
        self.key = key
        self.cmd_value = cmd_value
        
        self._attr_has_entity_name = True
        self._attr_translation_key = trans_key
        self._attr_unique_id = f"ippon_snmp_{host}_test_btn_{trans_key}"
        self._attr_icon = icon
        # Кладем кнопки в Диагностику
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {"identifiers": {(DOMAIN, host)}}

    async def async_press(self) -> None:
        await set_snmp_data(self.engine, self.host, self.port, self.user, self.key, OID_BATTERY_TEST_CMD, self.cmd_value)