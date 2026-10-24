# ficha.md — show the whole agent, every layer with its reason

You are about to show the person the agent you designed. They are here to learn how an agent is
built, so nothing stays hidden: each layer appears with its exact value and the reason for that
value, in words they can repeat to someone else. A summary such as "Opus with the security skill,
one agent" hides the decisions they came to learn; show the values themselves.

## When to show it

- At the end of step 9, before you write files: the whole ficha, filled in.
- After any change the person asks for: the ficha again, with the changed rows marked `← cambió`.
- Before `ant apply --dry-run`: point to the files where each row lives.
- In the final report: the ficha with the IDs that `ant apply` created.

## Do this

1. Fill every row below from the design. A layer the agent does not use stays in the table with
   "no usa" and the reason ("sin memoria: cada corrida empieza de cero y no necesita recordar").
2. Every value is the literal one that goes into the files: the model ID, the effort level, the
   cron string with its timezone, the amount in USD and in cents, each tool name, each MCP tool
   name, each host, each permission policy.
3. Every reason names the fact from the diagnosis it comes from (the trigger, the cost of an
   error, the input, who approves). A reason that would fit any agent ("es más seguro") is not
   a reason; name what it protects in this job.
4. Show the system prompt in full, in a code block, and under it two to four lines in Spanish on
   what each section makes the agent do. The prompt is in English; the person must still be able
   to read what it says.
5. Show the kickoff and the rubric in full. For each rubric criterion, one phrase on which
   failure it catches.
6. Say what you left out on purpose and why ("sin `web_search`: el trabajo no necesita internet
   abierto y así un resultado de búsqueda no puede darle instrucciones").

## The ficha (Spanish, filled with the person's values)

```
FICHA DEL AGENTE  <nombre>   (archivos en agents/<nombre>/)

Modelo        <id> · effort <nivel>                         model.yaml
              por qué: <costo del error / dificultad del trabajo>
Disparador    <cron> <zona> = "<en palabras: todos los días a las 3:00 a. m.>"  schedule.yaml
              o: evento <cuál> · o: una persona desde <dónde>
              por qué: <cuándo hace falta el resultado>
Entrega       <outcome con rúbrica de N criterios | mensaje>  kickoff.md · rubric.md
              iteraciones máx.: <n> · por qué: <qué es verificable>
Tope de costo USD <x> por corrida (amount "<centavos>")     schedule.yaml
              por qué: <costo medido o estimado; se ajusta tras la prueba>
System prompt system_prompt.md, completo abajo
Tools         habilitadas: <bash, read, write, edit, glob, grep> · política <auto>   tools.yaml
              apagadas: <web_fetch, web_search> · por qué cada una
MCP           <servidor> <url>                               mcp.yaml
              tools habilitadas: <lista exacta> · política por tool
              todo lo demás apagado · por qué
Skills        <skill> (<origen, licencia>) · por qué          skills.yaml
Herramientas  <nombre>: qué hace, quién la responde · por qué  tools.yaml
  propias     o: no usa
Subagentes    <ninguno> · por qué                             subagents.yaml
Environment   <cloud> · red <limited>                         environment.yaml
              hosts permitidos: <lista exacta> · MCP <sí/no> · gestores de paquetes <sí/no>
              por qué cada host
Memoria       <store> en /mnt/memory/<store>/ · <read_only|read_write>   memory_store-<x>.yaml
              qué guarda · por qué ese acceso
Archivos      <archivo> → <ruta de montaje>  o: no usa       files.yaml
Repos         <owner/repo> → <ruta>, rama <x>  o: no usa
Credenciales  vault <nombre>: <servicio> (<tipo>), permisos mínimos <lista>   credentials.md
              el agente nunca ve el valor
Compuerta     qué hace solo · qué deja para una persona · dónde lo ve
Fuera         <lo que dejé por fuera a propósito y por qué>
```

## Rules

- Never replace a row with "lo estándar" or "lo de siempre". Show the value.
- When the person changes one decision, show which other rows it moves (Opus raises the cost
  cap; a new connector adds a host and a credential).
- Keep the ficha in `agents/<name>/README.md` too, so it stays with the files after the session.
