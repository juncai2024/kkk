# main.py
import sys, os, json
from paddleocr import PaddleOCR
from item_parser import parse_text_to_item

ocr = PaddleOCR(use_angle_cls=True, lang='en')
RULES_FILE = "rules.json"

def load_rules(path=RULES_FILE):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)["rules"]

def get_text_from_image(path):
    result = ocr.ocr(path, cls=True)
    lines = []
    try:
        for line in result[0]:
            text = line[1][0]
            lines.append(text)
    except:
        for page in result:
            for line in page:
                try: lines.append(line[1][0])
                except: pass
    return "\n".join(lines)

def check_condition(item, cond):
    if not cond: return True
    if "defense_min" in cond:
        if item.get("defense") is None or item.get("defense") < cond["defense_min"]:
            return False
    if "allres_min" in cond:
        if item.get("allres") is None or item.get("allres") < cond["allres_min"]:
            return False
    if "fcr_min" in cond:
        if item.get("fcr") is None or item.get("fcr") < cond["fcr_min"]:
            return False
    if "sockets_min" in cond:
        if item.get("sockets",0) < cond["sockets_min"]:
            return False
    if "skills_plus_any_min" in cond:
        total = sum([s["value"] for s in item.get("skills_plus",[])])
        if total < cond["skills_plus_any_min"]:
            return False
    return True

def match_rule(item, rule):
    for k,v in rule.get("match",{}).items():
        keys = k.split(".")
        val = item
        for key in keys:
            val = val.get(key, {})
        if val != v:
            return False
    return True

def evaluate_item(item, rules):
    for r in rules:
        if match_rule(item, r) and check_condition(item, r.get("conditions",{})):
            return r["value"], r["reason"]
    return "未知价值", "未命中规则"

def process_file(path, rules):
    text = get_text_from_image(path)
    item = parse_text_to_item(text)
    value, reason = evaluate_item(item, rules)
    print(f"\n=== {item.get('name')} / {item.get('type')} ===")
    print(f"价值判断：{value}")
    print(f"原因：{reason}\n")

if __name__=="__main__":
    if len(sys.argv)<2:
        print("用法: python main.py <图片文件或文件夹>")
        sys.exit(1)
    path = sys.argv[1]
    rules = load_rules()
    if os.path.isfile(path):
        process_file(path, rules)
    elif os.path.isdir(path):
        for f in os.listdir(path):
            fp = os.path.join(path, f)
            if fp.lower().endswith((".png",".jpg",".jpeg")):
                process_file(fp, rules)
    else:
        print("无效路径")
