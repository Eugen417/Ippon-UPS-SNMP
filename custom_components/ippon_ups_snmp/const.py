from __future__ import annotations
from homeassistant.const import (
    PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature, 
    UnitOfTime, UnitOfFrequency, Platform
)

DOMAIN = "ippon_ups_snmp"
PLATFORMS = [Platform.SENSOR]

# Ключи конфигурации
CONF_OID = "oid"
CONF_NAME = "name"
CONF_UNIT = "unit"
CONF_DIVISOR = "divisor"
CONF_MAP = "map"

# Словари статусов из вашего YAML
MAPS = {
    "battery_status": {1: "unknown", 2: "normal", 3: "low", 4: "depleted"},
    "output_source": {1: "other", 2: "none", 3: "normal", 4: "bypass", 5: "battery", 6: "booster", 7: "reducer"},
    "system_status": {
        1: "power-on", 2: "stand-by", 3: "by-pass", 4: "line", 5: "battery",
        6: "battery-test", 7: "fault", 8: "converter", 9: "eco", 10: "shutdown",
        11: "on-booster", 12: "on-reducer", 13: "other"
    },
    "test_result": {1: "idle", 2: "processing", 3: "noFailure", 4: "failureOrWarning", 5: "notPossible", 6: "testCancel"}
}

SENSORS = {
    "battery_status": {CONF_OID: "1.3.6.1.2.1.33.1.2.1.0", CONF_NAME: "Battery Status", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "battery_status"},
    "battery_runtime": {CONF_OID: "1.3.6.1.2.1.33.1.2.3.0", CONF_NAME: "Battery Runtime", CONF_UNIT: UnitOfTime.MINUTES, CONF_DIVISOR: 1, CONF_MAP: None},
    "output_source": {CONF_OID: "1.3.6.1.2.1.33.1.4.1.0", CONF_NAME: "Output Source", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "output_source"},
    "battery_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.3.5.0", CONF_NAME: "Battery Voltage", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None},
    "input_frequency": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.16.1.2.1", CONF_NAME: "Input Frequency", CONF_UNIT: UnitOfFrequency.HERTZ, CONF_DIVISOR: 10, CONF_MAP: None},
    "input_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.16.1.3.1", CONF_NAME: "Input Voltage", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None},
    "output_frequency": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.2.1", CONF_NAME: "Output Frequency", CONF_UNIT: UnitOfFrequency.HERTZ, CONF_DIVISOR: 10, CONF_MAP: None},
    "output_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.3.1", CONF_NAME: "Output Voltage", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None},
    "system_status": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.1.0", CONF_NAME: "System Status", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "system_status"},
    "system_temperature": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.2.0", CONF_NAME: "System Temperature", CONF_UNIT: UnitOfTemperature.CELSIUS, CONF_DIVISOR: 10, CONF_MAP: None},
    "battery_temperature": {CONF_OID: "1.3.6.1.2.1.33.1.2.7.0", CONF_NAME: "Battery Temperature", CONF_UNIT: UnitOfTemperature.CELSIUS, CONF_DIVISOR: 1, CONF_MAP: None},
    "test_result": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.7.3.0", CONF_NAME: "Battery Test Result", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "test_result"},
    "battery_charge": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.3.4.0", CONF_NAME: "Battery Charge", CONF_UNIT: PERCENTAGE, CONF_DIVISOR: 1, CONF_MAP: None},
}
