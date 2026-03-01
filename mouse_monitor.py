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
    _MAGIC_MOUSE_TOKEN = '"Product" = "Magic Mouse"'
    _BATTERY_RE = re.compile(r'"BatteryPercent"\s*=\s*(\d+)')

    def __init__(self):
        self._setup_logging()
        self.is_connected = False
        logging.info("FlipMeOver initialized.")

    @staticmethod
    def _setup_logging():
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
        if sys.platform != "darwin":
            print(f"Error: FlipMeOver requires macOS. Detected: {platform.system()}")
            sys.exit(1)

    @staticmethod
    def notify(title, msg):
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
        return subprocess.check_output([*MouseMonitor._DEFAULTS_READ_CMD, domain, key], encoding="utf-8", stderr=subprocess.DEVNULL).strip()

    @staticmethod
    def _ioreg_dump(ioreg_class):
        return subprocess.check_output(["ioreg", "-rc", ioreg_class], encoding='utf-8', stderr=subprocess.DEVNULL)

    @staticmethod
    def is_bluetooth_on():
        try:
            val = MouseMonitor._read_defaults(MouseMonitor._BLUETOOTH_PREFS_PATH, MouseMonitor._BLUETOOTH_POWER_STATE_KEY)
            return val == "1"
        except (subprocess.SubprocessError, OSError):
            return True

    @classmethod
    def get_battery_level(cls):
        try:
            output = cls._ioreg_dump("AppleDeviceManagementHIDEventService")
            devices = output.split("+-o")
            for device_info in devices:
                if 'MOLowBattery' in device_info or '"Product" = "Magic Mouse"' in device_info:
                    match = cls._BATTERY_RE.search(device_info)
                    if match:
                        level = int(match.group(1))
                        return level
            return None
        except Exception as e:
            logging.error(f"Error in get_battery_level: {e}")
            return None

    def run(self):
        self.check_os()
        print("\n" + "=" * 30)
        print(f"{APP_NAME} CONTROL PANEL")
        print("=" * 30)
        is_bt = self.is_bluetooth_on()
        bt_status = "ON" if is_bt else "OFF"
        print(f"Bluetooth Status: {bt_status}")
        if not is_bt:
            self.notify(APP_NAME, "Bluetooth is OFF. Please enable it.")
        logging.info("FlipMeOver monitor loop started.")
        print(f"Monitoring Interval: 300s")
        print("Press Ctrl+C to exit safely.")
        print("-" * 30 + "\n")
        try:
            while True:
                print(f"[{time.strftime('%H:%M:%S')}] Polling Magic Mouse...", end=" ", flush=True)
                current = self.get_battery_level()
                if current is not None:
                    print(f"FOUND! Battery: {current}%")
                    if not self.is_connected:
                        self.notify(APP_NAME, f"Back in Action! Battery: {current}%")
                        self.is_connected = True
                else:
                    print("NOT FOUND (Sleeping or Charging)")
                    if self.is_connected:
                        self.is_connected = False
                if current is not None and current <= THRESHOLD:
                    print(f"!!! CRITICAL BATTERY: {current}% !!!")
                    self.notify(APP_NAME, f"Battery low ({current}%). Flip me over!")
                    print("Alert sent. Silencing for 2 hours...")
                    time.sleep(7200)
                time.sleep(300)
        except KeyboardInterrupt:
            print("\n\n FlipMeOver stopped by user. Happy sketching!")
            sys.exit(0)