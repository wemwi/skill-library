# Vertriebler

`tbl0ijvzkD7LH2XMM` · Kategorie **Stammdaten** (Geld-Sicht)

> Feld-Block: **Stand 2026-08-15**, aus `list_tables_for_base`. Verify-live — im Zweifel gewinnt die Base.

## Zweck

Der Vertriebler (in Lexware = **Kreditor**). Trägt den **laufenden Saldo** — die Summe, die selectedleafs ihm schuldet.

## Beziehungen

- **→ `Umsätze`** (Provision) · **→ `Lieferungen`** (Kostenanteil) · **→ `Auszahlungen`** (Ausgezahlt) · **→ `Bestandsprüfungen`**.
- **→ `Stores`** — die von ihm akquirierten Stores (`Stores.Akquise durch`, → [[stores]]).

## Tragende Felder — die Geldkette

- **`Nettoumsatz`** (Rollup ← Umsätze) · **`Kostenanteil`** (Rollup ← `Lieferungen.Kostenanteil`).
- **`Provision`** (Rollup ← `Umsätze.Provision`) — **nominal**, auf den vollen Nettoumsatz. Anzeige.
- **`Realprovision`** (Rollup ← `Umsätze.Realprovision`) — Provision auf den **tatsächlich Bezahlten** Betrag. **Das ist die saldo-relevante Größe.**
- **`Ausgezahlt`** (Rollup ← `Auszahlungen.Bezahlt`) — Σ der real überwiesenen Beträge (nicht statusgefiltert; `Bezahlt` ist bis zur Zahlung 0).
- **`Saldo`** (Formel, €) — **`Realprovision − Kostenanteil`**. ⚠️ nutzt **Realprovision**, nicht die nominale Provision.
- **`Offen`** (Formel, €) — `Saldo − Ausgezahlt`. Der Betrag, der noch aussteht.

## Weitere tragende Felder

- **`Besteuerung`** (Select: Kleinunternehmer / Regelbesteuerung) + **`Regelbesteuerung ab`** (Datum) — **wählt die passende [[konditionen]]-Version** (`Gültig für`). Kleinunternehmer ⇒ 0 % MwSt.
- **`Formularlink`** (Formel) — personalisierter Link auf das „Store anlegen"-Formular; belegt `Stores.Akquise durch` mit `RECORD_ID()` vor und blendet das Feld aus. Wird als `{Formularlink}` im Onboarding-Post ausgegeben. Bricht still, wenn Feld-ID von `Akquise durch` oder die Formular-Page-ID sich ändert.
- `Lexware ID` (Kreditor) · `Telegram Channel ID` (Sales-Channel) · PLZ / Ort / Straße · `Hinweis`.

## Fallstricke

- **`Saldo` = Realprovision − Kostenanteil**, nicht `Provision − Kostenanteil`. Die nominale `Provision` ist nur Anzeige; wer damit rechnet, überschätzt den Saldo bei offenen/teilbezahlten Umsätzen.
- `Ausgezahlt` rollt `Auszahlungen.Bezahlt` (real), nicht `Betrag` (beantragt) — Teilzahlungen zählen anteilig.

## Feld-Block (Stand 2026-08-15 · `list_tables_for_base`)

| Feld | Typ | fld-ID |
|---|---|---|
| Name | singleLineText | `fldhDp2HHI6BxjlZq` |
| Nettoumsatz | rollup € | `fldlpCAdVPTGNe5Nw` |
| Provision | rollup € (nominal) | `fldZYmnv1dlLiPpob` |
| Kostenanteil | rollup € | `fldHX32QucLsfDTr0` |
| Saldo | formula € | `fldZO8vJbgbwc5Udj` |
| Ausgezahlt | rollup € (← Ausz.Bezahlt) | `fldI2anszbyAWnqKa` |
| Offen | formula € | `fld3XtirjKm3VUBlw` |
| Realprovision | rollup € | `fldxv77iZbz3QxLJJ` |
| Hinweis | multilineText | `fldr6qhoPrJBK1enZ` |
| Umsätze | link → Umsätze | `fldxfb41lMhPDfWLi` |
| Auszahlungen | link → Auszahlungen | `fldD62ahzQlCCgwem` |
| Lieferungen | link → Lieferungen | `fldKQgIZ3NBsG1Xrx` |
| Bestandsprüfungen | link → Bestandsprüfungen | `fldZKAy9qPLA15BPl` |
| Besteuerung | singleSelect | `fldBcufVGhXAdxJHS` |
| Postleitzahl | number | `fldvsm8IZnzVQWJae` |
| Ort | singleLineText | `fldTfEX0YglBq8alh` |
| Straße / Nr. | singleLineText | `fldnwZ7yZ8A8B5yGt` |
| Lexware ID | singleLineText | `fldIP42qOvkdnnzHH` |
| Regelbesteuerung ab | date | `fldF4idsFUiCgAX1A` |
| Telegram Channel ID | singleLineText | `flduydWiRl0ZgGBGM` |
| Stores | link → Stores (Akquise durch) | `fldkydrhcYuCqb4lq` |
| Formularlink | formula | `flddGkcgwdmCvBEXF` |
| Realprovision (Rollup) | rollup € | `fldxv77iZbz3QxLJJ` |

*Neu ziehen: `list_tables_for_base` → Vertriebler; Formeln via `get_table_schema`.*

## 🟣 Make-Zugriff (Marker in der Base-Feldbeschreibung)

Trägt einen 🟣-Zugriffsmarker in der Base-Feldbeschreibung (SSoT: [[model]] §2).

- **`Name`** — 🟣 READ. Zeichengenauer Namens-Match (Vertriebler-Auflösung).
- **`Lexware ID`** — 🟣 READ. Kreditor-Referenz.
