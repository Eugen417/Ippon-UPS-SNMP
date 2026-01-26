import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from pysnmp.hlapi.asyncio import SnmpEngine

from .const import DOMAIN, SENSORS, MAPS, CONF_OID, CONF_NAME, CONF_UNIT, CONF_DIVISOR, CONF_MAP
from .snmp_helper import get_snmp_data_map

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    # Используем executor для создания движка, если это блокирующая операция в старых версиях
    if "engine" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["engine"] = await hass.async_add_executor_job(SnmpEngine)
    
    engine = hass.data[DOMAIN]["engine"]

    async def async_update_data():
        oids = {s_id: info[CONF_OID] for s_id, info in SENSORS.items()}
        return await get_snmp_data_map(engine, host, port, user, key, oids)

    coordinator = DataUpdateCoordinator(
        hass, _LOGGER, name=f"ippon_snmp_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_refresh()
    async_add_entities([IpponSnmpSensor(coordinator, host, s_id) for s_id in SENSORS])

class IpponSnmpSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, host, sensor_id):
        super().__init__(coordinator)
        self._config = SENSORS[sensor_id]
        self._attr_name = f"IPPON {self._config[CONF_NAME]}"
        self._attr_unique_id = f"ippon_snmp_{host}_{sensor_id}"
        self._attr_native_unit_of_measurement = self._config.get(CONF_UNIT)
        
        if self._attr_native_unit_of_measurement:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, host)},
            "name": f"IPPON UPS {host}",
            "manufacturer": "Ippon",
        }

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        
        raw_val = self.coordinator.data.get(self._config[CONF_OID])
        if raw_val is None:
            return None
            
        try:
            str_val = str(raw_val).strip()
            # Маппинг состояний (Норма, Батарея и т.д.)
            if self._config[CONF_MAP]:
                return MAPS[self._config[CONF_MAP]].get(int(str_val), f"Stat {str_val}")
            
            # Числовые значения с делителем
            return round(float(str_val) / self._config[CONF_DIVISOR], 1)
        except (ValueError, TypeError):
            return str(raw_val)
