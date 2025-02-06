import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN

class BoschConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bosch BPT-S4."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Step when user sets up Bosch from UI."""
        errors = {}

        if user_input is not None:
            # Validate the IP address by attempting to connect
            try:
                session = aiohttp_client.async_get_clientsession(self.hass)
                test_url = f"http://{user_input['ip_address']}/pvi?rName=InverterInfo"
                async with session.get(test_url, timeout=5) as response:
                    if response.status != 200:
                        errors["base"] = "cannot_connect"
                    else:
                        return self.async_create_entry(
                            title="Bosch BPT-S4 Inverter",
                            data={
                                "ip_address": user_input["ip_address"]
                            }
                        )
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return BoschOptionsFlow(config_entry)

class BoschOptionsFlow(config_entries.OptionsFlow):
    """Handle Bosch options in UI."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage Bosch options."""
        return self.async_create_entry(title="", data={})