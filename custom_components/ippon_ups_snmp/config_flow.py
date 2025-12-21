from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME

from .const import DOMAIN, CONF_AUTH_PROTOCOL

class IpponFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Обработчик настройки для Ippon UPS SNMP."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Первый шаг при добавлении интеграции через интерфейс."""
        errors = {}

        if user_input is not None:
            # Создаем запись в Home Assistant с введенными данными
            return self.async_create_entry(
                title=f"UPS {user_input[CONF_HOST]}", 
                data=user_input
            )

        # Описание полей формы, которые видит пользователь
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=161): int,
                    # Вставьте ваш логин в default ниже:
                    vol.Required(CONF_USERNAME, default="Eugen417"): str,
                    # Вставьте ваш пароль в default ниже:
                    vol.Optional("auth_key", default="HomeAs190"): str,
                    vol.Required(CONF_AUTH_PROTOCOL, default="hmac-md5"): vol.In(
                        ["hmac-md5", "none"]
                    ),
                }
            ),
            errors=errors,
        )
