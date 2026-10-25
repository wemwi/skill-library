# Audit (R1–R6, W1)

**Zweck:** prüft je Datei, ob nur Rollen und Kontext gebunden sind. Ziel: 0 Treffer in R1–R5 (Core zusätzlich R6). Läuft vor jeder Core-Veröffentlichung (Gate), nach jedem Library-Update und nach jedem Umbau.

## Inhalt
1. Ablauf
2. Regeln
3. Festgelegte Ausnahmen
4. Wertabgleich bei Umbauten
5. Ausgabe

---

## 1. Ablauf

1. Eingabe: Datei-Schlüssel, Liste der aktuellen Core-Variablen (Schlüssel → Name, Sammlung, Ebene Palette/Rollen/Kontext) und erlaubte Datei-lokale Sammlungen (Print: `Onlineprinters`).
2. Seiten holen, `_SANDBOX` auslassen (außer vor dem Löschen von Variablen: dann alle Seiten inklusive `_SANDBOX`). **Je Seite ein eigener Aufruf mit `setCurrentPageAsync`** — `page.loadAsync()` lädt Seiten nur teilweise. Seiten parallel.
3. Jede Ebene prüfen; Fundstelle = Seite › oberster Rahmen › Baustein › Ebene, Status „eigen“ oder „im Exemplar“.

**Zählweise:** je Ebene × Variable (eine Ebene mit Füllung und Kontur an derselben Variable zählt einmal), als **gesamt (eigene)**. „Eigene“ = Ebenen außerhalb von Exemplaren, also das, was man in der Datei selbst umbindet; der Rest erbt vom Baustein. `font-family/*` und `font/*`-Größen an Textebenen kommen über die Text Styles und sind keine direkten Bindungen. Exemplare des Core-Deckblatts in den INDEX-Seiten gehören Core.

**Variablen-IDs:** In Core lokal (`VariableID:315:215`), in Konsumenten mit Library-Schlüssel (`VariableID:<key>/…`). Suchen nach Bindungen decken beides ab.

---

## 2. Regeln

| Nr. | Prüft | Treffer, wenn | Ausnahme |
|---|---|---|---|
| R1 | Palette-Bindung | gebundene Variable gehört zur Palette | Schrift-Bindungen (`font-family/*`) an Textebenen, mit oder ohne Text Style. R1 prüft Farben, Deckkraft und Unschärfe |
| R2 | Waise | Variable ist weder in Core noch in einer erlaubten lokalen Sammlung | – |
| R3 | Fester Wert | sichtbare Vollfarbe (Füllung oder Kontur mit Stärke > 0) ohne Variable und ohne Farbstil | siehe Abschnitt 3 |
| R4 | Alte Kopie | Variable in Core, aber Name in der Datei ≠ Core-Name | – (Abhilfe: Update annehmen, Bindungen umziehen, `mcp.md`) |
| R5 | Modus | expliziter Modus an einer Sammlung, die nicht die aktuelle ist, oder Modusname veraltet; Color-Scheme-Modus an einem Tag-Exemplar | – |
| R6 (nur Core) | Rollen-Hygiene | Rolle/Kontext-Farbe mit festem Wert statt Alias; Scope ALL_SCOPES; fehlende Beschreibung; fehlender Code-Name, wo das Theme einen hat; Palette nicht verborgen (außer `font-family/*`); Palettenname passt nicht zum Wert (Stufe ≠ L* auf 5 gerundet, Alpha-Suffix ≠ Deckkraft); farbige Rolle wechselt je Modus die Farbfamilie (Modus-Regel) | `icon` → `text` (Alias in derselben Sammlung); Flächen- und Neutralrollen bei der Farbfamilie; `effect/glow` beim Scope (boolesche Variablen lassen sich in Figma nicht eingrenzen) |
| W1 (Hinweis) | Verlauf | Verlaufsstopps ohne Variable | – (Figma bindet Verlaufsstopps; W1 zählt nicht als Treffer) |

Treffer „im Exemplar“ verschwinden, wenn der Baustein umgebunden ist; was danach übrig bleibt, sind Überschreibungen an Exemplaren.

---

## 3. Festgelegte Ausnahmen

Kein Treffer, bleiben bewusst so:

**R1**
- Schrift-Bindungen an Textebenen, auch ohne Text Style (z. B. Kopfzeilen der Pricing Table, Widerspruchshinweis, große Texte in den Onlineprinters-Vorlagen).
- Core › File Meta: die Textebenen von Deckblatt, Inhaltsverzeichnis, Changelog, Status, Version Pill und Changelog Note behalten feste Größen und die direkte Schrift-Bindung; keine Text Styles.

**R3**
- Logo-Grafik in Core › Logos (eigene Farbwelt).
- Druckhilfen: Ebenen unter „Print Meta“, Schnittmarken, „Cut Mark“, „Cut Guide“; Schnittmarken des Ordnereinlegers fest #B8923A.
- Lila Standardrahmen von Variantensets.
- Bilder.
- Farben unter 100 % Deckkraft, wenn keine Alpha-Stufe der Palette über eine Rolle passt: Tönungen (Info Box, TierBox, Version Pill), Linien Weiß 40 % und Schwarz 20–40 % (Tabellen, Inhaltsverzeichnis, Bestandsprotokoll), Trennpunkte im Price Tier. Grund: eine gebundene Füllung läuft in Figma immer mit 100 % Deckkraft (`mcp.md`). Text mit Teil-Deckkraft bekommt Füllung 100 % an der Rolle und die Ebenen-Deckkraft an `opacity/*`.
- Etiketten in Product › 01 · Label (Vorlage, Mengenangabe hell/dunkel, Pflanzenzeichnungen, Footer, Badge, Export-Rahmen, Sortentitel) als Druckvorlage mit eigener Farbwelt.
- Sales App: Präsentationsrahmen „Light (Color Scheme: White)“ / „Dark (Color Scheme: Forest)“ und Gerätegrafik (Status Bar, Dynamic Island).

**W1**
- Mengenangabe-Verlauf auf den Etiketten (Gold → Creme) fest.
- Verlaufsstopp Creme im Poster-Badge (Print).
- Verläufe der Ebene „Glow“ im Baustein Screen (Sales App), Mini Chart, Favicon, Deckblatt-Hintergründe, Highlight und Callout Box in Print, Etiketten-Verläufe in Product.

**Sonst**
- Print › Components läuft im Layout-Modus Desktop (Rahmen „Global“ ohne Layout-Modus). Die Vorschau zeigt Desktop-Werte; die Dokumente setzen ihren Druckmodus selbst.

---

## 4. Wertabgleich bei Umbauten

- **Vorher sichern, nachher vergleichen:** aufgelöste Füllungen, Konturen, Deckkraft (wirksam = Füllung × Ebene), Effekte und Größen je Ebene. Feiner als ein Hash je Seitenrahmen: je Variante bzw. Unterrahmen einen Hash als unsichtbare Plugin-Daten an der Seite ablegen und danach dagegen prüfen; übersteht Aufrufgrenzen.
- **Wertprüfung am Baustein reicht nicht.** Eine Rolle ist modusabhängig, die Palette nicht. Exemplare auf anderer Fläche können anders aufgehen (Beispiel: ein Baustein mit Fläche `background` wird auf Weiß unsichtbar). Abhilfe: Baustein mit fester Fläche setzt seinen Modus selbst.
- **Prüfweg für Konsumenten:** Rollen probeweise zurück auf die Palette binden und den Rahmen-Abgleich rechnen, dann abbrechen (nichts bleibt). Abweichungen zeigen genau die betroffenen Ebenen.
- **Exemplar-Prüfung je Baustein:** nach dem Umbinden jedes Exemplar auf allen Seiten suchen (Hauptkomponente vergleichen), den Gegenknoten über die ID „Exemplar;Knoten“ holen und den aufgelösten Wert gegen den Sollwert prüfen.
- **Auch die Components-Seite abgleichen**, nicht nur die Dokumente: die Vorschau der Bausteine zeigt Rollen im Modus des umgebenden Rahmens.
- Gewollte Änderungen vorher als Liste erwarteter Unterschiede festhalten; andere Abweichungen = Abbruch.
- Sichtprüfung: Screenshots hell/dunkel je Seite bzw. PDF der Druckseiten an Joscha.

---

## 5. Ausgabe

Je Datei eine Tabelle Regel · Treffer eigen/gesamt · erste 10 Fundstellen mit Namen (Seite › Rahmen › Baustein › Ebene). Ausnahmen getrennt zählen. **Keine IDs in der Ausgabe an Joscha.**
