# Gate-Hooks

Diese beiden Dateien gehoeren ins `server-template/` der Foundation, damit jeder neue
MCP-Server sie automatisch erbt:

```
server-template/.claude/settings.json          <- aus settings.json
server-template/.claude/hooks/pre-push-gate.sh  <- aus pre-push-gate.sh (chmod +x)
```

Wirkung: Vor jedem `git push` prueft der Hook zuerst die `TOOL_ALLOWLIST` in
`src/server.ts` gegen `^[a-zA-Z0-9_-]{1,64}$` (kein Punkt/Leerzeichen — sonst
weist der Connector den Tool-Namen ab). Danach laufen `npm run typecheck` und
`npx wrangler deploy --dry-run`. Schlaegt eines fehl — oder fehlt die `wrangler.jsonc`
im Build-Root — wird der Push mit Exit 2 blockiert und Claude bekommt den Grund als
Feedback. Damit ist die Build-Verifikation erzwungen, nicht nur empfohlen.

Voraussetzung in der Claude-Code-Umgebung: `jq`, installierte Dependencies
(`npm install`, inkl. der echten Foundation-Tag-URL statt Platzhalter) und `wrangler`.
