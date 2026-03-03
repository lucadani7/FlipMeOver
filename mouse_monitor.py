import logging
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    from Foundation import NSUserNotification, NSUserNotificationCenter
    IS_MAC = True
except ImportError:
    NSUserNotification = None
    NSUserNotificationCenter = None
    IS_MAC = False

APP_NAME = "FlipMeOver"
THRESHOLD = 15


class MouseMonitor:
    _BLUETOOTH_PREFS_PATH = "/Library/Preferences/com.apple.Bluetooth"
    _BLUETOOTH_POWER_STATE_KEY = "ControllerPowerState"
    _DEFAULTS_READ_CMD = ("defaults", "read")
    _IOREG_CLASSES = ["AppleDeviceManagementHIDEventService", "AppleMultitouchMouse"]
    _BATTERY_RE = re.compile(r'"BatteryPercent"\s*=\s*(\d+)')

    def __init__(self):
        self._setup_logging()
        self.is_connected = False
        logging.info("FlipMeOver initialized.")

    @staticmethod
    def _setup_logging():
        """
        Sets up the logging configuration for the application.
        This method creates a directory structure for storing log files if it does not
        already exist and initializes logging settings. The logs will be stored in the
        file `flip_me_over.log` located under the user's home directory, specifically
        in the path `~/Library/Logs/FlipMeOver/`. Additionally, the log file will
        contain timestamps, logging level, and the logged message in its format.
        """
        log_dir = Path.home() / "Library/Logs/FlipMeOver"
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "flip_me_over.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            force=True
        )

    @staticmethod
    def check_os():
        """
        Checks if the operating system is macOS and terminates the program if it is not.
        This static utility method is designed to ensure that the program is running on
        a macOS system. If the detected operating system is not macOS, it prints an
        error message indicating the required and detected operating systems and
        terminates the program execution.
        """
        if sys.platform != "darwin":
            print(f"Error: FlipMeOver requires macOS. Detected: {platform.system()}")
            sys.exit(1)

    @staticmethod
    def notify(title, msg):
        """
        Sends a notification to the user through macOS's Notification Center. If the macOS Notification
        API is unavailable, it attempts to use an AppleScript alternative to display the notification.
        Logs the notification attempt, success, or failure.
        Note: This method is static. It does not depend on the object instance state.
        """
        if not IS_MAC or NSUserNotification is None:
            logging.warning(f"Notification suppressed: {title} - {msg}")
            return
        try:
            notification = NSUserNotification.alloc().init()
            notification.setTitle_(title)
            notification.setInformativeText_(msg)
            center = NSUserNotificationCenter.defaultUserNotificationCenter()
            if center is not None:
                center.deliverNotification_(notification)
                logging.info(f"Notification sent via Foundation: {title}")
            else:
                script = f'display notification "{msg}" with title "{title}"'
                subprocess.run(["osascript", "-e", script])
                logging.info(f"Notification sent via osascript: {title}")
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")

    @staticmethod
    def _read_defaults(domain, key):
        """
        Reads a specific value from the macOS defaults system using the provided domain and key.
        The method interacts with macOS's `defaults` command to retrieve configuration
        settings for specific applications or system components. The command output is
        processed and returned as a string. Errors and warnings from the `defaults`
        command are suppressed.
        """
        return subprocess.check_output([*MouseMonitor._DEFAULTS_READ_CMD, domain, key], encoding="utf-8", stderr=subprocess.DEVNULL).strip()

    @staticmethod
    def _ioreg_dump(ioreg_class):
        return subprocess.check_output(["ioreg", "-rc", ioreg_class], encoding='utf-8', stderr=subprocess.DEVNULL)

    @staticmethod
    def is_bluetooth_on():
        """
        Since macOS API can be unreliable on Apple Silicon, we use this
        only as a secondary hint. The primary source of truth is the battery data itself.
        """
        try:
            cmd = ["defaults", "read", "/Library/Preferences/com.apple.Bluetooth", "ControllerPowerState"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
            return res.stdout.strip() == "1"
        except (subprocess.SubprocessError, FileNotFoundError):
            return True

    @classmethod
    def get_battery_level(cls):
        """
        Retrieves the battery level for Magic Mouse devices.
        This class method identifies connected Magic Mouse devices by parsing the system's
        ioregistry information. It specifically looks for devices with the "MOLowBattery"
        attribute or the "Product" attribute set to "Magic Mouse". Once identified, it extracts
        the battery level using a predefined regular expression.
        """
        try:
            output = cls._ioreg_dump("AppleDeviceManagementHIDEventService")
            devices = output.split("+-o")
            for device_info in devices:
                if 'MOLowBattery' in device_info or '"Product" = "Magic Mouse"' in device_info:
                    match = cls._BATTERY_RE.search(device_info)
                    if match:
                        level = int(match.group(1))
                        return level
        except subprocess.SubprocessError as e:
            logging.error(f"System command 'ioreg' failed: {e}")
            return None
        except ValueError as e:
            logging.error(f"Data parsing error: {e}")
            return None

    def run(self):
        """
        Continuously monitors the battery level of a Magic Mouse and provides alerts when the
        battery is low, ensuring the user is informed early. The method checks the operating system
        compatibility before starting and maintains a regular monitoring interval. It also handles
        notification events for mouse connection, disconnection, and low battery scenarios.
        """
        self.check_os()
        print("\n" + "=" * 30)
        print(f"{APP_NAME.upper()} CONTROL PANEL")
        print("=" * 30)
        print(f"Monitoring Interval: 300s (Threshold: {THRESHOLD}%)")
        print("Press Ctrl+C to exit safely.")
        print("-" * 30 + "\n")
        try:
            while True:
                current_battery = self.get_battery_level()
                if current_battery is not None:
                    print(f"[{time.strftime('%H:%M:%S')}] 🔋 Mouse Found: {current_battery}%")
                    if not self.is_connected:
                        self.notify(APP_NAME, f"Mouse Connected! Battery: {current_battery}%")
                        self.is_connected = True
                    if current_battery <= THRESHOLD:
                        print(f"\n[!] ALERT: Battery is {current_battery}%!")
                        self.notify(APP_NAME, f"Battery low ({current_battery}%). Flip me over!")
                        print("Alert sent. Silencing for 2 hours...")
                        time.sleep(7200)
                else:
                    if not self.is_connected:
                        print(f"[{time.strftime('%H:%M:%S')}] ⏳ Searching for Magic Mouse...", flush=True)
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] 🔍 Mouse lost. Check Bluetooth or Mouse power.")
                        self.is_connected = False
                time.sleep(300)
        except KeyboardInterrupt:
            print("\n\n👋 FlipMeOver stopped by user. Happy sketching!")
            sys.exit(0)