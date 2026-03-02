# FlipMeOver
**FlipMeOver** is a lightweight macOS background utility that monitors your Magic Mouse battery level and sends native desktop notifications before your mouse becomes a paperweight!

> **The Problem:** The Magic Mouse has its charging port on the bottom. If you get the system's "Battery Low" alert at 2%, your workflow is already interrupted. **FlipMeOver** notifies you at a custom threshold (e.g., 15%), giving you plenty of time to charge it during a break.
>
> ---

## ✨ Features

-   **Zero-Guess Monitoring:** Specifically tracks Magic Mouse battery levels without getting confused by keyboards or trackpads.
-   **Apple Silicon Ready:** Optimized for M1, M2, and M3 chips (M-series Pro/Max tested).
-   **Robust "Plan B" Logic:** Automatically detects when the mouse is connected or disconnected, regardless of macOS Bluetooth reporting quirks.
-   **Native macOS Notifications:** Uses the `Foundation` API for sleek, integrated system alerts.
-   **Automatic Startup:** Includes an installer that sets up a background `LaunchAgent`.

---

## 🚀 Installation

You don't need to be a developer to install this. Just open your terminal and run:
1. **Clone the repository:**
   ```bash
   git clone https://github.com/lucadani7/FlipMeOver.git
   cd FlipMeOver
   ```
2. **Run the universal installer:** The installer creates a local environment, installs dependencies, and registers the background service.
   ```bash
   chmod +x install.sh && ./install.sh
   ```

---

## 🛠️ How it Works
Unlike apps that rely on inconsistent Bluetooth APIs, FlipMeOver queries the macOS IORegistry directly.
- It looks for the AppleDeviceManagementHIDEventService class.
- It filters specifically for the Magic Mouse product token.
- It parses the battery percentage using a robust Regex pattern.

If the mouse is turned off or Bluetooth is disabled, the app gracefully waits and resumes monitoring the moment the mouse is back in action.

---

## ⚙️ Configuration
You can customize the alert threshold in `mouse_monitor.py`:
- THRESHOLD = 15: The percentage that triggers the notification (default percentage is 15%)
- time.sleep(300): Default check is every 5 minutes.

Why 15%? > macOS typically warns you at 2%, which is often too late if you are in a meeting or deep in a creative flow. At 15%, a Magic Mouse still has roughly 1-2 days of typical use left. This gives you a comfortable window to finish your current task and "flip" the mouse for a quick charge during your next break.

---

## 🗑️ Uninstall
If you decide to live life on the edge again (or if you've finally bought a mouse that charges like a normal device), you can remove **FlipMeOver** completely with one command:
```bash
   chmod +x uninstall.sh && ./uninstall.sh
```

---

## 🧪 Development & Testing
This project uses uv for lightning-fast dependency management and pytest for unit testing. To run the test suite:
```bash
  uv run pytest -v
```

---

## 📂 Logs
Should you need to check the app's history or debug connection issues, logs are stored natively at: `~/Library/Logs/FlipMeOver/flip_me_over.log`.

---

## 🎯 Target Audience
This app is not a general-purpose battery monitor. It is a specialized tool for the Magic Mouse (2 & 3) community. If you use any other mouse—wired, wireless with a front - facing port, or even a Magic Trackpad — this app will do absolutely nothing for you. And that's by design.

It solves one specific problem: The "Dead Mouse" Syndrome caused by the bottom-charging port. But hey, feel free to run this app if you enjoy seeing a script look for something that isn't there!

---

## 📄 License

This project is licensed under the Apache-2.0 License.
