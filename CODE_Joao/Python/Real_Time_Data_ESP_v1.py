import serial
import json
import time
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ——— CONFIGURATION ———
PORT = '/dev/ttyUSB0'   # adjust to your serial port
BAUD = 115200
MAX_LEN = 100           # how many points to keep on screen

# ——— DATA STRUCTURES ———
t_data       = deque(maxlen=MAX_LEN)

# accelerometer
X            = deque(maxlen=MAX_LEN)
Y            = deque(maxlen=MAX_LEN)
Z            = deque(maxlen=MAX_LEN)
magnitude    = deque(maxlen=MAX_LEN)
vibration    = deque(maxlen=MAX_LEN)

# temperature and humidity
sht31_temp   = deque(maxlen=MAX_LEN)
sht31_hum    = deque(maxlen=MAX_LEN)
dht_temp     = deque(maxlen=MAX_LEN)
dht_hum      = deque(maxlen=MAX_LEN)

# sound level
sound_level  = deque(maxlen=MAX_LEN)

# ——— OPEN SERIAL PORT ———
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # wait for Arduino to reboot

# ——— PLOT SETUP ———
# now 5 rows instead of 6
fig, axes = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
lines = []

# 1) Accelerometer X/Y/Z
axes[0].set_ylabel('Accel (g)')
lines += axes[0].plot([], [], label='X')
lines += axes[0].plot([], [], label='Y')
lines += axes[0].plot([], [], label='Z')
axes[0].legend(loc='upper right')

# 2) Magnitude and Vibration
axes[1].set_ylabel('Magnitude / Vib')
lines += axes[1].plot([], [], label='Magnitude')
lines += axes[1].plot([], [], label='Vibration')
axes[1].legend(loc='upper right')

# 3) Temperatures
axes[2].set_ylabel('Temperature (°C)')
lines += axes[2].plot([], [], label='SHT31 Temp')
lines += axes[2].plot([], [], label='DHT Temp')
axes[2].legend(loc='upper right')

# 4) Humidities
axes[3].set_ylabel('Humidity (%)')
lines += axes[3].plot([], [], label='SHT31 Hum')
lines += axes[3].plot([], [], label='DHT Hum')
axes[3].legend(loc='upper right')

# 5) Sound Level
axes[4].set_ylabel('Sound Level')
lines += axes[4].plot([], [], label='Sound')
axes[4].set_xlabel('Time (ms)')
axes[4].legend(loc='upper right')

# initialize all lines as empty
def init():
    for ln in lines:
        ln.set_data([], [])
    return lines

# function called on each animation frame
def update(frame):
    raw = ser.readline().decode('utf-8').strip()
    if not raw:
        return lines

    try:
        msg = json.loads(raw)
        t   = msg['millis']
        d   = msg['data']
    except (json.JSONDecodeError, KeyError):
        return lines

    # append new data
    t_data.append(t)
    X.append(d['X']);    Y.append(d['Y']);    Z.append(d['Z'])
    magnitude.append(d['magnitude'])
    vibration.append(d['vibration'])
    sht31_temp.append(d['sht31_temperature'])
    sht31_hum.append(d['sht31_humidity'])
    dht_temp.append(d['dht_temperature'])
    dht_hum.append(d['dht_humidity'])
    sound_level.append(d['sound_level'])

    # update each line
    idx = 0
    def upd(series):
        nonlocal idx
        lines[idx].set_data(t_data, series)
        idx += 1

    # X, Y, Z
    upd(X); upd(Y); upd(Z)
    # magnitude, vibration
    upd(magnitude); upd(vibration)
    # temperatures
    upd(sht31_temp); upd(dht_temp)
    # humidities
    upd(sht31_hum); upd(dht_hum)
    # sound level
    upd(sound_level)

    # adjust x-axis limits
    t_min, t_max = min(t_data), max(t_data)
    for ax in axes:
        ax.set_xlim(t_min, t_max)

    # autoscale y-axes
    for ax in axes:
        ax.relim()
        ax.autoscale_view()

    return lines

# create the animation (matches ~200 ms update rate)
ani = animation.FuncAnimation(
    fig, update, init_func=init,
    blit=True, interval=200
)

plt.tight_layout()
plt.show()
