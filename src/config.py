import os
from pathlib import Path

class ProjectConfig:
    def __init__(self):
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            raise ValueError("❌ ERRORE CRITICO: ANTHROPIC_API_KEY non configurata nell'ambiente.")
        
        # Path del file di contesto/policy di sicurezza
        self.policy_path = Path("/app/CLAUDE.md")
        self.security_instructions = self._load_security_policy()

    def _load_security_policy(self) -> str:
        if self.policy_path.exists():
            return self.policy_path.read_text()
        return "Standard Policy: Genera codice sicuro, privo di vulnerabilità OWASP."