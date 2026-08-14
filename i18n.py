from datetime import datetime
import pytz
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 다국어 번역 사전 (전역 공통)
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
    },
    "JA": {
        "clock_title": "現在時刻",
        "clock_tz": "日本標準時 (JST)",
        "commute_in": "出勤",
        "commute_out": "退勤",
        "already_in": "出勤処理が完了しています。",
        "already_out": "退勤処理が完了しています。",
        "select_language": "🌐 言語選択 (Language)",
    },
    "EN": {
        "clock_title": "Current Time",
        "clock_tz": "Standard Time",
        "commute_in": "Clock In",
        "commute_out": "Clock Out",
        "already_in": "Already clocked in.",
        "already_out": "Already clocked out.",
        "select_language": "🌐 Select Language",
    },
}

# 언어 명칭 매핑
LANG_MAP_TO_CODE = {
    "한국어": "KO",
    "KO": "KO",
    "日本語": "JA",
    "JA": "JA",
    "English": "EN",
    "EN": "EN",
}

LANG_MAP_TO_NAME = {"KO": "한국어", "JA": "日本語", "EN": "English"}


# -----------------------------------------------------------------------------
# 2. 현재 사용자 및 세션 언어 감지 함수 (버그 수정 완료)
# -----------------------------------------------------------------------------
def get_language():
    """세션 상태 및 로그인 유저 정보에서 현재 언어 코드를 정확히 감지"""
    # 1. 글로벌 세션 'lang' 확인
    if "lang" in st.session_state and st.session_state["lang"]:
        raw_lang = st.session_state["lang"]
    # 2. 글로벌 세션 'language' 확인
    elif "language" in st.session_state and st.session_state["language"]:
        raw_lang = st.session_state["language"]
    # 3. 로그인된 유저의 선호 언어 확인
    elif "logged_in_user" in st.session_state and isinstance(
        st.session_state["logged_in_user"], dict
    ):
        raw_lang = st.session_state["logged_in_user"].get("language", "KO")
    else:
        raw_lang = "KO"

    return LANG_MAP_TO_CODE.get(str(raw_lang), "KO")


# -----------------------------------------------------------------------------
# 3. 텍스트 번역 출력 함수
# -----------------------------------------------------------------------------
def txt(key: str, default_text: str = None) -> str:
    """i18n 텍스트 반환 함수"""
    lang = get_language()

    # 1) 세션 상태에 커스텀 번역표가 있으면 우선 탐색
    custom_dict = st.session_state.get("translations", {})
    if (
        isinstance(custom_dict, dict)
        and lang in custom_dict
        and key in custom_dict[lang]
    ):
        return custom_dict[lang][key]

    # 2) 기본 번역 사전 탐색
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]

    # 3) 전달된 default_text 또는 key 그 자체 반환
    return default_text if default_text is not None else key


# -----------------------------------------------------------------------------
# 4. 언어 선택 셀렉트박스 렌더링 함수 (어디서나 호출 가능)
# -----------------------------------------------------------------------------
def render_language_selector(container=st.sidebar):
    """사이드바 등에 언어 선택 UI를 출력하고 변경 시 세션 및 유저 설정에 동시 반영"""
    current_code = get_language()
    current_name = LANG_MAP_TO_NAME.get(current_code, "한국어")

    options = ["한국어", "日本語", "English"]
    try:
        default_index = options.index(current_name)
    except ValueError:
        default_index = 0

    selected_name = container.selectbox(
        txt("select_language", "🌐 언어 선택"),
        options,
        index=default_index,
        key="global_language_selector",
    )

    selected_code = LANG_MAP_TO_CODE[selected_name]

    # 언어 변경 감지 시 즉시 세션 동기화 및 Rerun
    if selected_code != current_code:
        st.session_state["lang"] = selected_code
        st.session_state["language"] = selected_code

        if "logged_in_user" in st.session_state and isinstance(
            st.session_state["logged_in_user"], dict
        ):
            st.session_state["logged_in_user"]["language"] = selected_code

        st.rerun()


# -----------------------------------------------------------------------------
# 5. 실시간 시계 위젯 함수
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
