"""Configuration flow for Clever integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import CONN_CLASS_CLOUD_POLL, ConfigFlow
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from pyHASSClever import Clever
from pyHASSClever.exceptions import UnknownLocation

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ADDRESS): str,
    }
)

_LOGGER = logging.getLogger(__name__)


async def data_schema(hass: HomeAssistant) -> dict:
    """Generate the data_schema dynamically for use in a drop-down."""
    locs = []
    clever = await hass.async_add_executor_job(Clever)
    for location in clever.all_locations["clever"].items():
        locs.append(
            f"{location[1]['address']['address']}, {location[1]['address']['postalCode']} "
            f"{location[1]['address']['city']}, {location[1]['address']['countryCode']}"
        )
    for location in clever.all_locations["hubject"].items():
        locs.append(
            f"{location[1]['address']['address']}, {location[1]['address']['postalCode']} "
            f"{location[1]['address']['city']}, {location[1]['address']['countryCode']}"
        )

    locs.sort()

    schema = {
        vol.Required(CONF_ADDRESS): vol.In(locs),
    }

    return schema


async def validate_input(hass: HomeAssistant, data):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    clever = await hass.async_add_executor_job(Clever, data[CONF_ADDRESS])

    return {
        "title": f"{clever.address['address']}, {clever.address['postalCode']} "
        f"{clever.address['city']}, {clever.address['countryCode']}",
        "uuid": clever.uuid,
    }


class CleverEVConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Clever integration."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    def check_for_existing(self, data):
        """Check whether an existing entry is using the same settings."""
        return any(
            entry.data.get(CONF_ADDRESS) == data.get(CONF_ADDRESS)
            for entry in self._async_current_entries()
        )

    def __init__(self):
        """Initialize the config flow."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial Clever integration step."""
        self._errors = {}
        if user_input is not None:
            if self.check_for_existing(user_input):
                return self.async_abort(reason="already_exists")

            try:
                validated = await validate_input(self.hass, user_input)
            except UnknownLocation:
                _LOGGER.error("The location was not found")
                self._errors["base"] = "unknown_location"
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.error("Unexpected exception: %s", exc)
                self._errors["base"] = "unknown"

            if "base" not in self._errors:
                await self.async_set_unique_id(f"clever_{validated['uuid']}")

                return self.async_create_entry(
                    title=validated["title"],
                    data=user_input,
                    description=f"Clever chargepoint: '{validated['title']}'",
                )

        data_scheme = await data_schema(self.hass)
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_scheme), errors=self._errors
        )
