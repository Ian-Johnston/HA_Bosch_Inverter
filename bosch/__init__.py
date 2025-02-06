"""Bosch BPT-S4 Inverter integration for Home Assistant."""
import logging
import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from .const import DOMAIN
from .bosch_api import BoschAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]  # Define sensor platform

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Bosch BPT-S4 integration from a config entry."""
    _LOGGER.info("Setting up Bosch BPT-S4 Inverter Integration")

    hass.data.setdefault(DOMAIN, {})

    # Get IP address from config entry
    ip_address = entry.data.get("ip_address")
    if not ip_address:
        _LOGGER.error("No IP address configured for Bosch BPT-S4")
        return False

    # Initialize API connection
    api = BoschAPI(hass, f"http://{ip_address}")
    hass.data[DOMAIN][entry.entry_id] = api

    # Register device in HA device registry
    device_registry = async_get_device_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="Bosch",
        model="BPT-S4",
        name="Bosch BPT-S4 Inverter",
        sw_version="1.0.0",
    )

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.info("Unloading Bosch BPT-S4 Integration")

    # Close API session if it exists
    if entry.entry_id in hass.data[DOMAIN]:
        api = hass.data[DOMAIN][entry.entry_id]
        await api.close()

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, Platform.SENSOR)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok