import logging
import asyncio
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, OID_BATTERY_TEST_TIME, OID_CONF_CAPACITY_LIMIT, OID_CONF_TIME_LIMIT, OID_CONF_TEMP_LIMIT, OID_CONF_LOAD_LIMIT, OID_CONTROL_OFF_DELAY, OID_CONTROL_ON_DELAY
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
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_CONF_CAPACITY_LIMIT, "shutdown_capacity_limit", 0, 100, PERCENTAGE, "mdi:battery-arrow-down", EntityCategory.CONFIG),
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_CONF_TIME_LIMIT, "shutdown_runtime_limit", 0, 120, UnitOfTime.MINUTES, "mdi:timer-off-outline", EntityCategory.CONFIG),
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_CONF_TEMP_LIMIT, "over_temperature_limit", 30, 100, UnitOfTemperature.CELSIUS, "mdi:thermometer-alert", EntityCategory.CONFIG),
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_CONF_LOAD_LIMIT, "high_load_limit", 50, 110, PERCENTAGE, "mdi:gauge-full", EntityCategory.CONFIG),
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_CONTROL_OFF_DELAY, "control_off_delay", 0, 32767, UnitOfTime.SECONDS, "mdi:power-sleep", None),
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_CONTROL_ON_DELAY, "control_on_delay", 0, 9999, UnitOfTime.MINUTES, "mdi:timer-sand", None),
            IpponConfigNumber(coordinator, hass, host, port, user, key, OID_BATTERY_TEST_TIME, "battery_test_time", 1, 9999, UnitOfTime.MINUTES, "mdi:timer-sync", EntityCategory.DIAGNOSTIC)
        ])

class IpponConfigNumber(NumberEntity):
    def __init__(self, coordinator, hass_obj, host, port, user, key, oid, trans_key, min_val, max_val, unit, icon, category):
        self.coordinator = coordinator
        self.hass_obj = hass_obj
        self.host = host
        self.port = port
        self.user = user
        self.key = key
        self.oid = oid
        
        self._attr_has_entity_name = True
        self._attr_translation_key = trans_key
        self._attr_unique_id = f"ippon_snmp_{host}_{trans_key}"
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_mode = NumberMode.BOX
        self._attr_entity_category = category
        self._attr_device_info = {"identifiers": {(DOMAIN, host)}}

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        val = self.coordinator.data.get(self.oid)
        if val and val != "-1":
            try:
                float_val = float(val)
                if self.oid == OID_CONF_TEMP_LIMIT: 
                    return float_val / 10.0
                if self.oid in [OID_CONTROL_ON_DELAY, OID_BATTERY_TEST_TIME]:
                    return round(float_val / 60.0)
                return float_val
            except ValueError: return None
        return None

    async def async_set_native_value(self, value: float) -> None:
        send_val = int(value)
        if self.oid == OID_CONF_TEMP_LIMIT: 
            send_val = int(value * 10)
        elif self.oid in [OID_CONTROL_ON_DELAY, OID_BATTERY_TEST_TIME]:
            send_val = int(value * 60)
            
        if await async_set_snmp_data(self.hass_obj, self.host, self.port, self.user, self.key, self.oid, send_val):
            await self.coordinator.async_request_refresh()
