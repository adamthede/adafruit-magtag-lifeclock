# Project Report: Adafruit MagTag Multi-Person Life Timer

**Date:** 2025-05-24
**Device:** Adafruit MagTag - 2.9" Grayscale E-Ink WiFi Display

## 1. Project Goal

To develop a CircuitPython application for the Adafruit MagTag that:
1.  Connects to WiFi to fetch the current time from an internet source.
2.  Calculates and displays the precise age (in years, months, weeks, days, hours, minutes, and seconds) for multiple individuals.
3.  Configuration data (WiFi credentials, birth information for multiple people) is stored in a `settings.toml` file.
4.  The display updates at a regular interval (e.g., every 5 minutes).
5.  The on-screen display provides clear information about the current time, WiFi status, and the ages of configured individuals.

## 2. Hardware & Software Environment

*   **Hardware:** Adafruit MagTag ESP32-S2 with 2.9" e-ink display.
*   **Firmware:** CircuitPython (Version 9.2.7 during development).
*   **Primary Libraries Used:**
    *   `time`: For time structures and operations.
    *   `board`: For hardware pin definitions.
    *   `wifi`: For WiFi connectivity.
    *   `socketpool`: For network socket management.
    *   `ssl`: For HTTPS connections.
    *   `os`: For accessing environment variables (from `settings.toml`).
    *   `displayio`: Core library for managing the display.
    *   `terminalio`: For the default font.
    *   `adafruit_display_text.label`: For creating text labels on the display.
    *   `gc`: For garbage collection and memory monitoring.
    *   `rtc`: For setting and interacting with the Real Time Clock.
    *   `adafruit_requests`: For simplified and robust HTTP/HTTPS requests.
*   **Development Environment:**
    *   Cursor IDE for code editing and project management.
    *   `tio` (terminal I/O utility) for serial communication with the MagTag (REPL access and debugging).
*   **Configuration File:** `settings.toml` for storing all user-specific settings.

## 3. Core Functionality Implemented

### 3.1. Configuration Management
*   A `settings.toml` file is used to store:
    *   WiFi SSID and password (`CIRCUITPY_WIFI_SSID`, `CIRCUITPY_WIFI_PASSWORD`).
    *   Birth date, birth time, and display name for a primary individual (`BIRTH_DATE`, `BIRTH_TIME`, `DISPLAY_NAME`).
    *   Birth date, birth time, and display name for up to four additional family members (e.g., `FAMILY_MEMBER_1_NAME`, `FAMILY_MEMBER_1_BIRTH_DATE`, `FAMILY_MEMBER_1_BIRTH_TIME`, etc.).
    *   Update interval in minutes (`UPDATE_INTERVAL_MINUTES`).
*   The script loads these settings at startup using `os.getenv()`.

### 3.2. WiFi Connectivity
*   The `connect_wifi()` function handles connection to the WiFi network specified in `settings.toml`.
*   It provides a boolean status of the connection success.

### 3.3. Time Synchronization
*   The `get_http_time()` function fetches the current time from `worldtimeapi.org` using an HTTPS GET request to a specific timezone endpoint (e.g., `https://worldtimeapi.org/api/timezone/America/Chicago`).
*   It uses the `adafruit_requests` library for robust HTTPS communication.
*   The JSON response is parsed to extract:
    *   The full datetime string (e.g., "2024-05-16T10:30:00.123456-05:00").
    *   The timezone abbreviation (e.g., "CST", "CDT").
*   The MagTag's onboard Real Time Clock (RTC) is set using the parsed local time components from the API's `datetime` field.
*   The function returns a dictionary containing the `time.struct_time` object and the timezone abbreviation, or `None` on failure.

### 3.4. Age Calculation
*   The `parse_birth_params(date_str, time_str, person_name_for_log)` function parses individual birth date (YYYY-MM-DD) and time (HH:MM:SS or HH:MM) strings.
*   The `calculate_life(birth_tuple, current_time_obj)` function calculates the duration between a given birth `struct_time` and the current `struct_time`.
    *   It performs detailed calculations to break down the age into years, months, weeks, days, hours, minutes, and seconds.
    *   This involves handling "borrowing" across time units (e.g., negative seconds borrowing from minutes).
    *   A helper function `_days_in_month(year, month)` is used to accurately determine the number of days to borrow when calculating day differences.
*   The result is a dictionary containing all components of the age.

### 3.5. Display Management & Formatting
*   The script initializes a `displayio.Group` and adds six text labels using `terminalio.FONT`.
*   The `update_line(line_num, text)` function updates the text of a specific label.
*   E-ink display updates are triggered by `display.refresh()`, followed by `while display.busy: pass` to wait for completion.
*   The display layout is:
    *   **Line 0:** Current time and WiFi status: `Month Day, Year @ H:MMPM TZN | WiFi: [Connected/No WiFi]`
        *   Example: `May 24, 2025 @ 6:30PM CST | WiFi: Connected`
    *   **Lines 1-5:** Age of each configured person (up to 5 people): `PERSON_NAME: Xy, Xmo, Xw, Xd, Xh, Xmin, Xs`
        *   Example: `AT: 46y, 2mo, 3w, 5d, 3h, 38min, 2s`
*   A `format_age_string(life_stats)` helper function formats the age dictionary into the concise single-line string.
*   Unused display lines are cleared.

## 4. Key Code Structures

*   **`main()`:**
    *   Initializes configurations for up to 5 people by reading `settings.toml` keys.
    *   Handles critical failure if the primary person's configuration is missing/invalid.
    *   Enters an infinite loop that executes every `UPDATE_INTERVAL_MINUTES`.
    *   In each loop iteration:
        *   Connects to WiFi.
        *   Fetches and sets the current time.
        *   Formats and displays the time/WiFi status line.
        *   For each configured person:
            *   Calculates their age using `calculate_life()`.
            *   Formats the age string using `format_age_string()`.
            *   Updates the respective display line.
        *   Clears any unused display lines.
        *   Refreshes the e-ink display.
    *   Includes error handling for `KeyboardInterrupt` and general exceptions.
*   **`get_http_time()`:** As described in section 3.3.
*   **`connect_wifi()`:** As described in section 3.2.
*   **`calculate_life()`:** As described in section 3.4.
*   **`parse_birth_params()`:** As described in section 3.4. Handles "YYYY-MM-DD" and "HH:MM:SS" or "HH:MM".
*   **`format_age_string()`:** Creates the abbreviated age string for display.
*   **`update_line()`:** Sets text for a given displayio label.
*   **`_days_in_month()`:** Calculates days in a specific month/year for date arithmetic.
*   **`MONTH_NAMES` list:** Maps month numbers to abbreviated names for display.

## 5. Development Process & Challenges Overcome

The project began with an initial plan outlining the architecture and features. The implementation was iterative, involving several key refinements and troubleshooting steps:

1.  **Initial Time Synchronization:**
    *   The first attempts to get time via plain HTTP failed or were unreliable.
    *   The code was updated to use HTTPS for `worldtimeapi.org`.
2.  **HTTPS Implementation:**
    *   Directly using `ssl.wrap_socket` with `socketpool` led to attribute errors (e.g., `SSLSocket object has no attribute 'recv'`, then no `'read'`).
    *   This was resolved by adopting the `adafruit_requests` library, which abstracts these complexities and provides a more robust way to handle HTTPS requests on CircuitPython.
3.  **Age Calculation Granularity:**
    *   The requirement was to calculate age down to seconds. The `calculate_life` function was developed to handle the complex date and time arithmetic, including borrowing correctly across all units and accounting for varying month lengths.
4.  **E-Ink Display Refresh:**
    *   Initially, the display was not updating, or was updating with errors. Explicit `display.refresh()` calls were added.
    *   This led to "RuntimeError: Refresh too soon". This was mitigated by removing an early, unnecessary refresh call and ensuring sufficient delay between refresh operations (primarily managed by the main loop's 5-minute sleep interval).
5.  **Display Formatting:**
    *   The age display format evolved from multi-line per person to a concise single line using abbreviations (e.g., "y" for years, "mo" for months) to fit more information.
    *   The main time display format was refined to be more user-friendly (e.g., "May 24, 2025 @ 6:30PM CST").
6.  **Multi-Person Scalability:**
    *   The script was refactored from handling one or two hardcoded individuals to dynamically loading and processing up to 5 people based on configurations in `settings.toml`. This involved making parsing functions more generic and redesigning the main loop's loading and display logic.
7.  **Configuration Robustness:**
    *   Error handling was added for parsing birth dates and times, particularly to accommodate `HH:MM` in addition to `HH:MM:SS` for birth times.
    *   The script now includes checks for essential configuration for the primary user.

## 6. Final Setup & Operation

*   The final application consists of `code.py` and `settings.toml` on the MagTag's `CIRCUITPY` drive, with necessary libraries in the `/lib` directory.
*   On power-up (from USB wall adapter or computer), the device runs `code.py`.
*   It connects to WiFi, fetches the current time for `America/Chicago`, sets its RTC, and then calculates and displays the ages for all configured individuals.
*   This process repeats every 5 minutes (or as configured in `UPDATE_INTERVAL_MINUTES`).

This project successfully demonstrates a practical IoT application on the Adafruit MagTag, combining network connectivity, real-time data processing, and dynamic e-ink display updates.
