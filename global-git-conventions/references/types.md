# types.md — Repo-Typen

Der Repo-Name-Suffix steuert Template und Config. Drei Typen.

## `*-mcp` — MCP-Server (Cloudflare Worker)

- **Beispiele:** `google-sheets-mcp`, `lexware-mcp`, `telegram-mcp`
- **README:** `assets/readme/mcp.md`
- **release-type:** `node` (TS/JS mit `package.json`)
- **Besonderheiten:**
  - `## Bereitstellung` enthält die **Live-URL** (`https://mcp-<service>.wemwi.workers.dev/mcp` — Worker-Name mit `mcp-`-Präfix, nicht der Repo-Name) und die bereitgestellten Tools.
  - `## Setup` enthält die Secrets/Bindings als Tabelle. Die *Mechanik* (OAuth, KV, wrangler) ist in `global-mcp-framework` dokumentiert — die README listet nur Namen, Pflicht-Flag und repo-spezifische Hinweise.
  - Der Foundation-Pin steht in der `package.json` und wird von Renovate gepflegt (siehe `automation.md`) — keine README-Zone.

## `*-foundation` — gemeinsame Basis

- **Beispiel:** `mcp-foundation`
- **README:** `assets/readme/foundation.md`
- **release-type:** `node`
- **Besonderheiten:**
  - Wird als **Git-Tag-Dependency** von den `*-mcp`-Repos konsumiert.
  - `## Bereitstellung` beschreibt die **exportierte Oberfläche** (was Consumer importieren) und nennt die aktuelle Tag-Version prominent.
  - Versionierungsdisziplin ist hier am kritischsten — Breaking Changes MÜSSEN als solche markiert werden (siehe `versioning.md`).

## `*-library` — Inhalts-Sammlung (kein Code-Paket)

- **Beispiel:** `skill-library`
- **README:** `assets/readme/library.md`
- **release-type:** `simple` (kein `package.json`-Bump; versioniert nur via Tag + CHANGELOG)
- **Besonderheiten:**
  - `## Bereitstellung` listet das **Inventar** (welche Skills/Inhalte enthalten sind, jeweils mit eigener Version, falls relevant).
  - `## Setup` beschreibt, wie Inhalte genutzt/installiert werden (z.B. `.skill`-Pakete).
  - **Zwei Versionsebenen:** release-please versioniert das Repo als Einheit; die `metadata.version` im einzelnen `SKILL.md` wird von Hand gepflegt und ist davon entkoppelt. Details: `versioning.md`.

## Neuen Typ ergänzen

Kommt ein weiterer Suffix dazu (z.B. ein Theme-Repo): neues Template in `assets/readme/` anlegen, Zeile in der Tabelle in `SKILL.md` und hier ergänzen, `release-type` festlegen. Die Pflichtsektionen aus `conventions.md` bleiben gleich — nur `## Bereitstellung` und `## Setup` werden typ-spezifisch gefüllt.
