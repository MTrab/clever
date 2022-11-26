"""Clever chargepoints data update connector."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pyClever import Clever

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)


class CleverCoordinator(DataUpdateCoordinator[Optional[datetime]]):
    """Clever data update coordinator class."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the object."""
        DataUpdateCoordinator.__init__(
            self,
            hass,
            _LOGGER,
            name=f"'{entry.title}'",
            update_interval=SCAN_INTERVAL,
        )
        self.hass = hass
        self.entry = entry
        self.clever = None

    async def _async_update_data(self) -> None:
        """Update chargepoint data."""
        if isinstance(self.clever, type(None)):
            _LOGGER.debug("Initial data update for '%s'", self.entry.data[CONF_ADDRESS])
            self.clever = await self.hass.async_add_executor_job(
                Clever, self.entry.data[CONF_ADDRESS]
            )
        else:
            _LOGGER.debug("Updating data for '%s'", self.entry.data[CONF_ADDRESS])
            await self.hass.async_add_executor_job(self.clever.update)

        return True
