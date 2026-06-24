# <repo-name>

![Version](https://img.shields.io/github/v/release/<OWNER>/<repo-name>)

> <Einzeiler: welcher Dienst wird als MCP-Server bereitgestellt und wofür.>

## Zweck

<2–3 Sätze: Welches Problem löst dieser MCP-Server? Welchen Dienst kapselt er
(z.B. Google Sheets, Lexware, Telegram) und warum als eigener Worker?>

## Bereitstellung

**Live-URL** (für die Connector-Config):

```
https://<repo-name>.wemwi.workers.dev/mcp
```

Bereitgestellte Tools:

| Tool | Zweck |
|------|-------|
| `<tool_name>` | <einzeilige Beschreibung> |
| `<tool_name>` | <einzeilige Beschreibung> |

## Setup

Secrets & Bindings (Mechanik siehe `global-mcp-framework`):

| Name | Typ | Pflicht | Hinweis |
|------|-----|---------|---------|
| `<SECRET_NAME>` | Secret | ✅ | <Format-/Quelle-Hinweis> |
| `OAUTH_KV` | KV-Binding | ✅ | Namespace `MCP_OAUTH` |

## Gotchas

- _(noch keine — hier kommt rein, was beim letzten Mal Zeit gekostet hat: Symptom → Ursache → Fix)_

## Versionierung

Versionen und Änderungen: siehe [`CHANGELOG.md`](./CHANGELOG.md). Versionierung
läuft automatisch über Conventional Commits + release-please — Tags nicht von Hand setzen.
