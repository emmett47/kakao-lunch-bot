"""
ì¹´ì¹´ì¤í¡ ì ì¬ ì¶ì² ì±ë´ - ì¹í ìë²
Kakao i Open Builder ì¤í¬ ìë²ë¡ ëìí©ëë¤.
"""

import random
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============================================================
# ð½ï¸ ì ì¬ ë©ë´ ë°ì´í°
# ìíë ë©ë´ë¥¼ ìì ë¡­ê² ì¶ê°/ìì íì¸ì!
# ============================================================

MENU_DATA = {
    "íì": [
        {"name": "ê¹ì¹ì°ê°", "desc": "ì¼í°í ê¹ì¹ì°ê°ì ë°¥ í ê³µê¸° ëë±!"},
        {"name": "ëì¥ì°ê°", "desc": "êµ¬ìí ëì¥ì°ê°, íêµ­ì¸ì ìì¸í¸ë"},
        {"name": "ë¹ë¹ë°¥", "desc": "ìë¡ë¬ë¡ ê±´ê°í ë¹ë¹ë°¥ í ê·¸ë¦"},
        {"name": "ë¶ê³ ê¸° ì ì", "desc": "ë¬ì½¤ìJmì§¤í ë¶ê³ ê¸°ì ë°ë°ì°¬ê¹ì§"},
        {"name": "ì ì¡ë³¶ì", "desc": "ë§¤ì½¤í ì ì¡ì ë°¥ ë¹ë²¼ë¨¹ê¸° ìµê³ !"},
        {"name": "ìëë¶ì°ê°", "desc": "ë¶ëë½ê³  ì¼í°í ìëë¶, ê³ë í¡!"},
        {"name": "ì¼ê²¹ì´", "desc": "ì ì¬ ì¼ê²¹ì´ì ëª» ì°¸ì§... ì ì¸ë¨¹ì!"},
        {"name": "ì¹¼êµ­ì", "desc": "ììí êµ­ë¬¼ì ì«ê¹í ë©´ë°"},
        {"name": "ê¹ë°¥ + ë¡ë³¶ì´", "desc": "ë¶ìì ì ì, êµ­ë£° ì¡°í©"},
        {"name": "ëë©´", "desc": "ììíê² í ê·¸ë¦ íë£¨ë£©"},
    ],
    "ì¤ì": [
        {"name": "ì§ì¥ë©´", "desc": "ë¬ì½¤ì§­ì§¤í ì¶ì¥ì ë§¤ë ¥"},
        {"name": "ì§¬ë¼½", "desc": "ì¼í°í êµ­ë¬¼ì´ ë¹ê¸°ë ë "},
        {"name": "íìì¡", "desc": "ë°ì­í íìì¡, ë¶ë¨¹? ì°ë¨¹?"},
        {"name": "ë§íëë¶", "desc": "ë§¤ì½¤í ë§íëë¶ ë®ë°¥ í ê·¸ë¦"},
        {"name": "ìì¥í¼", "desc": "ììíê³  ìì½¤ë¬ì½¤í ìì¥í¼"},
    ],
    "ì¼ì": [
        {"name": "ì´ë°¥", "desc": "ì ì í ì´ë°¥ í ì ìë¡ ê¸°ë¶ ì í"},
        {"name": "ë¼ë©", "desc": "ì§í ëì½ì¸ ì¡ìì ë©´ í ì ê°ë½"},
        {"name": "ëì¹´ì°  ", "desc": "ë°ì­í ëì¹´ì¸ ì ìì¤ ë¬ë¿"},
        {"name": "ì°ë", "desc": "ë°ëí ì°ë êµ­ë¬¼ì ëª¸ë ë§ìë ë°ë»"},
        {"name": "ì¹´ë ", "desc": "ë ë í ì¼ë³¸ì ì¹´ë ë¼ì´ì¤"},
    ],
    "ìì": [
        {"name": "íì¤í", "desc": "í¬ë¦¼? í ë§í ? ì¤ì¼? ë­ë  ì¢ì!"},
        {"name": "íë²ê±°", "desc": "ì¡ì¦ ê°ë ë²ê±°ë¡ ìëì§ ì¶©ì "},
        {"name": "í¼ì", "desc": "ì¹ì¦ ì­~ ëì´ëë í¼ì í í"},
        {"name": "ì¤íì´í¬ ", "desc": "ì¤ëì ì¢ ë­ìë¦¬íê² ì¤íì´í¬"},
        {"name": "ë¦¬ì¡°ë", "desc": "í¬ë¦¬ë¯¸í ë¦¬ì¡°ë í ê·¸ë¦"},
    ],
    "ììì": [
        {"name": "ìêµ­ì", "desc": "ë² í¸ë¨ ì°êµ­ìë¡ ê¹éµíê²"},
        {"name": "ííì´", "desc": "ìì½¤ë¬ì½¤í íêµ­ì ë³¶ìë©´"},
        {"name": "ì¹´ì¤ë§ê°ì´", "desc": "ë¶ëë¬ì´ íêµ­ì ì¹í¨ë¼ ì´ì¤"},
        {"name": "ë¶ì§", "desc": "íëì´ì ë¶ì§¼ë¡ ì´êµ­ì ì¸ ì ì¬"},
    ],
    "ê°í¸ì": [
        {"name": "ìëìì¹", "desc": "ê°ë³ê² ìëìì¹ íë ì´ë?"},
        {"name": "ìë¬ë", "desc": "ì¤ëì ê±´ê°íê² ìë¬ë í ë³¼"},
        {"name": "í¸ìì  ëìë­", "desc": "ê°ì±ë¹ ê°©! í¸ìì  ëìë½"},
        {"name": "í  ì¤í¸", "desc": "ê¸¸ê±°ë¦¬ í ì¤í¸ì ê·¸ ë§"},
    ],
}

ALL_MENUS = []
for category, items in MENU_DATA.items():
    for item in items:
        ALL_MENUS.append({**item, "category": category})


# ============================================================
# ð¯ ì¶ì² ë¡ì§
# ============================================================

def get_random_menu(category=None):
    """ëë´ ë©ë´ ì¶ì²"""
    if category and category in MENU_DATA:
        menu = random.choice(MENU_DATA[category])
        return {**menu, "category": category}
    return random.choice(ALL_MENUS)


def get_multiple_recommendations(count=3, category=None):
    """ì¬ë¬ ê° ë©ë´ ì¶ì² (ì¤ë³µ ìì´)"""
    if category and category in MENU_DATA:
        pool = [{"name": m["name"], "desc": m["desc"], "category": category} for m in MENU_DATA[category]]
    else:
        pool = ALL_MENUS.copy()

    count = min(count, len(pool))
    return random.sample(pool, count)


# ============================================================
# ð¨ ì¹´ì¹´ì¤í¡ ìëµ í¬ë§· í¬í¼
# ============================================================

def make_simple_text(text):
    """SimpleText ìëµ"""
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ]
        }
    }


def make_card_response(menus):
    """BasicCard ë¦¬ì¤í¸ ìëµ"""
    items = []
    for menu in menus:
        items.append({
            "title": f"ð½ï¸ {menu['name']}",
            "description": f"[{menu['category']}] {menu['desc']}",
        })

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": "ð° ì¤ëì ì ì¬ ì¶ì²ì´ìì!"}}
            ] + [
                {
                    "basicCard": {
                        "title": item["title"],
                        "description": item["description"],
                    }
                }
                for item in items
            ],
            "quickReplies": [
                {"label": "ð² ë¤ì ì¶ì²", "action": "message", "messageText": "ì ì¬ ì¶ì²"},
                {"label": "ð íì", "action": "message", "messageText": "íì ì¶ì²"},
                {"label": "ð¥ ì¤ì", "action": "message", "messageText": "ì¤ì ì¶ì²"},
                {"label": "ð£ ì¼ì", "action": "message", "messageText": "ì¼ì ì¶ì²"},
                {"label": "ð ìì", "action": "message", "messageText": "ìì ì¶ì²"},
            ]
        }
    }


def make_category_list():
    """ì¹´íê³ ë¦¬ ì í ìëµ"""
    text = "ì´ë¤ ì¢ë¥ì ììì´ ë¡ê¸°ì¸ì?\n\n"
    emojis = {"íì": "ð", "ì¤ì": "ð¥", "ì¼ì": "ð£", "ìì": "ð", "ììì": "ð", "ê°í¸ì": "ð¥ª"}
    for cat in MENU_DATA:
        emoji = emojis.get(cat, "ð½ï¸")
        text += f"{emoji} {cat} ({len(MENU_DATA[cat])}ê° ë©ë´)\n"
    text += "\nìë ë²í¼ì ëë¬ ì ííê±°ë, 'OO ì¶ì²'ì´ë¼ê³  ìë ¥íì¸ì!"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ],
            "quickReplies": [
                {"label": "ð² ëë¤ ì¶ì²", "action": "message", "messageText": "ì ì¬ ì¶ì²"},
                {"label": "ð íì", "action": "message", "messageText": "íì ì¶ì²"},
                {"label": "ð¥ ì¤ì", "action": "message", "messageText": "ì¤ì ì¶ì²"},
                {"label": "ð£ ì¼ì", "action": "message", "messageText": "ì¼ì ì¶ì²"},
                {"label": "ð ìì", "action": "message", "messageText": "ìì ì¶ì²"},
            ]
        }
    }


# ============================================================
# ð ì¹´ì¹´ì¤ ì¹í ìëí¬ì¸í¸
# ============================================================

@app.route("/", methods=["GET"])
def health_check():
    """ìë² ìí íì¸"""
    return jsonify({"status": "ok", "message": "ì ì¬ ì¶ì² ë´ì´ ì¤í ì¤ìëë¤! ð½ï¸"})


@app.route("/api/lunch", methods=["POST"])
def lunch_recommend():
    """
    ë©ì¸ ì ì¬ ì¶ì² ì¤í¬ ìëí¬ì¸í¸
    Kakao i Open Builderìì ì´ URLì ì¤í¬ ìë²ë¡ ë±ë¡íì¸ì.
    """
    try:
        body = request.get_json()
        utterance = body.get("userRequest", {}).get("utterance", "").strip()

        # ì¹´íê³ ë¦¬ ê°ì§
        detected_category = None
        for category in MENU_DATA:
            if category in utterance:
                detected_category = category
                break

        # ë©ë´ ëª©ë¡ ìì²­
        if "ëª©ë¡" in utterance or "ì¹´íê³ ë¦¬" in utterance or "ì¢ë¥" in utterance:
            return jsonify(make_category_list())

        # ì¶ì² ìì²­ ì²ë¦¬
        if "ì¶ì²" in utterance or "ë­ ë¨¹" in utterance or "ì ì¬" in utterance or "ë©ë´" in utterance:
            menus = get_multiple_recommendations(3, detected_category)
            return jsonify(make_card_response(menus))

        # ê¸°ë³¸ ìëµ (ì¸ì¬ ë±)
        return jsonify(make_simple_text(
            "ìëíì¸ì! ð½ï¸ ì ì¬ ì¶ì² ë´ì´ìì!\n\n"
            "ìë ëªë ¹ì´ë¥¼ ì¬ì©í´ë³´ì¸ì:\n"
            "â¢ 'ì ì¬ ì¶ì²' - ëë´ 3ê° ë©ë´ ì¶ì²\n"
            "â¢ 'íì ì¶ì²' - íì ë©ë´ ì¶ì²\n"
            "â¢ 'ë©ë´ ëª©ë¡' - ì ì²´ ì¹´íê³ ë¦¬ ë³´ê¸°\n\n"
            "ì¤ë ì ì¬ ë­ ë¨¹ìì§ ê°ì´ ê³¨ë¼ë´ì! ð"
        ))

    except Exception as e:
        return jsonify(make_simple_text(f"ì, ì¤ë¥ê° ë°ìíì´ì ð\nì ì í ë¤ì ìëí´ì£¼ì¸ì."))


@app.route("/api/category", methods=["POST"])
def category_list():
    """ì¹´íê³ ë¦¬ ëª©ë¡ ì¤í¬ ìëí¬ì¸í¸"""
    return jsonify(make_category_list())


# ============================================================
# ð ìë² ì¤í
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
