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

# Storage: R2 (presigned Download)

Wenn ein Tool eine Datei zurückgeben muss, die zu groß oder zu binär für den
Modell-Kontext ist (gescanntes PDF, Bild, Archiv), läuft sie **nicht** als base64 durch
den Tool-Output — das bläht den Agenten-Kontext auf und ist teuer. Stattdessen: der
Worker holt die Bytes serverseitig, legt sie in R2 ab und gibt nur eine kurzlebige,
**token-freie** presigned GET-URL zurück. Der Consumer (z.B. eine Agent-Sandbox) zieht
sie per `curl -o <datei> "<url>"`.

## Binding vs. Bucket-Name

Zwei Ebenen wie bei KV — mit einer wichtigen Unterscheidung beim Binding:

- **Binding** (worker-lokal) = `<FUNKTION>_<TYP>`, z.B. `DOWNLOAD_R2`. **Funktional,
  nicht aussteller-basiert** — anders als ein Secret (`<AUSSTELLER>_<TYP>`, siehe
  `secrets.md`). Das Binding beschreibt, *wozu* der Worker die Ressource nutzt
  (Download-Ablage), nicht *wer* sie ausstellt. `OAUTH_KV` folgt derselben funktionalen
  Logik, ist dort nur zusätzlich vom Provider hardcodiert; R2-Bindings sind frei wählbar.
- **Bucket-Name** (globale Ressource) = `mcp-download-<service>`, z.B.
  `mcp-download-telegram`. Wie der KV-Namespace `MCP_OAUTH_<SERVICE>` service-getragen,
  aber **lowercase + Bindestrich** statt uppercase/Unterstrich — Bucket-Namen sind
  S3-kompatibel und dürfen weder Uppercase noch Unterstrich tragen
  (`MCP_DOWNLOAD_TELEGRAM` wäre ungültig).

## Vier Fallstricke

1. **Outbound-Token bleibt serverseitig.** Den Anbieter-Token (z.B. den Bot-Token im
   `getFile`-Pfad) nur **auf dem Worker** zum Abholen verwenden — **nie** in die
   zurückgegebene URL packen. Die presigned URL signiert ausschließlich gegen die
   R2-S3-Credentials und ist token-frei; der Outbound-Token verlässt den Worker nie.
2. **`signQuery: true`.** Die GET-URL wird über `aws4fetch` query-signiert
   (`AwsClient.sign(req, { aws: { signQuery: true } })`), nicht per Auth-Header — nur so
   ist sie ohne Zusatz-Header per `curl` ziehbar.
3. **`allowed_hosts` am Consumer.** Der konsumierende Managed Agent braucht
   `<account-id>.r2.cloudflarestorage.com` in seinen `allowed_hosts`, sonst schlägt der
   `curl`-Download **still** fehl. Build-Zeit-Kopplung zwischen MCP-Server und Agent —
   leicht zu übersehen, weil am Server selbst nichts fehlt.
4. **Zwei Ablauf-Uhren, nicht eine.** Die *URL-TTL* (`X-Amz-Expires`, kurz, z.B. 300 s)
   steuert, wie lange der Link signiert gilt. Die *Objekt-Lebensdauer* steuert eine
   **separate** Bucket-Lifecycle-Regel („delete after 1 day", im Dashboard). Beide
   unabhängig setzen — eine kurze URL-TTL räumt das Objekt nicht weg, und die
   Lifecycle-Regel verlängert die URL nicht.

## Skizze

```ts
// put läuft übers Binding (kein Credential nötig), presign über die S3-Creds:
await env.DOWNLOAD_R2.put(key, bytes, { httpMetadata: { contentType } });

const client = new AwsClient({
  accessKeyId: env.R2_ACCESS_KEY_ID,
  secretAccessKey: env.R2_SECRET_ACCESS_KEY,
  service: "s3",
  region: "auto",
});
const endpoint = new URL(
  `https://${env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com/${BUCKET_NAME}/${key}`,
);
endpoint.searchParams.set("X-Amz-Expires", "300");
const signed = await client.sign(new Request(endpoint, { method: "GET" }), {
  aws: { signQuery: true },
});
return signed.url; // token-frei, läuft nach 300 s ab
```

`aws4fetch` ist dependency-frei und hat eine `worker`-Export-Condition — als direkte
Server-Dependency eintragen **und ins `package-lock.json` aufnehmen**, sonst bricht der
Cloudflare-Build an `npm ci` („Missing: … from lock file").

## Conditional registrieren + Foundation

Das Tool nur registrieren, wenn der Worker R2 konfiguriert hat (Binding + die beiden
R2-Secrets vorhanden). Speist ein Repo zwei Worker über Environments und nur einer trägt
R2, exponiert der andere das Tool gar nicht erst (Guard im `buildServer`).

Der Presign-Code bleibt vorerst **im Server**, nicht in der Foundation — erst wenn ein
**zweiter** Konsument dasselbe Pattern braucht, lohnt das Hochziehen als
Foundation-Subpath (analog zur Schema-/SDK-Fassade). Ohne zweiten Nutzer wäre
Foundation-Code nur spekulative Abstraktion.
