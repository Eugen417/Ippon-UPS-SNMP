from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
)
from homeassistant.const import (
    PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature, UnitOfTime, UnitOfFrequency
)
from .const import DOMAIN, OIDS, BATTERY_STATUS_MAP, SYSTEM_STATUS_MAP, TEST_RESULT_MAP, OUTPUT_SOURCE_MAP
from .entity import IpponEntity

@dataclass(frozen=True, kw_only=True)
class IpponSensorDesc(SensorEntityDescription):
    scale: float = 1.0
    map_dict: dict | None = None

SENSOR_TYPES = [
    IpponSensorDesc(key="battery.status", name="Battery Status", map_dict=BATTERY_STATUS_MAP, device_class=SensorDeviceClass.ENUM, options=list(BATTERY_STATUS_MAP.values())),
    IpponSensorDesc(key="battery.runtime", name="Battery Runtime", native_unit_of_measurement=UnitOfTime.MINUTES, device_class=SensorDeviceClass.DURATION, state_class=SensorStateClass.MEASUREMENT),
    IpponSensorDesc(key="ups.source", name="Output Source", map_dict=OUTPUT_SOURCE_MAP, device_class=SensorDeviceClass.ENUM, options=list(OUTPUT_SOURCE_MAP.values())),
    IpponSensorDesc(key="battery.voltage", name="Battery Voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1),
    IpponSensorDesc(key="input.frequency", name="Input Frequency", native_unit_of_measurement=UnitOfFrequency.HERTZ, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, scale=0.1),
    IpponSensorDesc(key="input.voltage", name="Input Voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1),
    IpponSensorDesc(key="output.frequency", name="Output Frequency", native_unit_of_measurement=UnitOfFrequency.HERTZ, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, scale=0.1),
    IpponSensorDesc(key="output.voltage", name="Output Voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, scale=0.1),
    IpponSensorDesc(key="ups.status", name="System Status", map_dict=SYSTEM_STATUS_MAP, device_class=SensorDeviceClass.ENUM, options=list(SYSTEM_STATUS_MAP.values())),
    IpponSensorDesc(key="ups.temperature", name="System Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, scale=0.1),
    IpponSensorDesc(key="battery.temperature", name="Battery Temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT),
    IpponSensorDesc(key="battery.test_result", name="Battery Test Result", map_dict=TEST_RESULT_MAP, device_class=SensorDeviceClass.ENUM, options=list(TEST_RESULT_MAP.values())),
    IpponSensorDesc(key="battery.charge", name="Battery Charge", native_unit_of_measurement=PERCENTAGE, device_class=SensorDeviceClass.BATTERY, state_class=SensorStateClass.MEASUREMENT),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities(IpponSensor(coordinator, entry, desc) for desc in SENSOR_TYPES)

class IpponSensor(IpponEntity, SensorEntity):
    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        
        oid = OIDS.get(self.entity_description.key)
        raw = self.coordinator.data.get(oid)
        
        if raw is None or str(raw).lower() in ["none", ""]:
            return None
            
        try:
            if self.entity_description.map_dict:
                return self.entity_description.map_dict.get(int(raw), "unknown")
            
            val = float(raw)
            if self.entity_description.scale != 1.0:
                val = val * self.entity_description.scale
            
            return round(val, 1) if val % 1 != 0 else int(val)
        except (ValueError, TypeError):
            return raw