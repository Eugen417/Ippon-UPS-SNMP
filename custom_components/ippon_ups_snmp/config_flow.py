import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from pysnmp.hlapi.asyncio import SnmpEngine

from .const import DOMAIN
from .snmp_helper import get_snmp_data_map

# Тестовый OID для проверки связи (Battery Status)
TEST_OID = "1.3.6.1.2.1.33.1.2.1.0" 

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Проверка подключения к SNMP перед созданием записи."""
    # Создаем временный движок для проверки (или используем существующий, если есть)
    engine = SnmpEngine()
    
    test_map = {"test_check": TEST_OID}
    
    try:
        result = await get_snmp_data_map(
            engine,
            data[CONF_HOST],
            data[CONF_PORT],
            data[CONF_USERNAME],
            data[CONF_PASSWORD],
            test_map
        )
        # Если результат пустой или None, считаем, что связи нет
        if not result:
            raise CannotConnect
    except Exception:
        raise CannotConnect
    
    return {"title": f"UPS {data[CONF_HOST]}"}

class IpponFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=161): int,
                vol.Required(CONF_USERNAME, default="user"): str,
                vol.Required(CONF_PASSWORD, default="password"): str,
            }),
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
