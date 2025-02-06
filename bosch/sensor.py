import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN
from .bosch_api import BoschAPI

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Bosch BPT-S4 sensors dynamically from a config entry."""
    _LOGGER.info("Bosch: async_setup_entry is running.")

    # Retrieve the API instance
    api: BoschAPI = hass.data[DOMAIN].get(entry.entry_id)
    if not api:
        _LOGGER.error("Bosch API instance not found! Sensors will not load.")
        return

    async def async_update_data():
        """Fetch new data from the API asynchronously."""
        _LOGGER.debug("Fetching Bosch API data...")
        data = {}
        endpoints = {
            "solar_power": "/pvi?rName=AcPower",
            "grid_voltage": "/pvi?rName=GridVoltageAndCurrent",
            "grid_current": "/pvi?rName=GridVoltageAndCurrent",
            "grid_frequency": "/pvi?rName=GridVoltageAndCurrent",
            "string_a_voltage": "/pvi?rName=StringVoltageAndCurrent",
            "string_a_current": "/pvi?rName=StringVoltageAndCurrent",
            "string_b_voltage": "/pvi?rName=StringVoltageAndCurrent",
            "string_b_current": "/pvi?rName=StringVoltageAndCurrent",
            "inverter_mode": "/pvi?rName=InverterStatus",
            "system_temperature": "/pvi?rName=Temperature",
            "main_processor_temperature": "/pvi?rName=Temperature",
            "inverter_info": "/pvi?rName=InverterStatus",
            "inverter_error": "/pvi?rName=InverterStatus",
            "inverter_warning": "/pvi?rName=InverterStatus",
        }
        
        for sensor, endpoint in endpoints.items():
            try:
                _LOGGER.debug(f"Fetching data for {sensor} from endpoint: {endpoint}")
                response = await api.fetch_data(endpoint)
                _LOGGER.debug(f"Raw API response for {sensor}: {response}")
                
                if response and isinstance(response, dict):
                    if sensor == "solar_power":
                        data[sensor] = response.get("powerL1")
                    elif sensor == "grid_voltage":
                        data[sensor] = response.get("uGridL1")
                    elif sensor == "grid_current":
                        data[sensor] = response.get("iGridL1")
                    elif sensor == "grid_frequency":
                        data[sensor] = response.get("fGrid")
                    elif sensor == "string_a_voltage":
                        data[sensor] = response.get("uStringA")
                    elif sensor == "string_a_current":
                        data[sensor] = response.get("iStringA")
                    elif sensor == "string_b_voltage":
                        data[sensor] = response.get("uStringB")
                    elif sensor == "string_b_current":
                        data[sensor] = response.get("iStringB")
                    elif sensor == "inverter_mode":
                        data[sensor] = response.get("workMode")
                    elif sensor == "system_temperature":
                        data[sensor] = response.get("tSystem")
                    elif sensor == "main_processor_temperature":
                        data[sensor] = response.get("tPpMcu")
                    elif sensor == "inverter_info":
                        data[sensor] = response.get("hasInfo")
                    elif sensor == "inverter_error":
                        data[sensor] = response.get("hasError")
                    elif sensor == "inverter_warning":
                        data[sensor] = response.get("hasWarning")
                    
                    _LOGGER.debug(f"Extracted value for {sensor}: {data[sensor]}")
                else:
                    _LOGGER.warning(f"Invalid or empty response for {sensor}")
                    data[sensor] = None
                    
            except Exception as e:
                _LOGGER.error(f"Error fetching {sensor}: {str(e)}")
                data[sensor] = None
                
        _LOGGER.debug(f"Final coordinator data: {data}")
        return data

    # Create coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Bosch BPT-S4",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Perform initial refresh
    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("Initial coordinator refresh completed successfully")
    except Exception as e:
        _LOGGER.error(f"Error during initial coordinator refresh: {str(e)}")

    # Create sensor entities in the specified order
    sensors = [
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="solar_power",
            name="Solar Power",
            unit="W",
            icon="mdi:solar-power",
            device_class="power"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="grid_voltage",
            name="Grid Voltage",
            unit="V",
            icon="mdi:transmission-tower",
            device_class="voltage"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="grid_current",
            name="Grid Current",
            unit="A",
            icon="mdi:current-ac",
            device_class="current"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="grid_frequency",
            name="Grid Frequency",
            unit="Hz",
            icon="mdi:sine-wave",
            device_class="frequency"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="string_a_voltage",
            name="String A Voltage",
            unit="V",
            icon="mdi:current-dc",
            device_class="voltage"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="string_a_current",
            name="String A Current",
            unit="A",
            icon="mdi:current-ac",
            device_class="current"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="string_b_voltage",
            name="String B Voltage",
            unit="V",
            icon="mdi:current-dc",
            device_class="voltage"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="string_b_current",
            name="String B Current",
            unit="A",
            icon="mdi:current-ac",
            device_class="current"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="inverter_mode",
            name="Inverter Mode",
            unit=None,
            icon="mdi:information",
            device_class=None
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="system_temperature",
            name="System Temperature",
            unit="°C",
            icon="mdi:thermometer",
            device_class="temperature"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="main_processor_temperature",
            name="Main Processor Temperature",
            unit="°C",
            icon="mdi:thermometer",
            device_class="temperature"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="inverter_info",
            name="Inverter Info",
            unit=None,
            icon="mdi:information",
            device_class="binary_sensor"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="inverter_error",
            name="Inverter Error",
            unit=None,
            icon="mdi:alert",
            device_class="binary_sensor"
        ),
        BoschSensor(
            coordinator=coordinator,
            entry=entry,
            sensor_type="inverter_warning",
            name="Inverter Warning",
            unit=None,
            icon="mdi:alert-outline",
            device_class="binary_sensor"
        ),
    ]

    _LOGGER.info(f"Bosch: Sensors to be added: {sensors}")
    async_add_entities(sensors, True)

class BoschSensor(CoordinatorEntity, SensorEntity):
    """Bosch BPT-S4 sensor entity."""

    def __init__(self, coordinator, entry, sensor_type, name, unit, icon, device_class):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name
        self._unit = unit
        self._icon = icon
        self._entry_id = entry.entry_id
        self._device_class = device_class
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_should_poll = False

    @property
    def name(self):
        """Return the name of the sensor without 'Bosch' prefix."""
        return self._name

    @property
    def state(self):
        """Return the sensor state rounded to 1 decimal place if applicable."""
        if self.coordinator.data is None:
            _LOGGER.warning(f"No data available in coordinator for {self._sensor_type}")
            return None
            
        value = self.coordinator.data.get(self._sensor_type)
        
        if isinstance(value, (int, float)) and self._unit is not None:
            value = round(value, 1)
        
        _LOGGER.debug(f"State for {self._sensor_type}: {value}")
        return value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return self._attr_unique_id  

    @property
    def should_poll(self):
        """Return False because the entity updates from the coordinator."""
        return self._attr_should_poll

    @property
    def state_class(self):
        """Return the state class for statistics."""
        return "measurement" if self._device_class and self._device_class != "binary_sensor" else None

    @property
    def device_class(self):
        """Return the device class for better UI integration."""
        return self._device_class

    @property
    def device_info(self):
        """Return device registry information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="Bosch BPT-S4 Inverter",
            manufacturer="Bosch",
            model="BPT-S4",
            sw_version="1.0.0",
            configuration_url="http://192.168.1.204",
        )

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await self.coordinator.async_request_refresh()