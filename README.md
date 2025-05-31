# Adafruit MagTag Multi-Person Life Timer

## Description

This project turns an Adafruit MagTag into a "Life Timer" that displays the age of multiple configured individuals in years, months, weeks, days, hours, minutes, and seconds. It fetches the current time from the internet via Wi-Fi and updates the display periodically. It also shows the current date, time, timezone, Wi-Fi connection status, and battery percentage.

## Hardware Requirements

*   Adafruit MagTag (ESP32-S2 with E-Ink Display)
*   USB-C cable for programming and power (or battery for standalone operation)

## Software Requirements

*   **CircuitPython:** This project is designed for CircuitPython.
    *   Download the latest CircuitPython version for the Adafruit MagTag from [circuitpython.org](https://circuitpython.org/board/adafruit_magtag_2.9_grayscale/).
    *   Install CircuitPython on your MagTag by dragging the downloaded `.uf2` file to the `MAGTAGBOOT` drive.
*   **Code Editor/Serial Terminal:**
    *   A code editor like Mu, Thonny, VS Code with CircuitPython extensions, or Cursor.
    *   A serial terminal tool like `tio`, PuTTY, or Mu's built-in terminal for debugging.

## Library Installation

This project relies on several CircuitPython libraries. You will need to copy these libraries from the Adafruit CircuitPython Library Bundle to the `lib` folder on your MagTag's `CIRCUITPY` drive.

1.  Download the appropriate [Adafruit CircuitPython Library Bundle](https_old://circuitpython.org/libraries) for your version of CircuitPython (e.g., 9.x bundle).
2.  Unzip the bundle.
3.  From the `lib` folder of the unzipped bundle, copy the following files/folders into the `lib` folder on your MagTag's `CIRCUITPY` drive:
    *   `adafruit_requests.mpy`
    *   `adafruit_display_text` (folder)
    *   `adafruit_magtag` (folder - this contains `magtag.mpy`, `graphics.mpy`, `network.mpy`, `peripherals.mpy`, etc.)
    *   `adafruit_minimqtt` (folder or `.mpy` file - dependency for MagTag library)
    *   `adafruit_ticks.mpy` (dependency for `adafruit_minimqtt`)
    *   `simpleio.mpy` (or `adafruit_simpleio.mpy` - dependency for MagTag library)

    *Note: Some libraries like `wifi`, `socketpool`, `ssl`, `os`, `displayio`, `terminalio`, `gc`, `rtc`, `time`, and `board` are built into CircuitPython and do not need to be manually added to the `lib` folder.*

## File Structure

Once set up, your MagTag's `CIRCUITPY` drive should look something like this:

```
CIRCUITPY/
├── code.py                 # The main application script
├── settings.toml           # Your personal configuration (see below)
├── lib/
│   ├── adafruit_requests.mpy
│   ├── adafruit_display_text/
│   │   └── ...
│   ├── adafruit_magtag/
│   │   └── ...
│   ├── adafruit_minimqtt/  # or adafruit_minimqtt.mpy
│   │   └── ...
│   ├── adafruit_ticks.mpy
│   └── simpleio.mpy        # or adafruit_simpleio.mpy
└── ... (other files or folders you might have)
```

This repository also includes:
*   `.gitignore`: Specifies intentionally untracked files by Git (like `settings.toml` and the `lib/` folder).
*   `settings.toml.example`: A template for your `settings.toml` file.

## Configuration (`settings.toml`)

Sensitive information and personal details are stored in a `settings.toml` file in the root of the `CIRCUITPY` drive. This file is **not** and **should not** be committed to version control.

1.  Copy the provided `settings.toml.example` file to a new file named `settings.toml` in the root of your `CIRCUITPY` drive.
2.  Edit `settings.toml` with your specific details:
    *   `CIRCUITPY_WIFI_SSID`: Your Wi-Fi network name.
    *   `CIRCUITPY_WIFI_PASSWORD`: Your Wi-Fi network password.
    *   `DISPLAY_NAME`: Name of the primary person.
    *   `BIRTH_DATE`: Birth date of the primary person (YYYY-MM-DD).
    *   `BIRTH_TIME`: Birth time of the primary person (HH:MM:SS or HH:MM).
    *   `FAMILY_MEMBER_1_NAME` to `FAMILY_MEMBER_4_NAME`: Names for additional family members.
    *   `FAMILY_MEMBER_1_BIRTH_DATE` to `FAMILY_MEMBER_4_BIRTH_DATE`: Birth dates for additional family members.
    *   `FAMILY_MEMBER_1_BIRTH_TIME` to `FAMILY_MEMBER_4_BIRTH_TIME`: Birth times for additional family members.
    *   `UPDATE_INTERVAL_MINUTES`: How often the display refreshes (e.g., "5" for 5 minutes).

    Fill in details for as many family members as you want to display (up to 4 additional, for a total of 5 people). Leave fields blank for unused family member slots.

## Running the Project

1.  Ensure CircuitPython is installed on your MagTag.
2.  Ensure all required libraries are in the `lib` folder.
3.  Ensure `code.py` is present in the root of the `CIRCUITPY` drive.
4.  Ensure `settings.toml` is correctly configured in the root of the `CIRCUITPY` drive.
5.  Connect your MagTag to a power source (USB or battery).
6.  The `code.py` script will run automatically.

The MagTag will connect to Wi-Fi, fetch the current time, and then display the calculated ages and other information on the E-Ink screen. The display will refresh at the interval specified in `UPDATE_INTERVAL_MINUTES`.

## Troubleshooting/Notes

*   **Blank Screen:** If the screen is blank, check your USB connection or battery. Connect to the serial console to see error messages or logs. Ensure `magtag.display` is used for display operations if modifying the code.
*   **Wi-Fi Connection Issues:** Double-check your SSID and password in `settings.toml`. Ensure your Wi-Fi is 2.4GHz, as the ESP32-S2 typically doesn't support 5GHz.
*   **Time Sync Failures (`Name or service not known`, etc.):** This can indicate DNS or general network issues. A short delay (`time.sleep(1)`) was added after Wi-Fi connection in `code.py` to help stabilize the network stack, which often resolves this.
*   **`ImportError`:** If you see an `ImportError` on the serial console, make sure the required library is present in the `lib` folder and that all its dependencies are also present.
*   **Serial Output:** The script prints diagnostic information to the serial console, which is very helpful for debugging.
*   **Power Consumption:** To save power, the device sleeps between updates. For true deep sleep and significantly longer battery life, the `alarm` module would need to be integrated, which is a more advanced topic.

---
