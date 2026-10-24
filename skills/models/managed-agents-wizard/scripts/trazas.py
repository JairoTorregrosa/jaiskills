#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic>=0.80"]
# ///
"""Narrate one Managed Agents session as a timeline a person can follow next to the Console.

Usage:
  uv run --script <skill>/scripts/trazas.py <session_id>            # timeline, in Spanish
  uv run --script <skill>/scripts/trazas.py <session_id> --breve    # no explanation lines
  uv run --script <skill>/scripts/trazas.py <session_id> --json     # the same data, as JSON

Read-only, costs nothing. Prints the header (agent version, model, effort, duration, active time,
cost against the budget, tokens and cache), then every event in order with the seconds since
the start: each model request with its duration and tokens, each tool call with the permission
that let it run and the first characters of its input and result, messages, confirmations,
outcome evaluations, errors and the stop reason. The first time an event type appears, one line
explains what it is. Unknown event types are printed with their type, never dropped.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime

import anthropic

EXPLICA = {
    "session.status_running": "la Session empezó a trabajar; el tiempo en running es el que se cobra (USD 0,08 por hora)",
    "session.status_idle": "la Session se detuvo; stop_reason dice por qué (end_turn terminó, requires_action te espera, budget_reached llegó al tope)",
    "session.status_rescheduled": "error pasajero de la plataforma; la Session reintenta sola",
    "session.status_terminated": "la Session terminó del todo y no acepta más eventos",
    "session.thread_status_running": "un hilo de agente empezó; con subagentes hay un hilo por agente",
    "session.thread_status_idle": "un hilo de agente se detuvo",
    "user.message": "el mensaje que arrancó o siguió el trabajo (el kickoff)",
    "user.define_outcome": "el kickoff con rúbrica: un evaluador aparte calificará el resultado",
    "user.tool_confirmation": "alguien (tú o tu código) aprobó o negó una tool en always_ask",
    "user.custom_tool_result": "tu aplicación respondió una custom tool",
    "user.interrupt": "alguien detuvo al agente",
    "span.model_request_start": "una llamada al modelo: cuánto tardó, tokens nuevos, tokens leídos de caché (más baratos) y tokens escritos",
    "agent.thinking": "señal de que el modelo razonó; el contenido no se muestra",
    "agent.message": "lo que el agente escribió como respuesta",
    "agent.tool_use": "el agente usa una tool del sandbox (bash, archivos, web)",
    "agent.mcp_tool_use": "el agente usa una tool de un servidor MCP",
    "agent.custom_tool_use": "el agente pide una custom tool; tu aplicación debe responder",
    "agent.tool_result": "lo que devolvió la tool",
    "agent.mcp_tool_result": "lo que devolvió la tool MCP",
    "session.usage": "costo y tokens acumulados de la Session",
    "session.error": "error de la plataforma con detalle",
}


def ts(e) -> datetime | None:
    v = getattr(e, "processed_at", None)
    if isinstance(v, datetime):
        return v
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


def corto(x, n=110) -> str:
    if isinstance(x, (dict, list)):
        x = json.dumps(x, ensure_ascii=False)
    return " ".join(str(x or "").split())[:n]


def texto(content) -> str:
    out = []
    for b in content or []:
        d = b if isinstance(b, dict) else b.model_dump()
        out.append(str(d.get("text") or d.get("type", "")))
    return " ".join(out)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    sid = args[0]
    breve, como_json = "--breve" in sys.argv, "--json" in sys.argv
    c = anthropic.Anthropic()
    s = c.beta.sessions.retrieve(session_id=sid)
    events = list(c.beta.sessions.events.list(session_id=sid))
    t0 = ts(events[0]) if events else None

    u = s.usage.model_dump() if s.usage else {}
    budget = (s.budget.model_dump() if getattr(s, "budget", None) else {}) or {}
    tope = (budget.get("max_list_cost") or {}).get("amount")
    m = s.agent.model.model_dump() if s.agent and s.agent.model else {}
    effort = m.get("effort")
    effort = effort.get("type") if isinstance(effort, dict) else effort
    stats = s.stats.model_dump() if getattr(s, "stats", None) else {}
    cache_w = sum((u.get("cache_creation") or {}).values())
    head = {
        "session": sid,
        "console": f"https://platform.claude.com/workspaces/default/sessions/{sid}",
        "agent": f"{s.agent.name} v{s.agent.version}" if s.agent else "?",
        "model": m.get("id"), "effort": effort, "status": s.status,
        "duration_s": stats.get("duration_seconds"), "active_s": stats.get("active_seconds"),
        "cost_usd": int((u.get("list_cost") or {}).get("amount") or 0) / 100,
        "budget_usd": int(tope) / 100 if tope else None,
        "tokens": {"input": u.get("input_tokens"), "cache_write": cache_w,
                   "cache_read": u.get("cache_read_input_tokens"), "output": u.get("output_tokens")},
        "web": u.get("server_tool_use"),
    }

    rows, vistos, starts, uses = [], set(), {}, {}
    n_model = 0
    for e in events:
        t, d = e.type, e.model_dump(mode="json")
        at = (ts(e) - t0).total_seconds() if t0 and ts(e) else 0.0
        who = f" [{d['agent_name']}]" if d.get("agent_name") else ""
        line = t
        if t == "span.model_request_start":
            # the row is shown at the start time and filled in when the request ends
            n_model += 1
            starts[e.id] = (len(rows), at, n_model)
            rows.append({"t": round(at, 1), "type": t, "line": f"llamada al modelo #{n_model}: sin terminar",
                         "explica": None if breve or t in vistos else EXPLICA.get(t)})
            vistos.add(t)
            continue
        if t == "span.model_request_end":
            i, since, n = starts.get(d.get("model_request_start_id"), (None, at, "?"))
            mu = d.get("model_usage") or {}
            line = (f"llamada al modelo #{n}: {at - since:.1f} s · lee {mu.get('input_tokens', 0)}"
                    f" + caché nueva {mu.get('cache_creation_input_tokens', 0)}"
                    f" + de caché {mu.get('cache_read_input_tokens', 0)} · escribe {mu.get('output_tokens', 0)}"
                    + (" · ERROR" if d.get("is_error") else ""))
            if i is not None:
                rows[i]["line"] = line
                continue
        elif t in ("agent.tool_use", "agent.mcp_tool_use", "agent.custom_tool_use"):
            uses[e.id] = (d.get("name"), at)
            perm = d.get("evaluated_permission")
            pol = (d.get("evaluation") or {}).get("type") if isinstance(d.get("evaluation"), dict) else None
            srv = f"{d.get('mcp_server_name')}." if d.get("mcp_server_name") else ""
            line = (f"tool {srv}{d.get('name')}" + (f" [permiso {pol} → {perm}]" if perm else "")
                    + f": {corto(d.get('input'))}")
        elif t in ("agent.tool_result", "agent.mcp_tool_result"):
            ref = d.get("tool_use_id") or d.get("mcp_tool_use_id")
            name, since = uses.get(ref, ("?", at))
            body = texto(e.content if hasattr(e, "content") else None)
            estado = "NEGADA" if "has been denied" in body else ("ERROR" if d.get("is_error") else "ok")
            line = f"  ↳ {name} {estado} en {at - since:.1f} s: {corto(body)}"
        elif t == "agent.message":
            line = f"mensaje: {corto(texto(e.content), 160)}"
        elif t == "user.message":
            line = f"kickoff: {corto(texto(e.content), 160)}"
        elif t == "user.tool_confirmation":
            line = f"confirmación: {d.get('result')} para {uses.get(d.get('tool_use_id'), ('?',))[0]}"
        elif t in ("session.status_idle", "session.thread_status_idle"):
            sr = d.get("stop_reason") or {}
            line = f"{t}{who}: stop_reason={sr.get('type')}" + (f" esperando {sr.get('event_ids')}" if sr.get("event_ids") else "")
        elif t == "session.usage":
            lc = ((d.get("usage") or {}).get("list_cost") or {}).get("amount")
            line = f"costo acumulado: USD {int(lc or 0) / 100:.2f}"
        elif t == "session.error":
            line = f"ERROR de la Session: {corto(d, 200)}"
        else:
            line = f"{t}{who}"
        explica = None if breve or t in vistos else EXPLICA.get(t)
        vistos.add(t)
        rows.append({"t": round(at, 1), "type": t, "line": line, "explica": explica})

    if como_json:
        print(json.dumps({"header": head, "events": rows}, indent=2, ensure_ascii=False))
        return 0
    tk = head["tokens"]
    print(f"{head['console']}\n{head['agent']} · {head['model']} effort {head['effort']} · status {head['status']}")
    print(f"abierta {head['duration_s'] or 0:.1f} s (incluye idle), trabajando (cobrado) {head['active_s'] or 0:.1f} s · costo USD {head['cost_usd']:.2f}"
          + (f" de un tope de USD {head['budget_usd']:.2f}" if head["budget_usd"] else " (sin tope)"))
    print(f"tokens: entrada {tk['input']} · caché escrita {tk['cache_write']} · leída de caché {tk['cache_read']} · salida {tk['output']}")
    if not breve:
        print("  (la caché leída cuesta una fracción de la entrada normal; por eso la segunda llamada sale más barata)")
    print()
    for r in rows:
        print(f"t+{r['t']:>6.1f}s  {r['line']}")
        if r["explica"]:
            print(f"          · {r['explica']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
