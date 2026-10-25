# Figma-MCP: kann, kann nicht, Lehren

Gilt für den offiziellen Figma-Connector (`use_figma`, `get_metadata`, `get_screenshot` u. a.). Vor jedem `use_figma` den Skill figma-use laden. Die Grenze dessen, was das MCP kann, verschiebt sich; „geprüft“-Daten zeigen, wann ein Punkt zuletzt bestätigt wurde.

## Inhalt
1. Was MCP kann
2. Was MCP nicht zuverlässig kann
3. Lehren: Variablen und Modi
4. Lehren: Bausteine und Exemplare
5. Lehren: Lesen, Prüfen, Aufrufe

---

## 1. Was MCP kann

- Files lesen, Components/Frames auflisten, Variables/Styles auslesen, Screenshots/Exports anstoßen.
- Frames, Components und Variables **erstellen und editieren** (via `use_figma`), auch Scopes, Beschreibungen und Code-Namen.
- Pages anlegen (`figma.createPage()`, geprüft 2026-10-20) und Sections anlegen.
- Varianten an Exemplaren wechseln (`setProperties`) — Text- und Eigenschafts-Überschreibungen bleiben erhalten; die letzte Variante aus einem Set lösen, ohne dass Exemplare brechen (geprüft 2026-10-22).
- Verlaufsstopps an Variablen binden (geprüft 2026-10-22).
- Page-Listen via Workaround: `get_metadata` mit invalidem `nodeId` → Fehlermeldung enthält die vollständige Page-Liste.
- **Achtung:** `get_metadata` ohne `nodeId` liefert manchmal nicht alle Pages zurück (bekannter Bug). Verifizierung per Screenshot wenn die Page-Struktur kritisch ist.
- **Achtung Variablen-IDs:** In Core sind Variablen-IDs lokal (`VariableID:315:215`), in Consumer-Files enthalten sie den Library-Key (`VariableID:<key>/…`). Suchen nach Bindungen müssen beides abdecken.
- **Alte Kopien derselben Library-Sammlung teilen sich den Modus** (gleicher Schlüssel): Setzen des Modus an der aktuellen Kopie überschreibt den Eintrag der alten, Löschen entfernt beide. Skripte suchen vorhandene Modi über den Schlüssel, nicht über die Sammlungs-ID. **Umziehen auf die aktuelle Kopie:** erst den Modus an der alten Kopie löschen, dann an der aktuellen setzen (Modus-IDs sind über alle Kopien gleich); danach hängt der Eintrag an der aktuellen Kopie (geprüft 2026-10-23). Ausnahme: Slot-Vorgaben eines Bausteins liegen auf keiner Seite und lassen sich so nicht ändern; am Exemplar landet ein neu gesetzter Modus dann wieder an der alten Kopie. Dort den Modus nur löschen, wenn die Umgebung denselben Modus liefert (Farbabgleich davor und danach).
- **Bindungen an alten Library-Kopien:** `importVariableByKeyAsync` mit dem Schlüssel der gebundenen Variable liefert die aktuelle Kopie; weicht die ID ab, ist es eine alte Kopie. Im selben Aufruf umbinden, in zwei Durchgängen (erst Bausteine und eigene Ebenen, dann Exemplare und Slot-Inhalte), damit keine unnötigen Überschreibungen entstehen. Füllungen mit einer Alpha-Variable (z. B. Overlay) sind dabei wertgleich.
- **Baustein-Kopien aus fremden Bibliotheken:** Ein Exemplar kann an einem Baustein hängen, der als Library-Kopie in der Datei liegt, dessen Quelle aber in keiner veröffentlichten Bibliothek mehr steht. Bindungen darin lassen sich nicht ändern; Abhilfe ist der Tausch gegen den eigenen Baustein. Tausch im Baustein verwirft Überschreibungen in dessen Exemplaren: vorher sichern, danach wieder setzen.

## 2. Was MCP nicht zuverlässig kann

- DIN A2 @ 300 DPI rendern (übersteigt API-Renderer-Kapazität). Manuell aus Figma exportieren.
- Variable-Werte in JSON-Output zurückgeben (müssen ggf. per Screenshot/manuell beigesteuert werden).
- Sehr große Pages (~20+ Seiten Print-Content) in einem Call lesen — timeoutet. Frame-für-Frame nachladen.
- Community-Libraries (z. B. Apple iOS Kit) per API importieren („Not permitted“). Gerätedarstellung (Statusleiste, Home-Balken) selbst zeichnen.
- File-Thumbnail setzen (`setFileThumbnailNodeAsync` nicht unterstützt) — manuell per Rechtsklick.
- Mode-Reihenfolge einer Collection ändern — manuell im Variables-Panel ziehen.
- Library veröffentlichen und Library-Updates in Consumer-Files annehmen — manuell.
- Bindungen an Überschreibungen tief in verschachtelten Exemplaren (drei Ebenen) umsetzen — der Aufruf läuft ohne Fehler, die Bindung bleibt. (Gilt für Größen; Farbbindungen an Füllungen gingen 2026-10-22 auch vier Ebenen tief.)
- Füllungen mit Deckkraft unter 100 % an eine Variable binden — `setBoundVariableForPaint` setzt die Deckkraft auf 100 %, und Exemplare zeigen auch nach dem Zurücksetzen 100 %. Tönungen in Bausteinen fest lassen oder über eine Alpha-Stufe der Palette (Rolle) binden; nach jedem Binden ein Probe-Exemplar prüfen. Auch ein ausdrücklich gesetzter Wert hält nicht (geprüft 2026-10-23). Text mit Teil-Deckkraft: Füllung 100 % an der Rolle, Ebenen-Deckkraft an `opacity/*`; ohne passende Stufe bleibt der Wert fest (Ausnahme in R3).
- Scopes an booleschen Variablen setzen — wird abgelehnt (geprüft 2026-10-23).
- **Wenn MCP an Limits stößt** → manuell in Figma, oder REST API mit Personal Access Token.

---

## 3. Lehren: Variablen und Modi

- **Import nur zusammen mit Bindung:** `importVariableByKeyAsync` hält eine Variable nur, wenn sie im selben Aufruf gebunden wird; eine bloß importierte ist im nächsten Aufruf weg. Danach prüfen, dass die ID dem Muster `VariableID:<Schlüssel>/<Core-ID>` entspricht (keine zweite Kopie). Skripte binden nur an Variablen, die schon in der Datei hängen, oder prüfen vorher den Namen.
- **Variablenkopien wechseln beim Annehmen:** Nach einem Library-Update zeigen die Bindungen auf eine neue Kopie derselben Variable; die alte bleibt mit altem Wert lesbar. Variablen deshalb immer frisch aus einer bestehenden Bindung holen, nie aus einer gemerkten ID.
- **Modi fallen nach dem Annehmen zurück:** Nach einem Core-Update können die expliziten Farbmodi wieder an der alten Kopie hängen, während die Bindungen schon an der neuen hängen (R5). Umzug wie in Abschnitt 1, in zwei Durchgängen: erst eigene Ebenen, dann Exemplar-Ebenen mit eigenem Eintrag. Modus-Werte vorher sichern, weil ein Exemplar seinen geerbten Eintrag beim Umzug des Bausteins verliert. Nach jeder Annahme R5 prüfen.
- **Overlay mit Alpha:** Bei einer Farbvariable mit Alpha steht die Alpha als Deckkraft im Paint. Umbinden auf dieselbe Variable ist wertgleich; die Regel „Tönungen fest lassen“ betrifft nur Variablen ohne Alpha mit zusätzlicher Deckkraft.
- **Mischmodus und Variable:** Die Plugin-API verwirft den Mischmodus einer Vollfarb-Füllung, sobald sie an eine Variable gebunden wird. Ausweg: Verlauf mit zwei gleichen, gebundenen Stopps (Bild pixelgleich).
- **Verborgene Palette** löst über Rollen-Aliase in den Konsumenten korrekt auf (geprüft 2026-10-22). Vor dem Verbergen weiterer Palette-Werte prüfen, dass keine Datei sie direkt bindet (alle Seiten inklusive `_SANDBOX`), sonst entstehen Waisen.
- **Modi erben:** Exemplare erben den Farbmodus, den ihr Baustein selbst setzt (geprüft 2026-10-22).

## 4. Lehren: Bausteine und Exemplare

- **Austausch verwirft Slot-Inhalte:** `swapComponent` auf einen Baustein mit anders benanntem Slot verwirft den Inhalt dieses Slots; der Rücktausch stellt ihn nicht wieder her. Vor jedem Austausch Slot-Namen alt/neu vergleichen, Slot-Inhalte als Kopie sichern, tauschen, in den umbenannten Slot einsetzen; gleich benannte Slots behalten ihren Inhalt. Zuerst an einer Kopie testen.
- **Exemplare in Slot-Inhalten** nicht klonen und verschieben (verschwanden ohne Fehler); neu aus dem Baustein anlegen.
- **Gelöschte Hauptkomponenten:** Ein Exemplar kann an einem gelöschten Baustein hängen (`getMainComponentAsync` liefert ihn, er liegt auf keiner Seite). Dessen Bindungen tauchen im Audit nur im Exemplar auf.
- **Exemplar-Zählung:** `getInstancesAsync` zählt auch Exemplare in Slot-Vorgaben; die Zahl kann von der Seitenzählung abweichen. Nur Bausteine mit 0 Exemplaren löschen.
- **Komponenten-Eigenschaften steuern nur Sichtbarkeit.** Was abschaltbar sein soll (z. B. eine Trennlinie), wird eine eigene Ebene mit Boolean-Eigenschaft (Beispiel: Ebene „Divider“, absolut unten, 1 px, Fläche `border`, Eigenschaft „Show Divider“).
- **Text-Überschreibungen in Slots** fallen beim Einblenden einer Eigenschaft (z. B. „Show Status“) auf den Ausgangswert zurück; danach die Texte neu setzen.
- **Text-Ebenen an derselben TEXT-Component-Property** teilen Formatierung (Farbe, Unterstreichung) über die Varianten hinweg. Formatierung je Variante vor dem Binden setzen; nach Änderungen alle Varianten prüfen. Unterschiedliche Unterstreichung je Variante hält nicht.
- **Unterebenen ausgeblendeter Icons** sind am Baustein per Skript nicht erreichbar. Ein später eingeblendetes Icon folgt `icon` der Umgebung und muss dann gezielt gebunden werden (z. B. `color/global/<ton>-text` im Tag).

## 5. Lehren: Lesen, Prüfen, Aufrufe

- **`create_session`** mit dem fileKey vor allen Datei-Tools, auch beim reinen Lesen.
- **`use_figma` ist transaktional:** Ein Fehler rollt alle Schreibvorgänge des Aufrufs zurück.
- **Eine Seite je Aufruf:** `figma.setCurrentPageAsync()` je Seite in einem eigenen Aufruf; mehrere Seiten in einem Aufruf führen zu nicht gefundenen Knoten. `page.loadAsync()` lädt Seiten nur teilweise.
- **`get_metadata` auf einer Komponente** liefert keine Kinder; Unterrahmen direkt abfragen oder `get_design_context` nutzen (vorher figma-design-to-code laden).
- **Screenshots:** Die Download-Links von `get_screenshot` sind im Workspace gesperrt (Proxy). `get_screenshot` mit Base64-Antwort nutzen oder `node.screenshot()` als Datei ablegen; bei sehr großen Rahmen einzeln.
- **Automatische Ebenennamen:** Textebenen mit „Auto rename“ übernehmen beim Ändern der Füllung ihren Inhalt als Namen. Skripte merken den Namen vorher und setzen ihn zurück.
