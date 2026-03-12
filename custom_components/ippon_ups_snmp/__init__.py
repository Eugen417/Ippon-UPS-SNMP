from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from pysnmp.hlapi.asyncio import SnmpEngine
from .const import DOMAIN, PLATFORMS

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    
    if "engine" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["engine"] = await hass.async_add_executor_job(SnmpEngine)
        
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN, None)
    return unload_ok