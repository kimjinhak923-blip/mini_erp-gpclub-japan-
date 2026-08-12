import streamlit as st

I18N = {
    "KO": {
        # 공통 & 인증
        "title": "ERP 시스템",
        "login": "로그인",
        "logout": "로그아웃",
        "email": "이메일 주소",
        "password": "비밀번호",
        "remember_me": "자동 로그인 유지",
        "login_btn": "로그인 하기",
        "login_success": "성공적으로 로그인되었습니다.",
        "login_error": "이메일 또는 비밀번호가 올바르지 않습니다.",
        "lang_select": "언어 선택 / Language",
        "welcome": "환영합니다",
        
        # 근태 및 인사 관리
        "hr_title": "근태 및 인사 관리",
        "today_clock": "오늘의 출퇴근 체크",
        "clock_in_time": "출근 시간",
        "clock_out_time": "퇴근 시간",
        "not_checked": "미체크",
        "clock_in_btn": "🚀 출근하기",
        "clock_out_btn": "🚪 퇴근하기",
        "clock_in_success": "출근 처리되었습니다.",
        "clock_out_success": "퇴근 처리되었습니다.",
        "current_status": "현재 상태",
        "not_clocked_in": "미출근",
        "today_date": "오늘 날짜",
        "my_calendar": "나의 월별 근태 캘린더",
        "no_logs": "이번 달 근태 기록이 없습니다.",
        
        # 테이블 컬럼
        "col_date": "날짜",
        "col_clock_in": "출근시간",
        "col_clock_out": "퇴근시간",
        "col_status": "상태",
        "col_emp_code": "사번",
        "col_name": "이름",
        "col_dept": "부서",
        "col_position": "직급",
        "col_email": "이메일",
        "col_role": "권한",
        "col_active": "활성화",
        
        # 관리자 메뉴
        "admin_menu": "관리자 전용 인사 관리 메뉴",
        "tab_all_attendance": "📊 전체 직원 근태 관리 (수정/삭제)",
        "tab_create_account": "👤 직원 계정 생성 및 배포",
        "select_log_edit": "수정/삭제할 기록 선택 (ID)",
        "save_edit": "수정 저장",
        "delete_btn": "삭제하기",
        "edit_success": "근태 기록이 수정되었습니다.",
        "delete_success": "기록이 삭제되었습니다.",
        "create_emp_header": "➕ 신규 직원 등록 (로그인 계정 발급)",
        "emp_code_placeholder": "사번 (예: EMP-0002)",
        "emp_name_label": "직원 이름",
        "dept_label": "부서명",
        "pos_label": "직급",
        "login_email_label": "로그인용 이메일",
        "role_label": "권한 구분",
        "create_emp_btn": "직원 계정 생성하기",
        "required_fields_error": "사번, 이름, 이메일은 필수 입력 항목입니다.",
        "account_created_success": "계정이 생성되었습니다! 로그인 이메일:",
        "account_created_error": "계정 생성 실패:",
        "all_emp_list": "📋 등록된 전체 직원 목록",
        "admin_only_info": "🔒 관리자 권한(ADMIN)으로 로그인하시면 전체 직원 근태 관리 및 신규 계정 생성 메뉴가 활성화됩니다."
    },
    "JA": {
        # 共通 & 認証
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
        "welcome": "ようこそ",
        
        # 勤怠・人事管理
        "hr_title": "勤怠・人事管理",
        "today_clock": "本日の出退社チェック",
        "clock_in_time": "出勤時間",
        "clock_out_time": "退勤時間",
        "not_checked": "未チェック",
        "clock_in_btn": "🚀 出勤する",
        "clock_out_btn": "🚪 退勤する",
        "clock_in_success": "出勤処理が完了しました。",
        "clock_out_success": "退勤処理が完了しました。",
        "current_status": "現在のステータス",
        "not_clocked_in": "未出勤",
        "today_date": "本日の日付",
        "my_calendar": "マイ月間勤怠カレンダー",
        "no_logs": "今月の勤怠記録がありません。",
        
        # テーブルカラム
        "col_date": "日付",
        "col_clock_in": "出勤時間",
        "col_clock_out": "退勤時間",
        "col_status": "ステータス",
        "col_emp_code": "社員番号",
        "col_name": "氏名",
        "col_dept": "部署",
        "col_position": "役職",
        "col_email": "メールアドレス",
        "col_role": "権限",
        "col_active": "有効",
        
        # 管理者メニュー
        "admin_menu": "管理者専用人事メニュー",
        "tab_all_attendance": "📊 全社員勤怠管理 (修正/削除)",
        "tab_create_account": "👤 社員アカウント作成・発行",
        "select_log_edit": "修正/削除する記録を選択 (ID)",
        "save_edit": "変更を保存",
        "delete_btn": "削除する",
        "edit_success": "勤怠記録が修正されました。",
        "delete_success": "記録が削除されました。",
        "create_emp_header": "➕ 新規社員登録 (ログインアカウント発行)",
        "emp_code_placeholder": "社員番号 (例: EMP-0002)",
        "emp_name_label": "社員氏名",
        "dept_label": "部署名",
        "pos_label": "役職",
        "login_email_label": "ログイン用メールアドレス",
        "role_label": "権限区分",
        "create_emp_btn": "アカウントを作成する",
        "required_fields_error": "社員番号、氏名、メールアドレスは必須項目です。",
        "account_created_success": "アカウントが作成されました！ ログイン用メールアドレス:",
        "account_created_error": "アカウント作成失敗:",
        "all_emp_list": "📋 登録済み全社員一覧",
        "admin_only_info": "🔒 管理者権限(ADMIN)でログインすると全社員勤怠管理および新規アカウント作成メニューが有効化されます。"
    },
    "EN": {
        # Common & Auth
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
        "welcome": "Welcome",
        
        # HR Management
        "hr_title": "HR & Attendance Management",
        "today_clock": "Today's Attendance Check",
        "clock_in_time": "Clock-in Time",
        "clock_out_time": "Clock-out Time",
        "not_checked": "Not Checked",
        "clock_in_btn": "🚀 Clock In",
        "clock_out_btn": "🚪 Clock Out",
        "clock_in_success": "Clock-in recorded.",
        "clock_out_success": "Clock-out recorded.",
        "current_status": "Current Status",
        "not_clocked_in": "Not Clocked In",
        "today_date": "Today's Date",
        "my_calendar": "My Monthly Attendance Calendar",
        "no_logs": "No attendance records found for this month.",
        
        # Table Columns
        "col_date": "Date",
        "col_clock_in": "Clock In",
        "col_clock_out": "Clock Out",
        "col_status": "Status",
        "col_emp_code": "Emp Code",
        "col_name": "Name",
        "col_dept": "Department",
        "col_position": "Position",
        "col_email": "Email",
        "col_role": "Role",
        "col_active": "Active",
        
        # Admin Menu
        "admin_menu": "Admin HR Management Menu",
        "tab_all_attendance": "📊 All Attendance Logs (Edit/Delete)",
        "tab_create_account": "👤 Create & Issue Employee Account",
        "select_log_edit": "Select Log to Edit/Delete (ID)",
        "save_edit": "Save Changes",
        "delete_btn": "Delete",
        "edit_success": "Attendance record updated successfully.",
        "delete_success": "Record deleted successfully.",
        "create_emp_header": "➕ Register New Employee (Issue Login Account)",
        "emp_code_placeholder": "Emp Code (e.g. EMP-0002)",
        "emp_name_label": "Employee Name",
        "dept_label": "Department",
        "pos_label": "Position",
        "login_email_label": "Login Email",
        "role_label": "Role Type",
        "create_emp_btn": "Create Employee Account",
        "required_fields_error": "Emp code, Name, and Email are required fields.",
        "account_created_success": "Account created! Login email:",
        "account_created_error": "Failed to create account:",
        "all_emp_list": "📋 All Registered Employee List",
        "admin_only_info": "🔒 Log in with ADMIN role to access all employee logs and account creation tools."
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
