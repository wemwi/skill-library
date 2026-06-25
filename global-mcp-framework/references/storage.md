# Storage: KV

## Binding vs. Namespace-Name

- Das Binding **muss exakt `OAUTH_KV` heißen** — vom Provider hardcodiert, nicht
  konfigurierbar. In `wrangler.jsonc` steht `"binding": "OAUTH_KV"` und zeigt per ID
  auf den Namespace.
- Der Namespace-**Name** im Dashboard ist frei wählbar (Konvention:
  `MCP_OAUTH_<SERVICE>`, wobei `<SERVICE>` den Worker-Namen spiegelt — Worker-Name
  ohne `-mcp`, uppercase, Bindestrich → Unterstrich, z.B. `google-sheets-mcp` →
  `MCP_OAUTH_GOOGLE_SHEETS`). **Name ≠ Binding** — nur das Binding muss `OAUTH_KV` sein.
- Pro Server ein eigener Namespace.

## Inhalt

Gehashte Tokens (Access/Refresh), DCR-Client-Registrierungen, Grants, kurzlebiger
Login-State. Nur Hashes + verschlüsselte `props`, nie Klartext-Tokens. Ein kompletter
KV-Leak offenbart daher nur Metadaten.

## KV-Hygiene

Bei Single-User läuft KV praktisch nicht voll — TTLs räumen automatisch: Access-Token
~1h, Refresh-Token Default 30d, DCR-Clients Default 90d.

**Aber:** bei `refreshTokenTTL: undefined` (siehe `auth.md` — gewollt, damit headless
Agents verbunden bleiben) laufen Grants nicht von selbst ab, und jeder Reconnect
hinterlässt einen toten DCR-Client + Grant.

`purgeExpiredData()` würde abgelaufene und verwaiste Records räumen und liegt als
`scheduled`-Handler in der Foundation bereit (von `createOAuthWorker` geliefert, in der
Foundation gekapselt, damit alle Server ihn erben). Der **wird stack-weit aber nicht
getriggert**: Der Cloudflare Free Plan limitiert Cron Triggers, deshalb setzen wir gar
keine Cron Jobs — kein `triggers`/`crons`-Block in der `wrangler.jsonc` (siehe
`deploy.md`). Der Handler bleibt im Code erhalten und ist bei Bedarf reaktivierbar, läuft
aber nie automatisch.

**Bewusst akzeptierte Folge:** Ohne periodischen Purge und mit `refreshTokenTTL:
undefined` verfallen Grants und verwaiste DCR-Clients nicht von selbst. Bei Single-User
ist das unkritisch, weil KV praktisch nicht voll läuft; bei Bedarf den betroffenen
Namespace manuell im Dashboard räumen (Storage & Databases → KV). Das ist eine bewusste
Entscheidung, kein Versehen.
