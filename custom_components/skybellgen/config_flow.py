"""Config flow for SkyBell Gen integration."""

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

from .const import CONF_USE_LOCAL_SERVER, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Calls to the communications driver should be serialized
PARALLEL_UPDATES = 1


class SkybellFlowHandler(ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for SkyBell."""

    VERSION = 1
    MINOR_VERSION = 0

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle a reauthorization flow request."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle user's reauth credentials."""
        errors = {}
        entry = self._get_reauth_entry()
        reauth_email = entry.data.get(CONF_EMAIL, "").lower()
        if user_input:
            password = user_input[CONF_PASSWORD]
            _, error = await self._async_validate_user(
                email=reauth_email, password=password, auto_login=True
            )
            if error is None:
                entry = self._get_reauth_entry()
                path = self.hass.config.path(f"./skybellgen_{entry.unique_id}.pickle")
                if os.path.exists(path):
                    os.remove(path)  # pragma: no cover
                return self.async_update_reload_and_abort(
                    entry, data_updates=user_input
                )

            errors["base"] = error
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            description_placeholders={CONF_EMAIL: reauth_email},
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        email = entry.data.get(CONF_EMAIL, "").lower()
        data = {**entry.data}
        if user_input:
            password = user_input[CONF_PASSWORD]

            self._async_abort_entries_match({CONF_EMAIL: email})
            user_id, error = await self._async_validate_user(
                email=email, password=password
            )
            if error is None:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_mismatch(reason="wrong_account")
                entry = self._get_reconfigure_entry()
                path = self.hass.config.path(f"./skybellgen_{entry.unique_id}.pickle")
                if os.path.exists(path):
                    os.remove(path)  # pragma: no cover
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=user_input,
                )
            errors["base"] = error

        # Show the form
        user_input = user_input or {}
        return self.async_show_form(
            step_id="reconfigure",
            description_placeholders={CONF_EMAIL: email},
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(
                        CONF_USE_LOCAL_SERVER,
                        default=data.get(CONF_USE_LOCAL_SERVER, False),
                    ): bool,
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
            use_local_server = user_input[CONF_USE_LOCAL_SERVER]

            self._async_abort_entries_match({CONF_EMAIL: email})
            user_id, error = await self._async_validate_user(
                email=email, password=password
            )
            if error is None:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=email,
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_USE_LOCAL_SERVER: use_local_server,
                    },
                )
            errors["base"] = error

        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL)): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(
                        CONF_USE_LOCAL_SERVER,
                        default=user_input.get(CONF_USE_LOCAL_SERVER, False),
                    ): bool,
                }
            ),
            errors=errors,
        )

    async def _async_validate_user(
        self, email: str, password: str, auto_login: bool = False
    ) -> tuple:
        """Validate login credentials for user flow."""
        user_id = None
        msg = None
        try:
            skybell = Skybell(
                username=email,
                password=password,
                disable_cache=True,
                get_devices=False,
                auto_login=auto_login,
                session=async_get_clientsession(self.hass),
            )
            await skybell.async_initialize()
            user_id = skybell.user_id
        except SkybellAuthenticationException:
            msg = "invalid_auth"
        except SkybellException:
            msg = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            msg = "unknown"
        del skybell
        return user_id, msg
