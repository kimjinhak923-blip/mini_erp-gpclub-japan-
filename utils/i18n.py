import streamlit as st

# 다국어 번역 사원
I18N = {
    "KO": {
        "title": "ERP 시스템",
        "login": "로그인",
        "logout": "로그아웃",
        "email": "이메일 주소",
        "password": "비밀번호",
        "remember_me": "자동 로그인 유지 (브라우저 종료 시에도 유지)",
        "login_btn": "로그인 하기",
        "login_success": "성공적으로 로그인되었습니다.",
        "login_error": "이메일 또는 비밀번호가 올바르지 않습니다.",
        "lang_select": "언어 선택 / Language",
        "welcome": "환영합니다"
    },
    "JA": {
        "title": "ERP システム",
        "login": "ログイン",
        "logout": "ログアウト",
        "email": "メールアドレス",
        "password": "パスワード",
        "remember_me": "自動ログインを維持する",
        "login_btn": "ログイン",
        "login_success": "ログインに成功しました。",
        "login_error": "メールアドレスまたはパスワードが正しくありません。",
        "lang_select": "言語選択 / Language",
        "welcome": "ようこそ"
    },
    "EN": {
        "title": "ERP System",
        "login": "Login",
        "logout": "Logout",
        "email": "Email Address",
        "password": "Password",
        "remember_me": "Keep me logged in",
        "login_btn": "Log In",
        "login_success": "Logged in successfully.",
        "login_error": "Invalid email or password.",
        "lang_select": "Language",
        "welcome": "Welcome"
    }
}

def get_lang():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "KO"
    return st.session_state["lang"]

def render_lang_selector():
    current_lang = get_lang()
    options = ["KO", "JA", "EN"]
    idx = options.index(current_lang) if current_lang in options else 0
    selected = st.sidebar.selectbox("🌐 Language / 言語", options, index=idx, key="lang_selector")
    st.session_state["lang"] = selected

def t(key):
    lang = get_lang()
    return I18N.get(lang, I18N["KO"]).get(key, key)
