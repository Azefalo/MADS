import serial
import json

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
while True:
    line = ser.readline().decode('utf-8').strip()
    if not line:
        continue
    try:
        data = json.loads(line)
        print(f"Tempo: {data['millis']} ms, "
              f"Raw: {data['pot_raw']}, "
              f"Tensão: {data['pot_volt']:.2f} V")
    except json.JSONDecodeError:
        pass
