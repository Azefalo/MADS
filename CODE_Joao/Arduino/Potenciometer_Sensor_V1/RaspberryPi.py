import serial
import json

# Module-level variables
ser = None
params = {}

def setup():
    """
    Initializes the serial port using parameters from the global params dictionary.
    Expected params keys:
        - 'port': Serial port (e.g., '/dev/ttyACM0')
        - 'baudrate': Baud rate (e.g., 115200)
        - 'timeout': Read timeout in seconds (e.g., 1)
    """
    global ser
    port = params.get('port', '/dev/ttyACM0')
    baudrate = params.get('baudrate', 115200)
    timeout = params.get('timeout', 1)
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
    except serial.SerialException as e:
        raise RuntimeError(f"Failed to open serial port: {e}")

def get_output():
    """
    Reads one line from the serial port, parses it as JSON, and returns the JSON string.
    Returns None if no valid JSON line is received.
    """
    if ser is None:
        raise RuntimeError("Serial port not initialized. Call setup() first.")
    try:
        line = ser.readline().decode('utf-8').strip()
        if not line:
            return None
        data = json.loads(line)
        return json.dumps(data)
    except Exception:
        # Ignore errors and return None (could log if desired)
        return None