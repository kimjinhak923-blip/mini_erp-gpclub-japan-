import streamlit as st
import streamlit.components.v1 as components

# 다국어 딕셔너리
TRANSLATIONS = {
    "system_title": {
        "한국어": "🏢 사내 통합 관리 시스템 (ERP)",
        "English": "🏢 Enterprise Resource Planning (ERP)",
        "日本語": "🏢 社内統合管理システム (ERP)",
    },
    "live_clock": {
        "한국어": "🕒 도쿄 실시간 시계",
        "English": "🕒 Tokyo Live Clock",
        "日本語": "🕒 東京 リアルタイム時計",
    },
    "auth_center": {
        "한국어": "🔑 인증 센터",
        "English": "🔑 Authentication Center",
        "日本語": "🔑 認証センター",
    },
    "login": {
        "한국어": "로그인",
        "English": "Login",
        "日本語": "ログイン",
    },
    "signup": {
        "한국어": "회원가입",
        "English": "Sign Up",
        "日本語": "新規登録",
    },
    "user_id": {
        "한국어": "아이디",
        "English": "User ID",
        "日本語": "ユーザーID",
    },
    "password": {
        "한국어": "비밀번호",
        "English": "Password",
        "日本語": "パスワード",
    },
    "name": {
        "한국어": "이름",
        "English": "Name",
        "日本語": "氏名",
    },
    "preferred_lang": {
        "한국어": "선호 언어",
        "English": "Preferred Language",
        "日本語": "希望言語",
    },
    "pending_approval": {
        "한국어": "🔒 승인 대기 중인 계정입니다. 관리자에게 문의하세요.",
        "English": "🔒 Account pending approval. Please contact administrator.",
        "日本語": "🔒 承認待ちのアカウントです。管理者にお問い合わせください。",
    },
    "login_fail": {
        "한국어": "❌ 아이디 또는 비밀번호가 올바르지 않습니다.",
        "English": "❌ Invalid ID or password.",
        "日本語": "❌ IDまたはパスワードが正しくありません。",
    },
    "signup_btn": {
        "한국어": "회원가입 신청",
        "English": "Apply for Sign Up",
        "日本語": "新規登録申請",
    },
    "signup_success": {
        "한국어": "✅ 회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인 가능합니다.",
        "English": "✅ Sign up submitted. Available after admin approval.",
        "日本語": "✅ 登録申請が完了しました。管理者の承認後にログインできます。",
    },
    "fill_all": {
        "한국어": "⚠️ 모든 항목을 입력해 주세요.",
        "English": "⚠️ Please fill in all fields.",
        "日本語": "⚠️ すべての項目を入力してください。",
    },
    "commute_system": {
        "한국어": "⏱️ 출퇴근 시스템",
        "English": "⏱️ Time & Attendance System",
        "日本語": "⏱️ 勤怠管理システム",
    },
    "greeting": {
        "한국어": "👋 {name}님, 오늘 하루도 힘내세요!",
        "English": "👋 Have a great day, {name}!",
        "日本語": "👋 {name}さん、今日もお疲れ様です！",
    },
    "current_time_info": {
        "한국어": "📅 현재 기준 시각: Asia/Tokyo",
        "English": "📅 Current Time Zone: Asia/Tokyo",
        "日本語": "📅 現在のタイムゾーン: Asia/Tokyo",
    },
    "clock_in": {
        "한국어": "☀️ 출근하기",
        "English": "☀️ Clock In",
        "日本語": "☀️ 出勤する",
    },
    "clock_out": {
        "한국어": "🌙 퇴근하기",
        "English": "🌙 Clock Out",
        "日本語": "🌙 退勤する",
    },
    "clock_in_success": {
        "한국어": "[{time}] 출근 처리가 완료되었습니다!",
        "English": "[{time}] Clock-in recorded successfully!",
        "日本語": "[{time}] 出勤打刻が完了しました！",
    },
    "clock_out_success": {
        "한국어": "[{time}] 퇴근 처리가 완료되었습니다!",
        "English": "[{time}] Clock-out recorded successfully!",
        "日本語": "[{time}] 退勤打刻が完了しました！",
    },
    "todays_record": {
        "한국어": "📋 오늘의 기록",
        "English": "📋 Today's Record",
        "日本語": "📋 本日の記録",
    },
    "clock_in_time": {
        "한국어": "출근 시간",
        "English": "Clock In Time",
        "日本語": "出勤時間",
    },
    "clock_out_time": {
        "한국어": "퇴근 시간",
        "English": "Clock Out Time",
        "日本語": "退勤時間",
    },
    "unregistered": {
        "한국어": "미등록",
        "English": "Not Registered",
        "日本語": "未登録",
    },
    "login_required": {
        "한국어": "🔒 로그인이 필요합니다.",
        "English": "🔒 Login required.",
        "日本語": "🔒 ログインが必要です。",
    },
    "go_to_login": {
        "한국어": "🔑 로그인 화면으로 이동",
        "English": "🔑 Go to Login Page",
        "日本語": "🔑 ログイン画面へ移動",
    },
    "lang_select": {
        "한국어": "🌐 번역 선택 / Language",
        "English": "🌐 Language Selection",
        "日本語": "🌐 言語選択 / Language",
    },
    "logged_in_as": {
        "한국어": "👤 접속자",
        "English": "👤 User",
        "日本語": "👤 ログインユーザー",
    },
    "logout": {
        "한국어": "🚪 로그아웃",
        "English": "🚪 Logout",
        "日本語": "🚪 ログアウト",
    },
}

def txt(key: str, **kwargs) -> str:
    """현재 세션 언어(st.session_state.lang)에 따라 텍스트를 반환하는 함수"""
    lang = st.session_state.get("lang", "한국어")
    text = TRANSLATIONS.get(key, {}).get(lang, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def render_live_clock():
    """웹 브라우저에서 페이지 새로고침 없이 1초마다 초단위로 갱신되는 도쿄 실시간 시계"""
    components.html(
        """
        <div id="live-clock" style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 15px;
            font-weight: bold;
            color: #1f2937;
            background-color: #f3f4f6;
            padding: 8px 12px;
            border-radius: 6px;
            text-align: center;
            border: 1px solid #e5e7eb;
        ">
            🕒 Loading...
        </div>
        <script>
            function updateClock() {
                const options = {
                    timeZone: 'Asia/Tokyo',
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                };
                const formatter = new Intl.DateTimeFormat('sv-SE', options);
                const nowString = formatter.format(new Date());
                document.getElementById('live-clock').innerText = '🕒 ' + nowString + ' (Asia/Tokyo)';
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
        """,
        height=45,
    )
