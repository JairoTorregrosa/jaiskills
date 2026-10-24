# conectores.md — find the MCP server for a service and wire it

You are about to propose an MCP connector for a service the job names. Find a real, remote server,
learn how it authenticates, and allowlist only the tools the job needs.

## Facts already verified (2026-10-24)

- GitHub: `https://api.githubcopilot.com/mcp/x/all` (or `/mcp/x/<toolset>`; add `/readonly` for
  reads only). Auth: a fine-grained PAT as `static_bearer`. Tested in 8 agents. [live runs]
- Notion: `https://mcp.notion.com/mcp`, OAuth (`mcp_oauth`). Configured, not run: no token. [agent create]
- The official MCP Registry answers `GET https://registry.modelcontextprotocol.io/v0/servers?search=<name>`
  with each server's `remotes` (transport, URL, required headers). [curl, 2026-10-24]

## Do this

1. **Vendor first.** Search the vendor's own docs for "MCP server" (`web_search` or the
   `firecrawl` skill if installed). A vendor-hosted remote server beats a third-party one.
2. **Registry second.** `curl -s "https://registry.modelcontextprotocol.io/v0/servers?search=<name>&limit=10" | jq -c '.servers[] | {name: .server.name, remotes: .server.remotes}'`.
   Prefer the publisher whose namespace matches the vendor's domain (`com.notion/...`). Treat
   third-party wrappers as untrusted code that sees the person's data: say so before proposing one.
3. **Check it is usable here.** Managed Agents connects to remote servers by URL
   (`streamable-http`). A server that only runs locally (`stdio`, an npm package) does not work;
   say so and offer a custom tool or an API call from the sandbox instead.
4. **Learn the auth** from the registry `headers` or the docs, and map it to a vault credential:
   OAuth → `mcp_oauth`; a fixed token in `Authorization` → `static_bearer`. Write it in
   `credentials.md` with the minimum permissions.
5. **List its tools.** The names come from the server, not from you: the vendor docs, or a smoke
   test session with the toolset enabled and the prompt "List your MCP tools by name. Do nothing
   else." Then write `mcp.yaml` with `default_config: {enabled: false}` and one `configs` entry per
   needed tool: reads `always_allow`, writes `auto` or `always_ask`.
6. **Network.** Set `allow_mcp_servers: true` in `environment.yaml`, or session creation fails
   with a 400 that names the blocked host.

## Rules

- Never invent an MCP URL or a tool name. Unknown is "no connector found": fall back to a custom
  tool or to the service's HTTP API with an `environment_variable` credential.
- A mounted `github_repository` is files only. Opening a PR needs the GitHub MCP tools.

## Sources

- MCP connector: https://platform.claude.com/docs/en/managed-agents/mcp-connector.md
- Permission policies: https://platform.claude.com/docs/en/managed-agents/permission-policies.md
- MCP Registry API: https://registry.modelcontextprotocol.io/v0/servers?search=NAME
