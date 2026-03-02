import pytest
from unittest.mock import patch, MagicMock
from mouse_monitor import MouseMonitor


@pytest.fixture
def monitor():
    with patch('mouse_monitor.MouseMonitor._setup_logging'):
        return MouseMonitor()


class TestMouseMonitor:

    def test_is_bluetooth_on_logic(self, monitor):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="1", returncode=0)
            assert monitor.is_bluetooth_on() is True
            mock_run.return_value = MagicMock(stdout="0", returncode=0)
            assert monitor.is_bluetooth_on() is False

    def test_get_battery_level_success(self, monitor):
        mock_output = """
        +-o AppleDeviceManagementHIDEventService  <class AppleDeviceManagementHIDEventService>
          {
            "Product" = "Magic Mouse"
            "BatteryPercent" = 65
            "MOLowBattery" = No
          }
        """
        with patch('mouse_monitor.MouseMonitor._ioreg_dump', return_value=mock_output):
            assert monitor.get_battery_level() == 65

    def test_get_battery_level_not_found(self, monitor):
        mock_output = "No devices found"
        with patch('mouse_monitor.MouseMonitor._ioreg_dump', return_value=mock_output):
            assert monitor.get_battery_level() is None

    def test_get_battery_level_regex_failure(self, monitor):
        mock_output = '"Product" = "Magic Mouse", "SomethingElse" = 100'
        with patch('mouse_monitor.MouseMonitor._ioreg_dump', return_value=mock_output):
            assert monitor.get_battery_level() is None

    def test_notification_logic_foundation(self, monitor):
        with patch('mouse_monitor.IS_MAC', True), \
                patch('mouse_monitor.NSUserNotification') as mock_notif, \
                patch('mouse_monitor.NSUserNotificationCenter') as mock_center:
            mock_center.defaultUserNotificationCenter.return_value = MagicMock()
            monitor.notify("Test", "Message")
            assert mock_notif.alloc.called

    def test_connection_state_change(self, monitor):
        monitor.is_connected = True
        with patch('mouse_monitor.MouseMonitor.get_battery_level', return_value=None), \
                patch('mouse_monitor.MouseMonitor.is_bluetooth_on', return_value=True), \
                patch('time.sleep', side_effect=InterruptedError):
            try:
                monitor.run()
            except (InterruptedError, SystemExit):
                pass
            assert monitor.is_connected is False

    def test_check_os_failure(self, monitor):
        with patch('sys.platform', 'win32'), \
                patch('sys.exit') as mock_exit, \
                patch('builtins.print') as mock_print:
            monitor.check_os()
            mock_exit.assert_called_once_with(1)
            args, _ = mock_print.call_args
            assert "Error: FlipMeOver requires macOS" in args[0]

    def test_check_os_success(self, monitor):
        with patch('sys.platform', 'darwin'), \
                patch('sys.exit') as mock_exit:
            monitor.check_os()
            assert not mock_exit.called