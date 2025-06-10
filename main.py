import psutil

battery = psutil.sensors_battery()

if battery:
    percent = battery.percent
    pluged = battery.power_plugged
    status = "Charing" if pluged else "Not charging"
    print(f"Battery: {percent} % ({status})")

else:
    print("Battery information not available.")