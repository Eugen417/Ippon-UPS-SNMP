from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, OIDS, CONF_AUTH_PROTOCOL

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    from pysnmp.hlapi.asyncio import UsmUserData, usmHMACMD5AuthProtocol, usmNoAuthProtocol

    auth_proto = usmHMACMD5AuthProtocol if entry.data.get(CONF_AUTH_PROTOCOL) == "hmac-md5" else usmNoAuthProtocol
    
    user_data = UsmUserData(
        entry.data[CONF_USERNAME],
        authKey=entry.data.get("auth_key"),
        authProtocol=auth_proto
    )

    coordinator = IpponSnmpCoordinator(hass, entry.data[CONF_HOST], entry.data[CONF_PORT], user_data)
    await coordinator.async_config_entry_first_refresh()
    
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

class IpponSnmpCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, port, user_data):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=30))
        self.host = host
        self.port = port
        self.user_data = user_data

    async def _async_update_data(self):
        from pysnmp.hlapi.asyncio import SnmpEngine, getCmd, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

        try:
            engine = SnmpEngine()
            var_binds_req = [ObjectType(ObjectIdentity(oid)) for oid in OIDS.values()]
            
            res = await getCmd(
                engine,
                self.user_data,
                UdpTransportTarget((self.host, self.port), timeout=5, retries=1),
                ContextData(),
                *var_binds_req
            )
            
            error_indication, error_status, error_index, var_binds = res
            
            if error_indication:
                raise UpdateFailed(f"SNMP Error: {error_indication}")
            
            #     {OID: Value}
            return {str(v[0]).lstrip('.'): str(v[1]) for v in var_binds}
            
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(err)
