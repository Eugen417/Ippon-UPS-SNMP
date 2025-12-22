import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN, SENSORS, MAPS, CONF_OID, CONF_NAME, CONF_UNIT, CONF_DIVISOR, CONF_MAP
from pysnmp.hlapi.asyncio import SnmpEngine

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]
    
    engine = SnmpEngine()

    async def async_update_data():
        from .snmp_helper import get_snmp_data_map
        # ИСПРАВЛЕНО: Правильный обход словаря SENSORS
        oids_to_fetch = {s_id: info[CONF_OID] for s_id, info in SENSORS.items()}
        return await get_snmp_data_map(engine, host, port, user, key, oids_to_fetch)

    coordinator = DataUpdateCoordinator(
        hass, 
        _LOGGER, 
        name="ippon_snmp_coordinator",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Первый запуск для инициализации данных
    await coordinator.async_config_entry_first_refresh()

    entities = [IpponSnmpSensor(coordinator, host, s_id) for s_id in SENSORS]
    async_add_entities(entities)

class IpponSnmpSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, host, sensor_id):
        super().__init__(coordinator)
        info = SENSORS[sensor_id]
        self._sensor_id = sensor_id
        self._config = info
        self._attr_name = f"IPPON {info[CONF_NAME]}"
        self._attr_unique_id = f"ippon_{host}_{sensor_id}"
        self._attr_native_unit_of_measurement = info[CONF_UNIT]
        self._attr_state_class = SensorStateClass.MEASUREMENT if info[CONF_UNIT] else None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, host)}, 
            "name": f"IPPON UPS {host}",
            "manufacturer": "Ippon"
        }

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
            
        # Получаем значение по OID из данных координатора
        raw = self.coordinator.data.get(self._config[CONF_OID])
        if raw is None:
            return None
            
        try:
            val = int(raw)
            if self._config[CONF_MAP]:
                return MAPS[self._config[CONF_MAP]].get(val, "unknown")
            return round(val / self._config[CONF_DIVISOR], 1)
        except (ValueError, TypeError):
            return str(raw)
