# Icons (Font Awesome, Core › Icons)

Pipeline für Icons in Core. Konsumenten nutzen die Icons nur als Exemplare aus Core.

## Quelle
- Quelle ist das Pro-Paket (Stand 7.3.1), nie das Figma-Plugin (lieferte v6 bzw. Gruppen ohne Bindung).
- Kein Vollimport des Pakets (Tausende Komponenten, träge Library): nur angelegt, was ein File nutzt.

## Sets
- `Font Awesome Classic` und `Font Awesome Duotone` als Grid mit einer Spalte je Weight (Solid · Regular · Light), Zeilen alphabetisch, `Icons` als Default-Variante oben.
- `Font Awesome Brand` separat.

## Variante bauen
- Jede Variante 40 × 40 (Breite an `icon/large`), Glyphe im Font-Awesome-Raster (640 Einheiten = 40 px, Faktor 1/16).
- `createNodeFromSvg` mit dem SVG aus `svgs/<stil>/` (viewBox W × 512), `rescale(1/16)`, Versatz x + (640 − W)/32, y + 4.
- Füllung an `color/scheme/icon`, Constraints Scale.
- Duotone = zwei Ebenen (Sekundär 40 % Ebenendeckkraft, Primär 100 %). Duotone-Glyphen ohne Sekundärpfad (z. B. `list`) haben keinen Zweiton-Effekt.

## Tauschen statt neu anlegen
Icons immer **in bestehenden Varianten tauschen**, nie neu anlegen und alte löschen — sonst brechen die Instanzen in den Consumer-Files.

## Danach
- Core-Changelog (MINOR für neue Icons, eine Version pro Tag); Veröffentlichen und Annehmen macht Joscha.
- Nach der Annahme in den Konsumenten R4/R5 prüfen (`audit.md`).
