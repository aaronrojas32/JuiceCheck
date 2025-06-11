#!/usr/bin/env python3
import sys
import os
import argparse
import json
from datetime import datetime

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


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='JuiceCheck - Battery Health Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Show battery status
  %(prog)s --format json      # Output as JSON
  %(prog)s --export data.json # Save to file
        """
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Export data to file'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress banner and extra output'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'JuiceCheck {core.__version__}'
    )
    
    return parser


def get_battery_data():
    """Get combined battery data."""
    try:
        basic = core.get_basic_battery_status()
        advanced = core.get_full_battery_info()
        
        if not basic:
            return None
            
        # Combine data
        data = {
            'timestamp': datetime.now().isoformat(),
            'basic': basic,
            'advanced': advanced or {}
        }
        
        return data
        
    except Exception as e:
        print(f"Error getting battery data: {e}", file=sys.stderr)
        return None


def format_output(data, format_type):
    """Format data for output."""
    if not data:
        return "No battery data available"
        
    if format_type == 'json':
        return json.dumps(data, indent=2)
    elif format_type == 'csv':
        # Simple CSV format
        basic = data['basic']
        advanced = data.get('advanced', {})
        
        headers = ['timestamp', 'percent', 'plugged', 'health']
        values = [
            data['timestamp'],
            basic.get('percent', 'N/A'),
            basic.get('plugged', 'N/A'),
            advanced.get('health', 'N/A')
        ]
        
        return f"{','.join(headers)}\n{','.join(map(str, values))}"
    else:
        # Text format (existing display functions)
        return None  # Will use display functions


def export_data(data, filename):
    """Export data to file."""
    try:
        ext = filename.lower().split('.')[-1]
        
        if ext == 'json':
            content = json.dumps(data, indent=2)
        elif ext == 'csv':
            content = format_output(data, 'csv')
        else:
            content = json.dumps(data, indent=2)  # Default to JSON
            
        with open(filename, 'w') as f:
            f.write(content)
            
        print(f"Data exported to {filename}")
        
    except Exception as e:
        print(f"Error exporting data: {e}", file=sys.stderr)


def show_status_alert(data):
    """Show alerts based on battery status."""
    if not data or 'basic' not in data:
        return
        
    basic = data['basic']
    advanced = data.get('advanced', {})
    
    percent = 0
    try:
        percent = int(basic.get('percent', 0))
    except (ValueError, TypeError):
        pass

    # Battery level alerts
    if percent <= 10:
        print(f"CRITICAL: Battery at {percent}%!")
    elif percent <= 20:
        print(f"WARNING: Battery low at {percent}%")
    
    health_str = advanced.get('health', '')
    # Intentamos extraer número de health_str ("85.0%")
    try:
        health_value = float(health_str.rstrip('%'))
    except (ValueError, TypeError, AttributeError):
        health_value = None
    
    # Health alerts
    if health_value is not None and health_value < 80:
        print(f"WARNING: Battery health is {health_value}% - Consider replacement")


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Show banner unless quiet mode
    if not args.quiet:
        print(ASCII_ART.format(name='JuiceCheck', version=core.__version__))
    
    try:
        # Single battery report
        data = get_battery_data()
        
        if data:
            if args.format == 'text':
                display.show_basic_status(data['basic'])
                if data['advanced']:
                    display.show_advanced_info(data['advanced'])
                
                show_status_alert(data)
            else:
                print(format_output(data, args.format))
            
            if args.export:
                export_data(data, args.export)
        else:
            print("Could not retrieve battery information")
            sys.exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()