import subprocess
import shlex

class SecureToolHarness:
    def __init__(self):
        # Lista di comandi espliciti consentiti (Policy Engine)
        self.allowed_commands = ["pytest", "bandit", "grep"]

    def execute_bash(self, command_str: str) -> str:
        """Esegue comandi di testing o analisi statica validando la policy."""
        tokens = shlex.split(command_str)
        if not tokens:
            return "Errore: Comando vuoto."
        
        base_cmd = tokens[0]
        
        # Guardrail del Policy Engine
        if base_cmd not in self.allowed_commands:
            return f"❌ VIOLAZIONE DI SICUREZZA: Il comando '{base_cmd}' non è autorizzato."

        try:
            # Esecuzione sicura all'interno della sandbox (container)
            result = subprocess.run(
                tokens, capture_output=True, text=True, timeout=30, check=False
            )
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            return "❌ Errore: Il comando ha superato il timeout di 30 secondi."
        except Exception as e:
            return f"❌ Errore di esecuzione: {str(e)}"