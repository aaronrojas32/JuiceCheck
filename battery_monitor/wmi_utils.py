import wmi
import platform
import subprocess
import re
import os


def safe_int_convert(value):
    """Attempts to convert value to int; returns None if it fails."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float_convert(value):
    """Attempts to convert value to float; returns None if it fails."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def get_int_attr(obj, attr):
    """Extracts obj.attr and converts it to int safely."""
    return safe_int_convert(getattr(obj, attr, None))


def get_float_attr(obj, attr):
    """Extracts obj.attr and converts it to float safely."""
    return safe_float_convert(getattr(obj, attr, None))


def get_battery_data_from_powercfg():
    """Get battery data using powercfg command - often the most reliable method."""
    try:
        # Run powercfg /batteryreport command to generate HTML report
        result = subprocess.run(
            ['powercfg', '/batteryreport', '/output', 'temp_battery_report.html'], 
            capture_output=True, text=True, check=True, timeout=30
        )
        
        # Try to read the HTML report and extract capacity data
        if os.path.exists('temp_battery_report.html'):
            with open('temp_battery_report.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clean up the temporary file
            os.remove('temp_battery_report.html')
            
            # Extract design capacity and full charge capacity using regex
            design_match = re.search(r'DESIGN CAPACITY</td>\s*<td[^>]*>([0-9,]+)\s*mWh', content, re.IGNORECASE)
            full_match = re.search(r'FULL CHARGE CAPACITY</td>\s*<td[^>]*>([0-9,]+)\s*mWh', content, re.IGNORECASE)
            
            design_capacity = None
            full_capacity = None
            
            if design_match:
                design_capacity = safe_int_convert(design_match.group(1).replace(',', ''))
            
            if full_match:
                full_capacity = safe_int_convert(full_match.group(1).replace(',', ''))
            
            return design_capacity, full_capacity
            
    except Exception:
        # Silently fail and let other methods try
        pass
    
    return None, None


def get_battery_data_from_acpi():
    """Try to get battery data from ACPI through WMI namespace."""
    try:
        wmi_root = wmi.WMI(namespace="root\\wmi")
        
        # Try different ACPI battery classes that might contain capacity data
        acpi_classes = [
            'BatteryStaticData',
            'BatteryStatus', 
            'BatteryRuntime',
            'BatteryFullChargedCapacity',
            'MSBattery_BatteryStaticData',
            'MSBattery_BatteryStatus'
        ]
        
        acpi_data = {}
        
        for class_name in acpi_classes:
            try:
                wmi_class = getattr(wmi_root, class_name)
                instances = list(wmi_class())
                if instances:
                    instance = instances[0]
                    for prop in instance.properties:
                        prop_lower = prop.lower()
                        if 'capacity' in prop_lower or 'charge' in prop_lower:
                            value = getattr(instance, prop, None)
                            if value is not None:
                                acpi_data[f"{class_name}_{prop}"] = value
            except Exception:
                continue
        
        return acpi_data
        
    except Exception:
        return {}


def get_battery_chemistry_name(code):
    """Maps chemistry code to readable name."""
    chemistry_map = {
        1: "Other",
        2: "Unknown",
        3: "Lead Acid",
        4: "Nickel Cadmium",
        5: "Nickel Metal Hydride",
        6: "Lithium Ion",
        7: "Zinc Air",
        8: "Lithium Polymer"
    }
    c = safe_int_convert(code)
    return chemistry_map.get(c, f"Unknown ({c})")


def get_battery_status_name(code):
    """Maps status code to readable name."""
    status_map = {
        1: "Discharging",
        2: "On AC Power",
        3: "Fully Charged",
        4: "Low",
        5: "Critical",
        6: "Charging",
        7: "Charging High",
        8: "Charging Low",
        9: "Charging Critical",
        10: "Undefined",
        11: "Partially Charged"
    }
    s = safe_int_convert(code)
    return status_map.get(s, f"Unknown ({s})")


def convert_runtime_minutes(raw):
    """Converts minutes to 'Xh Ym' or 'Zm' format, or 'Unknown' if invalid."""
    mins = safe_int_convert(raw)
    # Not a valid integer, or negative, or the special value 71582788
    if not isinstance(mins, int) or mins < 0 or mins == 71582788:
        return "Unknown"
    # Discard more than 24h as unrealistic
    if mins > 1440:
        return "Unknown"
    h, m = divmod(mins, 60)
    return f"{h}h {m}m" if h else f"{m}m"


def get_advanced_battery_data():
    """
    Query WMI on Windows and return a dict with readable battery data.
    Uses multiple methods to ensure maximum data retrieval success.
    """
    if platform.system() != "Windows":
        return {"error": "WMI only available on Windows"}

    try:
        c = wmi.WMI()
        bats = list(c.Win32_Battery())
        if not bats:
            return {"error": "No battery found"}
        bat = bats[0]

        # Basic battery information
        data = {
            "name": getattr(bat, 'Name', 'Unknown'),
            "estimated_charge": get_int_attr(bat, 'EstimatedChargeRemaining'),
            "status": get_battery_status_name(bat.BatteryStatus),
            "estimated_runtime": convert_runtime_minutes(bat.EstimatedRunTime),
            "chemistry": get_battery_chemistry_name(bat.Chemistry),
        }

        # Voltage handling
        v = get_int_attr(bat, 'DesignVoltage')
        if isinstance(v, int):
            data["voltage"] = f"{v/1000:.2f}V" if v > 100 else f"{v}V"
        else:
            data["voltage"] = "Unknown"

        # Capacity data retrieval using multiple methods
        design_cap = None
        full_cap = None

        # Method 1: Standard WMI classes (root\wmi namespace)
        try:
            wroot = wmi.WMI(namespace="root\\wmi")
            sd = list(wroot.BatteryStaticData())
            if sd:
                design_cap = safe_int_convert(getattr(sd[0], 'DesignCapacity', None))
        except Exception:
            pass

        try:
            wroot = wmi.WMI(namespace="root\\wmi")
            fc = list(wroot.BatteryFullChargedCapacity())
            if fc:
                full_cap = safe_int_convert(getattr(fc[0], 'FullChargedCapacity', None))
        except Exception:
            pass

        # Method 2: Win32_PortableBattery fallback
        if design_cap is None or full_cap is None:
            try:
                pb_list = list(c.Win32_PortableBattery())
                if pb_list:
                    pb = pb_list[0]
                    if design_cap is None:
                        design_cap = safe_int_convert(getattr(pb, 'DesignCapacity', None))
                    
                    # Try multiple properties for full capacity
                    if full_cap is None:
                        for prop in ['Capacity', 'MaxCapacity', 'FullChargeCapacity']:
                            try:
                                value = safe_int_convert(getattr(pb, prop, None))
                                if value and value > 0:
                                    full_cap = value
                                    break
                            except:
                                continue
            except Exception:
                pass

        # Method 3: PowerCFG command (often most reliable)
        if design_cap is None or full_cap is None:
            pcfg_design, pcfg_full = get_battery_data_from_powercfg()
            if design_cap is None and pcfg_design:
                design_cap = pcfg_design
            if full_cap is None and pcfg_full:
                full_cap = pcfg_full

        # Method 4: ACPI data as last resort
        if design_cap is None or full_cap is None:
            acpi_data = get_battery_data_from_acpi()
            if acpi_data:
                # Look for capacity values in ACPI data
                for key, value in acpi_data.items():
                    value = safe_int_convert(value)
                    if value and value > 1000:  # Reasonable capacity value
                        if 'design' in key.lower() and design_cap is None:
                            design_cap = value
                        elif ('full' in key.lower() or 'charge' in key.lower()) and full_cap is None:
                            full_cap = value

        # Format capacity values
        data["design_capacity"] = f"{design_cap} mWh" if isinstance(design_cap, int) else "Unknown"
        data["full_charged_capacity"] = f"{full_cap} mWh" if isinstance(full_cap, int) else "Unknown"

        # Battery health calculation
        if isinstance(design_cap, int) and isinstance(full_cap, int) and design_cap > 0:
            health = (full_cap / design_cap) * 100
            data["health"] = f"{health:.1f}%"
        else:
            data["health"] = "Unable to calculate"

        # Charge cycles (if available)
        try:
            wroot = wmi.WMI(namespace="root\\wmi")
            cc = list(wroot.BatteryCycleCount())
            if cc:
                cnt = safe_int_convert(getattr(cc[0], 'CycleCount', None))
                if isinstance(cnt, int):
                    data["cycle_count"] = f"{cnt} cycles"
        except Exception:
            pass

        # Battery temperature (if available)
        temp = get_battery_temperature()
        if temp:
            data["temperature"] = temp

        return data

    except Exception as e:
        return {"error": f"WMI query failed: {e}"}


def get_battery_temperature():
    """Returns battery temperature in °C if available."""
    try:
        wroot = wmi.WMI(namespace="root\\wmi")
        td = list(wroot.BatteryTemperature())
        if td:
            t_kelvin_tenths = safe_float_convert(getattr(td[0], 'Temperature', None))
            if isinstance(t_kelvin_tenths, (int, float)):
                t_c = (t_kelvin_tenths / 10) - 273.15
                return f"{t_c:.1f}°C"
    except Exception:
        pass
    return None


def diagnose_battery_data_sources():
    """
    Diagnostic function to show what battery data sources are available.
    Useful for debugging when battery health calculation fails.
    """
    print("=== Battery Data Sources Diagnosis ===")
    
    try:
        c = wmi.WMI()
        
        # Check Win32_Battery
        batteries = list(c.Win32_Battery())
        print(f"Win32_Battery: {len(batteries)} batteries found")
        if batteries:
            battery = batteries[0]
            for prop in battery.properties:
                value = getattr(battery, prop, None)
                if value is not None:
                    print(f"  {prop}: {value}")
        
        # Check Win32_PortableBattery
        portable = list(c.Win32_PortableBattery())
        print(f"\nWin32_PortableBattery: {len(portable)} batteries found")
        if portable:
            pb = portable[0]
            for prop in pb.properties:
                value = getattr(pb, prop, None)
                if value is not None:
                    print(f"  {prop}: {value}")
        
        # Check WMI root\wmi namespace
        print(f"\n=== Namespace root\\wmi ===")
        try:
            wmi_root = wmi.WMI(namespace="root\\wmi")
            wmi_classes = ['BatteryStaticData', 'BatteryFullChargedCapacity', 'BatteryStatus', 'BatteryCycleCount']
            
            for class_name in wmi_classes:
                try:
                    wmi_class = getattr(wmi_root, class_name)
                    instances = list(wmi_class())
                    print(f"{class_name}: {len(instances)} instances")
                    if instances:
                        instance = instances[0]
                        for prop in instance.properties:
                            value = getattr(instance, prop, None)
                            if value is not None:
                                print(f"  {prop}: {value}")
                except Exception as e:
                    print(f"{class_name}: Error - {e}")
        except Exception as e:
            print(f"Error accessing root\\wmi: {e}")
        
        # Test powercfg method
        print(f"\n=== PowerCFG Method Test ===")
        design, full = get_battery_data_from_powercfg()
        if design or full:
            print(f"Design Capacity: {design} mWh")
            print(f"Full Capacity: {full} mWh")
        else:
            print("PowerCFG method failed or returned no data")
            
    except Exception as e:
        print(f"Diagnosis error: {e}")