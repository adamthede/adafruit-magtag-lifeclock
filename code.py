# code_fixed_ntp.py - Life Timer with HTTPS Time Sync
import time
import board
import wifi
import socketpool
import ssl
import os
import displayio
import terminalio
from adafruit_display_text import label
import gc
import rtc
import adafruit_requests # Added for HTTPS requests
from adafruit_magtag.magtag import MagTag # Import MagTag class

# Helper function for days in month
def _days_in_month(year, month):
    """Returns the number of days in a given month and year."""
    if month == 2:  # February
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        return 29 if is_leap else 28
    elif month in [4, 6, 9, 11]:  # April, June, September, November
        return 30
    else:  # Jan, Mar, May, Jul, Aug, Oct, Dec
        return 31

# Helper function for pluralizing units
def plural(value, unit):
    """Returns a string with the value and correctly pluralized unit."""
    return f"{value} {unit}{'s' if value != 1 else ''}"

print("Life Timer with HTTPS Time Starting...")
print(f"CircuitPython {os.uname().release}")

# Initialize display - Now handled by MagTag object
# display = board.DISPLAY # Commented out

# Load configuration
wifi_ssid = os.getenv("CIRCUITPY_WIFI_SSID")
wifi_password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
birth_date = os.getenv("BIRTH_DATE")  # "1999-01-01"
birth_time = os.getenv("BIRTH_TIME")  # "12:12:00"
display_name = os.getenv("DISPLAY_NAME")  # "Charles"
update_interval = int(os.getenv("UPDATE_INTERVAL_MINUTES", "5"))

# Configuration for the second person (LB) - This block will be replaced by a loop
# family_member_1_name = os.getenv("FAMILY_MEMBER_1_NAME", "P2")
# family_member_1_birth_date = os.getenv("FAMILY_MEMBER_1_BIRTH_DATE")
# family_member_1_birth_time = os.getenv("FAMILY_MEMBER_1_BIRTH_TIME")

print(f"Config loaded for: {display_name}") # Main display name
# Additional family members will be logged as they are loaded

# Create display group
main_group = displayio.Group()

# White background
color_bitmap = displayio.Bitmap(296, 128, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
main_group.append(bg_sprite)

# Create text labels
text_lines = []
for i in range(6):
    text_area = label.Label(
        terminalio.FONT,
        text="",
        color=0x000000,
        x=5,
        y=15 + (i * 18)
    )
    text_lines.append(text_area)
    main_group.append(text_area)

# Show display
# display.root_group = main_group
# display.refresh() # REMOVED: Initial refresh, will happen at end of first loop pass.
# while display.busy: # REMOVED
#     pass

def update_line(line_num, text):
    """Update a specific line of text"""
    if line_num < len(text_lines):
        text_lines[line_num].text = text[:40]  # Limit length
        print(f"Line {line_num}: {text}")

def connect_wifi():
    """Simple WiFi connection. Returns True on success, False on failure."""
    try:
        # update_line(1, "Connecting to WiFi...") # Will be handled in main
        print(f"Connecting to: {wifi_ssid}")

        wifi.radio.connect(wifi_ssid, wifi_password)
        ip = wifi.radio.ipv4_address

        # update_line(1, f"WiFi: Connected") # Will be handled in main
        print(f"Connected! IP: {ip}")
        return True

    except Exception as e:
        print(f"WiFi failed: {e}")
        # update_line(1, "WiFi: Failed") # Will be handled in main
        return False

def get_http_time():
    """Get time using HTTPS request. Returns a dict {'time_obj': time.struct_time, 'timezone_abbr': str} or None."""
    try:
        # update_line(2, "Getting time via HTTPS...") # Will be handled in main
        print("Getting time via HTTPS...")

        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())

        TIME_URL = "https://worldtimeapi.org/api/timezone/America/Chicago"
        print(f"Fetching time from {TIME_URL}")
        response = requests.get(TIME_URL)
        json_data = response.json()
        response.close()
        print("HTTPS response received")

        if "datetime" in json_data and "unixtime" in json_data and "abbreviation" in json_data:
            datetime_str = json_data["datetime"]
            unix_timestamp = int(json_data["unixtime"])
            timezone_abbr = json_data["abbreviation"]

            print(f"Datetime string from API: {datetime_str}")
            print(f"Unix timestamp from HTTPS: {unix_timestamp}")
            print(f"Timezone abbreviation: {timezone_abbr}")

            try:
                year = int(datetime_str[0:4])
                month = int(datetime_str[5:7])
                day = int(datetime_str[8:10])
                hour = int(datetime_str[11:13])
                minute = int(datetime_str[14:16])
                second = int(datetime_str[17:19])

                local_time_for_rtc = time.struct_time((year, month, day, hour, minute, second, 0, 0, -1))
                rtc.RTC().datetime = local_time_for_rtc
                print(f"RTC set with parsed local time: {local_time_for_rtc.tm_year}-{local_time_for_rtc.tm_mon:02d}-{local_time_for_rtc.tm_mday:02d} {local_time_for_rtc.tm_hour:02d}:{local_time_for_rtc.tm_min:02d}")

            except Exception as e:
                print(f"Failed to parse datetime_str '{datetime_str}': {e}. Falling back to unixtime.")
                rtc.RTC().datetime = time.localtime(unix_timestamp)

            current_time_obj = time.localtime() # Reads from RTC
            return {"time_obj": current_time_obj, "timezone_abbr": timezone_abbr}
        else:
            print("Could not parse required fields (datetime, unixtime, abbreviation) from HTTPS response")
            # Log which fields are missing if possible
            missing_fields = []
            if "datetime" not in json_data: missing_fields.append("datetime")
            if "unixtime" not in json_data: missing_fields.append("unixtime")
            if "abbreviation" not in json_data: missing_fields.append("abbreviation")
            print(f"Missing fields: {', '.join(missing_fields)}")
            return None # Indicate failure more clearly

    except Exception as e:
        print(f"HTTPS time failed: {e}")
        # Fallback time logic remains, but should also return in the new dict format or None
        print("Using fallback time...")
        fallback_time_struct = time.struct_time((2025, 5, 24, 18, 30, 0, 5, 144, 0))
        try:
            rtc.RTC().datetime = fallback_time_struct
            # For fallback, we don't have a live timezone_abbr, so use a placeholder or default
            return {"time_obj": time.localtime(), "timezone_abbr": "EST?"} # Or some other indicator
        except Exception as e2:
            print(f"Fallback RTC set failed: {e2}")
            return None

# Month names for formatting
MONTH_NAMES = [None, "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def _get_battery_percentage(voltage):
    """Converts battery voltage to an approximate percentage."""
    # Typical LiPo range: 3.2V (empty) to 4.2V (full)
    # Clamp voltage to this range first
    voltage = max(3.2, min(4.2, voltage))
    percentage = ((voltage - 3.2) / (4.2 - 3.2)) * 100
    return int(min(100, max(0, percentage))) # Ensure it's 0-100

def parse_birth_params(date_str, time_str, person_name_for_log):
    """Parse birth date and time strings. Handles HH:MM or HH:MM:SS for time."""
    if not date_str or not time_str:
        print(f"Birth date/time not configured for {person_name_for_log}.")
        return None
    try:
        # Parse "YYYY-MM-DD"
        year, month, day = map(int, date_str.split('-'))

        # Parse "HH:MM:SS" or "HH:MM"
        time_parts = time_str.split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 else 0 # Default seconds to 0 if not provided

        return (year, month, day, hour, minute, second)
    except Exception as e:
        print(f"Birth parse failed for {person_name_for_log} ({date_str} {time_str}): {e}")
        return None

def calculate_life(birth_tuple, current_time):
    """Calculate life duration in years, months, weeks, days, hours, minutes, seconds."""
    try:
        birth_year, birth_month, birth_day, birth_hour, birth_min, birth_sec = birth_tuple
        now_year, now_month, now_day, now_hour, now_min, now_sec = (
            current_time.tm_year, current_time.tm_mon, current_time.tm_mday,
            current_time.tm_hour, current_time.tm_min, current_time.tm_sec
        )

        print(f"Calculating detailed age: Birth {birth_year}-{birth_month}-{birth_day} {birth_hour}:{birth_min}:{birth_sec}, Current {now_year}-{now_month}-{now_day} {now_hour}:{now_min}:{now_sec}")

        # Basic sanity check
        if now_year < birth_year or (now_year == birth_year and now_month < birth_month) or \
           (now_year == birth_year and now_month == birth_month and now_day < birth_day):
            print("Current time is before birth time. Cannot calculate age.")
            return None

        # Calculate differences, starting from seconds and borrowing as needed
        secs_diff = now_sec - birth_sec
        mins_diff = now_min - birth_min
        hours_diff = now_hour - birth_hour
        days_diff = now_day - birth_day
        months_diff = now_month - birth_month
        years_diff = now_year - birth_year

        if secs_diff < 0:
            secs_diff += 60
            mins_diff -= 1
        if mins_diff < 0:
            mins_diff += 60
            hours_diff -= 1
        if hours_diff < 0:
            hours_diff += 24
            days_diff -= 1
        if days_diff < 0:
            # Borrow days from the previous month
            prev_month = now_month - 1 if now_month > 1 else 12
            prev_month_year = now_year if now_month > 1 else now_year - 1
            days_diff += _days_in_month(prev_month_year, prev_month)
            months_diff -= 1
        if months_diff < 0:
            months_diff += 12
            years_diff -= 1

        # Calculate weeks and remaining days
        weeks_diff = days_diff // 7
        days_diff %= 7

        print(f"Calculated age: {years_diff}y, {months_diff}m, {weeks_diff}w, {days_diff}d, {hours_diff}h, {mins_diff}min, {secs_diff}s")

        return {
            'years': years_diff,
            'months': months_diff,
            'weeks': weeks_diff,
            'days': days_diff,
            'hours': hours_diff,
            'minutes': mins_diff,
            'seconds': secs_diff,
        }

    except Exception as e:
        print(f"Detailed life calc failed: {e}")
        # Fallback to a simpler calculation or indicate failure
        age_simple = current_time.tm_year - birth_tuple[0]
        if (current_time.tm_mon, current_time.tm_mday) < (birth_tuple[1], birth_tuple[2]):
            age_simple -=1
        return {
            'years': age_simple,
            'months': 0, 'weeks': 0, 'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0, 'fallback': True
        }

# Helper function to format the age string
def format_age_string(life_stats):
    if not life_stats or 'fallback' in life_stats or life_stats['years'] < 0: # also check for negative years
        return "Calculating..."
    return (
        f"{life_stats['years']}y, " +
        f"{life_stats['months']}mo, " +
        f"{life_stats['weeks']}w, " +
        f"{life_stats['days']}d, " +
        f"{life_stats['hours']}h, " +
        f"{life_stats['minutes']}min, " +
        f"{life_stats['seconds']}s"
    )

def main():
    """Main loop"""
    magtag = MagTag() # Initialize MagTag for peripheral access
    magtag_display = magtag.display # Use the display object from MagTag instance

    # Define configurations for people to display
    # (Name_key, BDate_key, BTime_key, Default_Name)
    people_config_keys = [
        ("DISPLAY_NAME", "BIRTH_DATE", "BIRTH_TIME", "P1"), # Primary person
        ("FAMILY_MEMBER_1_NAME", "FAMILY_MEMBER_1_BIRTH_DATE", "FAMILY_MEMBER_1_BIRTH_TIME", "P2"),
        ("FAMILY_MEMBER_2_NAME", "FAMILY_MEMBER_2_BIRTH_DATE", "FAMILY_MEMBER_2_BIRTH_TIME", "P3"),
        ("FAMILY_MEMBER_3_NAME", "FAMILY_MEMBER_3_BIRTH_DATE", "FAMILY_MEMBER_3_BIRTH_TIME", "P4"),
        ("FAMILY_MEMBER_4_NAME", "FAMILY_MEMBER_4_BIRTH_DATE", "FAMILY_MEMBER_4_BIRTH_TIME", "P5"),
    ]

    people_data = [] # To store (name, birth_tuple) for valid people

    for i, (name_key, bdate_key, btime_key, default_name) in enumerate(people_config_keys):
        if i >= 5: # Max 5 people for display lines 1-5
            break
        person_name = os.getenv(name_key, default_name)
        person_bdate = os.getenv(bdate_key)
        person_btime = os.getenv(btime_key)

        if person_name and person_bdate and person_btime:
            birth_tuple = parse_birth_params(person_bdate, person_btime, person_name)
            if birth_tuple:
                people_data.append({"name": person_name, "birth_tuple": birth_tuple})
                print(f"Loaded config for: {person_name}")
            else:
                print(f"Failed to parse birth info for {person_name} from env keys: {name_key}, {bdate_key}, {btime_key}")
                # Optionally add a placeholder if primary person fails, or handle as critical error
                if i == 0: # If primary person (DISPLAY_NAME) fails to load
                    update_line(0, f"FATAL: Config Err for {person_name}")
                    update_line(1, "Check settings.toml & logs.")
                    magtag_display.root_group = main_group # Assign main_group
                    magtag_display.refresh()
                    while magtag_display.busy: pass
                    return # Halt script
        elif i == 0 : # Primary person MUST have all configs
            print(f"FATAL: Missing one or more env vars for primary person: {name_key}, {bdate_key}, {btime_key}")
            update_line(0, f"FATAL: Missing config for {default_name}")
            update_line(1, "Check settings.toml.")
            magtag_display.root_group = main_group # Assign main_group
            magtag_display.refresh()
            while magtag_display.busy: pass
            return # Halt script

    if not people_data: # Should be caught by primary person check, but as a safeguard
        print("FATAL: No valid person data loaded.")
        update_line(0, "FATAL: No people configured.")
        magtag_display.root_group = main_group # Assign main_group
        magtag_display.refresh()
        while magtag_display.busy: pass
        return

    # Ensure main_group (which holds text_labels) is set to the display
    magtag_display.root_group = main_group

    loop_count = 0
    while True:
        try:
            loop_count += 1
            print(f"\n--- Loop {loop_count} ---")

            # 1. WiFi Status & Battery Status
            wifi_is_connected = connect_wifi()
            if wifi_is_connected: # Add a small delay only if connected
                time.sleep(1) # Allow network stack a moment

            wifi_char = "C" if wifi_is_connected else "X" # C for Connected, X for No/Error

            battery_voltage = magtag.peripherals.battery
            battery_percent = _get_battery_percentage(battery_voltage)
            status_str = f"W:{wifi_char} B:{battery_percent}%"

            # 2. Get Current Time
            time_data = None
            time_str_for_display = "Time: Pending..."
            current_time_obj_for_calc = None

            if wifi_is_connected:
                time_data = get_http_time()

            if time_data and time_data["time_obj"]:
                tm = time_data["time_obj"]
                current_time_obj_for_calc = tm

                month_name = MONTH_NAMES[tm.tm_mon] # Using the 3-letter abbreviation from MONTH_NAMES
                year = tm.tm_year
                day = tm.tm_mday

                hour_12 = tm.tm_hour % 12
                if hour_12 == 0:
                    hour_12 = 12

                am_pm = "AM" if tm.tm_hour < 12 else "PM"
                minute = tm.tm_min
                timezone_abbr = time_data.get("timezone_abbr", "TZ?")

                # Using abbreviated month from MONTH_NAMES list
                time_str_for_display = f"{month_name} {day}, {year} @ {hour_12}:{minute:02d}{am_pm} {timezone_abbr}"
            else:
                if not wifi_is_connected:
                    time_str_for_display = "Time: No WiFi"
                elif time_data is None:
                    time_str_for_display = "Time: API Error"
                else:
                    time_str_for_display = "Time: Sync Failed"

            # Combine time and status for Line 0
            update_line(0, f"{time_str_for_display} | {status_str}")

            # 3. Calculate and Display Ages for all configured people
            for i in range(5): # Max 5 display lines for people (lines 1-5)
                display_line_index = i + 1
                if i < len(people_data):
                    person = people_data[i]
                    person_name = person["name"]
                    person_birth_tuple = person["birth_tuple"]

                    age_display_str = f"{person_name}: Error"
                    if current_time_obj_for_calc: # Use the potentially valid time object
                        life_stats = calculate_life(person_birth_tuple, current_time_obj_for_calc)
                        age_display_str = f"{person_name}: {format_age_string(life_stats)}"
                    else:
                        age_display_str = f"{person_name}: Waiting for time..."
                    update_line(display_line_index, age_display_str)
                else:
                    update_line(display_line_index, "") # Clear unused lines

            # Show memory & Refresh display
            free_mem = gc.mem_free()
            print(f"Free memory: {free_mem} bytes")
            magtag_display.refresh() # Use magtag_display
            while magtag_display.busy: # Use magtag_display
                pass

            # Sleep
            print(f"Sleeping {update_interval} minutes...")
            time.sleep(update_interval * 60)

        except KeyboardInterrupt:
            print("Stopped by user")
            break
        except Exception as e:
            print(f"Main error: {e}")
            try:
                update_line(0, "ERROR IN MAIN LOOP")
                error_msg_short = str(e)[:35]
                update_line(1, error_msg_short)
                update_line(2, "See serial console.")
                for i in range(3, 6): # Clear lower lines
                    update_line(i, "")
                magtag_display.refresh() # Use magtag_display
                while magtag_display.busy: # Use magtag_display
                    pass
            except Exception as e2:
                print(f"Error trying to display main loop error: {e2}")
            time.sleep(60)

if __name__ == "__main__":
    main()