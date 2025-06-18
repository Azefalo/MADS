import sys
import time
import json
import signal
import threading
import serial
import glob
import importlib

# Import your source module (assumed to be named RaspberryPi.py, adjust if needed)
import CODE_Joao.Arduino.Potenciometer_Sensor_V1.RaspberryPi as plugin

running = True

def enumerate_ports():
    """List available serial ports (cross-platform)."""
    ports = []
    if sys.platform.startswith('win'):
        ports = [f'COM{i + 1}' for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def handle_sigint(sig, frame):
    global running
    running = False
    print("\n[Python] Stopping...")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <port> | -e")
        sys.exit(1)

    if sys.argv[1] == "-e":
        print("Available serial ports:")
        for port in enumerate_ports():
            print(f"  {port}")
        sys.exit(0)

    # Set plugin params and state
    plugin.params = {
        "port": sys.argv[1],
        "baudrate": 115200,
        "timeout": 1
    }
    plugin.state = {}

    # Optional: send a setup command, if needed (e.g., plugin.params["cfg_cmd"] = "500p")
    if len(sys.argv) > 2:
        # Example: pass extra params as JSON string
        try:
            extra_params = json.loads(sys.argv[2])
            plugin.params.update(extra_params)
        except Exception:
            pass

    plugin.setup()

    i = 0
    while running:
        output = plugin.get_output()
        if output:
            print(f"message #{i:06d}: {output}")
            i += 1
        time.sleep(0.1)