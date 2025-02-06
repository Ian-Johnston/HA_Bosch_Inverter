DOMAIN = "bosch"
DEFAULT_SCAN_INTERVAL = 30
SENSOR_ENDPOINTS = {
    "solar_power": "/pvi?rName=AcPower",
    "grid_voltage": "/pvi?rName=GridVoltageAndCurrent",
    "grid_frequency": "/pvi?rName=GridVoltageAndCurrent",
    "temperature": "/pvi?rName=Temperature",
    "inverter_info": "/pvi?rName=InverterInfo"
}