import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN

class IpponFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"UPS {user_input[CONF_HOST]}", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=161): int,
                vol.Required(CONF_USERNAME, default="USERNAME"): str,
                vol.Required(CONF_PASSWORD, default="PASSWORD"): str,
            })
        )
