# Display Stats Script

This Python script displays system statistics on an OLED display connected to a Raspberry Pi. It utilizes the `psutil` library to gather system information and the `luma.oled` library for interfacing with the OLED display.

## Demo

![Preview](./images/preview.gif)

## Prerequisites

- Raspberry Pi with GPIO access
- OLED display
- Python 3.x installed on the Raspberry Pi
- `pip` package manager installed on the Raspberry Pi

## Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/display-stats-script.git
    cd display-stats-script
    ```

2. **Create and Activate a Virtual Environment:**

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Script

1. **Connect OLED Display:**

   Ensure your OLED display is properly connected to the Raspberry Pi.

2. **Activate Virtual Environment:**

    ```bash
    source env/bin/activate
    ```

3. **Run the Script:**

    ```bash
    python stats.py
    ```

    The script will continuously display system statistics on the OLED display.

4. **Exit the Script:**

    To stop the script, press `Ctrl+C`.

## Updating Dependencies

If you add or remove dependencies in your script, update the `requirements.txt` file:

```bash
pip freeze > requirements.txt
```

And re-install the dependencies:

```bash
pip install -r requirements.txt
```

## Autostart with systemd

To automatically start the `stats.py` script at bootup on your Raspberry Pi, you can create a systemd service. Follow these steps:

1. **Create a systemd Service File:**

    Create a new file named `display-stats.service` in the `/etc/systemd/system/` directory.

    ```bash
    sudo nano /etc/systemd/system/display-stats.service
    ```

    Add the following content to the file:

    ```ini
    [Unit]
    Description=Display Stats Script
    After=network.target

    [Service]
    ExecStart=/path/to/your/project/env/bin/python /path/to/your/project/stats.py
    WorkingDirectory=/path/to/your/project
    User=yourusername
    Group=yourusername
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `/path/to/your/project` with the actual path to your project directory and set `yourusername` to the username of your Raspberry Pi.

2. **Reload systemd and Enable the Service:**

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable display-stats.service
    ```

3. **Start the Service:**

    ```bash
    sudo systemctl start display-stats.service
    ```

    To check the status or troubleshoot, you can use:

    ```bash
    sudo systemctl status display-stats.service
    ```

    To stop or restart the service:

    ```bash
    sudo systemctl stop display-stats.service
    sudo systemctl restart display-stats.service
    ```

## Additional Group Memberships

To ensure proper access to GPIO and I2C functionalities, it may be necessary to add your default user to the `gpio` and `i2c` groups on your Raspberry Pi. Follow these steps:

1. **Add User to `gpio` Group:**

   ```bash
   sudo usermod -aG gpio $USER
   ```

2. **Add User to `i2c` Group:**

   ```bash
   sudo usermod -aG i2c $USER
   ```

3. **Restart Your Raspberry Pi:**

   To apply the changes, restart your Raspberry Pi:

   ```bash
   sudo reboot
   ```

After completing these steps, your user should have the necessary group memberships to access GPIO and I2C without requiring elevated privileges. This is important for running scripts interacting with hardware interfaces seamlessly.

## Font

The script uses the [Dogica](https://www.dafont.com/dogica.font) font. Dogica is a monospace typeface made with Inkscape and FontForge and tailored for GB Studio. It features more than 200 characters in an 8x8 grid and comes in two styles: monospace and pixel, the kerned version. Four pictures for GB Studio are included. It is free for personal and commercial use under the OFL license. Credit/attribution is not required for raster works.

## License

This project is licensed under the [MIT License](LICENSE).
