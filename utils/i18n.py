import streamlit as st

I18N = {
    "KO": {
        "title": "ERP 시스템",
        "login": "로그인",
        "logout": "로그아웃",
        "email": "이메일 주소",
        "password": "비밀번호",
        "remember_me": "자동 로그인 유지",
        "login_btn": "로그인 하기",
        "lang_select": "언어 선택 / Language",
        
        # 권한
        "role_admin": "관리자 (전체 권한)",
        "role_employee": "일반사원 (등록/수정)",
        "role_visitor": "방문자 (조회 전용)",
        
        # 근태 및 휴가
        "hr_title": "인사 / 근태 및 휴가 관리",
        "today_clock": "오늘의 출퇴근 체크",
        "clock_in": "출근 시간",
        "clock_out": "퇴근 시간",
        "clock_in_btn": "🚀 출근하기",
        "clock_out_btn": "🚪 퇴근하기",
        "not_checked": "미체크",
        "vacation_info": "나의 연차 현황",
        "total_vacation": "부여 연차",
        "used_vacation": "사용 연차",
        "remain_vacation": "잔여 연차",
        "apply_leave": "🌴 휴가 신청하기",
        "leave_history": "휴가 신청 내역 및 승인 상태",
        
        # 대시보드
        "dashboard_title": "📊 ERP 메인 대시보드",
        "monthly_summary": "월별 매출 개요",
        "select_month": "조회 월 선택",
        "total_sales": "총 매출액",
        "offline_sales": "오프라인 (납품) 매출",
        "online_sales": "온라인 (EC) 매출",
        "sales_trend": "월별 매출 추이 그래프",
        "detail_search": "🔍 매출 상세 조회 (기간별/일별)",
        "period_select": "조회 기간 선택 (최대 1년)",
        "daily_breakdown": "일별 매출 상세 내역 (납품일 기준)"
    },
    "JA": {
        "title": "ERP システム",
        "login": "ログイン",
        "logout": "ログアウト",
        "email": "メールアドレス",
        "password": "パスワード",
        "remember_me": "自動ログインを維持する",
        "login_btn": "ログイン",
        "lang_select": "言語選択 / Language",
        
        "role_admin": "管理者 (全権限)",
        "role_employee": "一般社員 (登録/修正)",
        "role_visitor": "訪問者 (照会のみ)",
        
        "hr_title": "人事 / 勤怠・休暇管理",
        "today_clock": "本日の出退社チェック",
        "clock_in": "出勤時間",
        "clock_out": "退勤時間",
        "clock_in_btn": "🚀 出勤する",
        "clock_out_btn": "🚪 退勤する",
        "not_checked": "未チェック",
        "vacation_info": "マイ有給休暇状況",
        "total_vacation": "付与日数",
        "used_vacation": "消化日数",
        "remain_vacation": "残日数",
        "apply_leave": "🌴 休暇申請",
        "leave_history": "休暇申請履歴・承認状況",
        
        "dashboard_title": "📊 ERP メインダッシュボード",
        "monthly_summary": "月間売上概要",
        "select_month": "照会月選択",
        "total_sales": "総売上高",
        "offline_sales": "オフライン (納品) 売上",
        "online_sales": "オンライン (EC) 売上",
        "sales_trend": "月間売上推移グラフ",
        "detail_search": "🔍 売上詳細照会 (期間別/日別)",
        "period_select": "照会期間選択 (最大1年)",
        "daily_breakdown": "日別売上詳細 (納品日基準)"
    },
    "EN": {
        "title": "ERP System",
        "login": "Login",
        "logout": "Logout",
        "email": "Email Address",
        "password": "Password",
        "remember_me": "Keep me logged in",
        "login_btn": "Log In",
        "lang_select": "Language",
        
        "role_admin": "Admin (Full Access)",
        "role_employee": "Employee (Create/Edit)",
        "role_visitor": "Visitor (Read Only)",
        
        "hr_title": "HR / Attendance & Leave",
        "today_clock": "Today's Attendance",
        "clock_in": "Clock In",
        "clock_out": "Clock Out",
        "clock_in_btn": "🚀 Clock In",
        "clock_out_btn": "🚪 Clock Out",
        "not_checked": "Not Checked",
        "vacation_info": "My Vacation Balance",
        "total_vacation": "Total Allocated",
        "used_vacation": "Used Days",
        "remain_vacation": "Remaining Days",
        "apply_leave": "🌴 Request Leave",
        "leave_history": "Leave Request History",
        
        "dashboard_title": "📊 ERP Main Dashboard",
        "monthly_summary": "Monthly Sales Summary",
        "select_month": "Select Month",
        "total_sales": "Total Sales",
        "offline_sales": "Offline Sales",
        "online_sales": "Online (EC) Sales",
        "sales_trend": "Sales Trend Graph",
        "detail_search": "🔍 Detailed Analytics (Period/Daily)",
        "period_select": "Select Date Range (Max 1 Year)",
        "daily_breakdown": "Daily Breakdown (By Delivery Date)"
    }
}

def get_lang():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "KO"
    return st.session_state["lang"]

def t(key):
    lang = get_lang()
    return I18N.get(lang, {}).get(key, I18N["KO"].get(key, key))

def render_lang_selector():
    lang_options = {"한국어": "KO", "日本語": "JA", "English": "EN"}
    current_lang = get_lang()
    current_label = [k for k, v in lang_options.items() if v == current_lang][0]
    
    selected = st.sidebar.selectbox(
        t("lang_select"),
        options=list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_label)
    )
    if lang_options[selected] != current_lang:
        st.session_state["lang"] = lang_options[selected]
        st.rerun()
