# item_parser.py
"""
增强版 item_parser（PaddleOCR 中文优先）
功能：
 - 使用 PaddleOCR 识别图片并返回文本行
 - 解析并标准化常见 D2R 词条：defense, frw, mf, sockets, allres, res_fire/res_cold/res_light,
   fcr, ias, life, mana, skills_plus 列表, ethereal 标记, damage_min/max, type, name
 - 返回结构化 dict 供 rules_engine 使用
"""

import re
from paddleocr import PaddleOCR

# OCR 初始化（单例）
_OCR = None
def get_ocr():
    global _OCR
    if _OCR is None:
        # 使用中文模型（含英文）并开启角度校正
        _OCR = PaddleOCR(use_angle_cls=True, lang="ch")
    return _OCR

# ----------------- 工具函数 -----------------
def _to_int_safe(s):
    try:
        return int(s)
    except:
        if s is None:
            return None
        s2 = re.sub(r"[^\d\-]", "", str(s))
        return int(s2) if s2 else None

def _clean(s: str):
    if s is None:
        return ""
    s = s.replace("（", "(").replace("）", ")")
    s = s.replace("：", ":").replace("％", "%")
    return s.strip()

# ----------------- 文本抽取 -----------------
def extract_lines_from_image(img_path):
    ocr = get_ocr()
    res = ocr.ocr(img_path, cls=True)
    lines = []
    # PaddleOCR 返回格式层级不同，稳健提取
    try:
        for page in res:
            for line in page:
                txt = _clean(line[1][0])
                if txt:
                    lines.append(txt)
    except Exception:
        # fallback flatten
        try:
            for block in res:
                for line in block:
                    txt = _clean(line[1][0])
                    if txt:
                        lines.append(txt)
        except:
            pass
    return lines

# ----------------- 解析器核心 -----------------
def parse_item_from_lines(lines):
    """
    lines: list[str] OCR 每行文本
    return: dict item
    """
    txt = "\n".join(lines)
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
        "skills_plus": [],   # list of {"skill": str, "value": int}
        "life": None,
        "mana": None,
        "str": None,
        "dex": None,
        "ias": None,
        "damage_min": None,
        "damage_max": None,
        "mf": None,
        "frw": None,
        "misc": {}
    }

    # heuristics: first non-empty line -> name ; second line -> type (often)
    if lines:
        item["name"] = lines[0]
    if len(lines) > 1:
        item["type"] = lines[1]

    # Patterns
    # defense
    m = re.search(r"(?:Defense|防御)[:：]?\s*([0-9]+)", txt, re.I)
    if m:
        item["defense"] = _to_int_safe(m.group(1))

    # ED
    m = re.search(r"(?:Enhanced Damage|增加伤害|伤害加强|附加伤害)[:：]?\s*\+?([0-9]+)%", txt, re.I)
    if m:
        item["ed"] = _to_int_safe(m.group(1))

    # FCR
    m = re.search(r"\+?([0-9]+)%\s*(?:Faster Cast Rate|FCR|施法速度|施法加速)", txt, re.I)
    if m:
        item["fcr"] = _to_int_safe(m.group(1))

    # All resist
    m = re.search(r"(?:All Resistances|All Res|全抗|所有抗性)[:：]?\s*\+?([\-]?[0-9]+)", txt, re.I)
    if m:
        item["allres"] = _to_int_safe(m.group(1))

    # single resistances
    m = re.search(r"(?:Fire Resist|火焰抗性|火抗)[:：]?\s*\+?([\-]?\d+)", txt, re.I)
    if m: item["res_fire"] = _to_int_safe(m.group(1))
    m = re.search(r"(?:Cold Resist|冰冷抗性|冰抗)[:：]?\s*\+?([\-]?\d+)", txt, re.I)
    if m: item["res_cold"] = _to_int_safe(m.group(1))
    m = re.search(r"(?:Lightning Resist|闪电抗性|电抗)[:：]?\s*\+?([\-]?\d+)", txt, re.I)
    if m: item["res_light"] = _to_int_safe(m.group(1))

    # life / mana
    m = re.search(r"\+?([0-9]+)\s*(?:to Life|生命值|生命)", txt, re.I)
    if m: item["life"] = _to_int_safe(m.group(1))
    m = re.search(r"\+?([0-9]+)\s*(?:to Mana|法力值|法力)", txt, re.I)
    if m: item["mana"] = _to_int_safe(m.group(1))

    # strength / dex
    m = re.search(r"(?:Required )?Strength[:：]?\s*([0-9]+)", txt, re.I)
    if m: item["str"] = _to_int_safe(m.group(1))
    m = re.search(r"(?:Required )?Dexterity[:：]?\s*([0-9]+)", txt, re.I)
    if m: item["dex"] = _to_int_safe(m.group(1))
    # 中文 alternate
    m = re.search(r"(?:需要力量|力量)[:：]?\s*([0-9]+)", txt)
    if m and not item["str"]:
        item["str"] = _to_int_safe(m.group(1))
    m = re.search(r"(?:需要敏捷|敏捷)[:：]?\s*([0-9]+)", txt)
    if m and not item["dex"]:
        item["dex"] = _to_int_safe(m.group(1))

    # IAS
    m = re.search(r"\+?([0-9]+)%\s*(?:Increased Attack Speed|IAS|提高攻击速度|攻击速度)", txt, re.I)
    if m: item["ias"] = _to_int_safe(m.group(1))

    # damage min/max
    m = re.search(r"([0-9]+)\s*(?:to|-)\s*([0-9]+)\s*(?:Damage|伤害)", txt, re.I)
    if m:
        item["damage_min"] = _to_int_safe(m.group(1))
        item["damage_max"] = _to_int_safe(m.group(2))
    else:
        m = re.search(r"(?:伤害)[:：]?\s*([0-9]+)\s*[-至]\s*([0-9]+)", txt)
        if m:
            item["damage_min"] = _to_int_safe(m.group(1))
            item["damage_max"] = _to_int_safe(m.group(2))

    # sockets: many patterns (Socketed (4), Sockets: 4, 插槽:4, 孔:4, 4os)
    m = re.search(r"Socketed\s*\(?([0-9]+)\)?|Sockets[:：]?\s*([0-9]+)|插槽[:：]?\s*([0-9]+)|孔[:：]?\s*([0-9]+)|(\d)os\b", txt, re.I)
    if m:
        for g in m.groups():
            if g and g.isdigit():
                item["sockets"] = _to_int_safe(g)
                break

    # ethereal / 无形
    if re.search(r"(?:Ethereal|无形)", txt, re.I):
        item["ethereal"] = True

    # MF / Magic Find
    m = re.search(r"\+?([0-9]+)%\s*(?:Magic Find|MF|魔法物品发现率|掉落率|掉率)", txt, re.I)
    if m:
        item["mf"] = _to_int_safe(m.group(1))
    else:
        m = re.search(r"(?:魔法发现率|发现率)[:：]?\+?([0-9]+)", txt)
        if m:
            item["mf"] = _to_int_safe(m.group(1))

    # FRW / Run/Walk / 跑速
    frw = None
    m = re.search(r"\+?([0-9]+)%\s*(?:Faster Run/Walk|Run/Walk|Run Walk|FRW|跑步|跑速|移动速度)", txt, re.I)
    if m:
        frw = _to_int_safe(m.group(1))
    if not frw:
        m = re.search(r"(?:跑步速度|移动速度|跑速)[:：]?\s*\+?([0-9]+)%?", txt)
        if m:
            frw = _to_int_safe(m.group(1))
    if frw:
        item["frw"] = frw

    # skills: "+2 to All Skills", "所有技能 +2", "+3 to Fire Skills" etc.
    # pattern 1: "+N to <SkillName>"
    for lm in re.finditer(r"\+([0-9]+)\s+to\s+([A-Za-z0-9\u4e00-\u9fff\s'-]+(?:Skill|Skill[s]?|Skills|技能))", txt, re.I):
        try:
            val = _to_int_safe(lm.group(1))
            skl = lm.group(2).strip()
            item["skills_plus"].append({"skill": skl, "value": val})
        except:
            pass
    # pattern 2: "All Skills +N" or "所有技能 +N"
    for lm in re.finditer(r"(?:All Skills|所有技能)[\s:：]*\+?([0-9]+)", txt, re.I):
        try:
            val = _to_int_safe(lm.group(1))
            item["skills_plus"].append({"skill": "All Skills", "value": val})
        except:
            pass

    # runeword detection (common ones; contains wide list for easier matching)
    rw_names = ["Spirit","Insight","Grief","Fort","Infinity","Enigma","Bramble","Chains of Honor","Breath of the Dying","Heart of the Oak","Stone of Jordan"]
    for rw in rw_names:
        # match english or chinese common translations
        if re.search(rf"\b{re.escape(rw)}\b", txt, re.I):
            item["misc"]["runeword"] = rw
    # chinese direct keywords mapping
    if not item["misc"].get("runeword"):
        if re.search(r"精神之灵|精神|灵魂之盾|Spirit", txt, re.I):
            item["misc"]["runeword"] = "Spirit"
        if re.search(r"洞察|Insight", txt, re.I):
            item["misc"]["runeword"] = "Insight"
        if re.search(r"痛苦|Grief", txt, re.I):
            item["misc"]["runeword"] = "Grief"

    # guess type from lines (Monarch / Amulet / Ring / Boots / Gloves / Staff / Helm / Armor / Phase Blade etc.)
    t = item.get("type") or ""
    if not t:
        for ln in lines:
            l = ln.lower()
            if "monarch" in l or "君主" in l or "圆盾" in l:
                item["type"] = "Monarch"; break
            if "amulet" in l or "项链" in l or "护身符" in l:
                item["type"] = "Amulet"; break
            if "ring" in l or "戒指" in l:
                item["type"] = "Ring"; break
            if "boots" in l or "鞋" in l:
                item["type"] = "Boots"; break
            if "gloves" in l or "手套" in l:
                item["type"] = "Gloves"; break
            if "staff" in l or "法杖" in l:
                item["type"] = "Staff"; break
            if "helm" in l or "头盔" in l:
                item["type"] = "Helm"; break
            if "phase blade" in l or "相位刀" in l:
                item["type"] = "Phase Blade"; break
            if "tower shield" in l or "塔盾" in l:
                item["type"] = "Tower Shield"; break
            if "sacred" in l or "圣盾" in l:
                item["type"] = "Sacred Targe"; break

    return item

# 简单入口（图片路径） -> item
def parse_item(img_path):
    lines = extract_lines_from_image(img_path)
    return parse_item_from_lines(lines)

# 如果作为脚本运行，做简单测试（需替换 test.png）
if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("用法: python item_parser.py <image>")
        sys.exit(1)
    img = sys.argv[1]
    it = parse_item(img)
    print(json.dumps(it, ensure_ascii=False, indent=2))
