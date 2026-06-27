import os
import json
import docker
from openai import OpenAI
from dotenv import load_dotenv

# 1. SETUP INIZIALE
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    docker_client = docker.from_env()
except Exception as e:
    print("ERRORE CRITICO: Docker Desktop non è in esecuzione.")
    exit(1)

CONTEXT_FILE = "CONTEXT.md"
MAX_STEPS = 5
MODEL = "gpt-4o-mini" # Modello economico per i test

def inizializza_contesto(task_desc, test_code):
    """Crea il file di stato iniziale partendo dal task (Simulazione AIDev)."""
    stato = f"""# CONTEXT FILE - STATO DEL PROGETTO
## OBIETTIVO ATTUALE
{task_desc}

## TEST DA SUPERARE (test_code.py)
```python\n{test_code}\n```

## STATO DELL'IMPLEMENTAZIONE
- Nessun codice ancora scritto nel file `main_code.py`.
- Tentativi eseguiti: 0
"""
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(stato)
    print("-> CONTEXT.md inizializzato.")

def main():
    # --- FASE 1: RICEZIONE TASK (Hardcoded per l'esempio, estraibile da JSON) ---
    task_desc = "Scrivi una funzione `fibonacci(n)` che ritorni una lista dei primi n numeri. Se n <= 0, ritorna una lista vuota."
    test_code = """
from main_code import fibonacci
def test_fib():
    assert fibonacci(0) == []
    assert fibonacci(5) == [0, 1, 1, 2, 3]
"""
    inizializza_contesto(task_desc, test_code)

    # Avvio Sandbox
    print("-> Avvio Sandbox Docker...")
    container = docker_client.containers.run("agent-sandbox", detach=True, tty=True)

    try:
        # Inietto il file di test nel container (rimane fisso)
        container.exec_run(f"python -c 'import json; open(\"test_code.py\", \"w\").write(json.loads({json.dumps(json.dumps(test_code))}))'")

        # --- FASE 2: IL LOOP DELL'AGENTE ---
        for step in range(1, MAX_STEPS + 1):
            print(f"\n================ STEP {step} ================")
            
            # Lettura del contesto (unica fonte di verità)
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                contesto_corrente = f.read()

            prompt = f"""
Sei un AI Software Engineer autonomo. Ecco lo STATO REALE del progetto.
Non hai memoria di conversazioni passate, basati SOLO su questo file.

{contesto_corrente}

Rispondi ESCLUSIVAMENTE con un JSON valido con questa struttura:
{{
    "ragionamento": "Spiega brevemente cosa non andava e cosa scriverai",
    "codice": "L'intero codice Python per `main_code.py`",
    "nuovo_context": "Riscrivi l'intero CONTEXT FILE aggiornando la sezione STATO DELL'IMPLEMENTAZIONE"
}}
"""
            # Generazione Azione
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            agent_output = json.loads(response.choices[0].message.content)
            print(f"🧠 Ragionamento: {agent_output['ragionamento']}")

            # Esecuzione: inietto il codice generato nel container
            codice_pulito = agent_output['codice']
            escaped_code = json.dumps(codice_pulito)
            container.exec_run(f"python -c 'import json; open(\"main_code.py\", \"w\").write(json.loads({escaped_code}))'")

            # Valutazione: lancio pytest
            print("⚙️ Esecuzione test in sandbox...")
            exec_result = container.exec_run("pytest test_code.py -v")
            output_test = exec_result.output.decode('utf-8')
            esito = "SUCCESSO" if exec_result.exit_code == 0 else "FALLIMENTO"
            print(f"📊 Esito: {esito}")

            # Aggiornamento Contesto
            nuovo_stato = agent_output['nuovo_context']
            log_aggiuntivo = f"\n\n## LOG STEP {step} (Esito: {esito})\n```text\n{output_test.strip()[-500:]}\n```" # Troncamento log per salvare token
            
            with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
                f.write(nuovo_stato + log_aggiuntivo)

            if esito == "SUCCESSO":
                print("\n✅ Task completato! L'agente ha superato i test.")
                break
        else:
            print(f"\n❌ L'agente non è riuscito a risolvere il task entro {MAX_STEPS} step.")

    finally:
        print("\n🧹 Pulizia: Spegnimento container Docker...")
        container.stop()
        container.remove()

if __name__ == "__main__":
    main()