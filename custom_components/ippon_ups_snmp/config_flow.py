from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME
from .const import DOMAIN, CONF_AUTH_PROTOCOL

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
                vol.Required(CONF_USERNAME,): str,
                vol.Optional("auth_key",): str,
                vol.Required(CONF_AUTH_PROTOCOL, default="hmac-md5"): vol.In(["hmac-md5", "none"]),
            })
        )