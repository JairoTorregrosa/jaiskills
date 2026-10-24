# Credenciales

| Servicio | Tipo de credencial | Para qué |
|---|---|---|
| <GitHub MCP> | `static_bearer` (URL del MCP) | <leer PRs, comentar> |

Permisos mínimos: <lista>.

Carga (el secreto lo pegas tú; nunca pasa por el chat ni por un archivo):

```sh
read -rs CMA_TOKEN && export CMA_TOKEN
jq -n -f /dev/stdin <<'JQ' | ant beta:vaults:credentials create --vault-id <vlt_...>
{display_name: "<servicio>", auth: {type: "static_bearer", mcp_server_url: "<https://.../mcp>", token: (env.CMA_TOKEN // error("CMA_TOKEN is not set"))}}
JQ
unset CMA_TOKEN
```
