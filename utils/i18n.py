import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 🌐 ERP 통합 다국어 번역 사전 (i18n)
# ==========================================
I18N = {
    "한국어": {
        # 메인 및 시스템 공통
        "system_title": "🏢 사내 통합 관리 시스템 (ERP)",
        "auth_center": "🔐 인증 센터",
        "login": "로그인",
        "signup": "회원가입",
        "user_id": "사원번호 또는 아이디",
        "password": "비밀번호",
        "name": "이름 (성명)",
        "preferred_lang": "기본 언어 선택",
        "signup_btn": "가입 신청",
        "pending_approval": "아직 관리자 승인이 완료되지 않은 계정입니다.",
        "login_fail": "아이디 또는 비밀번호가 올바르지 않습니다.",
        "signup_success": "회원가입 신청이 완료되었습니다. 관리자 승인 후 로그인할 수 있습니다.",
        "fill_all": "모든 항목을 입력해주세요.",
        "logout": "🚪 로그아웃",
        "logged_in_as": "👤 **{name}** ({role}) 님",
        "live_clock": "⏱️ 실시간 서버 시계",
        
        # 사이드바 메뉴명
        "menu_commute": "⏱️ 출퇴근 시스템",
        "menu_dashboard": "📊 대시보드",
        "menu_sales": "💰 매출 관리",
        "menu_inout_history": "📜 입출고 이력 조회",
        "menu_inventory": "📦 재고 관리 (입출고)",
        "menu_clients": "🏢 거래처 관리",
        "menu_products": "🏷️ 마스터 상품 관리",
        "menu_timecard": "📅 타임카드 / 캘린더",
        "menu_system": "⚙️ 시스템 관리",
        "menu_mypage": "👤 마이페이지",
        
        # 공통 버튼 및 라벨
        "save": "저장",
        "cancel": "취소",
        "edit": "수정",
        "delete": "삭제",
        "search": "검색",
        "confirm": "확인",
        "status": "상태",
        "note": "비고",
        "date": "날짜",
    },
    "English": {
        # Main & Common
        "system_title": "🏢 Enterprise Resource Planning (ERP)",
        "auth_center": "🔐 Authentication Center",
        "login": "Login",
        "signup": "Sign Up",
        "user_id": "Employee ID or Username",
        "password": "Password",
        "name": "Full Name",
        "preferred_lang": "Preferred Language",
        "signup_btn": "Apply for Account",
        "pending_approval": "This account is pending administrator approval.",
        "login_fail": "Invalid ID or Password.",
        "signup_success": "Registration submitted. You can log in after admin approval.",
        "fill_all": "Please fill in all fields.",
        "logout": "🚪 Logout",
        "logged_in_as": "👤 **{name}** ({role})",
        "live_clock": "⏱️ Real-time Clock",
        
        # Sidebar Menus
        "menu_commute": "⏱️ Clock In/Out System",
        "menu_dashboard": "📊 Dashboard",
        "menu_sales": "💰 Sales Management",
        "menu_inout_history": "📜 In/Out History",
        "menu_inventory": "📦 Inventory Management",
        "menu_clients": "🏢 Client Management",
        "menu_products": "🏷️ Master Product Catalog",
        "menu_timecard": "📅 Timecard & Calendar",
        "menu_system": "⚙️ System Administration",
        "menu_mypage": "👤 My Page",
        
        # Common Buttons & Labels
        "save": "Save",
        "cancel": "Cancel",
        "edit": "Edit",
        "delete": "Delete",
        "search": "Search",
        "confirm": "Confirm",
        "status": "Status",
        "note": "Note",
        "date": "Date",
    },
    "日本語": {
        # メインおよび共通
        "system_title": "🏢 社内統合管理システム (ERP)",
        "auth_center": "🔐 認証センター",
        "login": "ログイン",
        "signup": "新規会員登録",
        "user_id": "社員番号またはID",
        "password": "パスワード",
        "name": "氏名",
        "preferred_lang": "デフォルト言語選択",
        "signup_btn": "登録申請",
        "pending_approval": "まだ管理者の承認が完了していないアカウントです。",
        "login_fail": "IDまたはパスワードが正しくありません。",
        "signup_success": "会員登録の申請が完了しました。管理者の承認後にログインできます。",
        "fill_all": "すべての項目を入力してください。",
        "logout": "🚪 ログアウト",
        "logged_in_as": "👤 **{name}** ({role}) 様",
        "live_clock": "⏱️ リアルタイム時計",
        
        # サイドバーメニュー名
        "menu_commute": "⏱️ 出退勤システム",
        "menu_dashboard": "📊 ダッシュボード",
        "menu_sales": "💰 売上管理",
        "menu_inout_history": "📜 入出庫履歴照会",
        "menu_inventory": "📦 在庫管理 (入出庫)",
        "menu_clients": "🏢 取引先管理",
        "menu_products": "🏷️ マスター商品管理",
        "menu_timecard": "📅 タイムカード / カレンダー",
        "menu_system": "⚙️ システム管理",
        "menu_mypage": "👤 マイページ",
        
        # 共通ボタンおよびラベル
        "save": "保存",
        "cancel": "キャンセル",
        "edit": "修正",
        "delete": "削除",
        "search": "検索",
        "confirm": "確認",
        "status": "状態",
        "note": "備考",
        "date": "日付",
    }
}

def txt(key, **kwargs):
    """현재 세션 언어에 맞는 텍스트를 반환하는 다국어 함수"""
    lang = st.session_state.get("lang", "한국어")
    text_dict = I18N.get(lang, I18N["한국어"])
    raw = text_dict.get(key, I18N["한국어"].get(key, key))
    if isinstance(raw, str) and kwargs:
        return raw.format(**kwargs)
    return raw

def render_live_clock():
    """초 단위 실시간 디지털 시계 컴포넌트"""
    clock_html = """
    <div style="background-color: #1A202C; color: #63B3ED; padding: 8px 15px; border-radius: 8px; font-family: 'Courier New', Courier, monospace; font-size: 1.1rem; font-weight: bold; display: inline-block; border: 1px solid #2B6CB0; text-align: center;">
        <span id="live_clock_display">0000-00-00 00:00:00</span>
    </div>
    <script>
        function updateClock() {
            var now = new Date();
            var yyyy = now.getFullYear();
            var mm = String(now.getMonth() + 1).padStart(2, '0');
            var dd = String(now.getDate()).padStart(2, '0');
            var hh = String(now.getHours()).padStart(2, '0');
            var mi = String(now.getMinutes()).padStart(2, '0');
            var ss = String(now.getSeconds()).padStart(2, '0');
            var str = yyyy + '-' + mm + '-' + dd + ' ' + hh + ':' + mi + ':' + ss;
            document.getElementById('live_clock_display').textContent = str;
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """
    components.html(clock_html, height=50)
