import calendar
from datetime import datetime, time, timedelta

import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

# 1. 다국어 딕셔너리 정의 (한국어 / 일본어 / 영어)
TRANSLATIONS = {
    "KO": {
        "page_title": "타임카드 & 캘린더",
        "title": "⏰ 타임카드 & 근무 캘린더 관리",
        "tab1": "📅 월간 근무 캘린더",
        "tab2": "✍️ 출퇴근 기록 입력",
        "tab3": "📊 근무 이력 및 급여 정산",
        "tab4": "⚙️ 근무 및 수당 정책 설정",
        # Tab 1: Calendar
        "sub_calendar": "월별 근무 현황 캘린더",
        "sel_year": "연도 선택",
        "sel_month": "월 선택",
        "no_records_month": "해당 월에 등록된 근무 기록이 없습니다.",
        "metric_total_hours": "월 총 근무시간",
        "metric_total_pay": "월 총 예상 지급액",
        "metric_total_count": "월 총 근무 건수",
        # Tab 2: Entry
        "sub_entry": "신규 출퇴근 기록 작성",
        "label_date": "근무 일자",
        "label_emp": "직원명 / 담당자",
        "label_start": "출근 시간",
        "label_end": "퇴근 시간",
        "label_break": "휴게 시간 (시간 단위)",
        "label_wage": "기본 시급 (엔)",
        "label_memo": "비고 / 메모",
        "calc_std_hours": "기본 근무시간",
        "calc_over_hours": "연장 근무시간",
        "calc_night_hours": "야간 근무시간",
        "calc_total_pay": "최종 예상 일급 (수당 포함)",
        "btn_add_timecard": "⏰ 출퇴근 기록 저장",
        "msg_add_success": "출퇴근 기록이 성공적으로 등록되었습니다.",
        "msg_err_emp": "직원명을 입력해 주세요.",
        "msg_err_time": "퇴근 시간은 출근 시간보다 나중이어야 합니다.",
        # Tab 3: History & Settlement
        "sub_history": "전체 근무 이력 관리 및 급여 정산 요약",
        "sub_summary_emp": "👤 직원별 월간 급여 정산 요약",
        "col_emp": "직원명",
        "col_work_cnt": "근무일수",
        "col_sum_hours": "총 근무시간",
        "col_sum_pay": "총 지급예정액",
        "btn_save_changes": "💾 근무 기록 수정사항 저장",
        "msg_save_success": "근무 이력이 저장되었습니다.",
        "msg_no_timecards": "등록된 출퇴근 기록이 없습니다.",
        # Tab 4: Settings
        "sub_settings": "근무 수당 및 가산율 설정",
        "label_std_limit": "1일 기준 근무시간 (초과 시 연장수당)",
        "label_over_rate": "연장 근무 수당 가산율 (배)",
        "label_night_rate": "야간 근무 수당 가산율 (배)",
        "label_night_start": "야간 근무 시작 시간",
        "label_night_end": "야간 근무 종료 시간",
        "btn_save_settings": "⚙️ 설정 저장",
        "msg_settings_saved": "근무 정책 설정이 저장되었습니다.",
        # Units & Days
        "unit_hours": "시간",
        "unit_jpy": "엔",
        "unit_cnt": "건",
        "days_short": ["월", "화", "수", "목", "금", "토", "일"],
    },
    "JA": {
        "page_title": "タイムカード & カレンダー",
        "title": "⏰ タイムカード & 勤務カレンダー管理",
        "tab1": "📅 月間勤務カレンダー",
        "tab2": "✍️ 出退勤記録入力",
        "tab3": "📊 勤務履歴および給与精算",
        "tab4": "⚙️ 勤務および手当政策設定",
        "sub_calendar": "月別勤務状況カレンダー",
        "sel_year": "年を選択",
        "sel_month": "月を選択",
        "no_records_month": "該当月に登録された勤務記録がありません。",
        "metric_total_hours": "月間総勤務時間",
        "metric_total_pay": "月間総予想支給額",
        "metric_total_count": "月間総勤務件数",
        "sub_entry": "新規出退勤記録作成",
        "label_date": "勤務日付",
        "label_emp": "従業員名 / 担当者",
        "label_start": "出勤時間",
        "label_end": "退勤時間",
        "label_break": "休憩時間 (時間単位)",
        "label_wage": "基本時給 (円)",
        "label_memo": "備考 / メモ",
        "calc_std_hours": "基本勤務時間",
        "calc_over_hours": "残業時間",
        "calc_night_hours": "深夜勤務時間",
        "calc_total_pay": "最終予想日給 (手当含む)",
        "btn_add_timecard": "⏰ 出退勤記録を保存",
        "msg_add_success": "出退勤記録が正常に登録されました。",
        "msg_err_emp": "従業員名を入力してください。",
        "msg_err_time": "退勤時間は出勤時間より後でなければなりません。",
        "sub_history": "全勤務履歴管理および給与精算サマリー",
        "sub_summary_emp": "👤 従業員別月間給与精算サマリー",
        "col_emp": "従業員名",
        "col_work_cnt": "勤務日数",
        "col_sum_hours": "総勤務時間",
        "col_sum_pay": "総支給予定額",
        "btn_save_changes": "💾 勤務記録の変更事項を保存",
        "msg_save_success": "勤務履歴が保存されました。",
        "msg_no_timecards": "登録された出退勤記録がありません。",
        "sub_settings": "割増手当および加算率設定",
        "label_std_limit": "1日所定労働時間 (超過時残業手当)",
        "label_over_rate": "残業手当加算率 (倍)",
        "label_night_rate": "深夜手当加算率 (倍)",
        "label_night_start": "深夜勤務開始時間",
        "label_night_end": "深夜勤務終了時間",
        "btn_save_settings": "⚙️ 設定を保存",
        "msg_settings_saved": "勤務政策設定が保存されました。",
        "unit_hours": "時間",
        "unit_jpy": "円",
        "unit_cnt": "件",
        "days_short": ["月", "火", "水", "木", "金", "土", "日"],
    },
    "EN": {
        "page_title": "Timecard & Calendar",
        "title": "⏰ Timecard & Work Calendar Management",
        "tab1": "📅 Monthly Work Calendar",
        "tab2": "✍️ Log Attendance",
        "tab3": "📊 Work Logs & Payroll Summary",
        "tab4": "⚙️ Work Policy & Rates Settings",
        "sub_calendar": "Monthly Work Status Calendar",
        "sel_year": "Select Year",
        "sel_month": "Select Month",
        "no_records_month": "No work logs registered for this month.",
        "metric_total_hours": "Total Monthly Hours",
        "metric_total_pay": "Est. Total Monthly Pay",
        "metric_total_count": "Total Work Logs",
        "sub_entry": "New Attendance Log",
        "label_date": "Work Date",
        "label_emp": "Employee Name",
        "label_start": "Clock In",
        "label_end": "Clock Out",
        "label_break": "Break Time (Hours)",
        "label_wage": "Base Hourly Wage (JPY)",
        "label_memo": "Memo",
        "calc_std_hours": "Standard Hours",
        "calc_over_hours": "Overtime Hours",
        "calc_night_hours": "Night Shift Hours",
        "calc_total_pay": "Est. Daily Pay (Incl. Allowances)",
        "btn_add_timecard": "⏰ Save Attendance Log",
        "msg_add_success": "Attendance log saved successfully.",
        "msg_err_emp": "Please enter employee name.",
        "msg_err_time": "Clock out time must be later than clock in time.",
        "sub_history": "All Work Logs & Payroll Summary",
        "sub_summary_emp": "👤 Monthly Payroll Summary by Employee",
        "col_emp": "Employee Name",
        "col_work_cnt": "Work Days",
        "col_sum_hours": "Total Hours",
        "col_sum_pay": "Total Est. Pay",
        "btn_save_changes": "💾 Save Changes to Logs",
        "msg_save_success": "Work logs saved successfully.",
        "msg_no_timecards": "No attendance logs found.",
        "sub_settings": "Overtime & Night Rates Policy",
        "label_std_limit": "Standard Work Hours/Day",
        "label_over_rate": "Overtime Rate Multiplier",
        "label_night_rate": "Night Shift Rate Multiplier",
        "label_night_start": "Night Shift Start Time",
        "label_night_end": "Night Shift End Time",
        "btn_save_settings": "⚙️ Save Settings",
        "msg_settings_saved": "Work policy settings saved.",
        "unit_hours": "hrs",
        "unit_jpy": "JPY",
        "unit_cnt": "logs",
        "days_short": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
}

# 테이블 컬럼 매핑 (내부 DB 표준 key <-> 화면 표시 라벨)
COLUMN_MAPS = {
    "KO": {
        "date": "근무일자",
        "employee_name": "직원명",
        "start_time": "출근시간",
        "end_time": "퇴근시간",
        "break_hours": "휴게시간(h)",
        "work_hours": "총근무시간(h)",
        "std_hours": "기본근무(h)",
        "overtime_hours": "연장근무(h)",
        "night_hours": "야간근무(h)",
        "hourly_wage": "시급(엔)",
        "daily_pay": "총일급(엔)",
        "memo": "비고",
    },
    "JA": {
        "date": "勤務日付",
        "employee_name": "従業員名",
        "start_time": "出勤時間",
        "end_time": "退勤時間",
        "break_hours": "休憩時間(h)",
        "work_hours": "総勤務時間(h)",
        "std_hours": "基本勤務(h)",
        "overtime_hours": "残業時間(h)",
        "night_hours": "深夜勤務(h)",
        "hourly_wage": "時給(円)",
        "daily_pay": "総日給(円)",
        "memo": "備考",
    },
    "EN": {
        "date": "Date",
        "employee_name": "Employee Name",
        "start_time": "Clock In",
        "end_time": "Clock Out",
        "break_hours": "Break (h)",
        "work_hours": "Total Hours (h)",
        "std_hours": "Std Hours (h)",
        "overtime_hours": "Overtime (h)",
        "night_hours": "Night (h)",
        "hourly_wage": "Hourly Wage (JPY)",
        "daily_pay": "Total Daily Pay (JPY)",
        "memo": "Memo",
    },
}

# 2. 현재 선택된 언어 감지 ('lang' 또는 'language' 세션 키 호환 처리)
raw_lang = st.session_state.get("lang") or st.session_state.get("language") or "KO"
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
current_col_map = COLUMN_MAPS[current_lang]

# 3. Streamlit 페이지 설정 (최상단 고정)
st.set_page_config(page_title=t["page_title"], layout="wide")

# 4. 사이드바 렌더링
render_sidebar()

# 5. 세션 상태 초기화 (기존 100% 로직 변수 보존)
if "timecards" not in st.session_state:
    st.session_state.timecards = []
if "work_policy" not in st.session_state:
    st.session_state.work_policy = {
        "std_limit_hours": 8.0,
        "overtime_rate": 1.25,
        "night_rate": 1.25,
        "night_start": time(22, 0),
        "night_end": time(5, 0),
    }

# 6. 메인 타이틀
st.title(t["title"])
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([t["tab1"], t["tab2"], t["tab3"], t["tab4"]])

# --- [TAB 1] 월간 근무 캘린더 ---
with tab1:
    st.subheader(t["sub_calendar"])

    c1, c2 = st.columns(2)
    today = datetime.today()
    with c1:
        sel_year = st.selectbox(
            t["sel_year"], range(2024, 2031), index=(today.year - 2024)
        )
    with c2:
        sel_month = st.selectbox(
            t["sel_month"], range(1, 13), index=(today.month - 1)
        )

    # 월별 데이터 필터링
    monthly_logs = []
    for log in st.session_state.timecards:
        try:
            log_dt = datetime.strptime(str(log["date"]), "%Y-%m-%d")
            if log_dt.year == sel_year and log_dt.month == sel_month:
                monthly_logs.append(log)
        except (ValueError, TypeError):
            continue

    if monthly_logs:
        df_m = pd.DataFrame(monthly_logs)
        total_h = df_m["work_hours"].sum() if "work_hours" in df_m else 0.0
        total_p = df_m["daily_pay"].sum() if "daily_pay" in df_m else 0
        total_cnt = len(df_m)

        m1, m2, m3 = st.columns(3)
        m1.metric(
            t["metric_total_hours"], f"{total_h:,.1f} {t['unit_hours']}"
        )
        m2.metric(t["metric_total_pay"], f"¥{total_p:,.0f}")
        m3.metric(t["metric_total_count"], f"{total_cnt} {t['unit_cnt']}")
        st.markdown("---")

        # 캘린더 그리드 출력
        cal = calendar.monthcalendar(sel_year, sel_month)
        cols = st.columns(7)

        for i, day_name in enumerate(t["days_short"]):
            cols[i].markdown(f"**{day_name}**")

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write(" ")
                else:
                    date_str = f"{sel_year}-{sel_month:02d}-{day:02d}"
                    day_logs = [
                        l for l in monthly_logs if str(l["date"]) == date_str
                    ]

                    cell_html = f"**{day}**"
                    if day_logs:
                        for dl in day_logs:
                            cell_html += f"<br><small>👤 {dl.get('employee_name', '')}: {dl.get('work_hours', 0)}h (¥{dl.get('daily_pay', 0):,})</small>"

                    cols[i].markdown(cell_html, unsafe_allow_html=True)
    else:
        st.info(t["no_records_month"])

# --- [TAB 2] 출퇴근 기록 입력 및 수당 자동 연산 ---
with tab2:
    st.subheader(t["sub_entry"])

    with st.form("add_timecard_form"):
        fc1, fc2 = st.columns(2)

        with fc1:
            work_date = st.date_input(t["label_date"], value=today)
            emp_name = st.text_input(t["label_emp"], placeholder="예: 홍길동 / 山田太郎")
            start_t = st.time_input(t["label_start"], value=time(9, 0))
            end_t = st.time_input(t["label_end"], value=time(18, 0))

        with fc2:
            break_h = st.number_input(
                t["label_break"],
                min_value=0.0,
                max_value=12.0,
                value=1.0,
                step=0.5,
            )
            hourly_w = st.number_input(
                t["label_wage"], min_value=0, value=1200, step=50
            )
            memo_txt = st.text_input(t["label_memo"])

        # 야간 및 연장 근무 시간 연산 로직 (기존 정교한 시간 계산 유지)
        dt_start = datetime.combine(work_date, start_t)
        dt_end = datetime.combine(work_date, end_t)
        if dt_end <= dt_start:
            dt_end += timedelta(days=1)

        raw_diff_hours = (dt_end - dt_start).total_seconds() / 3600.0
        tot_work_h = max(0.0, round(raw_diff_hours - break_h, 2))

        policy = st.session_state.work_policy
        std_limit = policy["std_limit_hours"]
        std_h = min(tot_work_h, std_limit)
        over_h = max(0.0, tot_work_h - std_limit)

        # 야간 시간 계산 (22:00 ~ 05:00 구간 자동 감지)
        night_h = 0.0
        curr_t = dt_start
        step_min = 15
        while curr_t < dt_end:
            next_t = curr_t + timedelta(minutes=step_min)
            # 야간 구간 여부 검사
            if curr_t.hour >= 22 or curr_t.hour < 5:
                night_h += step_min / 60.0
            curr_t = next_t
        night_h = max(0.0, round(night_h, 2))

        # 급여 산출 수식 (기본 + 연장가산 + 야가가산)
        pay_std = std_h * hourly_w
        pay_over = over_h * hourly_w * policy["overtime_rate"]
        pay_night = night_h * hourly_w * (policy["night_rate"] - 1.0) # 야간 할증분
        calc_pay = int(round(pay_std + pay_over + pay_night))

        st.markdown("---")
        r1, r2, r3, r4 = st.columns(4)
        r1.info(f"{t['calc_std_hours']}: **{std_h} {t['unit_hours']}**")
        r2.warning(f"{t['calc_over_hours']}: **{over_h} {t['unit_hours']}**")
        r3.warning(f"{t['calc_night_hours']}: **{night_h} {t['unit_hours']}**")
        r4.success(f"{t['calc_total_pay']}: **¥{calc_pay:,.0f}**")

        if st.form_submit_button(t["btn_add_timecard"]):
            if not emp_name:
                st.error(t["msg_err_emp"])
            elif tot_work_h <= 0 and raw_diff_hours <= 0:
                st.error(t["msg_err_time"])
            else:
                st.session_state.timecards.append({
                    "date": work_date.strftime("%Y-%m-%d"),
                    "employee_name": emp_name,
                    "start_time": start_t.strftime("%H:%M"),
                    "end_time": end_t.strftime("%H:%M"),
                    "break_hours": break_h,
                    "work_hours": tot_work_h,
                    "std_hours": std_h,
                    "overtime_hours": over_h,
                    "night_hours": night_h,
                    "hourly_wage": hourly_w,
                    "daily_pay": calc_pay,
                    "memo": memo_txt,
                })
                st.success(t["msg_add_success"])
                st.rerun()

# --- [TAB 3] 근무 이력 및 급여 정산 요약 ---
with tab3:
    st.subheader(t["sub_history"])

    if st.session_state.timecards:
        df_tc = pd.DataFrame(st.session_state.timecards)

        # 직원별 집계 표 (기존 집계 기능 100% 보존)
        st.write(t["sub_summary_emp"])
        emp_summary = (
            df_tc.groupby("employee_name")
            .agg(
                work_days=("date", "count"),
                sum_hours=("work_hours", "sum"),
                sum_pay=("daily_pay", "sum"),
            )
            .reset_index()
        )
        emp_summary.columns = [
            t["col_emp"],
            t["col_work_cnt"],
            t["col_sum_hours"],
            t["col_sum_pay"],
        ]
        emp_summary[t["col_sum_hours"]] = emp_summary[
            t["col_sum_hours"]
        ].apply(lambda x: f"{x:,.1f} {t['unit_hours']}")
        emp_summary[t["col_sum_pay"]] = emp_summary[t["col_sum_pay"]].apply(
            lambda x: f"¥{x:,.0f}"
        )
        st.dataframe(emp_summary, use_container_width=True)

        st.markdown("---")

        # 데이터 편집 및 역매핑 저장
        df_tc_renamed = df_tc.rename(columns=current_col_map)
        edited_tc = st.data_editor(
            df_tc_renamed, num_rows="dynamic", use_container_width=True
        )

        if st.button(t["btn_save_changes"]):
            inv_map = {v: k for k, v in current_col_map.items()}
            st.session_state.timecards = edited_tc.rename(
                columns=inv_map
            ).to_dict("records")
            st.success(t["msg_save_success"])
            st.rerun()
    else:
        st.info(t["msg_no_timecards"])

# --- [TAB 4] 근무 및 수당 정책 설정 ---
with tab4:
    st.subheader(t["sub_settings"])

    p = st.session_state.work_policy
    with st.form("policy_form"):
        set_std_limit = st.number_input(
            t["label_std_limit"],
            min_value=1.0,
            max_value=12.0,
            value=float(p["std_limit_hours"]),
            step=0.5,
        )
        set_over_rate = st.number_input(
            t["label_over_rate"],
            min_value=1.0,
            max_value=3.0,
            value=float(p["overtime_rate"]),
            step=0.05,
        )
        set_night_rate = st.number_input(
            t["label_night_rate"],
            min_value=1.0,
            max_value=3.0,
            value=float(p["night_rate"]),
            step=0.05,
        )

        if st.form_submit_button(t["btn_save_settings"]):
            st.session_state.work_policy["std_limit_hours"] = set_std_limit
            st.session_state.work_policy["overtime_rate"] = set_over_rate
            st.session_state.work_policy["night_rate"] = set_night_rate
            st.success(t["msg_settings_saved"])
            st.rerun()
