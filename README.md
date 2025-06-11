# JuiceCheck

A comprehensive battery health monitoring tool for laptops that provides detailed information about your battery status, health, and performance metrics.

## Features

- **Basic Battery Information**: Current charge level, power status, and estimated runtime
- **Advanced Health Metrics**: Battery health percentage, design vs current capacity, voltage, and chemistry
- **Multiple Output Formats**: Text (human-readable), JSON, and CSV formats
- **Data Export**: Save battery reports to files for analysis
- **Cross-Platform Support**: Works on Windows (with advanced WMI data)
- **Command-Line Interface**: Easy to use with various options and flags

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - `psutil` - For basic battery information
  - `colorama` - For colored terminal output
  - `wmi` - For advanced Windows battery data (Windows only)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/juicecheck.git
cd juicecheck
```

2. Install dependencies:
```bash
pip install psutil colorama
# On Windows, also install:
pip install wmi
```

## Usage

### Basic Usage

Run the battery report with default text output:
```bash
python scripts/run.py
```

### Command Line Options

```bash
# Show help
python scripts/run.py --help

# Output in JSON format
python scripts/run.py --format json

# Output in CSV format
python scripts/run.py --format csv

# Export data to file
python scripts/run.py --export battery_report.json

# Quiet mode (no banner)
python scripts/run.py --quiet

# Show version
python scripts/run.py --version
```

### Output Examples

**Text Format (Default):**
```
=== Basic Battery Status ===
Charge: 85%
Plugged In: Yes
Estimated Runtime: 240 minutes

=== Advanced Battery Information ===
Name: Primary Battery
Estimated Charge: 85%
Health: 92.3%
Design Capacity: 50000 mWh
Full Charged Capacity: 46150 mWh
```

**JSON Format:**
```json
{
  "timestamp": "2025-06-11T10:30:00.123456",
  "basic": {
    "percent": 85.0,
    "plugged": true,
    "secsleft": 14400
  },
  "advanced": {
    "name": "Primary Battery",
    "estimated_charge": 85,
    "health": 92.3,
    "design_capacity": 50000,
    "full_charged_capacity": 46150
  }
}
```

## Project Structure

```
juicecheck/
├── battery_monitor/
│   ├── __init__.py
│   ├── core.py          # Core battery functions
│   ├── display.py       # Output formatting
│   └── wmi_utils.py     # Windows WMI integration
├── scripts/
│   └── run.py           # Main application entry point
├── test/
│   └── test_core.py     # Unit tests
└── README.md
```

## Battery Health Interpretation

- **90-100%**: Excellent battery health
- **80-89%**: Good battery health
- **70-79%**: Fair battery health, monitor closely
- **Below 70%**: Poor battery health, consider replacement

## Platform Support

### Windows
- Full support with advanced WMI data
- Provides detailed battery chemistry, capacity, and health metrics
- Requires `wmi` Python package

### Linux/macOS
- Basic support through `psutil`
- Shows charge level, power status, and runtime estimates
- Advanced metrics may not be available

## Development

### Running Tests

```bash
python -m pytest test/
```

### Adding New Features

1. Core functionality goes in `battery_monitor/core.py`
2. Display formatting in `battery_monitor/display.py`
3. Platform-specific code in separate modules (like `wmi_utils.py`)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues

**"Could not retrieve basic battery status"**
- Ensure you're running on a laptop with a battery
- Check that `psutil` is properly installed

**"Could not retrieve advanced battery information" (Windows)**
- Install the `wmi` package: `pip install wmi`
- Run as administrator if needed
- Some virtual machines may not expose WMI battery data

**Permission Errors**
- On Linux/macOS, some battery information may require elevated privileges
- Try running with `sudo` if basic information is not available
