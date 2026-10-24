# credenciales.md — put every secret in a vault without it ever reaching the chat

You are about to store the credentials the design needs. The person types each secret into their
own shell; you build the request from environment variables and never print, store or log a value.

## Facts already verified (2026-10-24)

- `vault.yaml` is the container only (`type: vault`, `display_name`); `ant apply` never reads or
  diffs credentials. Credentials are created with `ant beta:vaults:credentials create`. [ant apply]
- Credential types that worked: `static_bearer` (GitHub MCP), `environment_variable` (configured).
  `mcp_oauth` refreshes by itself. [live runs, platform docs]
- MCP credentials match their server by URL: one vault with a GitHub MCP credential served 8
  agents that use the same URL. [live runs]
- Deployments and sessions take vaults by ID (`vault_ids: [vlt_...]`), not by path. [ant apply]
- Fine-grained GitHub PATs have no Checks permission. Read CI through `actions_*` tools. [live runs]
- The Admin API (usage, cost) is not available to individual accounts. [platform docs]

## Do this

1. List each credential in `credentials.md`: service, type, minimum permissions, what for.
2. Apply `vault.yaml`, then read its ID: `jq -r '.resources["./agents/<name>/vault.yaml"].id' claude-lock.json`.
3. Give the person the block for each credential and wait for "listo". They run it; in Claude Code
   they can prefix each line with `!`.

MCP with a fixed token:
```sh
read -rs CMA_TOKEN && export CMA_TOKEN
jq -n -f /dev/stdin <<'JQ' | ant beta:vaults:credentials create --vault-id <vlt_...>
{display_name: "<service>", auth: {type: "static_bearer", mcp_server_url: "<exact MCP URL from mcp.yaml>", token: (env.CMA_TOKEN // error("CMA_TOKEN is not set"))}}
JQ
unset CMA_TOKEN
```

MCP with OAuth (refreshed by the platform; read `token_endpoint` from the server's
`/.well-known/oauth-authorization-server`):
```sh
read -rs CMA_ACCESS && read -rs CMA_REFRESH && read -r CMA_CLIENT_ID && export CMA_ACCESS CMA_REFRESH CMA_CLIENT_ID
jq -n -f /dev/stdin <<'JQ' | ant beta:vaults:credentials create --vault-id <vlt_...>
{display_name: "<service>", auth: {type: "mcp_oauth", mcp_server_url: "<MCP URL>", access_token: env.CMA_ACCESS,
  refresh: {refresh_token: env.CMA_REFRESH, client_id: env.CMA_CLIENT_ID, token_endpoint: "<token endpoint>", token_endpoint_auth: {type: "none"}}}}
JQ
unset CMA_ACCESS CMA_REFRESH CMA_CLIENT_ID
```

An API key the sandbox calls over HTTP (the sandbox sees a placeholder; the real value is added
only in the header, only toward the listed host):
```sh
read -rs CMA_KEY && export CMA_KEY
jq -n -f /dev/stdin <<'JQ' | ant beta:vaults:credentials create --vault-id <vlt_...>
{display_name: "<service>", auth: {type: "environment_variable", secret_name: "<ENV_NAME>", secret_value: env.CMA_KEY,
  networking: {type: "limited", allowed_hosts: ["<api.host.com>"]}, injection_location: {header: true}}}
JQ
unset CMA_KEY
```

A repo mount (`github_repository`) takes its token as `authorization_token` when the session is
created: from the person's environment in a script, from a repository secret in a GitHub Action.
Never write it into a committed file.

4. Verify without spending much: a smoke session with the prompt "Confirm you can reach <service>
   and list 1 item. Do not start the task." A wrong token shows up only here, not at session
   creation.

## Rules

- Never ask for a secret in the chat, never echo it, never put it in a file, a URL or a log.
- If the person pastes a secret into the chat anyway, tell them to rotate it, and do not use it.
- Rotate by creating the credential again with the new value; archive the old one only if asked.
