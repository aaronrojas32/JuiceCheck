import psutil
from battery_monitor import wmi_utils

__version__ = "1.1.4"


def get_basic_battery_status():
    """
    Fetch basic battery status using psutil.
    Returns dict with: percent, plugged, secsleft; or None.
    """
    battery = psutil.sensors_battery()
    if not battery:
        return None

    return {
        "percent": battery.percent,
        "plugged": battery.power_plugged,
        "secsleft": battery.secsleft
    }


def get_full_battery_info():
    """
    Fetch advanced battery data via WMI on Windows.
    Returns dict with attributes and health calculation.
    """
    return wmi_utils.get_advanced_battery_data()