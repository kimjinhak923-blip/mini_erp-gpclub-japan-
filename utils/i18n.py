from datetime import datetime
import pytz
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 다국어 번역 사전
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "KO": {
        "clock_title": "현재 시간",
        "clock_tz": "한국 표준시 (KST)",
        "commute_in": "출근하기",
        "commute_out": "퇴근하기",
        "already_in": "이미 출근 처리되었습니다.",
        "already_out": "이미 퇴근 처리되었습니다.",
    },
    "JA": {
        "clock_title": "現在時刻",
        "clock_tz": "日本標準時 (JST)",
        "commute_in": "出勤",
        "commute_out": "退勤",
        "already_in": "出勤処理が完了しています。",
        "already_out": "退勤処理が完了しています。",
    },
    "EN": {
        "clock_title": "Current Time",
        "clock_tz": "Standard Time",
        "commute_in": "Clock In",
        "commute_out": "Clock Out",
        "already_in": "Already clocked in.",
        "already_out": "Already clocked out.",
    },
}


# -----------------------------------------------------------------------------
# 2. 현재 사용자/세션 언어 감지 함수
# -----------------------------------------------------------------------------
def get_language():
    """로그인 사용자 선호 언어 또는 세션 글로벌 언어 감지"""
    user = st.session_state.get("logged_in_user", {})
    raw_lang = (
        (user.get("language") if isinstance(user, dict) else None)
        or st.session_state.get("lang")
        or st.session_state.get("language")
        or "KO"
    )

    mapping = {
        "한국어": "KO",
        "KO": "KO",
        "日本語": "JA",
        "JA": "JA",
        "English": "EN",
        "EN": "EN",
    }
    return mapping.get(raw_lang, "KO")


# -----------------------------------------------------------------------------
# 3. 번역 텍스트 반환 함수 (txt)
# -----------------------------------------------------------------------------
def txt(key: str, default_text: str = None) -> str:
    """i18n 텍스트 반환 함수"""
    lang = get_language()

    # 1) 세션 상태에 저장된 공통 번역 테이블이 있다면 우선 탐색
    custom_dict = st.session_state.get("translations", {})
    if lang in custom_dict and key in custom_dict[lang]:
        return custom_dict[lang][key]

    # 2) 기본 내장 사전 탐색
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]

    # 3) 없을 경우 전달받은 default_text 또는 키 이름 그대로 반환
    return default_text if default_text is not None else key


# -----------------------------------------------------------------------------
# 4. 실시간 시계 위젯 함수 (render_live_clock)
# -----------------------------------------------------------------------------
def render_live_clock(timezone_str: str = "Asia/Tokyo"):
    """출퇴근 페이지용 시계 렌더링 함수"""
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()

    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

    st.markdown(
        f"""
        <div style="
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 12px 20px;
            text-align: center;
            margin-bottom: 15px;
        ">
            <span style="font-size: 14px; color: #6c757d;">🕒 {txt('clock_title', '현재 시간')}</span>
            <h2 style="margin: 4px 0 0 0; font-size: 24px; color: #1e293b;">{formatted_time}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
