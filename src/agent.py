import json
from anthropic import Anthropic
from src.config import ProjectConfig

class SE4AIOrchestrator:
    def __init__(self, config: ProjectConfig, harness):
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.security_policy = config.security_instructions
        self.harness = harness

    def run_cycle(self, task_description: str, max_steps: int = 3):
        # System Prompt arricchito con le NFR (Non-Functional Requirements) di AGENTS.md
        system_prompt = f"""
        Sei un agente autonomo di SE4AI. Il tuo obiettivo è risolvere il task richiesto rispettando le seguenti policy di sicurezza:
        {self.security_policy}
        
        Devi rispondere SEMPRE in formato JSON con questa struttura esatta:
        {{
            "thought": "Il tuo ragionamento logico passo-passo",
            "action": "Esegui un comando consentito (es. 'pytest' o 'bandit') oppure 'stop' se hai finito",
            "argument": "Gli argomenti del comando"
        }}
        """
        
        context_history = [{"role": "user", "content": task_description}]
        
        print("🚀 Avvio del ciclo agentico...")
        for step in range(max_steps):
            print(f"\n--- [Passo {step + 1}/{max_steps}] ---")
            
            # 1. THOUGHT: Invocazione del modello di frontiera
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=system_prompt,
                messages=context_history
            )
            
            raw_output = response.content[0].text
            print(f"🧠 Claude output grezzo: {raw_output}")
            
            try:
                action_json = json.loads(raw_output)
            except json.JSONDecodeError:
                print("❌ Errore: L'agente non ha risposto in JSON valido. Interruzione.")
                break

            # Registra il pensiero nella cronologia
            context_history.append({"role": "assistant", "content": raw_output})
            
            # Verifica se l'agente ha completato il task
            if action_json.get("action") == "stop":
                print("🏁 L'agente ha dichiarato il completamento del task.")
                break
                
            # 2. ACTION & OBSERVATION: Esecuzione tramite l'Harness protetto
            full_command = f"{action_json.get('action')} {action_json.get('argument', '')}"
            print(f"⚙️ Esecuzione azione: {full_command}")
            
            observation = self.harness.execute_bash(full_command)
            print(f"👁️ Osservazione (Risultato del tool):\n{observation}")
            
            # Reinserisce l'osservazione nel contesto per il prossimo ciclo di pensiero
            context_history.append({"role": "user", "content": f"Risultato dell'azione:\n{observation}"})