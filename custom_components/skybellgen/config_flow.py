"""Config flow for Skybell Gen integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
import os
from typing import Any

from aioskybellgen import Skybell
from aioskybellgen.exceptions import SkybellAuthenticationException, SkybellException
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SkybellFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Skybell."""

    reauth_email: str

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle a reauthorization flow request."""
        self.reauth_email = entry_data[CONF_EMAIL]
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle user's reauth credentials."""
        errors = {}
        if user_input:
            password = user_input[CONF_PASSWORD]
            _, error = await self._async_validate_reauth_input(
                email=self.reauth_email, password=password
            )
            if error is None:
                entry = self._get_reauth_entry()
                path = self.hass.config.path(f"./skybellgen_{entry.unique_id}.pickle")
                if os.path.exists(path):
                    os.remove(path)
                return self.async_update_reload_and_abort(
                    entry, data_updates=user_input
                )

            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            description_placeholders={CONF_EMAIL: self.reauth_email},
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        if user_input:
            email = user_input[CONF_EMAIL].lower()
            password = user_input[CONF_PASSWORD]

            self._async_abort_entries_match({CONF_EMAIL: email})
            user_id, error = await self._async_validate_user_input(
                email=email, password=password
            )
            if error is None:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_mismatch(reason="wrong_account")
                entry = self._get_reconfigure_entry()
                path = self.hass.config.path(f"./skybellgen_{entry.unique_id}.pickle")
                if os.path.exists(path):
                    os.remove(path)
                return self.async_update_reload_and_abort(
                    entry, data_updates=user_input
                )
            errors["base"] = error

        # Show the form
        user_input = user_input or {}
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL)): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL].lower()
            password = user_input[CONF_PASSWORD]

            self._async_abort_entries_match({CONF_EMAIL: email})
            user_id, error = await self._async_validate_user_input(
                email=email, password=password
            )
            if error is None:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=email,
                    data={CONF_EMAIL: email, CONF_PASSWORD: password},
                )
            errors["base"] = error

        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL)): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def _async_validate_reauth_input(self, email: str, password: str) -> tuple:
        """Validate login credentials for reauthorization flow."""
        try:
            skybell = Skybell(
                username=email,
                password=password,
                disable_cache=True,
                get_devices=False,
                auto_login=True,
                session=async_get_clientsession(self.hass),
            )
            await skybell.async_initialize()
        except SkybellAuthenticationException:
            return None, "invalid_auth"
        except SkybellException:
            return None, "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            return None, "unknown"
        return skybell.user_id, None

    async def _async_validate_user_input(self, email: str, password: str) -> tuple:
        """Validate login credentials for user flow."""
        try:
            skybell = Skybell(
                username=email,
                password=password,
                disable_cache=True,
                get_devices=False,
                auto_login=False,
                session=async_get_clientsession(self.hass),
            )
            await skybell.async_initialize()
        except SkybellAuthenticationException:
            return None, "invalid_auth"
        except SkybellException:
            return None, "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            return None, "unknown"
        return skybell.user_id, None
