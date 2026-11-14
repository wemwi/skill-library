// make-run-view.js — Text einer Make-Seite lesen, ohne dass Zugangsdaten in den Chat kommen.
//
// Für Laufansichten (…/scenarios/<Szenario>/logs/<Lauf>) und den Reiter der unvollständigen
// Ausführungen (…/scenarios/<Szenario>/dlq). Regel und Anlass: references/tools.md,
// Abschnitt „Laufansichten im Browser lesen“.
//
// Gebrauch: den Inhalt dieser Datei als Skript an das Skript-Werkzeug des Browsers geben
// (Claude in Chrome: javascript_tool). Vorher nur die Werte unter „Einstellungen“ setzen,
// den Rest nicht ändern. Antwort: JSON { teil, teile, ersetzt, text } oder { fehler }.
// „ersetzt“ zählt die ersetzten Stellen. Bleibt nach dem Ersetzen etwas stehen, das wie eine
// Adresse mit Pfad oder wie ein Bot-Token aussieht, kommt kein Text zurück, nur { fehler }.
await (async () => {
  // ── Einstellungen ──────────────────────────────────────────────────────────────────────
  const TEIL = 0; // welches Stück der Ausgabe, ab 0; „teile“ nennt die Gesamtzahl
  const AB = ''; // Text, ab dem gelesen wird (leer: ganze Seite), z. B. 'Advanced log'
  const BIS = ''; // Text, vor dem das Lesen endet (leer: bis zum Ende)
  const KLICK = ''; // genauer Text eines Elements, das vorher geklickt wird, z. B. 'Show all'
  const WARTEN_MS = 4000; // Wartezeit auf die Seite und nach dem Klick
  const LAENGE = 850; // Zeichen je Stück; das Werkzeug kürzt Ausgaben bei rund 1000

  // ── Ersetzen ───────────────────────────────────────────────────────────────────────────
  let ersetzt = 0;
  const rep = (s, re, fn) =>
    s.replace(re, (...m) => {
      ersetzt += 1;
      return fn(...m);
    });
  const mask = (s) => {
    let t = String(s);
    // Adressen: Schema und Host bleiben. Pfad und Abfrage tragen Tokens und Schlüssel.
    t = rep(
      t,
      /\b([a-z][a-z0-9+.-]{1,15}:\/\/)([^\s/?#"'<>]+)[^\s"'<>]*/gi,
      (_, schema, host) => schema + host.replace(/^.*@/, '') + '/[…]',
    );
    // Bot-Token von Telegram (Zahl, Doppelpunkt, langer Schlüssel), auch ohne Adresse
    t = rep(t, /\b(?:bot)?\d{6,12}:[A-Za-z0-9_-]{30,}/gi, () => '[Token]');
    // JWT
    t = rep(t, /\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}/g, () => '[Token]');
    // Schlüssel mit bekanntem Anfang (Airtable, GitHub, Shopify, Slack, Google und ähnliche)
    t = rep(
      t,
      /\b(?:pat[A-Za-z0-9]{14}\.[A-Za-z0-9]{20,}|key[A-Za-z0-9]{14}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|shp(?:at|ss|ca|pa)_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[A-Za-z0-9_-]{30,})\b/g,
      () => '[Token]',
    );
    // Kopfzeilen und Paare aus Name und Wert
    t = rep(t, /\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}/g, (_, art) => art + ' [Token]');
    t = rep(
      t,
      /\b(api[_-]?key|x-api-key|access[_-]?token|refresh[_-]?token|bot[_-]?token|client[_-]?secret|token|secret|password|passwort|authorization)\b(["']?\s*[:=]\s*["']?)(?!\[Token\]|Bearer |Basic )([^\s"',;}&]{6,})/gi,
      (_, name, trenner) => name + trenner + '[Token]',
    );
    // Lange Zeichenketten ohne Leerzeichen (ab 40 Zeichen). Lauf-IDs mit 32 Zeichen bleiben.
    t = rep(t, /[A-Za-z0-9_+/=-]{40,}/g, () => '[lang]');
    return t;
  };
  // Was nach dem Ersetzen nicht mehr vorkommen darf
  const rest = (t) =>
    /\d{6,12}:[A-Za-z0-9_-]{30,}/.test(t) || /[a-z][a-z0-9+.-]{1,15}:\/\/[^\s/]+\/(?!\[…\])/i.test(t);

  // ── Lesen ──────────────────────────────────────────────────────────────────────────────
  const warten = (ms) => new Promise((fertig) => setTimeout(fertig, ms));
  await warten(WARTEN_MS);
  if (KLICK) {
    const ziel = [...document.querySelectorAll('button, a, [role="button"], span, div')].find(
      (e) => e.textContent.trim() === KLICK && e.children.length <= 1,
    );
    if (!ziel) return JSON.stringify({ fehler: 'KLICK nicht gefunden' });
    ziel.click();
    await warten(WARTEN_MS);
  }
  let roh = document.body.innerText;
  if (AB) {
    const von = roh.indexOf(AB);
    if (von < 0) return JSON.stringify({ fehler: 'AB nicht gefunden' });
    roh = roh.slice(von);
  }
  if (BIS) {
    const bis = roh.indexOf(BIS, AB.length);
    if (bis >= 0) roh = roh.slice(0, bis);
  }
  const text = mask(roh)
    .replace(/[ \t ]+/g, ' ')
    .replace(/\s*\n\s*/g, ' | ');
  if (rest(text)) return JSON.stringify({ fehler: 'Ersetzen unvollständig, kein Text ausgegeben', ersetzt });
  const teile = Math.max(1, Math.ceil(text.length / LAENGE));
  return JSON.stringify({ teil: TEIL, teile, ersetzt, text: text.slice(TEIL * LAENGE, (TEIL + 1) * LAENGE) });
})();
