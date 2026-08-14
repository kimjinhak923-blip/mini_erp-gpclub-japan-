import streamlit as st
from sidebar_menu import render_sidebar
from utils.i18n import txt

# 1. 공통 사이드바 및 언어선택기 호출
render_sidebar()

# 2. 페이지 헤더
st.title(txt("menu_mypage", "👤 마이페이지"))

# ... (이하 기존 마이페이지 로직 코드)

# -----------------------------------------------------------------------------
# 1. 다국어 사전 정의 (한국어 / 日本語 / English)
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "KO": {
        "page_title": "마이페이지",
        "title": "👤 마이페이지",
        "login_required": "로그인이 필요한 페이지입니다.",
        "sec_info": "📋 기본 정보",
        "label_id": "아이디",
        "label_name": "이름",
        "label_position": "직급",
        "label_role": "시스템 권한",
        "default_position": "사원",
        "default_role": "일반 사용자",
        "sec_leave": "🌴 근태 및 연차 정보",
        "label_hire_date": "입사일",
        "label_remaining_leave": "잔여 연차",
        "unregistered": "미등록",
        "days": "일",
        "sec_lang": "🌐 선호 언어 설정",
        "label_select_lang": "시스템 사용 언어 선택",
        "btn_save_lang": "언어 설정 저장",
        "msg_lang_saved": "선호 언어가 변경되었습니다.",
        "sec_pw": "🔑 비밀번호 변경",
        "label_current_pw": "현재 비밀번호",
        "label_new_pw": "새 비밀번호",
        "label_confirm_pw": "새 비밀번호 확인",
        "btn_change_pw": "비밀번호 변경",
        "err_current_pw": "현재 비밀번호가 일치하지 않습니다.",
        "err_confirm_pw": "새 비밀번호 확인이 일치하지 않습니다.",
        "err_empty_pw": "새 비밀번호를 입력해 주세요.",
        "msg_pw_success": "비밀번호가 성공적으로 변경되었습니다.",
    },
    "JA": {
        "page_title": "マイページ",
        "title": "👤 マイページ",
        "login_required": "ログインが必要なページです。",
        "sec_info": "📋 基本情報",
        "label_id": "ユーザーID",
        "label_name": "氏名",
        "label_position": "役職",
        "label_role": "システム権限",
        "default_position": "社員",
        "default_role": "一般ユーザー",
        "sec_leave": "🌴 勤怠・年次有給休暇情報",
        "label_hire_date": "入社日",
        "label_remaining_leave": "残有給日数",
        "unregistered": "未登録",
        "days": "日",
        "sec_lang": "🌐 言語設定",
        "label_select_lang": "システム使用言語の選択",
        "btn_save_lang": "言語設定を保存",
        "msg_lang_saved": "言語設定が変更されました。",
        "sec_pw": "🔑 パスワード変更",
        "label_current_pw": "現在のパスワード",
        "label_new_pw": "新しいパスワード",
        "label_confirm_pw": "新しいパスワード(確認)",
        "btn_change_pw": "パスワード変更",
        "err_current_pw": "現在のパスワードが一致しません。",
        "err_confirm_pw": "新しいパスワード(確認)が一致しません。",
        "err_empty_pw": "新しいパスワードを入力してください。",
        "msg_pw_success": "パスワードが 정상的に変更されました。",
    },
    "EN": {
        "page_title": "My Page",
        "title": "👤 My Page",
        "login_required": "Login is required to access this page.",
        "sec_info": "📋 Basic Information",
        "label_id": "User ID",
        "label_name": "Name",
        "label_position": "Position",
        "label_role": "System Role",
        "default_position": "Staff",
        "default_role": "General User",
        "sec_leave": "🌴 Attendance & Leave Info",
        "label_hire_date": "Hire Date",
        "label_remaining_leave": "Remaining Leave",
        "unregistered": "Not Registered",
        "days": "days",
        "sec_lang": "🌐 Preferred Language",
        "label_select_lang": "Select System Language",
        "btn_save_lang": "Save Language Setting",
        "msg_lang_saved": "Preferred language updated successfully.",
        "sec_pw": "🔑 Change Password",
        "label_current_pw": "Current Password",
        "label_new_pw": "New Password",
        "label_confirm_pw": "Confirm New Password",
        "btn_change_pw": "Change Password",
        "err_current_pw": "Current password does not match.",
        "err_confirm_pw": "New password confirmation does not match.",
        "err_empty_pw": "Please enter a new password.",
        "msg_pw_success": "Password successfully changed.",
    },
}

# -----------------------------------------------------------------------------
# 2. 세션 사용자 및 언어 감지
# -----------------------------------------------------------------------------
user = st.session_state.get("logged_in_user")

# 사용자 개별 설정 언어 우선 감지 -> 없으면 세션 글로벌 언어 감지
raw_lang = (
    (user.get("language") if user else None)
    or st.session_state.get("lang")
    or st.session_state.get("language")
    or "KO"
)

lang_mapping = {
    "한국어": "KO",
    "KO": "KO",
    "日本語": "JA",
    "JA": "JA",
    "English": "EN",
    "EN": "EN",
}
current_lang = lang_mapping.get(raw_lang, "KO")
t = TRANSLATIONS[current_lang]

# -----------------------------------------------------------------------------
# 3. Streamlit Page Config 설정 (최상단)
# -----------------------------------------------------------------------------
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링
render_sidebar()

# -----------------------------------------------------------------------------
# 5. 메인 UI 렌더링
# -----------------------------------------------------------------------------
st.title(t["title"])
st.markdown("---")

if not user:
    st.warning(t["login_required"])
else:
    # --- 기본 정보 및 근태 정보 ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t["sec_info"])
        st.write(f"**{t['label_id']}:** {user.get('id', '')}")
        st.write(f"**{t['label_name']}:** {user.get('name', '')}")
        st.write(
            f"**{t['label_position']}:** {user.get('position', t['default_position'])}"
        )
        st.write(f"**{t['label_role']}:** {user.get('role', t['default_role'])}")

    with col2:
        st.subheader(t["sec_leave"])
        st.write(
            f"**{t['label_hire_date']}:** {user.get('hire_date', t['unregistered'])}"
        )
        st.write(
            f"**{t['label_remaining_leave']}:** {user.get('remaining_leave', 0)} {t['days']}"
        )

    st.markdown("---")

    # --- 선호 언어 설정 (직원별 언어 설정 유지) ---
    st.subheader(t["sec_lang"])
    lang_options = ["한국어", "日本語", "English"]

    # 현재 설정된 언어의 인덱스 계산
    default_idx = 0
    if current_lang == "JA":
        default_idx = 1
    elif current_lang == "EN":
        default_idx = 2

    selected_lang = st.selectbox(
        t["label_select_lang"], lang_options, index=default_idx
    )

    if st.button(t["btn_save_lang"]):
        selected_code = lang_mapping[selected_lang]

        # 1) 로그인된 사용자 객체에 저장 (로그인 시 유지 목적)
        user["language"] = selected_code

        # 2) 전체 세션 상태 언어 키 업데이트
        st.session_state["lang"] = selected_code
        st.session_state["language"] = selected_code

        # 3) 사용자 목록 세션이 있다면 원본 데이터도 동기화
        if "users" in st.session_state:
            for u in st.session_state.users:
                if u.get("id") == user.get("id"):
                    u["language"] = selected_code
                    break

        st.success(t["msg_lang_saved"])
        st.rerun()

    st.markdown("---")

    # --- 비밀번호 변경 폼 ---
    st.subheader(t["sec_pw"])
    with st.form("change_pw_form"):
        current_pw = st.text_input(t["label_current_pw"], type="password")
        new_pw = st.text_input(t["label_new_pw"], type="password")
        new_pw_confirm = st.text_input(t["label_confirm_pw"], type="password")
        submit_pw = st.form_submit_button(t["btn_change_pw"])

        if submit_pw:
            if current_pw != user.get("pw"):
                st.error(t["err_current_pw"])
            elif new_pw != new_pw_confirm:
                st.error(t["err_confirm_pw"])
            elif not new_pw:
                st.error(t["err_empty_pw"])
            else:
                user["pw"] = new_pw

                # 사용자 목록 세션 동기화
                if "users" in st.session_state:
                    for u in st.session_state.users:
                        if u.get("id") == user.get("id"):
                            u["pw"] = new_pw
                            break

                st.success(t["msg_pw_success"])
