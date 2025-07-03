import serial
import json
import time
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ————— CONFIGURAÇÃO —————
PORT = '/dev/ttyUSB0'   # ajuste para sua porta serial
BAUD = 115200
MAX_LEN = 100           # quantos pontos manter na tela

# ————— STRUCTS PARA DADOS —————
t_data   = deque(maxlen=MAX_LEN)

# acelerômetro
X = deque(maxlen=MAX_LEN)
Y = deque(maxlen=MAX_LEN)
Z = deque(maxlen=MAX_LEN)
mag       = deque(maxlen=MAX_LEN)
vibration = deque(maxlen=MAX_LEN)

# temperatura e umidade
sht31_temp = deque(maxlen=MAX_LEN)
sht31_hum  = deque(maxlen=MAX_LEN)
dht_temp   = deque(maxlen=MAX_LEN)
dht_hum    = deque(maxlen=MAX_LEN)

# som e vibração digital
sound_level     = deque(maxlen=MAX_LEN)
vibration_state = deque(maxlen=MAX_LEN)

# abre a porta serial
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # aguarda o Arduino reiniciar

# ————— CONFIGURAÇÃO DOS GRÁFICOS —————
fig, axes = plt.subplots(6, 1, figsize=(10, 12), sharex=True)
lines = []

# 1) Acelerômetro X/Y/Z
axes[0].set_ylabel('Accel (g)')
lines += axes[0].plot([], [], label='X')
lines += axes[0].plot([], [], label='Y')
lines += axes[0].plot([], [], label='Z')
axes[0].legend(loc='upper right')

# 2) Magnitude e Vibração
axes[1].set_ylabel('Mag / Vib')
lines += axes[1].plot([], [], label='Magnitude')
lines += axes[1].plot([], [], label='Vibration')
axes[1].legend(loc='upper right')

# 3) Temperaturas
axes[2].set_ylabel('Temp °C')
lines += axes[2].plot([], [], label='SHT31 Temp')
lines += axes[2].plot([], [], label='DHT Temp')
axes[2].legend(loc='upper right')

# 4) Umidades
axes[3].set_ylabel('Umid. %')
lines += axes[3].plot([], [], label='SHT31 Hum')
lines += axes[3].plot([], [], label='DHT Hum')
axes[3].legend(loc='upper right')

# 5) Nível de som
axes[4].set_ylabel('Sound Level')
lines += axes[4].plot([], [], label='Sound')
axes[4].legend(loc='upper right')

# 6) Estado do sensor de vibração
axes[5].set_ylabel('Vib State')
lines += axes[5].plot([], [], label='Vibration')
axes[5].set_xlabel('Millis (ms)')
axes[5].legend(loc='upper right')

# inicializa todos os lines vazios
def init():
    for ln in lines:
        ln.set_data([], [])
    return lines

# função chamada a cada frame
def update(frame):
    raw = ser.readline().decode('utf-8').strip()
    if not raw:
        return lines

    try:
        msg = json.loads(raw)
        t = msg['millis']
        d = msg['data']
    except (json.JSONDecodeError, KeyError):
        return lines

    # insere nos deques
    t_data.append(t)
    X.append(d['X']);    Y.append(d['Y']);    Z.append(d['Z'])
    mag.append(d['magnitude']);    vibration.append(d['vibration'])
    sht31_temp.append(d['sht31_temperature']);  sht31_hum.append(d['sht31_humidity'])
    dht_temp.append(d['dht_temperature']);      dht_hum.append(d['dht_humidity'])
    sound_level.append(d['sound_level']);       vibration_state.append(d['vibration_state'])

    # atualiza cada linha
    idx = 0
    def upd(serie):
        nonlocal idx
        lines[idx].set_data(t_data, serie)
        idx += 1

    # X, Y, Z
    upd(X); upd(Y); upd(Z)
    # magnitude, vibration
    upd(mag); upd(vibration)
    # temps
    upd(sht31_temp); upd(dht_temp)
    # hums
    upd(sht31_hum); upd(dht_hum)
    # sound
    upd(sound_level)
    # vib digital
    upd(vibration_state)

    # ajustar eixos x
    tmin, tmax = min(t_data), max(t_data)
    for ax in axes:
        ax.set_xlim(tmin, tmax)

    # ajustar eixos y dinamicamente (opcional: direto por sensor)
    axes[0].relim(); axes[0].autoscale_view()
    axes[1].relim(); axes[1].autoscale_view()
    axes[2].relim(); axes[2].autoscale_view()
    axes[3].relim(); axes[3].autoscale_view()
    axes[4].relim(); axes[4].autoscale_view()
    axes[5].set_ylim(-0.1, 1.1)  # vib state é 0 ou 1

    return lines

# cria animação (delay ~ mesmo do Arduino: 200 ms)
ani = animation.FuncAnimation(
    fig, update, init_func=init,
    blit=True, interval=200
)

plt.tight_layout()
plt.show()
