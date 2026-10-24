# previews.md — the drawing for every option of every question

Paste each fenced block, without the fence, into the `preview` of that option. The `description`
is one short sentence. Labels are Spanish; translate them on the fly if the person writes in
another language, keeping the layout. Max 14 lines × 70 columns.

## Disparador — "¿Qué arranca a tu agente?"

### Un horario (Recomendado for reports, sweeps, monitors)
```
 cron "0 7 * * 1-5"  America/Bogota
      │
      ▼
 Deployment ──► Session nueva cada vez ──► resultado en outputs/
 nadie la mira en vivo: ninguna llamada puede esperar a una persona
```
### Un evento de otro sistema
```
 GitHub: PR abierto / CI falló      tu helpdesk: ticket nuevo
            │                                  │
            ▼                                  ▼
   GitHub Action (curl)              tu webhook (SDK)
            └──────────► crea la Session ◄─────┘
                         con el dato del evento en el kickoff
```
### Una persona
```
 tú / tu usuario ──► tu app o la Console ──► Session
        ▲                                     │
        └──────── respuestas, aprobaciones ◄──┘
 conversación: puedes aprobar cada llamada en vivo
```

## Entrega — "¿Qué entrega cada corrida?"

### Mensaje (Recomendado)
```
 kickoff: user.message  ("Revisa los repos y abre los PR que hagan falta")
   agente ──► trabajo ──► revisa su propio Goal ──► listo
   1 corrida = 1 costo; ves el resultado y decides si hace falta más
```
### Outcome con rúbrica (después de 1-2 corridas buenas)
```
 kickoff: user.define_outcome + rúbrica
   agente ──► reporte.md ──► evaluador aparte ──► ¿cumple 1..N?
      ▲                                           │ no
      └────────────── revisa y corrige ◄──────────┘
   sí ─► listo (máx. max_iterations vueltas)
   cuesta hasta max_iterations × la corrida + el evaluador
```

## Modelo — "¿Qué tan capaz lo necesitas?"

Recommend by cost of error (`diagnostico.md` § 4): Sonnet for most jobs; Opus first when an error
costs a fine, a legal or a safety problem. Adapt every cron preview to the job's real schedule.

### Sonnet 5.5 (Recomendado unless an error is costly)
```
 claude-sonnet-5-5   effort medium (low para triage/chat)
 casi todo: briefs, revisiones, reportes, soporte
 medido: USD 0,02 – 0,41 por corrida
```
### Opus 5.5 (Recomendado for legal, clinical, safety, tax)
```
 claude-opus-5-5   effort high
 trabajo largo y difícil: auditorías, refactors grandes
 medido: auditoría de 3 repos > USD 100
```
### Haiku 5.5
```
 claude-haiku-5-5   effort low
 workers baratos y tareas cortas y repetidas
 (lector de papers, clasificador)
```

## Permisos — "¿Quién autoriza las escrituras?"

Ask only when it is still open (SKILL.md rule 0). Pick at most 4 options that fit the trigger:
drop "Una persona aprueba" for unattended runs unless there is a webhook that answers.

### El servidor decide (auto) (Recomendado for unattended runs)
```
 escritura ──► el servidor la juzga
                 ├─ segura   → corre
                 ├─ riesgosa → la niega (el agente sigue sin ella)
                 └─ dudosa   → pausa (en un horario nadie responde)
```
### Una persona aprueba (always_ask)
```
 escritura ──► pausa ──► tú: aprobar / negar ──► sigue
 bien en conversación; en un horario necesita un webhook que responda
```
### Siempre permitir, con regla en el prompt (always_allow)
```
 escritura ──► corre siempre
 la regla vive en system_prompt.md: "Merge only if ..."
 úsalo solo en una tool angosta (una, no todas)
```
### Solo en su propio espacio (Recomendado when it reads untrusted input unattended)
```
 escribe solo en outputs/, su pestaña o un borrador para ti
 nada sale a terceros: el borrador es la compuerta, tú lo envías
 nunca se queda en pausa esperando a alguien
```
### Solo lectura
```
 sin tools de escritura: el agente lee y reporta
 la persona actúa con el reporte
```

## Subagentes — "¿Un agente o varios?"

### Un agente con skills (Recomendado)
```
 Agent ── skills (procedimientos) ── tools
 todo el contexto en un lugar, más barato y más fácil de depurar
 notas por unidad en /tmp si hay mucho que leer
```
### Un agente + un worker en paralelo
```
 coordinador (Sonnet) ──┬─► worker (Haiku) papel 1
                        ├─► worker (Haiku) papel 2   contexto nuevo c/u
                        └─► worker (Haiku) papel 8
 solo si cada pieza llenaría el contexto del coordinador
```

## Red — "¿A qué puede salir tu agente?"

### Solo a hosts que listo (Recomendado)
```
 networking: limited
   allowed_hosts: api.github.com, ...
   + servidores MCP  (allow_mcp_servers)
   + pypi/npm        (allow_package_managers)
 todo lo demás: bloqueado
```
### A cualquier host
```
 networking: unrestricted
 solo si no puedes listar los hosts antes
 las web tools tampoco quedan limitadas
```
