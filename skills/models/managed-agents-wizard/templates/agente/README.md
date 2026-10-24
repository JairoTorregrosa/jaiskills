# <nombre>

<Una o dos frases: qué hace, para quién, qué entrega.>

- **Modelo:** `<model id>`, effort `<effort>`
- **Arranque:** <Horario: `<cron>` (<zona>), Deployment `<archivo>` (pausado) | Evento: <qué lo dispara> | Una persona: <dónde>>
- **Costo medido por corrida:** USD <x> (<fecha>)

## Archivos

| Archivo | Qué es |
|---|---|
| `model.yaml` | Nombre, descripción, modelo y effort |
| `system_prompt.md` | El system prompt, en Simplified Technical English |
| `tools.yaml` | Tools del sandbox, permisos y custom tools |
| `mcp.yaml` | Conectores MCP y la lista blanca de sus tools |
| `skills.yaml` | Skills que carga el agente |
| `environment.yaml` | El contenedor: red y paquetes |
| `vault.yaml` + `credentials.md` | El vault (nunca un secreto) y qué credencial va en él |
| `memory_store-<x>.yaml` + `memory/` | La memoria entre corridas y su contenido inicial |
| `files.yaml` + `files/` | Archivos de entrada: ruta local, dónde se montan, `file_id` |
| `schedule.yaml` + `kickoff.md` + `rubric.md` | El Deployment: cuándo, con qué mensaje, cómo se califica |
| `trigger/` | Cómo otro sistema crea la Session |
| `tests/` | Casos de prueba para `scripts/probar.py` |
| `agent.md`, `deployment-*.yaml` | Generados por `scripts/ensamblar.py`. No los edites a mano |

Borra las filas de las partes que este agente no usa.

## Cambiar algo

```sh
uv run --script scripts/ensamblar.py agents/<nombre>
ant apply --dry-run agents/<nombre>/agent.md <agents/<nombre>/deployment-<x>.yaml>
ant apply agents/<nombre>/agent.md <agents/<nombre>/deployment-<x>.yaml>
```

## Probar y depurar

```sh
uv run --script scripts/probar.py agents/<nombre>/tests/basico.json
uv run --script scripts/inspeccionar.py <session_id>
```

## IDs

| Recurso | ID |
|---|---|
| agent.md | `<agent_...>` |
| environment.yaml | `<env_...>` |
