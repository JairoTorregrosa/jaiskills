# conectores.md — find the MCP server for a service and wire it

You are about to propose an MCP connector for a service the job names. Find a real, remote server,
learn how it authenticates, and allowlist only the tools the job needs.

## Facts already verified (2026-10-24)

- GitHub: `https://api.githubcopilot.com/mcp/x/all` (or `/mcp/x/<toolset>`; add `/readonly` for
  reads only). Auth: a fine-grained PAT as `static_bearer`. Tested in 8 agents. [live runs]
- Notion: `https://mcp.notion.com/mcp`, OAuth (`mcp_oauth`). Configured, not run: no token. [agent create]
- The official MCP Registry answers `GET https://registry.modelcontextprotocol.io/v0/servers?search=<name>`
  with each server's `remotes` (transport, URL, required headers). [curl, 2026-10-24]

- Anthropic's `knowledge-work-plugins` (Apache-2.0) wire 78 remote MCP URLs in their `.mcp.json`
  files; they are the best starting list for business agents:
  `gh api repos/anthropics/knowledge-work-plugins/contents/<plugin>/.mcp.json --jq .content | base64 -d`.
- Some servers need an OAuth app the person registers first (no dynamic client registration):
  Google Workspace, Slack, HubSpot, Salesforce, Snowflake, Microsoft 365. Plan 15-30 minutes for
  that before the workshop session; otherwise start with a file upload. [vendor docs]
- AWS's MCP server needs SigV4 signing, which a vault credential cannot produce: use the AWS
  Knowledge server for docs, or the CLI with keys in an `environment_variable`. [AWS docs]

## Official remote servers (probed 2026-10-24)

"OAuth" = answered 401 with OAuth resource metadata → `mcp_oauth`. "none" = public. Check the
vendor page before trusting a row marked *preview*.

| Family need | Service | URL | Auth |
|---|---|---|---|
| Email, calendar, files | Gmail · Calendar · Drive · Sheets | `https://gmailmcp.googleapis.com/mcp/v1` · `calendarmcp` · `drivemcp` · `sheetsmcp` (`.googleapis.com/mcp/v1`) | OAuth, own Google Cloud client; *developer preview* |
| | Microsoft 365 | Work IQ / Agent 365 servers; needs an Entra admin | OAuth; *preview*. Fallback: Graph API + `environment_variable` |
| | Box · Egnyte | `https://mcp.box.com` · `https://mcp-server.egnyte.com/mcp` | OAuth |
| Chat, tasks, docs | Slack | `https://mcp.slack.com/mcp` | OAuth, own Slack app |
| | Notion | `https://mcp.notion.com/mcp` | OAuth |
| | Linear | `https://mcp.linear.app/mcp` (`/mcp/readonly`) | OAuth |
| | Atlassian (Jira, Confluence) | `https://mcp.atlassian.com/v1/mcp` | OAuth |
| | Asana · Monday · ClickUp · Trello | `https://mcp.asana.com/v2/mcp` · `https://mcp.monday.com/mcp` · `https://mcp.clickup.com/mcp` · `https://mcp.trello.com/v1` | OAuth |
| | Airtable | `https://mcp.airtable.com/mcp` | OAuth |
| CRM, sales | HubSpot | `https://mcp.hubspot.com/` | OAuth, own app |
| | Salesforce | `https://api.salesforce.com/platform/mcp/v1/platform/<server>` | OAuth + PKCE (External Client App) |
| | Apollo · Clay · Close · Outreach · ZoomInfo | `https://mcp.apollo.io/mcp` · `https://api.clay.com/v3/mcp` · `https://mcp.close.com/mcp` · `https://api.outreach.io/mcp/` · `https://mcp.zoominfo.com/mcp` | OAuth |
| Money | Stripe · PayPal · Square | `https://mcp.stripe.com` · `https://mcp.paypal.com/mcp` · `https://mcp.squareup.com/mcp` | OAuth |
| | QuickBooks · Xero · Zoho Books · Ramp · Expensify | `https://ai-inc.quickbooks.intuit.com/v1/mcp` · `https://mcp.xero.com/mcp` · `https://claude-zohobooks.zohomcp.com/mcp/message` · `https://mcp.ramp.com/mcp` · `https://www.expensify.com/mcp` | OAuth |
| | Mercado Pago · Mercado Libre | `https://mcp.mercadopago.com/mcp` · `https://mcp.mercadolibre.com/mcp` | OAuth; both mostly docs and app setup, not store operations |
| | Market data | Alpha Vantage `https://mcp.alphavantage.co/mcp` | OAuth |
| Marketing | Meta Ads | `https://mcp.facebook.com/ads` | OAuth; *open beta* |
| | TikTok Ads · Klaviyo · Mailchimp · Supermetrics | `https://business-api.tiktok.com/open_mcp/tt-ads-mcp-layer` · `https://mcp.klaviyo.com/mcp` · `https://ai-inc.mailchimp.com/claude/mcp/v2` · `https://mcp.supermetrics.com/mcp` | OAuth |
| | Canva · Figma | `https://mcp.canva.com/mcp` · `https://mcp.figma.com/mcp` | OAuth |
| | Ahrefs · Similarweb | `https://api.ahrefs.com/mcp/mcp` · `https://mcp.similarweb.com/mcp` | OAuth |
| Web data | Apify | `https://mcp.apify.com/` | OAuth |
| | Firecrawl · Exa | `https://mcp.firecrawl.dev/v2/mcp` · `https://mcp.exa.ai/mcp` | API key for real use; check the vendor page for the header |
| Support | Intercom | `https://mcp.intercom.com/mcp` | OAuth |
| | Zendesk | none confirmed → REST API + `environment_variable` | — |
| Engineering | GitHub | `https://api.githubcopilot.com/mcp/` (tested: `/mcp/x/all`) | `static_bearer` PAT |
| | Sentry · Datadog · PagerDuty · Grafana | `https://mcp.sentry.dev/mcp` · `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp` · `https://mcp.pagerduty.com/mcp` · `https://mcp.grafana.com/mcp` | OAuth (PagerDuty: check token form) |
| | Supabase · Neon · Vercel · Cloudflare | `https://mcp.supabase.com/mcp` · `https://mcp.neon.tech/mcp` · `https://mcp.vercel.com` · `https://mcp.cloudflare.com/mcp` | OAuth |
| Data | BigQuery | `https://bigquery.googleapis.com/mcp` | Google OAuth; enable only `execute_sql_readonly` and reads |
| | Snowflake | `https://<account>.snowflakecomputing.com/api/v2/databases/<db>/schemas/<schema>/mcp-servers/<name>` | OAuth or programmatic access token |
| | Hex · Amplitude | `https://app.hex.tech/mcp` · `https://mcp.amplitude.com/mcp` | OAuth |
| Research, health | PubMed (Anthropic-hosted) | `https://pubmed.mcp.claude.com/mcp` | none |
| | Clinical trials · bioRxiv · ChEMBL | `https://hcls.mcp.claude.com/{clinical_trials,biorxiv,chembl}/mcp` | none |
| | Consensus · Wiley Scholar Gateway | `https://mcp.consensus.app/mcp` · `https://connector.scholargateway.ai/mcp` | OAuth |
| Glue | Zapier | `https://mcp.zapier.com/api/v1/connect` | OAuth; exposes only actions the person configured |
| | n8n | `https://<instance>/mcp-server/http` | bearer or OAuth; *beta* |
| Docs only | AWS Knowledge · Autodesk Help | `https://knowledge-mcp.global.api.aws` · `https://developer.api.autodesk.com/knowledge/public/v1/mcp` | none |

No official remote server: WhatsApp messaging (Graph API + system-user token), arXiv
(`export.arxiv.org/api/query`, no key), NCBI E-utilities (`NCBI_API_KEY`), Looker Studio, Zendesk,
Belvo. Use the service's HTTP API from the sandbox with an `environment_variable` credential and
the host in `allowed_hosts`; WhatsApp and Telegram inbound go through the person's webhook,
which creates the Session.

Zapier or n8n is the bridge when the person already automates the service there: the agent calls
their workflow as a tool, and the person keeps control of what that workflow can do.

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
- Business connectors: https://github.com/anthropics/knowledge-work-plugins (`*/.mcp.json`)
- Google Workspace: https://developers.google.com/workspace/guides/configure-mcp-servers
- Meta: https://developers.facebook.com/documentation/mcp
- Slack: https://docs.slack.dev/ai/mcp-server/ · HubSpot: https://developers.hubspot.com/mcp
- Salesforce: https://developer.salesforce.com/blogs/2026/04/salesforce-hosted-mcp-servers-are-now-generally-available
- Snowflake: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp
- AWS: https://docs.aws.amazon.com/agent-toolkit/latest/userguide/getting-started-aws-mcp-server.html
- Mercado Libre: https://developers.mercadolibre.com.ar/en_us/mcp-server · n8n: https://docs.n8n.io/connect/connect-to-n8n-mcp-server
