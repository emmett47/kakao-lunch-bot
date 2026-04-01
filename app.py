"""
카카오톡 점심 추천 챗봇 - 웹훅 서버
Kakao i Open Builder 스킬 서버로 동작합니다.
"""

import random
import threading
import time
import urllib.request
from flask import Flask, request, jsonify

app = Flask(__name__)


# ============================================================
# ⏰ Keep-Alive (Render 무료 티어 슬립 방지)
# ============================================================

def keep_alive():
    """14분마다 자기 자신에게 요청을 보내 서버가 잠들지 않게 합니다."""
    while True:
        time.sleep(840)  # 14분
        try:
            urllib.request.urlopen("https://kakao-lunch-bot-h8l6.onrender.com/")
        except Exception:
            pass

keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

# ============================================================
# 🍽️ 점심 메뉴 데이터
# 원하는 메뉴를 자유롭게 추가/수정하세요!
# ============================================================

MENU_DATA = {
    "한식": [
        {"name": "김치찌개", "desc": "얼큰한 김치찌개에 밥 한 공기 뚝딱!"},
        {"name": "된장찌개", "desc": "구수한 된장찌개, 한국인의 소울푸드"},
        {"name": "비빔밥", "desc": "알록달록 건강한 비빔밥 한 그릇"},
        {"name": "불고기 정식", "desc": "달콤짭짤한 불고기에 밑반찬까지"},
        {"name": "제육볶음", "desc": "매콤한 제육에 밥 비벼먹기 최고!"},
        {"name": "순두부찌개", "desc": "부드럽고 얼큰한 순두부, 계란 톡!"},
        {"name": "삼겹살", "desc": "점심 삼겹살은 못 참지... 쌈 싸먹자!"},
        {"name": "칼국수", "desc": "시원한 국물에 쫄깃한 면발"},
        {"name": "김밥 + 떡볶이", "desc": "분식의 정석, 국룰 조합"},
        {"name": "냉면", "desc": "시원하게 한 그릇 후루룩"},
    ],
    "중식": [
        {"name": "짜장면", "desc": "달콤짭짤한 춘장의 매력"},
        {"name": "짬뽕", "desc": "얼큰한 국물이 당기는 날"},
        {"name": "탕수육", "desc": "바삭한 탕수육, 부먹? 찍먹?"},
        {"name": "마파두부", "desc": "매콤한 마파두부 덮밥 한 그릇"},
        {"name": "양장피", "desc": "시원하고 새콤달콤한 양장피"},
    ],
    "일식": [
        {"name": "초밥", "desc": "신선한 초밥 한 접시로 기분 전환"},
        {"name": "라멘", "desc": "진한 돈코츠 육수에 면 한 젔가락"},
        {"name": "돈카츠", "desc": "바삭한 돈카츠에 소스 듬뻑"},
        {"name": "우동", "desc": "따끈한 우동 국물에 몸도 마음도 따뜻"},
        {"name": "카레", "desc": "든든한 일본식 카레라이스"},
    ],
    "양식": [
        {"name": "파스타", "desc": "크림? 토마토? 오일? 뭐든 좋아!"},
        {"name": "햄버거", "desc": "육즙 가득 버거로 에너지 충전"},
        {"name": "피자", "desc": "치즈 쥐~ 늘어나는 피자 한 판"},
        {"name": "스테이크", "desc": "오늘은 좀 럭셔리하게 스테이크"},
        {"name": "리조또", "desc": "크리미한 리조또 한 그릇"},
    ],
    "아시안": [
        {"name": "쌀국수", "desc": "베트남 쌀국수로 깔끔하게"},
        {"name": "팯타이", "desc": "새콤달콤한 태국식 볶음면"},
        {"name": "카오만가이", "desc": "부드러운 태국식 치킨라이스"},
        {"name": "분짜", "desc": "하노이식 분짜로 이국적인 점심"},
    ],
    "간편식": [
        {"name": "샌드위치", "desc": "가볍게 샌드위치 하나 어때?"},
        {"name": "샐러드", "desc": "오늘은 건강하게 샐러드 한 볼"},
        {"name": "편의점 도시락", "desc": "가성비 갑! 편의점 도시락"},
        {"name": "토스트", "desc": "길거리 토스트의 그 맛"},
    ],
}

ALL_MENUS = []
for category, items in MENU_DATA.items():
    for item in items:
        ALL_MENUS.append({**item, "category": category})


# ============================================================
# 🎯 추천 로직
# ============================================================

def get_random_menu(category=None):
    """랜덤 메뉴 추천"""
    if category and category in MENU_DATA:
        menu = random.choice(MENU_DATA[category])
        return {**menu, "category": category}
    return random.choice(ALL_MENUS)


def get_multiple_recommendations(count=3, category=None):
    """여러 개 메뉴 추천 (중복 없이)"""
    if category and category in MENU_DATA:
        pool = [{"name": m["name"], "desc": m["desc"], "category": category} for m in MENU_DATA[category]]
    else:
        pool = ALL_MENUS.copy()

    count = min(count, len(pool))
    return random.sample(pool, count)


# ============================================================
# 📨 카카오톡 응답 포맷 헬퍼
# ============================================================

def make_simple_text(text):
    """SimpleText 응답"""
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ]
        }
    }


def make_card_response(menus):
    """추천 메뉴 응답 (SimpleText로 통합 - 카카오 outputs 최대 3개 제한 준수)"""
    text = "🎰 오늘의 점심 추천이에요!\n\n"
    for i, menu in enumerate(menus, 1):
        text += f"{i}. 🍽️ {menu['name']}\n"
        text += f"   [{menu['category']}] {menu['desc']}\n\n"
    text += "마음에 드는 메뉴가 있나요? 😋"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ],
            "quickReplies": [
                {"label": "🎲 다시 추천", "action": "message", "messageText": "점심 추천"},
                {"label": "🍚 한식", "action": "message", "messageText": "한식 추천"},
                {"label": "🥟 중식", "action": "message", "messageText": "중식 추천"},
                {"label": "🍣 일식", "action": "message", "messageText": "일식 추천"},
                {"label": "🍝 양식", "action": "message", "messageText": "양식 추천"},
            ]
        }
    }


def make_category_list():
    """카테고리 선택 응답"""
    text = "어떤 종류의 음식이 땥기세요?\n\n"
    emojis = {"한식": "🍚", "중식": "🥟", "일식": "🍣", "양식": "🍝", "아시안": "🍜", "간편식": "🥪"}
    for cat in MENU_DATA:
        emoji = emojis.get(cat, "🍽️")
        text += f"{emoji} {cat} ({len(MENU_DATA[cat])}개 메뉴)\n"
    text += "\n아래 버튼을 눌러 선택하거나, 'OO 추천'이라고 입력하세요!"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {"simpleText": {"text": text}}
            ],
            "quickReplies": [
                {"label": "🎲 랜덤 추천", "action": "message", "messageText": "점심 추천"},
                {"label": "🍚 한식", "action": "message", "messageText": "한식 추천"},
                {"label": "🥟 중식", "action": "message", "messageText": "중식 추천"},
                {"label": "🍣 일식", "action": "message", "messageText": "일식 추천"},
                {"label": "🍝 양식", "action": "message", "messageText": "양식 추천"},
            ]
        }
    }


# ============================================================
# 🌐 카카오 웹훅 엔드포인트
# ============================================================

@app.route("/", methods=["GET"])
def health_check():
    """서버 상태 확인"""
    return jsonify({"status": "ok", "message": "점심 추천 봇이 실행 중입니다! 🍽️"})


@app.route("/api/lunch", methods=["POST"])
def lunch_recommend():
    """
    메인 점심 추천 스킬 엔드포인트
    Kakao i Open Builder에서 이 URL을 스킬 서버로 등록하세요.
    """
    try:
        body = request.get_json()
        utterance = body.get("userRequest", {}).get("utterance", "").strip()

        # 카테고리 감지
        detected_category = None
        for category in MENU_DATA:
            if category in utterance:
                detected_category = category
                break

        # 메뉴 목록 요청
        if "목록" in utterance or "카테고리" in utterance or "종류" in utterance:
            return jsonify(make_category_list())

        # 추천 요청 처리
        if "추천" in utterance or "뭐 먹" in utterance or "점심" in utterance or "메뉴" in utterance:
            menus = get_multiple_recommendations(3, detected_category)
            return jsonify(make_card_response(menus))

        # 기본 응답 (인사 등)
        return jsonify(make_simple_text(
            "안녕하세요! 🍽️ 점심 추천 봇이에요!\n\n"
            "아래 명령어를 사용해보세요:\n"
            "• '점심 추천' - 랜덤 3개 메뉴 추천\n"
            "• '한식 추천' - 한식 메뉴 추천\n"
            "• '메뉴 목록' - 전체 카테고리 보기\n\n"
            "오늘 점심 뭐 먹을지 같이 골라봐요! 😋"
        ))

    except Exception as e:
        return jsonify(make_simple_text(f"앛, 오류가 발생했어요 😅\n잠시 후 다시 시도해주세요."))


@app.route("/api/category", methods=["POST"])
def category_list():
    """카테고리 목록 스킬 엔드포인트"""
    return jsonify(make_category_list())


# ============================================================
# 🚀 서버 실행
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
