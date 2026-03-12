import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, PERCENTAGE,
    UnitOfElectricPotential, UnitOfTemperature, UnitOfFrequency, 
    UnitOfElectricCurrent, UnitOfPower, UnitOfApparentPower
)
from pysnmp.hlapi.asyncio import SnmpEngine

from .const import (
    DOMAIN, SENSORS, MAPS, CONF_OID, CONF_UNIT, CONF_DIVISOR, CONF_MAP, CONF_ENABLED, CONF_CATEGORY,
    OID_MANUFACTURER, OID_MODEL, OID_FW_VERSION, OID_DESCRIPTION, OID_NMC_VERSION, OID_MAC_ADDRESS,
    OID_BUZZER, OID_BATTERY_TEST_CMD, OID_BATTERY_TEST_TIME, OID_CONF_CAPACITY_LIMIT, OID_CONF_TIME_LIMIT, OID_CONF_TEMP_LIMIT, OID_CONF_LOAD_LIMIT,
    OID_CONTROL_ACTION, OID_CONTROL_OFF_DELAY, OID_CONTROL_ON_DELAY
)
from .snmp_helper import get_snmp_data_map

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, 161)
    user = entry.data[CONF_USERNAME]
    key = entry.data[CONF_PASSWORD]
    
    if DOMAIN not in hass.data: hass.data[DOMAIN] = {}
    
    engine = hass.data[DOMAIN].get("engine")
    if not engine:
        engine = await hass.async_add_executor_job(SnmpEngine)
        hass.data[DOMAIN]["engine"] = engine

    async def async_update_data():
        oids = {s_id: info[CONF_OID] for s_id, info in SENSORS.items()}
        oids["_dev_man"] = OID_MANUFACTURER
        oids["_dev_mod"] = OID_MODEL
        oids["_dev_fw"] = OID_FW_VERSION
        oids["_dev_desc"] = OID_DESCRIPTION
        oids["_dev_nmc"] = OID_NMC_VERSION
        oids["_dev_mac"] = OID_MAC_ADDRESS
        
        oids["_dev_buz"] = OID_BUZZER
        oids[OID_BATTERY_TEST_CMD] = OID_BATTERY_TEST_CMD
        oids[OID_BATTERY_TEST_TIME] = OID_BATTERY_TEST_TIME
        
        oids[OID_CONF_CAPACITY_LIMIT] = OID_CONF_CAPACITY_LIMIT
        oids[OID_CONF_TIME_LIMIT] = OID_CONF_TIME_LIMIT
        oids[OID_CONF_TEMP_LIMIT] = OID_CONF_TEMP_LIMIT
        oids[OID_CONF_LOAD_LIMIT] = OID_CONF_LOAD_LIMIT
        
        oids[OID_CONTROL_ACTION] = OID_CONTROL_ACTION
        oids[OID_CONTROL_OFF_DELAY] = OID_CONTROL_OFF_DELAY
        oids[OID_CONTROL_ON_DELAY] = OID_CONTROL_ON_DELAY
        
        return await get_snmp_data_map(engine, host, port, user, key, oids)

    coordinator = DataUpdateCoordinator(
        hass, _LOGGER, name=f"ippon_snmp_{host}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    hass.data[DOMAIN][f"coordinator_{host}"] = coordinator
    await coordinator.async_refresh()
    async_add_entities([IpponSnmpSensor(coordinator, host, s_id) for s_id in SENSORS])

class IpponSnmpSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, host, sensor_id):
        super().__init__(coordinator)
        self.host = host
        self._sensor_id = sensor_id
        self._config = SENSORS[sensor_id]
        
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_id
        self._attr_unique_id = f"ippon_snmp_{host}_{sensor_id}"
        self._attr_native_unit_of_measurement = self._config.get(CONF_UNIT)
        self._attr_entity_registry_enabled_default = self._config.get(CONF_ENABLED, True)
        
        if CONF_CATEGORY in self._config:
            self._attr_entity_category = self._config[CONF_CATEGORY]
            
        if self._attr_native_unit_of_measurement:
            self._attr_state_class = SensorStateClass.MEASUREMENT
            unit = self._attr_native_unit_of_measurement
            if unit == UnitOfTemperature.CELSIUS: self._attr_device_class = SensorDeviceClass.TEMPERATURE
            elif unit == UnitOfElectricPotential.VOLT: self._attr_device_class = SensorDeviceClass.VOLTAGE
            elif unit == UnitOfElectricCurrent.AMPERE: self._attr_device_class = SensorDeviceClass.CURRENT
            elif unit == UnitOfPower.WATT: self._attr_device_class = SensorDeviceClass.POWER
            elif unit == UnitOfApparentPower.VOLT_AMPERE: self._attr_device_class = SensorDeviceClass.APPARENT_POWER
            elif unit == UnitOfFrequency.HERTZ: self._attr_device_class = SensorDeviceClass.FREQUENCY
            elif unit == PERCENTAGE:
                if "battery" in sensor_id or "charge" in sensor_id:
                    self._attr_device_class = SensorDeviceClass.BATTERY

    @property
    def device_info(self):
        data = self.coordinator.data or {}
        manufacturer = str(data.get("_dev_man") or "EPPC").strip()
        model = str(data.get("_dev_mod") or "ON-LINE").strip()
        ups_fw = str(data.get("_dev_fw") or "Unknown").strip()
        nmc_fw = str(data.get("_dev_nmc") or "Unknown").strip()
        
        description = str(data.get("_dev_desc") or "").strip()
        if description.startswith("0x"):
            try: description = bytes.fromhex(description[2:]).decode('utf-8')
            except Exception: pass
                
        model_display = f"{model} ({description})" if description and description.lower() != "none" else model
        mac_raw = str(data.get("_dev_mac") or "").strip()
        mac_address = None
        if mac_raw.startswith("0x"):
            mac_clean = mac_raw[2:]
            if len(mac_clean) == 12: mac_address = ":".join(mac_clean[i:i+2] for i in range(0, 12, 2)).upper()
        elif "-" in mac_raw: mac_address = mac_raw.replace("-", ":").upper()
            
        dev_info = {
            "identifiers": {(DOMAIN, self.host)},
            "name": f"{self.host} (IPPON {model})",
            "manufacturer": manufacturer,
            "model": model_display,
            "sw_version": ups_fw,
            "hw_version": f"NMC: {nmc_fw}"
        }
        if mac_address: dev_info["connections"] = {(CONNECTION_NETWORK_MAC, mac_address)}
        return dev_info

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        raw_val = self.coordinator.data.get(self._config[CONF_OID])
        if raw_val is None or str(raw_val).strip() == "" or str(raw_val) == "-1": return None
            
        str_val = str(raw_val).strip()

        if self._sensor_id in ["battery_status"]:
            sys_status = str(self.coordinator.data.get("1.3.6.1.4.1.935.10.1.1.2.1.0"))
            charge = 100
            try: charge = int(self.coordinator.data.get("1.3.6.1.4.1.935.10.1.1.3.4.0", 100))
            except Exception: pass

            if sys_status == "4" and charge < 100: return "charging"
            elif sys_status == "5": return "discharging"

        if self._config[CONF_MAP]:
            try: return MAPS[self._config[CONF_MAP]].get(int(str_val), f"Stat {str_val}")
            except ValueError: return str_val
            
        if self._config.get(CONF_DIVISOR, 1) > 1:
            try: return round(float(str_val) / self._config[CONF_DIVISOR], 1)
            except ValueError: return str_val

        try: return float(str_val) if '.' in str_val else int(str_val)
        except ValueError: return str_val