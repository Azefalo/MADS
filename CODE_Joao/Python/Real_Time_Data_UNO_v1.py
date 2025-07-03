import serial
import json
import time
from collections import deque
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ————— CONFIGURAÇÃO —————
PORT = '/dev/ttyACM0'    # ajuste para sua porta serial
BAUD = 115200
MAX_LEN = 100            # quantos pontos exibir no gráfico

# deque para armazenar dados
t_data = deque(maxlen=MAX_LEN)
I1, I2, I3 = deque(maxlen=MAX_LEN), deque(maxlen=MAX_LEN), deque(maxlen=MAX_LEN)
P1, P2, P3 = deque(maxlen=MAX_LEN), deque(maxlen=MAX_LEN), deque(maxlen=MAX_LEN)

# abre serial
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # aguarda Arduino reiniciar

# configura figura
fig, (ax_cur, ax_pow) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
ax_cur.set_ylabel("Corrente (A)")
ax_pow.set_ylabel("Potência (W)")
ax_pow.set_xlabel("Tempo (ms)")

line_I1, = ax_cur.plot([], [], label="I1")
line_I2, = ax_cur.plot([], [], label="I2")
line_I3, = ax_cur.plot([], [], label="I3")
line_P1, = ax_pow.plot([], [], label="P1")
line_P2, = ax_pow.plot([], [], label="P2")
line_P3, = ax_pow.plot([], [], label="P3")

ax_cur.legend(loc="upper right")
ax_pow.legend(loc="upper right")

# função de inicialização
def init():
    for ln in (line_I1, line_I2, line_I3, line_P1, line_P2, line_P3):
        ln.set_data([], [])
    return line_I1, line_I2, line_I3, line_P1, line_P2, line_P3

# função de atualização para cada frame
def update(frame):
    try:
        raw = ser.readline().decode('utf-8').strip()
        if not raw:
            return line_I1, line_I2, line_I3, line_P1, line_P2, line_P3
        msg = json.loads(raw)
        t = msg['millis']
        dat = msg['data']
    except (json.JSONDecodeError, KeyError):
        # pula linhas malformadas
        return line_I1, line_I2, line_I3, line_P1, line_P2, line_P3

    # atualiza deques
    t_data.append(t)
    I1.append(float(dat['I1'])); I2.append(float(dat['I2'])); I3.append(float(dat['I3']))
    P1.append(float(dat['P1'])); P2.append(float(dat['P2'])); P3.append(float(dat['P3']))

    # ajusta dados dos plots
    line_I1.set_data(t_data, I1)
    line_I2.set_data(t_data, I2)
    line_I3.set_data(t_data, I3)
    line_P1.set_data(t_data, P1)
    line_P2.set_data(t_data, P2)
    line_P3.set_data(t_data, P3)

    # ajusta limites
    ax_cur.set_xlim(max(t_data)-MAX_LEN*frame_interval_ms, max(t_data))
    all_I = list(I1) + list(I2) + list(I3)
    ax_cur.set_ylim(min(all_I)*0.9, max(all_I)*1.1)
    all_P = list(P1) + list(P2) + list(P3)
    ax_pow.set_ylim(min(all_P)*0.9, max(all_P)*1.1)

    return line_I1, line_I2, line_I3, line_P1, line_P2, line_P3

# intervalo entre frames em ms (deve bater com delay do Arduino, aqui 200 ms)
frame_interval_ms = 200

ani = animation.FuncAnimation(
    fig, update, init_func=init, blit=True,
    interval=frame_interval_ms
)

plt.tight_layout()
plt.show()
