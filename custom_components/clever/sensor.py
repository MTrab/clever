"""Clever sensor definition."""
from __future__ import annotations
import logging

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .coordinator import CleverCoordinator

from .const import DOMAIN, STATE_UNIT_OF_MEASUREMENT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add sensor entry."""
    sensor_entity = [CleverSensor(hass, entry)]
    async_add_entities(sensor_entity)


class CleverSensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, dict[str, Any]]]], SensorEntity
):
    """Defines a Clever sensor entity."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor entity."""
        super().__init__(hass.data[DOMAIN][entry.entry_id]["coordinator"])
        self._hass = hass
        self._coordinator: CleverCoordinator = hass.data[DOMAIN][entry.entry_id][
            "coordinator"
        ]
        self._entry = entry
        self._attr_name = entry.data[CONF_ADDRESS]
        self._attr_native_value = self._coordinator.clever.chargepoint_available
        self._attr_native_unit_of_measurement = STATE_UNIT_OF_MEASUREMENT
        self._attr_unique_id = self._coordinator.clever.uuid
        self._attr_icon = "mdi:ev-station"
        self._attr_attribution = "Source: Clever Ladekort, https://ladekort.clever.dk"
        self._attr_extra_state_attributes = {
            "location": self._coordinator.clever.name,
            "address": f"{self._coordinator.clever.address['address']}, "
            f"{self._coordinator.clever.address['postalCode']} "
            f"{self._coordinator.clever.address['city']}, "
            f"{self._coordinator.clever.address['countryCode']}",
            "directions": self._coordinator.clever.directions,
            "coordinates": self._coordinator.clever.coordinates,
            "available_sockets": self._coordinator.clever.chargepoint_available_per_socket_type,
            "occupied_sockets": self._coordinator.clever.chargepoint_occupied_per_socket_type,
            "total_sockets": self._coordinator.clever.chargepoint_total_per_socket_type,
        }

    async def async_added_to_hass(self) -> None:
        """Register entity for updates from API."""
        await super().async_added_to_hass()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data."""
        _LOGGER.debug("Updating states for '%s'", self._entry.data[CONF_ADDRESS])
        self._attr_native_value = self._coordinator.clever.chargepoint_available
        self._attr_extra_state_attributes = {
            "location": self._coordinator.clever.name,
            "address": f"{self._coordinator.clever.address['address']}, "
            f"{self._coordinator.clever.address['postalCode']} "
            f"{self._coordinator.clever.address['city']}, "
            f"{self._coordinator.clever.address['countryCode']}",
            "directions": self._coordinator.clever.directions,
            "coordinates": self._coordinator.clever.coordinates,
            "available_sockets": self._coordinator.clever.chargepoint_available_per_socket_type,
            "occupied_sockets": self._coordinator.clever.chargepoint_occupied_per_socket_type,
            "total_sockets": self._coordinator.clever.chargepoint_total_per_socket_type,
        }

        self.async_write_ha_state()
