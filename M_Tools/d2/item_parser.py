# item_parser.py
import re

def normalize_line(s: str) -> str:
    return s.strip().replace('\r','')

def parse_text_to_item(text: str) -> dict:
    """
    将 OCR 文本解析成结构化字典
    """
    lines = [normalize_line(l) for l in text.splitlines() if l.strip()]
    item = {
        "raw_lines": lines,
        "name": None,
        "type": None,
        "defense": None,
        "ed": None,
        "fcr": None,
        "allres": None,
        "res_fire": None,
        "res_cold": None,
        "res_light": None,
        "sockets": 0,
        "ethereal": False,
        "skills_plus": [],
        "life": None,
        "mana": None,
        "str": None,
        "dex": None,
        "ias": None,
        "damage_min": None,
        "damage_max": None,
        "misc": {}
    }

    if len(lines) >= 1:
        item["name"] = lines[0]
    if len(lines) >= 2:
        item["type"] = lines[1]

    txt = "\n".join(lines)

    # Defense: 148
    m = re.search(r"Defense[:\s]*([0-9]+)", txt, re.I)
    if m: item["defense"] = int(m.group(1))

    # Required Strength / Dexterity
    m = re.search(r"Required Strength[:\s]*([0-9]+)", txt, re.I)
    if m: item["str"] = int(m.group(1))
    m = re.search(r"Required Dexterity[:\s]*([0-9]+)", txt, re.I)
    if m: item["dex"] = int(m.group(1))

    # FCR
    m = re.search(r"\+(\d+)%\s*Faster Cast Rate", txt, re.I)
    if m: item["fcr"] = int(m.group(1))

    # ED
    m = re.search(r"\+(\d+)%\s*Enhanced Damage", txt, re.I)
    if m:
        item["ed"] = int(m.group(1))
    else:
        m = re.search(r"Enhanced Damage[:\s]*\+?(\d+)%", txt, re.I)
        if m:
            item["ed"] = int(m.group(1))

    # All Resistances
    m = re.search(r"All Resistances\s*\+(\-?\d+)", txt, re.I)
    if m: item["allres"] = int(m.group(1))

    # Single resistances
    m = re.search(r"Fire Resist(?:ance)?\s*\+?(\-?\d+)", txt, re.I)
    if m: item["res_fire"] = int(m.group(1))
    m = re.search(r"Cold Resist(?:ance)?\s*\+?(\-?\d+)", txt, re.I)
    if m: item["res_cold"] = int(m.group(1))
    m = re.search(r"Lightning Resist(?:ance)?\s*\+?(\-?\d+)", txt, re.I)
    if m: item["res_light"] = int(m.group(1))

    # Sockets
    m = re.search(r"Socketed\s*\(?(\d+)\)?", txt, re.I)
    if not m:
        m = re.search(r"Sockets[:\s]*([0-9]+)", txt, re.I)
    if m:
        try:
            item["sockets"] = int(m.group(1))
        except:
            item["sockets"] = 0

    # Ethereal
    if re.search(r"Ethereal", txt, re.I):
        item["ethereal"] = True

    # Mana / Life
    m = re.search(r"\+?([0-9]+)\s*to Mana", txt, re.I)
    if m: item["mana"] = int(m.group(1))
    m = re.search(r"\+?([0-9]+)\s*to Life", txt, re.I)
    if m: item["life"] = int(m.group(1))

    # Skills
    for lm in re.finditer(r"\+([0-9]+)\s+to\s+([A-Za-z0-9\s'-]+(?:Skills|Skill|Skills\)))", txt, re.I):
        try:
            val = int(lm.group(1))
            skl = lm.group(2).strip()
            item["skills_plus"].append({"skill": skl, "value": val})
        except:
            pass
    for lm in re.finditer(r"(All Skills)\s*\+([0-9]+)", txt, re.I):
        item["skills_plus"].append({"skill": lm.group(1), "value": int(lm.group(2))})

    # IAS
    m = re.search(r"\+(\d+)%\s*Increased Attack Speed", txt, re.I)
    if m:
        item["ias"] = int(m.group(1))

    # Weapon damage
    m = re.search(r"([0-9]+)\s*to\s*([0-9]+)\s*Damage", txt, re.I)
    if m:
        item["damage_min"] = int(m.group(1))
        item["damage_max"] = int(m.group(2))

    # Runeword识别
    name = item.get("name","") or ""
    for rw in ["Spirit","Insight","Grief","Fort","Infinity"]:
        if re.search(rf"\b{rw}\b", name, re.I):
            item["misc"]["runeword"] = rw

    return item
