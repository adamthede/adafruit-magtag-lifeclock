# MagTag Life Timer Project: Complete Implementation Guide

## Project Overview

**Goal**: Create a "life timer" application for the Adafruit MagTag that displays real-time life duration statistics with internet-connected time synchronization.

**Hardware**:
- Adafruit MagTag 2.9" Grayscale E-Ink WiFi Display (PID: 4819)
- 3x AAA Battery Holder (PID: 727)
- ESP32-S2 microcontroller with 296x128 pixel display

## Part 1: Development Environment Setup

### 1.1 Computer Software Installation

**Primary Development Environment:**
- **Cursor IDE**: You'll be using Cursor for all code editing and project management
- **Terminal Tools**: Built-in terminal for file transfer and device communication
- **Git**: For version control (likely already installed)
- **CircuitPython Bundle**: Latest version from Adafruit

**Additional Tools (already available on macOS):**
```bash
# Verify required tools are available
which screen  # For serial communication (alternative to tio)
which tio     # Modern serial tool (preferred if installed)
python3 --version  # For local testing and development

# tio is recommended for serial communication
# If not installed: brew install tio
```

**Optional Alternative Editors (for reference only):**
- **Mu Editor**: Beginner-friendly CircuitPython IDE (not needed with Cursor)
- **Thonny IDE**: Python IDE with CircuitPython support (not needed with Cursor)

### 1.1.1 Cursor-Based Development Workflow

**File Transfer to MagTag:**
```bash
# MagTag appears as a USB drive when connected
# Copy files directly from your project directory:
cp code.py /Volumes/CIRCUITPY/
cp settings.toml /Volumes/CIRCUITPY/
cp -r lib/ /Volumes/CIRCUITPY/

# Verify files copied successfully
ls /Volumes/CIRCUITPY/
```

**Serial Communication for Debugging:**
```bash
# Find the MagTag device (look for usbmodem)
ls /dev/cu.usbmodem*

# Connect using tio (preferred)
tio /dev/cu.usbmodem*

# Or use screen (alternative)
screen /dev/cu.usbmodem* 115200

# To exit tio: Ctrl+T then Q
# To exit screen: Ctrl+A then K, then Y
```

**Project Structure in Cursor:**
```
Project - Adafruit MagTag/
├── MagTag_Life_Timer_Complete_Guide.md
├── code.py                    # Main application
├── settings.toml             # Configuration (don't commit to git)
├── lib/                      # CircuitPython libraries
├── tests/                    # Test scripts
├── hardware_test.py          # Hardware verification
└── README.md                 # Project documentation
```

### 1.2 MagTag Firmware Setup

**CircuitPython Installation:**
1. Download latest CircuitPython UF2 file for MagTag from circuitpython.org
2. Connect MagTag via USB-C
3. Double-press reset button to enter bootloader mode
4. Drag UF2 file to MAGTAG drive
5. Device will restart with CircuitPython installed

**Library Installation:**
```python
# Required CircuitPython libraries (copy to /lib folder):
# - adafruit_magtag
# - adafruit_display_text
# - adafruit_bitmap_font
# - adafruit_datetime
# - adafruit_requests
# - adafruit_esp32spi
```

## Part 2: Project Architecture

### 2.1 Core Components

**Software Architecture:**
```
┌─────────────────────────────────────┐
│           Main Application          │
├─────────────────────────────────────┤
│  ├─ Time Sync Module                │
│  ├─ Life Calculation Engine         │
│  ├─ Display Manager                 │
│  ├─ Configuration Handler           │
│  └─ Error Recovery System           │
├─────────────────────────────────────┤
│         Hardware Abstraction        │
├─────────────────────────────────────┤
│  ├─ E-ink Display Driver            │
│  ├─ WiFi Connection Manager         │
│  ├─ NTP Time Client                 │
│  └─ Power Management                │
└─────────────────────────────────────┘
```

**Data Flow:**
1. **Initialization**: Load configuration, connect WiFi
2. **Time Sync**: Fetch current time from NTP/Adafruit IO
3. **Calculation**: Compute life duration from birth date
4. **Display**: Format and render information on e-ink
5. **Sleep**: Enter deep sleep until next update cycle

### 2.2 Configuration System

**settings.toml Structure:**
```toml
# WiFi Configuration
CIRCUITPY_WIFI_SSID = "your_wifi_network"
CIRCUITPY_WIFI_PASSWORD = "your_wifi_password"

# Adafruit IO (optional for enhanced time services)
ADAFRUIT_AIO_USERNAME = "your_username"
ADAFRUIT_AIO_KEY = "your_api_key"

# Personal Configuration
BIRTH_DATE = "1990-01-15"
BIRTH_TIME = "14:30:00"
BIRTH_TIMEZONE = "America/New_York"
DISPLAY_NAME = "Your Name"

# Family Members (optional)
FAMILY_MEMBER_1_NAME = "Partner"
FAMILY_MEMBER_1_BIRTH = "1985-03-22 09:15:00"
FAMILY_MEMBER_1_TIMEZONE = "America/New_York"

# Update Schedule
UPDATE_INTERVAL_MINUTES = 5
DEEP_SLEEP_ENABLED = true
```

## Part 3: Step-by-Step Implementation Plan

### Phase 1: Basic Time Display (Days 1-2)

**Objective**: Get basic time synchronization and display working

**Tasks:**
1. Create basic CircuitPython script using Cursor
2. Implement WiFi connection
3. Fetch current time from NTP
4. Display current date/time on screen
5. Test power consumption and sleep modes

**Cursor Workflow:**
- Create files directly in Cursor with AI assistance
- Use integrated terminal for file transfer to MagTag
- Use `tio` or `screen` for real-time debugging
- Leverage Cursor's code completion and error detection

**Key Files to Create:**
- `code.py` (main application)
- `settings.toml` (configuration)
- `lib/` (CircuitPython libraries directory)
- `hardware_test.py` (basic hardware verification)

### Phase 2: Life Timer Core (Days 3-4)

**Objective**: Implement life duration calculations

**Tasks:**
1. Create birth date parsing system
2. Implement duration calculation algorithm
3. Add timezone handling
4. Create formatted display output
5. Test accuracy with known dates

**Algorithm Pseudocode:**
```python
def calculate_life_duration(birth_datetime, current_datetime):
    total_seconds = (current_datetime - birth_datetime).total_seconds()

    years = total_seconds // (365.25 * 24 * 3600)
    remaining_seconds = total_seconds % (365.25 * 24 * 3600)

    months = remaining_seconds // (30.44 * 24 * 3600)  # Average month
    remaining_seconds %= (30.44 * 24 * 3600)

    weeks = remaining_seconds // (7 * 24 * 3600)
    remaining_seconds %= (7 * 24 * 3600)

    days = remaining_seconds // (24 * 3600)
    remaining_seconds %= (24 * 3600)

    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60

    return {
        'years': int(years),
        'months': int(months),
        'weeks': int(weeks),
        'days': int(days),
        'hours': int(hours),
        'minutes': int(minutes),
        'seconds': int(seconds)
    }
```

### Phase 3: Display Optimization (Days 5-6)

**Objective**: Create visually appealing and readable display layout

**Tasks:**
1. Design display layout for 296x128 screen
2. Implement font selection and sizing
3. Add graphical elements (progress bars, icons)
4. Optimize for e-ink refresh characteristics
5. Test readability in various lighting conditions

**Display Layout Design:**
```
┌─────────────────────────────────────┐
│  Life Timer - [Your Name]          │
├─────────────────────────────────────┤
│                                     │
│  🎂 32 years, 5 months, 2 weeks    │
│     15 days, 8 hours, 42 minutes   │
│     and 18 seconds young            │
│                                     │
│  ⏰ Next update: 14:35             │
│  🔋 Battery: 85%                   │
│  📶 WiFi: Connected                │
└─────────────────────────────────────┘
```

### Phase 4: Advanced Features (Days 7-8)

**Objective**: Add family members and advanced functionality

**Tasks:**
1. Implement multi-person display cycling
2. Add button controls for manual updates
3. Create battery monitoring system
4. Implement error handling and recovery
5. Add visual/audio notifications

### Phase 5: Testing & Optimization (Days 9-10)

**Objective**: Ensure reliability and optimize power consumption

**Tasks:**
1. Stress test WiFi connectivity
2. Optimize sleep/wake cycles
3. Test battery life under various conditions
4. Implement watchdog timer for crash recovery
5. Create debugging and diagnostic modes

## Part 4: Code Implementation Templates

### 4.1 Main Application Structure

```python
# code.py - Main MagTag Life Timer Application

import time
import board
import busio
import wifi
import socketpool
import adafruit_requests
from adafruit_magtag.magtag import MagTag
from adafruit_datetime import datetime, timezone
import supervisor

# Initialize MagTag
magtag = MagTag()

# Configuration
BIRTH_DATE = "1990-01-15"
BIRTH_TIME = "14:30:00"
BIRTH_TIMEZONE = "America/New_York"
UPDATE_INTERVAL = 300  # 5 minutes

def connect_wifi():
    """Connect to WiFi network"""
    try:
        wifi.radio.connect(
            os.getenv("CIRCUITPY_WIFI_SSID"),
            os.getenv("CIRCUITPY_WIFI_PASSWORD")
        )
        print("Connected to WiFi")
        return True
    except Exception as e:
        print(f"WiFi connection failed: {e}")
        return False

def get_current_time():
    """Fetch current time from NTP server"""
    # Implementation here
    pass

def calculate_life_duration(birth_dt, current_dt):
    """Calculate life duration breakdown"""
    # Implementation here
    pass

def update_display(duration_data):
    """Update the MagTag display"""
    # Implementation here
    pass

def main():
    """Main application loop"""
    while True:
        try:
            if connect_wifi():
                current_time = get_current_time()
                duration = calculate_life_duration(birth_datetime, current_time)
                update_display(duration)

            # Sleep until next update
            time.sleep(UPDATE_INTERVAL)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main()
```

### 4.2 AI Assistance Prompts for Development

**Using Cursor's AI for CircuitPython Development:**

You can use these prompts directly in Cursor to get targeted help with your MagTag project:

**For Time Handling:**
> "Help me implement precise timezone-aware datetime calculations in CircuitPython for the MagTag. I need to handle birth dates with timezone conversion and calculate exact durations accounting for leap years, daylight saving time changes, and variable month lengths. Provide complete working code."

**For Display Layout:**
> "Design an optimal text layout for a 296x128 pixel grayscale e-ink display showing life duration statistics. Consider font readability, information hierarchy, and e-ink refresh characteristics. Provide CircuitPython code using the adafruit_magtag library for the display formatting."

**For Power Optimization:**
> "Optimize CircuitPython code for MagTag deep sleep and WiFi power management. The device should wake every 5 minutes, sync time, update display, then sleep. Minimize power consumption while maintaining accurate timekeeping. Show the complete power management implementation."

**For Error Handling:**
> "Implement robust error handling and recovery mechanisms for a WiFi-connected MagTag application. Handle network timeouts, malformed time data, display errors, and automatic retry logic with exponential backoff. Provide complete exception handling code."

**For Debugging:**
> "Create a comprehensive debugging system for CircuitPython on MagTag that can log errors, monitor system state, and provide diagnostic information through serial output. Include memory usage tracking and WiFi status monitoring."

**Cursor-Specific Development Tips:**
- Use Cursor's autocomplete for CircuitPython library imports
- Leverage the AI chat for real-time coding assistance
- Use the integrated terminal for immediate testing
- Take advantage of Cursor's code analysis for catching errors early

## Part 5: Testing & Validation Plan

### 5.1 Unit Testing Strategy

**Time Calculation Tests:**
- Test with various birth dates and current times
- Verify leap year handling
- Test timezone conversions
- Validate edge cases (midnight, year boundaries)

**Display Tests:**
- Test text rendering at different sizes
- Verify layout with long/short names
- Test refresh rates and partial updates

**Connectivity Tests:**
- Test WiFi connection/reconnection
- Simulate network timeouts
- Test offline graceful degradation

### 5.2 Integration Testing

**End-to-End Scenarios:**
1. Fresh boot with empty memory
2. Normal operation cycle (wake, sync, display, sleep)
3. Network interruption recovery
4. Low battery behavior
5. Button interaction testing

**Performance Benchmarks:**
- WiFi connection time: < 10 seconds
- NTP sync time: < 5 seconds
- Display update time: < 3 seconds
- Sleep current: < 20µA
- Active current: < 100mA

## Part 6: Deployment & Maintenance

### 6.1 Installation Checklist

**Pre-deployment:**
- [ ] CircuitPython firmware updated
- [ ] All libraries installed in /lib
- [ ] settings.toml configured with personal data
- [ ] Initial functionality test completed
- [ ] Battery installed and tested

**Deployment:**
- [ ] Upload final code.py to MagTag
- [ ] Verify WiFi connectivity in target location
- [ ] Test display in target lighting conditions
- [ ] Set up monitoring/debugging access

### 6.2 Maintenance Schedule

**Weekly:**
- Check battery level
- Verify time accuracy
- Review any error logs

**Monthly:**
- Update CircuitPython libraries
- Backup configuration
- Clean display if needed

**Quarterly:**
- Review and update timezone data
- Check for firmware updates
- Perform full functionality test

## Part 7: Troubleshooting Guide

### 7.1 Common Issues

**WiFi Connection Problems:**
- Verify SSID/password in settings.toml
- Check signal strength at device location
- Test with mobile hotspot for isolation

**Time Sync Issues:**
- Verify NTP server accessibility
- Check timezone configuration
- Test with Adafruit IO time service

**Display Problems:**
- Check for proper library installation
- Verify font files are present
- Test with minimal display code

**Power Issues:**
- Monitor battery voltage levels
- Check sleep mode implementation
- Verify deep sleep current draw

### 7.2 Debug Mode Implementation

```python
# Debug mode activation via button press
DEBUG_MODE = False

def debug_info():
    """Display debug information"""
    if DEBUG_MODE:
        print(f"WiFi: {wifi.radio.connected}")
        print(f"Battery: {magtag.peripherals.battery}")
        print(f"Memory: {gc.mem_free()}")
        print(f"Time: {time.time()}")
```

## Part 8: Hardware Setup Instructions

### 8.1 Physical Assembly

**Battery Installation:**
1. Connect 3x AAA battery holder to MagTag JST connector
2. Ensure proper polarity (red = positive, black = negative)
3. Install fresh alkaline batteries for best performance
4. Test power-on by pressing reset button

**Mounting Options:**
- Desktop stand: Use included acrylic stand
- Wall mount: 3D print custom bracket or use adhesive strips
- Portable: Add lanyard hole or clip attachment

### 8.2 Initial Hardware Testing

```python
# hardware_test.py - Basic hardware verification
import board
import time
from adafruit_magtag.magtag import MagTag

magtag = MagTag()

# Test display
magtag.add_text(text_position=(10, 10), text="Hardware Test")
magtag.add_text(text_position=(10, 30), text="Display: OK")

# Test buttons
print("Press buttons to test...")
while True:
    if magtag.peripherals.button_a_pressed:
        print("Button A pressed")
    if magtag.peripherals.button_b_pressed:
        print("Button B pressed")
    if magtag.peripherals.button_c_pressed:
        print("Button C pressed")
    if magtag.peripherals.button_d_pressed:
        print("Button D pressed")

    # Test battery level
    battery_voltage = magtag.peripherals.battery
    print(f"Battery: {battery_voltage:.2f}V")

    time.sleep(1)
```

## Part 9: Advanced Features & Extensions

### 9.1 Future Enhancement Ideas

**Display Enhancements:**
- Graphical progress bars for life milestones
- Weather integration for current conditions
- Calendar integration for upcoming birthdays
- Custom fonts and icon sets

**Data Features:**
- Life statistics (total heartbeats, breaths, steps)
- Goal tracking (days until retirement, anniversaries)
- Historical data logging to SD card
- Web dashboard for data visualization

**Hardware Extensions:**
- Motion sensor for wake-on-movement
- Temperature/humidity sensors
- External LED status indicators
- Audio alerts for milestones

### 9.2 IoT Integration Options

**Cloud Services:**
- IFTTT integration for automation
- Google Calendar sync for events
- Social media milestone sharing
- Family member status sharing

**Home Automation:**
- Smart home integration via MQTT
- Alexa/Google Assistant voice queries
- Notification system integration
- Smart lighting mood indicators

## Part 10: Learning Resources & References

### 10.1 Essential Documentation

**CircuitPython Resources:**
- [CircuitPython Documentation](https://docs.circuitpython.org/)
- [Adafruit CircuitPython Library Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)
- [MagTag Guide](https://learn.adafruit.com/adafruit-magtag)

**Time & Date Handling:**
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html)
- [Timezone handling best practices](https://pytz-deprecation-shim.readthedocs.io/)
- [NTP protocol overview](https://en.wikipedia.org/wiki/Network_Time_Protocol)

### 10.2 Community & Support

**Forums & Communities:**
- [Adafruit Discord Server](https://adafru.it/discord)
- [CircuitPython Community Forum](https://forums.adafruit.com/viewforum.php?f=60)
- [Reddit r/CircuitPython](https://www.reddit.com/r/circuitpython/)

**Code Examples & Projects:**
- [Adafruit Learning System](https://learn.adafruit.com/)
- [CircuitPython GitHub Examples](https://github.com/adafruit/circuitpython)
- [Community Projects Showcase](https://blog.adafruit.com/category/circuitpython/)

## Conclusion

This comprehensive guide provides everything needed to create your MagTag Life Timer project. The modular approach allows for incremental development and testing, while the detailed architecture ensures scalability for future enhancements.

**Project Summary:**
- **Estimated Timeline**: 10 days for full implementation
- **Skill Level**: Intermediate (with provided templates and AI assistance)
- **Power Consumption**: Estimated 3-6 months on 3x AAA batteries with 5-minute updates
- **Learning Value**: IoT fundamentals, time synchronization, display management, and power optimization

The project combines practical IoT development with meaningful personal technology, creating both an educational experience and a unique personal device that celebrates the passage of time.

**Next Steps:**
1. Set up development environment
2. Install CircuitPython on MagTag
3. Create basic configuration files
4. Begin Phase 1 implementation
5. Test and iterate through each phase

Remember to document your progress and don't hesitate to use the provided AI assistance prompts when you encounter challenges. Good luck with your MagTag Life Timer project!