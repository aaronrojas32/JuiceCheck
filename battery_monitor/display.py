from colorama import init, Fore, Style

# Initialize color support
init(autoreset=True)


def _to_int(value, default=0):
    """Convierte value a int, devolviendo default si falla."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def show_basic_status(status):
    """Display basic battery status with improved formatting."""
    print("=== Basic Battery Status ===")
    
    # Charge percentage with color coding
    percent = _to_int(status.get('percent', 0))
    if percent >= 80:
        color = Fore.GREEN
    elif percent >= 50:
        color = Fore.YELLOW
    elif percent >= 20:
        color = Fore.MAGENTA
    else:
        color = Fore.RED
    
    print(f"{color}Charge: {percent}%{Style.RESET_ALL}")
    
    # Power status
    plugged = bool(status.get('plugged', False))
    plug_color = Fore.GREEN if plugged else Fore.YELLOW
    plug_text = "Yes" if plugged else "No"
    print(f"{plug_color}Plugged In: {plug_text}{Style.RESET_ALL}")

    # Runtime estimation
    secsleft = _to_int(status.get('secsleft', -1), default=-1)
    if secsleft > 0:
        hours = secsleft // 3600
        minutes = (secsleft % 3600) // 60
        if hours > 0:
            runtime_text = f"{hours}h {minutes}m"
        else:
            runtime_text = f"{minutes}m"
        print(f"{Fore.CYAN}Estimated Runtime: {runtime_text}{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN}Estimated Runtime: Unknown{Style.RESET_ALL}")
    print()


def show_advanced_info(info):
    """Display advanced battery information with better formatting."""
    print("=== Advanced Battery Information ===")
    
    # Check if there's an error
    if 'error' in info:
        print(f"{Fore.RED}Error: {info['error']}{Style.RESET_ALL}")
        return
    
    # Define display order and formatting
    display_fields = [
        ('name', 'Battery Name', Fore.CYAN),
        ('estimated_charge', 'Current Charge', Fore.GREEN, '%'),
        ('voltage', 'Design Voltage', Fore.BLUE),
        ('status', 'Battery Status', Fore.YELLOW),
        ('chemistry', 'Battery Chemistry', Fore.MAGENTA),
        ('estimated_runtime', 'Estimated Runtime', Fore.CYAN),
        ('design_capacity', 'Design Capacity', Fore.WHITE),
        ('full_charged_capacity', 'Full Charge Capacity', Fore.WHITE),
        ('health', 'Battery Health', Fore.GREEN),
        ('cycle_count', 'Charge Cycles', Fore.BLUE),
    ]
    
    for field_info in display_fields:
        key, label, color = field_info[:3]
        suffix = field_info[3] if len(field_info) > 3 else ''
        
        if key in info and info[key] is not None:
            value = info[key]
            # Si viene con sufijo de unidad y es numérico, añadir sufijo
            if suffix and isinstance(value, (int, float)):
                value = f"{value}{suffix}"
            print(f"{color}{label}: {value}{Style.RESET_ALL}")
    
    # Health status interpretation
    health_str = info.get('health', '')
    if health_str and health_str != "Unable to calculate":
        try:
            # Extrae sólo la parte numérica (sin '%')
            health_value = float(health_str.rstrip('%'))
            print()
            print("=== Health Assessment ===")
            
            if health_value >= 90:
                print(f"{Fore.GREEN}Excellent - Battery is in great condition{Style.RESET_ALL}")
            elif health_value >= 80:
                print(f"{Fore.YELLOW}Good - Battery health is acceptable{Style.RESET_ALL}")
            elif health_value >= 70:
                print(f"{Fore.MAGENTA}Fair - Monitor battery health closely{Style.RESET_ALL}")
            elif health_value >= 60:
                print(f"{Fore.RED}Poor - Consider replacing the battery soon{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Critical - Battery replacement recommended{Style.RESET_ALL}")
        except (ValueError, TypeError):
            pass
    
    print()
