"""
카카오톡 점심 추천 챗봇 - 웹훅 서버
Kakao i Open Builder 스킬 서버로 동작합니다.

직장인 점심 메뉴 추천 전문 봇 v2.0
"""

import os
import random
import logging
import threading
import time
import urllib.request
from flask import Flask, request, jsonify

# ============================================================
# 🔧 설정
# ============================================================

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RENDER_URL = os.environ.get("RENDER_URL", "https://kakao-lunch-bot-h8l6.onrender.com/")


# ============================================================
# ⏰ Keep-Alive (Render 무료 티어 슬립 방지)
# ============================================================

def keep_alive():
    """14분마다 자기 자신에게 요청을 보내 서버가 잠들지 않게 합니다."""
    while True:
        time.sleep(840)  # 14분
        try:
            urllib.request.urlopen(RENDER_URL)
        except Exception:
            pass

keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()


# ============================================================
# 🍽️ 점심 메뉴 데이터
# 직장인이 점심에 먹을 수 있는 모든 카테고리
# ============================================================

MENU_DATA = {
    "한식 밥류": [
        {"name": "김치찌개 + 밥", "desc": "언큰한 김치찌개에 밥 한 공기 뚝딱!"},
        {"name": "된장찌개 + 밥", "desc": "구수한 된장찌개, 한국인의 소울푸드"},
        {"name": "비빔밥", "desc": "알록달록 건강한 비빔밥 한 그릇"},
        {"name": "제육볶음 정식", "desc": "매콤한 제육에 밥 비벼먹기 최고!"},
        {"name": "불고기 정식", "desc": "달콤짭짤한 불고기에 밑반찬까지"},
        {"name": "오므라이스", "desc": "케첩 뿌린 오므라이스, 소확행"},
        {"name": "카레라이스", "desc": "든든한 카레 한 접시"},
        {"name": "김치볶음밥", "desc": "고소한 김치볶음밥에 계란 프라이"},
        {"name": "돌솥비빔밥", "desc": "율끈한 돌솥에 바삭한 누룽지까지"},
        {"name": "낙지볶음 정식", "desc": "매콤 쫄깃한 낙지볶음 정식"},
    ],
    "찌개/탕/전골": [
        {"name": "순두부찌개", "desc": "부드럽고 얼큰한 순두부, 계란 톡!"},
        {"name": "부대찌개", "desc": "햄, 라면사리 넣은 푸짐한 부대찌개"},
        {"name": "감자탕", "desc": "뼈다귀 감자탕으로 든든하게"},
        {"name": "삼계탕", "desc": "보양식의 정석, 삼계탕 한 그릇"},
        {"name": "갈비탕", "desc": "맑은 국물에 갈비 한 점의 행복"},
        {"name": "설렁탕", "desc": "뽀얀 국물의 설렁탕, 소금 간 해서"},
        {"name": "육개장", "desc": "칼칼한 육개장으로 속 풀기"},
        {"name": "해물탕", "desc": "해물 가득 시원한 해물탕"},
        {"name": "뚝배기 불고기", "desc": "보글보글 뚝배기 불고기 정식"},
        {"name": "청국장", "desc": "호불호 갈리지만 중독성 있는 청국장"},
    ],
    "면류": [
        {"name": "칼국수", "desc": "시원한 국물에 쫄깃한 면발"},
        {"name": "냉면", "desc": "시원하게 한 그릇 후루룩"},
        {"name": "잔치국수", "desc": "멸치국물에 소면, 소박한 한 끼"},
        {"name": "쫄면", "desc": "매콤새콤 쫄깃한 쫄면"},
        {"name": "비빔국수", "desc": "새콤달콤 비빔국수 한 그릇"},
        {"name": "수제비", "desc": "뜨끈한 국물에 쫄깃한 수제비"},
        {"name": "콩국수", "desc": "고소한 콩국수 (여름 한정)"},
        {"name": "막국수", "desc": "메밀향 가득 막국수"},
    ],
    "분식": [
        {"name": "떡볶이 + 김밥", "desc": "분식의 정석, 국룰 조합"},
        {"name": "라볶이", "desc": "라면 + 떡볶이 = 라볶이"},
        {"name": "순대", "desc": "찹쌀순대에 소금장 찍어서"},
        {"name": "튀김 모둠", "desc": "바삭한 튀김 한 접시"},
        {"name": "쫄볶이", "desc": "쫄면 + 떡볶이 매콤 조합"},
        {"name": "만두", "desc": "고기만두, 김치만두 취향대로"},
        {"name": "부침개 + 막걸리", "desc": "비 오는 날엔 이거지 (점심 한 잔?)"},
    ],
    "고기/구이": [
        {"name": "삼겹살", "desc": "점심 삼겹살은 못 참지... 쌈 싸먹자!"},
        {"name": "목살 구이", "desc": "부드러운 목살에 쌈장 한 스푼"},
        {"name": "갈비", "desc": "양념갈비 한 점의 행복"},
        {"name": "족발", "desc": "쫄깃한 족발 점심 특선"},
        {"name": "보쌈", "desc": "수육에 김치 싸먹는 보쌈 정식"},
        {"name": "닭갈비", "desc": "매콤한 닭갈비에 볶음밥 마무리"},
        {"name": "곱창", "desc": "불맛 가득 곱창 한 판"},
        {"name": "제주 흑돼지", "desc": "두툼한 흑돼지 구이 (사칙 부릸)"},
    ],
    "해산물": [
        {"name": "회덮밥", "desc": "신선한 회에 초장 비벼서"},
        {"name": "해물파전", "desc": "바삭하고 ꭄ깃한 해물파전"},
        {"name": "조개구이", "desc": "조개 구워먹는 점심 (특별한 날)"},
        {"name": "새우튀김 정식", "desc": "바삭한 새우튀김 도시락"},
        {"name": "장어덮밥", "desc": "기력 보충에 장어덮밥"},
        {"name": "연어덮밥", "desc": "연어 두툼하게 올린 포케 스타일"},
        {"name": "꼬막비빔밥", "desc": "통통한 꼬막에 양념장 비빔"},
        {"name": "생선구이 정식", "desc": "고등어/삼치 구이에 밥 한 공기"},
    ],
    "중식": [
        {"name": "짜장면", "desc": "달콤짭짤한 춘장의 매력"},
        {"name": "짬뽕", "desc": "얼큰한 국물이 당기는 날"},
        {"name": "탕수육", "desc": "바삭한 탕수육, 부먹? 찍먹?"},
        {"name": "마파두부 덮밥", "desc": "매콤한 마파두부 한 그릇"},
        {"name": "양장피", "desc": "시원하고 새콤달콤한 양장피"},
        {"name": "볶음밥", "desc": "중국집 볶음밥의 불맛"},
        {"name": "깐풍기", "desc": "바삭 매콤한 깐풍기"},
        {"name": "잡채밥", "desc": "당면 가득 잡채밥"},
    ],
    "일식": [
        {"name": "초밥", "desc": "신선한 초밥 한 접시로 기분 전환"},
        {"name": "라멘", "desc": "진한 돈코츠 육수에 면 한 젓가락"},
        {"name": "돈카츠", "desc": "바삭한 돈카츠에 소스 듬뿍"},
        {"name": "우동", "desc": "따끈한 우동 국물에 몸도 마음도 따뜻"},
        {"name": "덮밥 (규동)", "desc": "소고기 덮밥 규동 한 그릇"},
        {"name": "카츠카레", "desc": "돈카츠 + 카레 = 최강 조합"},
        {"name": "연어 사시미", "desc": "신선한 사시미 한 점시"},
        {"name": "타코야끼", "desc": "간식 겸 점시, 타코야끼"},
    ],
    "양식": [
        {"name": "파스타", "desc": "크림? 토마토? 오일? 뭐든 좋아!"},
        {"name": "햄버거", "desc": "육즙 가득 버거로 에너지 충전"},
        {"name": "피자", "desc": "치즈 쭉~ 늘어나는 피자 한 판"},
        {"name": "스테이크", "desc": "오늘은 좀 럭셔리하게 스테이크"},
        {"name": "리조또", "desc": "크리미한 리조또 한 그릇"},
        {"name": "오믈렛", "desc": "폭신한 오믈렛 브런치"},
        {"name": "그라탱", "desc": "치즈 녹은 그라탱 한 접시"},
        {"name": "스프+빵", "desc": "따뜻한 스프에 바삭한 빵"},
    ],
    "아시안": [
        {"name": "쌀국수 (포)", "desc": "베트남 쌀국수로 깔끔하게"},
        {"name": "팟타이", "desc": "새콤달콤한 태국식 볶음면"},
        {"name": "카오만가이", "desc": "부드러운 태국식 치킨라이스"},
        {"name": "분짜", "desc": "하노이식 분짜로 이국적인 점심"},
        {"name": "반미 샌드위치", "desc": "바삭한 바겈트에 베트남 반미"},
        {"name": "똠양꿍", "desc": "새콤매콤 태국식 수프"},
        {"name": "나시고렝", "desc": "인도네시아 볶음밥"},
        {"name": "커리 (인도식)", "desc": "향신료 가득 인도 커리에 난"},
    ],
    "패스트푸드": [
        {"name": "치m��", "desc": "점심 치킨 한 마리의 유혹"},
        {"name": "맥도날드/버거킹", "desc": "빠르게 세트메뉴 하나"},
        {"name": "서브웨이", "desc": "건강한 척 서브웨이 한 줄"},
        {"name": "피자 (배달)", "desc": "다 같이 시킬면 가성비 최고"},
        {"name": "타코/부리또", "desc": "멕시칸 한 끼, 타코벨 스타일"},
        {"name": "핫도그", "desc": "명랑핫도그/이삭토스트 간편하게"},
    ],
    "건강식/다이어트": [
        {"name": "샐러드", "desc": "오늘은 건강하게 샐러드 한 볼"},
        {"name": "닭가슴살 도시락", "desc": "다이어트 중이라면 닭가슴살"},
        {"name": "포케", "desc": "하와이안 포케볼로 가볍게"},
        {"name": "두부 정식", "desc": "담백한 두부 요리 한 상"},
        {"name": "곤약 비빔면", "desc": "칼로리 걱정 없는 곤약면"},
        {"name": "그릭 요거트 볼", "desc": "그래넀라 + 요거트 브런치"},
    ],
    "간편식/도시락": [
        {"name": "편의점 도시락", "desc": "가성비 갑! 편의점 도시락"},
        {"name": "샌드위치", "desc": "가볍게 샌드위치 하나 어때?"},
        {"name": "토스트", "desc": "길거리 토스트의 그 맛"},
        {"name": "삼각김밥 + 컵라면", "desc": "직장인의 소울 조합"},
        {"name": "주먹밥", "desc": "간편하게 주먹밥 한 개"},
        {"name": "컵밥", "desc": "컵밥으로 빠르게 해결"},
    ],
    "국밥/해장": [
        {"name": "순대국밥", "desc": "뜨끉한 순대국밥 한 그릇"},
        {"name": "돼지국밥", "desc": "부산숝 돼지국밥 속 풀기"},
        {"name": "소머리국밥", "desc": "진한 국물의 소머리국밥"},
        {"name": "콩나물국밥", "desc": "전주식 콩나물국밥 해장"},
        {"name": "내장탕", "desc": "뜨끈한 내장탕으로 속 달래기"},
        {"name": "뼈해장국", "desc": "어젯밤 술 마셨다면 뼈해장국"},
        {"name": "황태해장국", "desc": "시원한 황태국물로 해장"},
    ],
    "카페/브런치": [
        {"name": "크로와상 + 커픸", "desc": "가볍게 크로와상 브런치"},
        {"name": "에그 베네딕트", "desc": "반숙 달걀이 흐르는 브런치"},
        {"name": "프렌치토스트", "desc": "달콤한 프렌치토스트 한 접시"},
        {"name": "베이글 + 크림치즈", "desc": "베이글에 크림치즈 듬뿍"},
        {"name": "팬케이크", "desc": "메이플시럽 뿌린 팬케이크"},
        {"name": "아보카도 토스트", "desc": "힙한 아보카도 토스트"},
    ],
}

# 전체 메뉴 리스트 (카테고리 포함)
ALL_MENUS = []
for category, items in MENU_DATA.items():
    for item in items:
        ALL_MENUS.append({**item, "category": category})

# 메뉴 이름 → 메뉴 정보 매핑 (메뉴 이름 검색용)
MENU_LOOKUP = {}
for menu in ALL_MENUS:
    MENU_LOOKUP[menu["name"]] = menu
    # 짧은 이름으로도 찾을 수 있게 (괄호, + 앞부분)
    short = menu["name"].split("(")[0].split("+")[0].strip()
    if short != menu["name"]:
        MENU_LOOKUP[short] = menu

# 카테고리 이모지 매핑
CATEGORY_EMOJI = {
    "한식 밥류": "🍚", "찌개/탕/전골": "🍲", "면류": "🍜", "분식": "🧆",
    "고기/구이": "🥩", "해산물": "🐟", "중식": "🥟", "일식": "🍣",
    "양식": "🍝", "아시안": "🍛", "패스트푸드": "🍔", "건강식/다이어트": "🥗",
    "간편식/도시락": "🍱", "국밥/해장": "🥘", "카페/브런치": "☕",
}


# ============================================================
# 🎯 추천 로직
# ============================================================

def get_recommendations(count=3, category=None):
    """메뉴 추천 (중복 없이)"""
    if category and category in MENU_DATA:
        pool = [{"name": m["name"], "desc": m["desc"], "category": category}
                for m in MENU_DATA[category]]
    else:
        pool = ALL_MENUS.copy()

    count = min(count, len(pool))
    return random.sample(pool, count)


def find_menu_by_name(text):
    """사용자 입력에서 메뉴 이름 찾기"""
    text = text.strip()
    # 정확히 일치
    if text in MENU_LOOKUP:
        return MENU_LOOKUP[text]
    # 폨함 검색 (짧은 입력으로도 찾기)
    for name, menu in MENU_LOOKUP.items():
        if text in name or name in text:
            return menu
    return None


def detect_category(text):
    """사용자 입력에서 카테고리 감지"""
    # 정확한 카테고리 이름 매칭
    for category in MENU_DATA:
        if category in text:
            return category
    # 축약어/별칭 매핑
    aliases = {
        "한식": "한식 밥류", "밥": "한식 밥류",
        "찌개": "찌개/탕/전골", "탕": "찌개/탕/전골", "전골": "찌개/탕/전골",
        "면": "면류", "국수": "면류", "라면": "면류",
        "분식": "분식", "떡본이": "분식",
        "고기": "고기/구이", "구이": "고기/구이", "삼겼살": "고기/구이",
        "해산물": "해산물", "회": "해산물", "생선": "해산물",
        "중식": "중식", "중국": "중식", "짜장": "중식", "여뽕": "중식",
        "일식": "일식", "일본": "일식", "초밥": "일식", "돈카츠": "일식",
        "양식": "양식", "파스타": "양식", "피자": "양식", "스테이크": "양식",
        "아시안": "아시안", "베트남": "아시안", "태국": "아시안",
        "패스트푸드": "패스트푸드", "패스트": "패스트푸드", "치킨": "패스트푸드", "버거": "패스트푸드",
        "건강": "건강식/다이어트", "다이어트": "건강식/다이어트", "샐러드": "건강식/다이어트",
        "간편": "간편식/도시락", "도시락": "간편식/도시락", "편의점": "간편식/도시락",
        "국밥": "국밥/해장", "해장": "국밥/해장",
        "브런치": "카페/브런치", "카페": "카페/브런치",
    }
    for keyword, cat in aliases.items():
        if keyword in text:
            return cat
    return None


# ============================================================
# 📨 카카오톡 응답 포맷
# ============================================================

def make_simple_text(text):
    """SimpleText 응답"""
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}]
        }
    }


def make_recommendation_response(menus):
    """추천 결과 응답 — 깔끔한 SimpleText + 다시 추천/맛있게 드세요 버튼"""
    text = "🎰 오늘의 점심 추천!\n\n"
    for i, menu in enumerate(menus, 1):
        emoji = CATEGORY_EMOJI.get(menu["category"], "🍽️")
        text += f"{i}. {emoji} {menu['name']}\n"
        text += f"   {menu['desc']}\n\n"
    text += "마음에 드는 메뉴가 있나요? 😋"

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": [
                {"label": "🎲 다시 추천해줘", "action": "message", "messageText": "다시 추천"},
                {"label": "🍽️ 카테고리 골라볼래", "action": "message", "messageText": "카테고리"},
                {"label": "😋 맛있게 먹을게!", "action": "message", "messageText": "맛있게 먹을게"},
            ]
        }
    }


def make_category_recommendation(category, menus):
    """특정 카테고리 추천 결과"""
    emoji = CATEGORY_EMOJI.get(category, "🍽️")
    text = f"{emoji} [{category}] 추천 메뉴!\n\n"
    for i, menu in enumerate(menus, 1):
        text += f"{i}. {menu['name']}\n"
        text += f"   {menu['desc']}\n\n"
    text += "이 중에 땡기는 거 있나요? 😋"

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": [
                {"label": f"🎲 {category} 다시", "action": "message", "messageText": f"{category} 추천"},
                {"label": "🔀 전체에서 추천", "action": "message", "messageText": "아무거나 추천"},
                {"label": "😋 맛있게 먹을게!", "action": "message", "messageText": "맛있게 먹을게"},
            ]
        }
    }


def make_category_list():
    """카테고리 목록 응답"""
    text = "어떤 종류의 음식이 땡기세요? 🤔\n\n"
    for cat, items in MENU_DATA.items():
        emoji = CATEGORY_EMOJI.get(cat, "🍽️")
        text += f"{emoji} {cat} ({len(items)}개)\n"
    text += f"\n총 {len(ALL_MENUS)}개 메뉴가 준비되어 있어요!\n"
    text += "카테고리 이름을 입력하거나 그냥 '추천'이라고 해주세요 😊"

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": [
                {"label": "🎲 아무거나!", "action": "message", "messageText": "아무거나 추천"},
                {"label": "🍚 한식", "action": "message", "messageText": "한식 추천"},
                {"label": "🍜 면류", "action": "message", "messageText": "면류 추천"},
                {"label": "🥩 고기", "action": "message", "messageText": "고기 추천"},
                {"label": "🍝 양식", "action": "message", "messageText": "양식 추천"},
            ]
        }
    }


def make_goodbye():
    """맛있게 드세요 응답"""
    messages = [
        "맛있게 드세요! 😋🍽️\n다음에 또 골라드릴게요!",
        "좋은 선택! 맠점 하세요! 🎉\n또 고민되메 불러주세요~",
        "오늘 점심도 해결! 👍\n맛있게 드시고 오후도 화이팅!",
        "맛점 되세요~! 🍚✨\n식후 커피도 잊지 마세요 ☕",
    ]
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": random.choice(messages)}}],
            "quickReplies": [
                {"label": "🎲 내일은 �� 먹지?", "action": "message", "messageText": "점시 추천"},
            ]
        }
    }


def make_menu_info(menu):
    """특정 메뉴 정보 응답"""
    emoji = CATEGORY_EMOJI.get(menu["category"], "🍽️")
    text = f"{emoji} {menu['name']}\n"
    text += f"[{menu['category']}] {menu['desc']}\n\n"
    text += "이거 먹을래요? 아니메 다른 거 추천해드릴까요?"

    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": [
                {"label": "😋 이거 먹을래!", "action": "message", "messageText": "맛있게 먹을게"},
                {"label": "🎲 다른 거 추천", "action": "message", "messageText": "다시 추천"},
                {"label": f"🔀 {menu['category']} 더 보기", "action": "message", "messageText": f"{menu['category']} 추천"},
            ]
        }
    }


# ============================================================
# 🌐 카카오 웹훅 엔드포인트
# ============================================================

@app.route("/", methods=["GET"])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        "status": "ok",
        "message": "점심 추천 봇 v2.0 실행 중! 🍽️",
        "menus": len(ALL_MENUS),
        "categories": len(MENU_DATA),
    })


@app.route("/api/lunch", methods=["POST"])
def lunch_recommend():
    """
    메인 점심 추천 스킬 엔드포인트
    """
    try:
        body = request.get_json()
        utterance = body.get("userRequest", {}).get("utterance", "").strip()
        logger.info(f"사용자 입력: {utterance}")

        # 1) 맛있게 먹을게" / 고마워 → 인사 마무기
        if any(kw in utterance for kw in ["맛있게", "먹을게", "고마워", "감사", "ㄱㅅ", "ㄱㅁ", "잠밙"]):
            return jsonify(make_goodbye())

        # 2) 카테고리 목록 요청
        if any(kw in utterance for kw in ["목록", "카테고리", "종류", "뙀 있"]):
            return jsonify(make_category_list())

        # 3) 카테고리 감지 → 해당 카테고리에서 추천
        detected = detect_category(utterance)
        if detected:
            menus = get_recommendations(3, detected)
            return jsonify(make_category_recommendation(detected, menus))

        # 4) 메뉴 이름 감지 → 해당 메뉴 정보
        found_menu = find_menu_by_name(utterance)
        if found_menu:
            return jsonify(make_menu_info(found_menu))

        # 5) 기본: 어떤 입력이든 추천해주기 (이 액의 조재 이유!)
        menus = get_recommendations(3)
        return jsonify(make_recommendation_response(menus))

    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        return jsonify(make_simple_text("앗오류가 발생햄어요 😅\n잠시 후 다시 시도해주세요."))

# ============================================================
# 🚀 서버 실행
# ========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
