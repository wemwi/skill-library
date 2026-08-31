#!/usr/bin/env python3
"""
clean_dieline.py — Onlineprinters Dieline-Cleaner (selectedleafs)

Aufruf:  python3 clean_dieline.py vorlage_raw.svg vorlage_clean.svg

WICHTIG: Die Farbkonstanten unten sind die DIAGNOSTIZIERTEN Werte der Vorlage
"Produkt-Display tief, Theke" — als Beispiel. Pro neuer Vorlage via §3a (Element-
Inventur + Scanline + Farb-Isolation) NEU diagnostizieren und hier ersetzen.
Niemals blind übernehmen — RGB-Werte sind vorlagenspezifisch.

Behalten:  Bleed(mint fill) · Trim(teal stroke) · Safe Zone(grau fill+stroke)
           · Fold(teal/grau stroke) · Crop(black stroke) · Direction "A"(grau fill)
Entfernen: Bemaßung(grau fill+stroke) · mm-Text(glyph <use> UND ggf. black-fill paths)
           · Badge(blau/rosa/teal-fill/darkgrey/white-filter) · alle <use> + glyph-Defs

Rollen als Layer-Namen: erhaltene Guide-Elemente, deren Fill/Stroke in KEEP_ROLES
matcht, bekommen id="<Rolle>" (z.B. id="Bleed"). Figma übernimmt id-Attribute beim
SVG-Import als Layer-Namen — siehe SKILL.md §3c. KEEP_ROLES ist bis auf den bereits
verifizierten Fold-Stroke LEER und muss pro Vorlage aus der §3a/§3b-Diagnose befüllt
werden (gleiches Prinzip wie REMOVE_FILL/REMOVE_STROKE — niemals blind übernehmen).
"""
import sys
from lxml import etree

SVG = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"

# --- DIAGNOSTIZIERTE Farben (rgb%-Strings exakt wie im SVG). Pro Vorlage prüfen! ---
DIM_GREY    = "rgb(57.88269%, 58.247375%, 59.310913%)"   # Bemaßung (fill+stroke) -> weg
BLACK_TEXT  = "rgb(9.516907%, 9.120178%, 9.751892%)"      # mm-Labels als Füll-Pfade -> weg
BADGE_ROSE  = "rgb(80.758667%, 58.592224%, 62.371826%)"   # Badge -> weg
BADGE_BLUE  = "rgb(52.487183%, 70.863342%, 87.898254%)"   # Badge -> weg
BADGE_TEAL2 = "rgb(39.756775%, 61.979675%, 64.099121%)"   # Badge -> weg
BADGE_DGREY = "rgb(37.660217%, 36.911011%, 40.731812%)"   # Badge -> weg
FOLD_BADGE  = "rgb(24.848938%, 52.102661%, 50.67749%)"     # DUAL: stroke=Fold (behalten) / fill=Badge (weg)
BLACK_PURE  = "rgb(0%, 0%, 0%)"                            # Badge white-filter bg / Clip-Maske -> weg

# Fills, die immer entfernt werden (egal welche Rolle):
REMOVE_FILL = {DIM_GREY, BLACK_TEXT, BADGE_ROSE, BADGE_BLUE, BADGE_TEAL2, BADGE_DGREY,
               FOLD_BADGE, BLACK_PURE}
# Strokes, die immer entfernt werden:
REMOVE_STROKE = {DIM_GREY}
# Hinweis: FOLD_BADGE als STROKE bleibt (= Fold) -> NICHT in REMOVE_STROKE.

# --- Rollen-Zuordnung für erhaltene Guides (id-Attribut = Layer-Name in Figma). ---
# Pro Vorlage aus der §3a/§3b-Diagnose befüllen. Format: Rolle -> {"fill": {...}, "stroke": {...}}
# Leer = kein Rollen-Tagging für diese Rolle. Nur der Fold-Stroke ist hier bereits verifiziert
# (siehe REMOVE_STROKE-Hinweis oben) — Bleed/Trim/Safe Zone/Crop/Direction sind für DIESE Vorlage
# ("tief") noch nicht diagnostiziert und deshalb bewusst leer gelassen.
KEEP_ROLES = {
    "Fold": {"stroke": {FOLD_BADGE}},
}

import re
def norm(v):
    return re.sub(r"\s+", " ", v.strip()) if v else v

def localname(el):
    return etree.QName(el).localname if el.tag is not etree.Comment else "#comment"

def should_remove(el):
    tag = localname(el)
    # 1) ALLE <use> entfernen (mm-Text-Glyphs UND Badge-/source-Referenzen;
    #    "A"-Richtungsangaben sind eigene Pfade und überleben)
    if tag == "use":
        return True
    # 2) Onlineprinters Foto-Platzhalter-Gruppen (white-filter)
    if el.get("filter") == "url(#filter-remove-color)":
        return True
    # 3) Rollenbasierte Farbentfernung
    f = norm(el.get("fill"))
    s = norm(el.get("stroke"))
    if f and f != "none" and f in REMOVE_FILL:
        return True
    if s and s in REMOVE_STROKE:
        return True
    return False

def strip_glyph_defs(root):
    n = 0
    for g in list(root.iter(f"{{{SVG}}}g")):
        if (g.get("id") or "").startswith("glyph-"):
            p = g.getparent()
            if p is not None:
                p.remove(g); n += 1
    return n

def walk_remove(root):
    n = 0
    for el in list(root.iter()):
        if el is root or el.tag is etree.Comment:
            continue
        if should_remove(el):
            p = el.getparent()
            if p is not None:
                p.remove(el); n += 1
    return n

def assign_role_ids(root):
    """Setzt id=<Rolle> auf erhaltene Elemente, deren Fill/Stroke in KEEP_ROLES matcht."""
    n = 0
    for el in root.iter():
        if el is root or el.tag is etree.Comment:
            continue
        f = norm(el.get("fill"))
        s = norm(el.get("stroke"))
        for role, colors in KEEP_ROLES.items():
            if (f and f in colors.get("fill", set())) or (s and s in colors.get("stroke", set())):
                el.set("id", role)
                n += 1
                break
    return n

def prune_empty(root):
    """leere <g> entfernen (auch leer gewordene #source-Defs der Badges)."""
    total, changed = 0, True
    while changed:
        changed = False
        for g in list(root.iter(f"{{{SVG}}}g")):
            if g is root or g.getparent() is None:
                continue
            if len(g) == 0 and not g.get("filter"):
                g.getparent().remove(g); total += 1; changed = True
    return total

def main(src, dst):
    tree = etree.parse(src, etree.XMLParser(remove_blank_text=False))
    root = tree.getroot()
    d = strip_glyph_defs(root)
    r = walk_remove(root)
    p = prune_empty(root)
    i = assign_role_ids(root)
    tree.write(dst, xml_declaration=True, encoding="UTF-8")
    print(f"glyph-defs removed: {d}")
    print(f"elements removed:   {r}")
    print(f"empty <g> pruned:   {p}")
    print(f"role ids assigned:  {i}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "vorlage_raw.svg",
         sys.argv[2] if len(sys.argv) > 2 else "vorlage_clean.svg")
