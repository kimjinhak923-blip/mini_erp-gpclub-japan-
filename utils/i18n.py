from datetime import datetime
import pytz
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 전역 번역 사전
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "KO": {
        "clock_title": "현재 시간",
        "clock_tz": "한국 표준시 (KST)",
        "commute_in": "출근하기",
        "commute_out": "퇴근하기",
        "already_in": "이미 출근 처리되었습니다.",
        "already_out": "이미 퇴근 처리되었습니다.",
        "select_language": "🌐 언어 선택 (Language)",
        "menu_commute": "⏱️ 출퇴근 관리 / 타임카드",
        "menu_system": "⚙️ 시스템 및 사용자 관리",
        "menu_mypage": "👤 마이페이지",
        "default_position": "사원",
        "default_role": "일반 사용자",
        "label_role": "권한",
        "btn_logout": "🚪 로그아웃",
    },
    "JA": {
        "clock_title": "現在時刻",
        "clock_tz": "日本標準時 (JST)",
        "commute_in": "出勤",
        "commute_out": "退勤",
        "already_in": "出勤処理が完了しています。",
        "already_out": "退勤処理が完了しています。",
        "select_language": "🌐 言語選択 (Language)",
        "menu_commute": "⏱️ 勤怠管理 / タイムカード",
        "menu_system": "⚙️ システムおよびユーザー管理",
        "menu_mypage": "👤 マイページ",
        "default_position": "社員",
        "default_role": "一般ユーザー",
        "label_role": "権限",
        "btn_logout": "🚪 ログアウト",
    },
    "EN": {
        "clock_title": "Current Time",
        "clock_tz": "Standard Time",
        "commute_in": "Clock In",
        "commute_out": "Clock Out",
        "already_in": "Already clocked in.",
        "already_out": "Already clocked out.",
        "select_language": "🌐 Select Language",
        "menu_commute": "⏱️ Attendance / Timecard",
        "menu_system": "⚙️ System & User Management",
        "menu_mypage": "👤 My Page",
        "default_position": "Staff",
        "default_role": "General User",
        "label_role": "Role",
        "btn_logout": "🚪 Logout",
    },
}

LANG_MAP_TO_CODE = {
    "한국어": "KO",
    "KO": "KO",
    "日本語": "JA",
    "JA": "JA",
    "English": "EN",
    "EN": "EN",
}

LANG_MAP_TO_NAME = {"KO": "한국어", "JA": "日本語", "EN": "English"}


def get_language():
    """세션 및 유저 설정에서 현재 언어 감지"""
    if "lang" in st.session_state and st.session_state["lang"]:
        raw_lang = st.session_state["lang"]
    elif "language" in st.session_state and st.session_state["language"]:
        raw_lang = st.session_state["language"]
    elif "logged_in_user" in st.session_state and isinstance(
        st.session_state["logged_in_user"], dict
    ):
        raw_lang = st.session_state["logged_in_user"].get("language", "KO")
    else:
        raw_lang = "KO"

    return LANG_MAP_TO_CODE.get(str(raw_lang), "KO")


def txt(key: str, default_text: str = None) -> str:
    """텍스트 번역 반환"""
    lang = get_language()
    custom_dict = st.session_state.get("translations", {})
    if (
        isinstance(custom_dict, dict)
        and lang in custom_dict
        and key in custom_dict[lang]
    ):
        return custom_dict[lang][key]

    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]

    return default_text if default_text is not None else key


def render_live_clock(timezone_str: str = "Asia/Tokyo"):
    """실시간 시계 렌더링"""
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
