import json
import time
import serial

# Especifique que este é um agente fonte
agent_type = "source"

# Porta serial será inicializada no setup()
ser = None

def setup():
    global ser
    print("[Python] Setting up source...")
    print("[Python] Parameters: " + json.dumps(params))
    # Abre a porta serial só uma vez
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    state["n"] = 0

def get_output():
    global ser
    try:
        raw = ser.readline().decode('utf-8').strip()
        if not raw:
            # Se não vier nada, retorna um JSON vazio (ou null)
            return json.dumps({"processed": False})
        
        # Tenta converter o que veio por serial em JSON
        data = json.loads(raw)
        state["n"] += 1
        data["processed"] = False
        return json.dumps(data)

    except json.JSONDecodeError as e:
        # Se vier uma linha mal-formada, só faz log e devolve um JSON vazio
        print(f"[Python] JSON decode error: {e}; line was: {raw!r}")
        return json.dumps({"processed": False})

    except Exception as e:
        # Qualquer outro erro de I/O, log e devolve JSON válido
        print(f"[Python] Serial error: {e}")
        return json.dumps({"processed": False})
