import wmi


def get_advanced_battery_data():
    """
    Query WMI for advanced battery data on Windows.
    Returns dict:
      - name
      - estimated_charge (%)
      - voltage (mV)
      - status_code
      - estimated_runtime (minutes)
      - chemistry code
      - design_capacity (mWh)
      - full_charged_capacity (mWh)
      - health (%) = (full_charged_capacity / design_capacity) * 100
    """
    c = wmi.WMI()
    data = {}

    # Win32_Battery
    for b in c.Win32_Battery():
        data["name"] = b.Name
        data["estimated_charge"] = b.EstimatedChargeRemaining
        data["voltage"] = b.DesignVoltage
        data["status_code"] = b.BatteryStatus
        data["estimated_runtime"] = b.EstimatedRunTime
        data["chemistry"] = b.Chemistry

    # Try static data from root\wmi
    try:
        wmi_root = wmi.WMI(namespace="root\\wmi")
        static = wmi_root.BatteryStaticData()[0]
        data["design_capacity"] = static.DesignCapacity
    except Exception:
        data["design_capacity"] = None

    # Try full charged capacity
    try:
        wmi_root = wmi.WMI(namespace="root\\wmi")
        full = wmi_root.BatteryFullChargedCapacity()[0]
        data["full_charged_capacity"] = full.FullChargedCapacity
    except Exception:
        data["full_charged_capacity"] = None

    # Calculate health
    if data.get("design_capacity") and data.get("full_charged_capacity"):
        health = (data["full_charged_capacity"] / data["design_capacity"]) * 100
        data["health"] = round(health, 1)
    else:
        data["health"] = None

    return data