import sys
import os

# Ensure project root in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from battery_monitor import core, display

ASCII_ART = r"""
       _       _           _____ _               _    
      | |     (_)         / ____| |             | |   
      | |_   _ _  ___ ___| |    | |__   ___  ___| | __
  _   | | | | | |/ __/ _ \ |    | '_ \ / _ \/ __| |/ /
 | |__| | |_| | | (_|  __/ |____| | | |  __/ (__|   < 
  \____/ \__,_|_|\___\___|\_____|_| |_|\___|\___|_|\_\
                                                                                                        
           {name} v{version}
"""


def main():
    # Print banner
    print(ASCII_ART.format(name='JuiceCheck', version=core.__version__))

    basic = core.get_basic_battery_status()
    advanced = core.get_full_battery_info()

    if basic:
        display.show_basic_status(basic)
    else:
        print("⚠️ Could not retrieve basic battery status.")

    if advanced:
        display.show_advanced_info(advanced)
    else:
        print("⚠️ Could not retrieve advanced battery information.")


if __name__ == '__main__':
    main()