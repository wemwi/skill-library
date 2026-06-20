# Transport: stateless

Streamable-HTTP, **stateless** betrieben.

## Die drei Regeln

- `sessionIdGenerator: undefined` — der Server vergibt keine MCP-Session-Id und
  erwartet keine Session-Persistenz. Jeder Request ist eigenständig.
- **Pro Request eine frische `McpServer`- UND Transport-Instanz** (Guard ab
  MCP-SDK 1.26.0 / Agents-SDK v0.4.0). KEINE modul-globale Instanz — sonst
  Cross-Client-Response-Leakage bzw. Verbindungsfehler.
- KEIN Durable Object, KEIN McpAgent.

## Warum stateless kritisch ist

Lief der Transport stateful (Session-Id vergeben, aber kein DO/State, das sie hält),
dann kam `initialize` durch — der Connector zeigt die Tools an. Der erste echte
Tool-Call traf aber eine frische Worker-Invocation ohne diese Session und scheiterte
mit **`Session terminated`**.

Stateless löst das, weil über Requests hinweg keine Session gehalten werden muss.

Wenn `Session terminated` trotz `sessionIdGenerator: undefined` auftritt, ist die
zweite Ursache eine klebende MCP-Session im langen Debug-Thread → im frischen Chat
testen. Siehe `diagnostics.md`.

## Kontext

Der authentifizierte Kontext erreicht den Handler über `ctx.props` (siehe `auth.md`).
Ein eigener Token-Check ist nicht nötig — der Provider validiert vor dem `apiHandler`.
