# rules_engine.py
"""
规则引擎：加载 rules_full.json 并对 item (parse_item 输出) 做匹配判断
"""

import json
import os

RULES_PATH = "rules_full.json"

def load_rules(path=RULES_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"规则文件未找到: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    rules = data.get("rules", [])
    return rules

def deep_get(dct, dotted, default=None):
    # dotted like "misc.runeword"
    if not dotted:
        return default
    cur = dct
    for k in dotted.split("."):
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur

def check_condition(item, cond):
    # cond: dict of thresholds
    # supported keys (see rules_full.json notes)
    if not cond:
        return True

    # helper numeric compare
    def ge(item_key, thresh):
        v = item.get(item_key)
        if v is None:
            return False
        try:
            return v >= thresh
        except:
            return False

    # numeric checks
    if "defense_min" in cond:
        if not ge("defense", cond["defense_min"]): return False
    if "allres_min" in cond:
        if not ge("allres", cond["allres_min"]): return False
    if "fcr_min" in cond:
        if not ge("fcr", cond["fcr_min"]): return False
    if "sockets_min" in cond:
        if not ge("sockets", cond["sockets_min"]): return False
    if "ed_min" in cond:
        if not ge("ed", cond["ed_min"]): return False
    if "damage_max_min" in cond:
        if item.get("damage_max") is None or item.get("damage_max") < cond["damage_max_min"]:
            return False
    if "damage_min_min" in cond:
        if item.get("damage_min") is None or item.get("damage_min") < cond["damage_min_min"]:
            return False
    if "frw_min" in cond:
        if not ge("frw", cond["frw_min"]): return False
    if "mf_min" in cond:
        if not ge("mf", cond["mf_min"]): return False
    if "resist_each_min" in cond or "resist_count_min" in cond or "resist_any_min" in cond:
        # compute resist list
        rlist = [item.get("res_fire"), item.get("res_cold"), item.get("res_light")]
        # resist_any_min: at least one >= value
        if "resist_any_min" in cond:
            v = cond["resist_any_min"]
            if not any([(r is not None and r >= v) for r in rlist]): return False
        if "resist_each_min" in cond:
            v = cond["resist_each_min"]
            if not all([(r is not None and r >= v) for r in rlist]): return False
        if "resist_count_min" in cond:
            count_need = cond["resist_count_min"]
            # default sub-threshold for counting is resist_each_min if present else 0
            floor = cond.get("resist_each_min", 0)
            cnt = sum([(r is not None and r >= floor) for r in rlist])
            if cnt < count_need: return False
    if "ias_min" in cond:
        if not ge("ias", cond["ias_min"]): return False
    if "skills_plus_any_min" in cond:
        need = cond["skills_plus_any_min"]
        total = sum([s.get("value",0) for s in item.get("skills_plus", [])])
        if total < need: return False
    if "life_min" in cond:
        if not ge("life", cond["life_min"]): return False
    if "mana_min" in cond:
        if not ge("mana", cond["mana_min"]): return False
    if "str_min" in cond:
        if not ge("str", cond["str_min"]): return False
    if "dex_min" in cond:
        if not ge("dex", cond["dex_min"]): return False
    if "ethereal" in cond:
        if item.get("ethereal") != cond["ethereal"]:
            return False
    if "skill_exact" in cond:
        target = cond["skill_exact"].lower()
        found = False
        # check raw_lines
        for ln in item.get("raw_lines", []):
            if target in ln.lower():
                found = True; break
        # check skills_plus
        if not found:
            for sp in item.get("skills_plus", []):
                if target in str(sp.get("skill","")).lower() or target in str(sp.get("value","")).lower():
                    found = True; break
        if not found:
            return False

    return True

def match_rule(item, rule):
    # match: dict of dotted keys equality (e.g. {"type":"Amulet", "misc.runeword":"Spirit"})
    for k,v in rule.get("match", {}).items():
        val = deep_get(item, k, None)
        if val != v:
            return False
    return True

def evaluate(item, rules=None):
    if rules is None:
        rules = load_rules()
    # iterate rules in order
    for r in rules:
        try:
            if match_rule(item, r) and check_condition(item, r.get("conditions", {})):
                return {
                    "rule_id": r.get("id"),
                    "value": r.get("value"),
                    "reason": r.get("reason")
                }
        except Exception as e:
            # skip rule on error
            continue
    # fallback scoring
    score = 0
    if item.get("allres"): score += min(item["allres"], 50)
    if item.get("fcr"): score += item["fcr"] * 2
    if item.get("defense"): score += (item["defense"] // 5)
    if item.get("ed"): score += item["ed"] * 3
    score += sum([s.get("value",0) * 10 for s in item.get("skills_plus", [])])
    if item.get("mf"): score += item["mf"] * 1.5
    est = f"未知价值（估计分: {int(score)}）"
    return {
        "rule_id": None,
        "value": est,
        "reason": "未命中任何规则，使用估计分数回退"
    }
