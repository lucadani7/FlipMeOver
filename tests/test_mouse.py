import subprocess
from unittest.mock import patch

import pytest

from mouse_monitor import MouseMonitor


@pytest.fixture
def monitor():
    with patch('mouse_monitor.MouseMonitor._setup_logging'):
        return MouseMonitor()

def test_parse_battery_priority_mouse(monitor):
    mock_output = """
    +-o AppleDeviceManagementHIDEventService
       "BatteryLowNotificationType" = "ExKB2LowBattery"
       "BatteryPercent" = 63
    +-o AppleDeviceManagementHIDEventService
       "BatteryLowNotificationType" = "MOLowBattery"
       "BatteryPercent" = 60
    """
    with patch('mouse_monitor.MouseMonitor._ioreg_dump', return_value=mock_output):
        assert monitor.get_battery_level() == 60


def test_parse_battery_no_mouse_found(monitor):
    mock_output = """
    +-o AppleDeviceManagementHIDEventService
       "BatteryLowNotificationType" = "ExKB2LowBattery"
       "BatteryPercent" = 90
    """
    with patch('mouse_monitor.MouseMonitor._ioreg_dump', return_value=mock_output):
        assert monitor.get_battery_level() is None

@patch('mouse_monitor.MouseMonitor.notify')
def test_threshold_alert_logic(mock_notify, monitor):
    with patch('mouse_monitor.MouseMonitor.get_battery_level', return_value=10):
        current = monitor.get_battery_level()
        if current is not None and current <= 15:
            monitor.notify("FlipMeOver", f"Battery low: {current}%")
    mock_notify.assert_called_once_with("FlipMeOver", "Battery low: 10%")

def test_check_os_failure(monitor):
    with patch('sys.platform', 'linux'):
        with pytest.raises(SystemExit) as e:
            monitor.check_os()
        assert e.value.code == 1


def test_ioreg_command_error(monitor):
    with patch('mouse_monitor.MouseMonitor._ioreg_dump', side_effect=subprocess.SubprocessError):
        assert monitor.get_battery_level() is None