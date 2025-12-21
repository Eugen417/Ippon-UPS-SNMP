from __future__ import annotations
from typing import Final

DOMAIN: Final = "ippon_ups_snmp"
CONF_AUTH_PROTOCOL: Final = "auth_protocol"

#  
BATTERY_STATUS_MAP: Final = {1: "unknown", 2: "normal", 3: "low", 4: "depleted"}
SYSTEM_STATUS_MAP: Final = {
    1: "power-on", 2: "stand-by", 3: "by-pass", 4: "line", 5: "battery",
    6: "battery-test", 7: "fault", 8: "converter", 9: "eco", 10: "shutdown",
    11: "on-booster", 12: "on-reducer", 13: "other"
}
OUTPUT_SOURCE_MAP: Final = {
    1: "other", 2: "none", 3: "normal", 4: "bypass", 5: "battery", 6: "booster", 7: "reducer"
}
TEST_RESULT_MAP: Final = {
    1: "idle", 2: "processing", 3: "noFailure", 4: "failureOrWarning", 
    5: "notPossible", 6: "testCancel"
}

#  OID
OIDS: Final = {
    "battery.status": "1.3.6.1.2.1.33.1.2.1.0",
    "battery.runtime": "1.3.6.1.2.1.33.1.2.3.0",
    "ups.source": "1.3.6.1.2.1.33.1.4.1.0",
    "battery.voltage": "1.3.6.1.4.1.935.10.1.1.3.5.0",
    "input.frequency": "1.3.6.1.4.1.935.10.1.1.2.16.1.2.1",
    "input.voltage": "1.3.6.1.4.1.935.10.1.1.2.16.1.3.1",
    "output.frequency": "1.3.6.1.4.1.935.10.1.1.2.18.1.2.1",
    "output.voltage": "1.3.6.1.4.1.935.10.1.1.2.18.1.3.1",
    "ups.status": "1.3.6.1.4.1.935.10.1.1.2.1.0",
    "ups.temperature": "1.3.6.1.4.1.935.10.1.1.2.2.0",
    "battery.temperature": "1.3.6.1.2.1.33.1.2.7.0",
    "battery.test_result": "1.3.6.1.4.1.935.10.1.1.7.3.0",
    "battery.charge": "1.3.6.1.4.1.935.10.1.1.3.4.0"
}