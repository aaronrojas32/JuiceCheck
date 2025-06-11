import wmi
import platform

def safe_int_convert(value):
    """Intenta convertir value a int; devuelve None si falla."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def safe_float_convert(value):
    """Intenta convertir value a float; devuelve None si falla."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def get_int_attr(obj, attr):
    """Extrae obj.attr y lo convierte a int de forma segura."""
    return safe_int_convert(getattr(obj, attr, None))

def get_float_attr(obj, attr):
    """Extrae obj.attr y lo convierte a float de forma segura."""
    return safe_float_convert(getattr(obj, attr, None))

def get_battery_chemistry_name(code):
    """Mapea código de química a nombre legible."""
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
    """Mapea código de estado a nombre legible."""
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
    """Convierte minutos a formato 'Xh Ym' o 'Zm', o 'Unknown' si no es válido."""
    mins = safe_int_convert(raw)
    # No es un entero válido, o negativo, o el valor especial 71582788
    if not isinstance(mins, int) or mins < 0 or mins == 71582788:
        return "Unknown"
    # Descarta más de 24h
    if mins > 1440:
        return "Unknown"
    h, m = divmod(mins, 60)
    return f"{h}h {m}m" if h else f"{m}m"

def get_advanced_battery_data():
    """Consulta WMI en Windows y devuelve un dict con datos de batería legibles."""
    if platform.system() != "Windows":
        return {"error": "WMI only available on Windows"}

    try:
        c = wmi.WMI()
        bats = list(c.Win32_Battery())
        if not bats:
            return {"error": "No battery found"}
        bat = bats[0]

        data = {
            "name": getattr(bat, 'Name', 'Unknown'),
            "estimated_charge": get_int_attr(bat, 'EstimatedChargeRemaining'),
            "status": get_battery_status_name(bat.BatteryStatus),
            "estimated_runtime": convert_runtime_minutes(bat.EstimatedRunTime),
            "chemistry": get_battery_chemistry_name(bat.Chemistry),
        }

        # Voltaje
        v = get_int_attr(bat, 'DesignVoltage')
        if isinstance(v, int):
            data["voltage"] = f"{v/1000:.2f}V" if v > 100 else f"{v}V"
        else:
            data["voltage"] = "Unknown"

        # Capacidades: Design y Full Charged
        design_cap = None
        full_cap = None

        # Intento BatteryStaticData
        try:
            wroot = wmi.WMI(namespace="root\\wmi")
            sd = list(wroot.BatteryStaticData())
            if sd:
                design_cap = safe_int_convert(sd[0].DesignCapacity)
        except Exception:
            pass

        # Intento BatteryFullChargedCapacity
        try:
            wroot = wmi.WMI(namespace="root\\wmi")
            fc = list(wroot.BatteryFullChargedCapacity())
            if fc:
                full_cap = safe_int_convert(fc[0].FullChargedCapacity)
        except Exception:
            pass

        # Fallback Win32_PortableBattery
        if design_cap is None or full_cap is None:
            try:
                pb_list = list(c.Win32_PortableBattery())
                if pb_list:
                    pb = pb_list[0]
                    if design_cap is None:
                        design_cap = safe_int_convert(pb.DesignCapacity)
                    if full_cap is None:
                        full_cap = safe_int_convert(pb.MaxRechargeTime)
            except Exception:
                pass

        data["design_capacity"] = f"{design_cap} mWh" if isinstance(design_cap, int) else "Unknown"
        data["full_charged_capacity"] = f"{full_cap} mWh" if isinstance(full_cap, int) else "Unknown"

        # Salud de la batería
        if isinstance(design_cap, int) and isinstance(full_cap, int) and design_cap > 0:
            health = (full_cap / design_cap) * 100
            data["health"] = f"{health:.1f}%"
        else:
            data["health"] = "Unable to calculate"

        # Ciclos de carga (si está disponible)
        try:
            wroot = wmi.WMI(namespace="root\\wmi")
            cc = list(wroot.BatteryCycleCount())
            if cc:
                cnt = safe_int_convert(cc[0].CycleCount)
                if isinstance(cnt, int):
                    data["cycle_count"] = f"{cnt} cycles"
        except Exception:
            pass

        return data

    except Exception as e:
        return {"error": f"WMI query failed: {e}"}

def get_battery_temperature():
    """Devuelve temperatura de batería en °C si está disponible."""
    try:
        wroot = wmi.WMI(namespace="root\\wmi")
        td = list(wroot.BatteryTemperature())
        if td:
            t_kelvin_tenths = safe_float_convert(td[0].Temperature)
            if isinstance(t_kelvin_tenths, (int, float)):
                t_c = (t_kelvin_tenths / 10) - 273.15
                return f"{t_c:.1f}°C"
    except Exception:
        pass
    return None
