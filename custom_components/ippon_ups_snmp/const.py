from __future__ import annotations
from homeassistant.const import (
    PERCENTAGE, UnitOfElectricPotential, UnitOfTemperature, 
    UnitOfTime, UnitOfFrequency, UnitOfElectricCurrent,
    UnitOfPower, UnitOfApparentPower, Platform
)
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "ippon_ups_snmp"
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.BUTTON, Platform.NUMBER, Platform.SELECT]

CONF_OID = "oid"
CONF_UNIT = "unit"
CONF_DIVISOR = "divisor"
CONF_MAP = "map"
CONF_ENABLED = "enabled"
CONF_CATEGORY = "category"

OID_MANUFACTURER = "1.3.6.1.4.1.935.10.1.1.1.1.0"
OID_MODEL = "1.3.6.1.4.1.935.10.1.1.1.2.0"
OID_FW_VERSION = "1.3.6.1.4.1.935.10.1.1.1.3.0"
OID_DESCRIPTION = "1.3.6.1.4.1.935.10.1.1.1.5.0"
OID_NMC_VERSION = "1.3.6.1.4.1.935.10.1.1.1.6.0"
OID_MAC_ADDRESS = "1.3.6.1.2.1.2.2.1.6.2"
OID_BUZZER = "1.3.6.1.2.1.33.1.9.8.0"

OID_BATTERY_TEST_CMD = "1.3.6.1.4.1.935.10.1.1.7.1.0"
OID_BATTERY_TEST_TIME = "1.3.6.1.4.1.935.10.1.1.7.2.0"

OID_CONF_CAPACITY_LIMIT = "1.3.6.1.4.1.935.10.1.1.2.21.0"
OID_CONF_TIME_LIMIT = "1.3.6.1.4.1.935.10.1.1.2.22.0"
OID_CONF_TEMP_LIMIT = "1.3.6.1.4.1.935.10.1.1.2.12.0"
OID_CONF_LOAD_LIMIT = "1.3.6.1.4.1.935.10.1.1.2.11.0"
OID_CONTROL_OFF_DELAY = "1.3.6.1.4.1.935.10.1.1.8.1.0"
OID_CONTROL_ON_DELAY = "1.3.6.1.4.1.935.10.1.1.8.2.0"
OID_CONTROL_ACTION = "1.3.6.1.4.1.935.10.1.1.8.3.0"

MAPS = {
    "battery_status": {1: "unknown", 2: "normal", 3: "low", 4: "depleted"},
    "output_source": {1: "other", 2: "none", 3: "normal", 4: "bypass", 5: "battery", 6: "booster", 7: "reducer"},
    "system_status": {
        1: "power-on", 2: "stand-by", 3: "by-pass", 4: "line", 5: "battery",
        6: "battery-test", 7: "fault", 8: "converter", 9: "eco", 10: "shutdown",
        11: "on-booster", 12: "on-reducer", 13: "other"
    },
    "test_result": {1: "idle", 2: "processing", 3: "noFailure", 4: "failureOrWarning", 5: "notPossible", 6: "testCancel"},
    "abm_status": {1: "charge", 2: "float", 3: "rest", 4: "discharge", 5: "disable"},
    "control_action": { "turn_off": 1, "turn_on_cancel": 2, "sleep": 3, "none": 4 }
}

SENSORS = {
    "test_result": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.7.3.0", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "test_result", CONF_ENABLED: True, CONF_CATEGORY: EntityCategory.DIAGNOSTIC},
    "battery_status": {CONF_OID: "1.3.6.1.2.1.33.1.2.1.0", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "battery_status", CONF_ENABLED: True},
    "battery_charge": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.3.4.0", CONF_UNIT: PERCENTAGE, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: True},
    "battery_runtime": {CONF_OID: "1.3.6.1.2.1.33.1.2.3.0", CONF_UNIT: UnitOfTime.MINUTES, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: True},
    "battery_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.3.5.0", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: True},
    "battery_temperature": {CONF_OID: "1.3.6.1.2.1.33.1.2.7.0", CONF_UNIT: UnitOfTemperature.CELSIUS, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: True},
    "input_frequency": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.16.1.2.1", CONF_UNIT: UnitOfFrequency.HERTZ, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: True},
    "input_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.16.1.3.1", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: True},
    "output_frequency": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.2.1", CONF_UNIT: UnitOfFrequency.HERTZ, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: True},
    "output_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.3.1", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: True},
    "output_load": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.7.1", CONF_UNIT: PERCENTAGE, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: True},
    "system_status": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.1.0", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "system_status", CONF_ENABLED: True},
    "system_temperature": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.2.0", CONF_UNIT: UnitOfTemperature.CELSIUS, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: True},
    "output_source": {CONF_OID: "1.3.6.1.2.1.33.1.4.1.0", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "output_source", CONF_ENABLED: True},
    "alarms_present": {CONF_OID: "1.3.6.1.2.1.33.1.6.1.0", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: True},
    "seconds_on_battery": {CONF_OID: "1.3.6.1.2.1.33.1.2.2.0", CONF_UNIT: UnitOfTime.SECONDS, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: True},

    "battery_current": {CONF_OID: "1.3.6.1.2.1.33.1.2.6.0", CONF_UNIT: UnitOfElectricCurrent.AMPERE, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "input_current": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.16.1.4.1", CONF_UNIT: UnitOfElectricCurrent.AMPERE, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "input_watts": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.16.1.5.1", CONF_UNIT: UnitOfPower.WATT, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: False},
    "output_current": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.4.1", CONF_UNIT: UnitOfElectricCurrent.AMPERE, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "output_watts": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.5.1", CONF_UNIT: UnitOfPower.WATT, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: False},
    "output_va": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.18.1.6.1", CONF_UNIT: UnitOfApparentPower.VOLT_AMPERE, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: False},
    "bypass_frequency": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.20.1.2.1", CONF_UNIT: UnitOfFrequency.HERTZ, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "bypass_voltage": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.2.20.1.3.1", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "battery_voltage_negative": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.3.6.0", CONF_UNIT: UnitOfElectricPotential.VOLT, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "battery_abm_status": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.3.10.0", CONF_UNIT: None, CONF_DIVISOR: 1, CONF_MAP: "abm_status", CONF_ENABLED: False},
    "env_temperature": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.6.1.1.0", CONF_UNIT: UnitOfTemperature.CELSIUS, CONF_DIVISOR: 10, CONF_MAP: None, CONF_ENABLED: False},
    "env_humidity": {CONF_OID: "1.3.6.1.4.1.935.10.1.1.6.2.1.0", CONF_UNIT: PERCENTAGE, CONF_DIVISOR: 1, CONF_MAP: None, CONF_ENABLED: False}
}