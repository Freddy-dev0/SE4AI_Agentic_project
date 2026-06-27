
# Agentic Context Engineering Experiment

## Obiettivo del Progetto
Questo progetto sperimentale (Software Engineering for AI) analizza il degrado comportamentale degli agenti autonomi di coding. Nello specifico, testa l'efficacia del paradigma **State-Driven (Agent Loop)** — dove l'agente comunica esclusivamente aggiornando un file di stato (`CONTEXT.md`) — per mitigare il *Context Rot* e l'effetto *Lost in the Middle* su task reali estratti dal dataset AIDev.

## Architettura
- **Cervello (Orchestratore):** Script Python nativo (OpenAI API).
- **Memoria:** File fisico `CONTEXT.md` (sovrascritto a ogni ciclo, no chat lineare).
- **Corpo (Sandbox):** Container Docker locale (`python:3.11-slim`) usato per isolare l'esecuzione del codice e i test unitari.

## Setup Locale (Windows / VS Code)
1. Installa Docker Desktop (con WSL 2) e assicurati che sia in esecuzione.
2. Clona la repo e crea l'ambiente virtuale: `python -m venv venv`
3. Attiva il venv: `.\venv\Scripts\activate`
4. Installa le dipendenze: `pip install -r requirements.txt` (openai, docker, python-dotenv)
5. Copia `.env.example` in `.env` e inserisci la tua API Key.
6. Compila la sandbox: `docker build -t agent-sandbox .`

