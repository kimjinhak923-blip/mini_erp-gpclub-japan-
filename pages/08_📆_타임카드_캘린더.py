import calendar
import datetime
import io
import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar

st.set_page_config(page_title="타임카드 및 캘린더", layout="wide")

render_sidebar()
user = st.session_state.get("logged_in_user")

st.title("📅 타임카드 관리 및 스케줄/사내 캘린더")
st.markdown("---")

# ==========================================
# 1. 세션 상태 초기화
# ==========================================
if "tc_year" not in st.session_state:
    st.session_state.tc_year = 2026
if "tc_month" not in st.session_state:
    st.session_state.tc_month = 8

if "user_vacation_info" not in st.session_state:
    st.session_state.user_vacation_info = {
        "관리자": {"granted": 15.0, "used": 2.0},
        "김사원": {"granted": 15.0, "used": 1.0},
        "이대리": {"granted": 15.0, "used": 0.0},
    }

if "schedule_requests" not in st.session_state:
    st.session_state.schedule_requests = [
        {
            "id": 1,
            "user_name": "김사원",
            "date": "2026-08-10",
            "type": "연차/휴가",
            "start_time": "-",
            "end_time": "-",
            "reason": "개인 사유 휴가",
            "status": "승인완료",
            "deducted": True,
        }
    ]

if "attendance_logs" not in st.session_state:
    st.session_state.attendance_logs = [
        {"user_name": "관리자", "date": "2026-08-03", "clock_in": "08:50", "clock_out": "18:30", "note": ""},
        {"user_name": "관리자", "date": "2026-08-04", "clock_in": "09:05", "clock_out": "18:00", "note": ""},
        {"user_name": "김사원", "date": "2026-08-03", "clock_in": "09:00", "clock_out": "18:00", "note": ""},
        {"user_name": "김사원", "date": "2026-08-05", "clock_in": "14:00", "clock_out": "15:30", "note": "외근"},
        {"user_name": "이대리", "date": "2026-08-04", "clock_in": "08:45", "clock_out": "19:15", "note": ""},
        {"user_name": "이대리", "date": "2026-08-12", "clock_in": "09:00", "clock_out": "18:00", "note": ""},
    ]

if "company_holidays" not in st.session_state:
    st.session_state.company_holidays = [
        {"date": "2026-08-14", "name": "회사 창립기념일 휴무", "type": "공휴일표기"},
        {"date": "2026-08-17", "name": "하계 특별 휴무", "type": "평일표기"},
    ]

if "company_schedules" not in st.session_state:
    st.session_state.company_schedules = [
        {"id": 1, "creator": "김사원", "date": "2026-08-05", "time": "14:00~15:30", "title": "A상사 외부 미팅", "category": "외부미팅"},
        {"id": 2, "creator": "이대리", "date": "2026-08-12", "time": "10:00~11:00", "title": "대회의실 신제품 회의", "category": "회의실사용"},
    ]

JAPAN_HOLIDAYS_2026 = {
    "2026-01-01": "신정 (元日)",
    "2026-01-12": "성인의 날 (成人の日)",
    "2026-02-11": "건국기념의 날 (建国記念の日)",
    "2026-02-23": "일왕 탄생일 (天皇誕生日)",
    "2026-03-20": "춘분의 날 (春分の日)",
    "2026-04-29": "쇼와의 날 (昭和の日)",
    "2026-05-03": "헌법기념일 (憲法記念日)",
    "2026-05-04": "녹색의 날 (みどもの日)",
    "2026-05-05": "어린이의 날 (こどもの日)",
    "2026-07-20": "바다의 날 (海の日)",
    "2026-08-11": "산의 날 (山の日)",
    "2026-09-21": "경로의 날 (敬老の日)",
    "2026-09-22": "국민의 휴일 (国民の休日)",
    "2026-09-23": "추분의 날 (秋分の日)",
    "2026-10-12": "체육의 날 (スポーツの日)",
    "2026-11-03": "문화의 날 (文化の日)",
    "2026-11-23": "근로감사의 날 (勤労感謝の日)",
}


# ==========================================
# 2. 사용자 권한 및 관리자 드롭다운 설정 (전체 동적 연동)
# ==========================================
logged_user_name = user["name"] if user else "관리자"
is_admin = (user.get("role") == "admin") if user else True

all_users = st.session_state.get("users", [])
if all_users:
    user_list = [u["name"] for u in all_users if isinstance(u, dict) and "name" in u]
else:
    user_list = ["관리자", "김사원", "이대리"]

for u_name in ["관리자", "김사원", "이대리"]:
    if u_name not in user_list:
        user_list.append(u_name)

if is_admin:
    col_adm1, col_adm2 = st.columns([2, 3])
    with col_adm1:
        selected_target_user = st.selectbox(
            "👤 [관리자] 조회 및 관리 대상 직원 선택", 
            user_list, 
            index=0,
            key="target_user_select"
        )
    with col_adm2:
        st.info(f"🔑 관리자 권한 로그인: 현재 **[{selected_target_user}]** 님의 근태/타임카드/일정을 관리 중입니다.")
else:
    selected_target_user = logged_user_name
    st.caption(f"👤 **[{selected_target_user}]** 님의 타임카드/개인 캘린더 화면입니다.")

if selected_target_user not in st.session_state.user_vacation_info:
    st.session_state.user_vacation_info[selected_target_user] = {"granted": 15.0, "used": 0.0}

v_info = st.session_state.user_vacation_info[selected_target_user]
rem_vacation = v_info["granted"] - v_info["used"]

st.markdown(
    f"💡 **[{selected_target_user}] 님의 연차 현황:** 부여 연차 `{v_info['granted']}일` | 사용 연차 `{v_info['used']}일` | **잔여 연차 `{rem_vacation}일`**"
)

year = st.session_state.tc_year
month = st.session_state.tc_month
weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]

_, last_day = calendar.monthrange(year, month)
start_date = datetime.date(year, month, 1)
end_date = datetime.date(year, month, last_day)

start_str = f"{start_date.strftime('%Y/%m/%d')}({weekdays_kr[start_date.weekday()]})"
end_str = f"{end_date.strftime('%Y/%m/%d')}({weekdays_kr[end_date.weekday()]})"
period_display = f"{start_str} ~ {end_str}"


# ==========================================
# 3. 타임카드 연산 로직 함수
# ==========================================
def calculate_daily_timecard(clock_in_str, clock_out_str):
    if not clock_in_str or not clock_out_str or clock_in_str == "-" or clock_out_str == "-":
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    fmt = "%H:%M"
    try:
        t_in = datetime.datetime.strptime(clock_in_str, fmt)
        t_out = datetime.datetime.strptime(clock_out_str, fmt)
        std_in = datetime.datetime.strptime("09:00", fmt)
        std_out = datetime.datetime.strptime("18:00", fmt)
    except ValueError:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    tardiness = round((t_in - std_in).total_seconds() / 3600.0, 2) if t_in > std_in else 0.0
    early_leave = round((std_out - t_out).total_seconds() / 3600.0, 2) if t_out < std_out else 0.0
    overtime = round((t_out - std_out).total_seconds() / 3600.0, 2) if t_out > std_out else 0.0
    break_time = 1.00
    work_time = max(0.00, round(8.00 - tardiness - early_leave, 2))
    total_labor = round(work_time + overtime, 2)

    return work_time, overtime, tardiness, early_leave, break_time, total_labor


# ==========================================
# 4. 월 선택 네비게이션
# ==========================================
col_nav1, col_nav2, col_nav3 = st.columns([1.2, 3, 1.2])

with col_nav1:
    if st.button("◀ 지난달", use_container_width=True):
        if month == 1:
            st.session_state.tc_year -= 1
            st.session_state.tc_month = 12
        else:
            st.session_state.tc_month -= 1
        st.rerun()

with col_nav2:
    st.markdown(
        f"<h3 style='text-align: center; margin:0;'>🗓️ {year}년 {month:02d}월</h3>"
        f"<p style='text-align: center; color: #555; font-weight: bold; margin-top: 4px;'>기간: {period_display}</p>",
        unsafe_allow_html=True,
    )

with col_nav3:
    if st.button("다음달 ▶", use_container_width=True):
        if month == 12:
            st.session_state.tc_year += 1
            st.session_state.tc_month = 1
        else:
            st.session_state.tc_month += 1
        st.rerun()

st.markdown("---")


# ==========================================
# 5. 상단 작업 버튼 (스케줄 신청 / 일정 등록 / 관리자 대리 근태 수정 / 엑셀)
# ==========================================
col_btn1, col_btn2, col_btn3 = st.columns([1.3, 1.3, 1.3])

with col_btn1:
    with st.popover("📝 스케줄 / 휴가 / 근태 등록 및 수정", use_container_width=True):
        st.subheader(f"📝 [{selected_target_user}] 근태 및 휴가 관리")
        
        if is_admin:
            tab_req_new, tab_admin_direct = st.tabs(["➕ 본인/신규 신청", "⚡ [관리자] 대리 휴가/근태 변경 및 수정"])
        else:
            tab_req_new = st.container()

        # 본인 신청
        with tab_req_new:
            with st.form("sched_form"):
                req_date = st.date_input("신청 날짜", datetime.date(year, month, 1))
                req_type = st.selectbox("신청 구분", ["연차/휴가", "반차", "출근시간 변경", "퇴근시간 변경", "휴일 근무", "결근", "공가"])
                
                c_t1, c_t2 = st.columns(2)
                with c_t1:
                    req_start = st.time_input("희망/변경 출근시간", datetime.time(9, 0))
                with c_t2:
                    req_end = st.time_input("희망/변경 퇴근시간", datetime.time(18, 0))
                    
                req_reason = st.text_area("신청/수정 사유", placeholder="사유를 입력해 주세요 (예: 당일 개인사정 휴가, 당일 외근 등)")

                if st.form_submit_button("신청 제출"):
                    new_id = max([r["id"] for r in st.session_state.schedule_requests], default=0) + 1
                    st.session_state.schedule_requests.append({
                        "id": new_id,
                        "user_name": selected_target_user,
                        "date": str(req_date),
                        "type": req_type,
                        "start_time": req_start.strftime("%H:%M") if "시간" in req_type else "-",
                        "end_time": req_end.strftime("%H:%M") if "시간" in req_type else "-",
                        "reason": req_reason,
                        "status": "승인대기",
                        "deducted": False,
                    })
                    st.success(f"[{selected_target_user}] 님의 근태/휴가 신청이 제출되었습니다.")
                    st.rerun()

        # [관리자 전용] 직원의 당일 급작스러운 결근/휴가/근태 직접 변경 기능
        if is_admin:
            with tab_admin_direct:
                st.caption("💡 당일 급작스러운 휴가/결근 등 직원이 직접 신청하지 못한 건을 관리자가 즉시 변경 처리합니다.")
                with st.form("admin_direct_edit_form"):
                    ad_date = st.date_input("대상 날짜 선택", datetime.date.today())
                    ad_type = st.selectbox("근태/휴가 항목", ["연차/휴가", "오전반차", "오후반차", "출/퇴근시간 직접입력", "결근 처리", "공가/조퇴"])
                    
                    c_ad1, c_ad2 = st.columns(2)
                    with c_ad1:
                        ad_start = st.text_input("출근시간 (HH:MM)", value="09:00")
                    with c_ad2:
                        ad_end = st.text_input("퇴근시간 (HH:MM)", value="18:00")

                    ad_reason = st.text_area("관리자 처리 사유", value="관리자 대리 입력 (개인사정 당일 휴가 처리 등)")

                    if st.form_submit_button("⚡ 즉시 변경 및 승인 적용", type="primary"):
                        date_str = str(ad_date)
                        
                        # 1. 스케줄 신청 내역에 자동 승인으로 등록
                        new_id = max([r["id"] for r in st.session_state.schedule_requests], default=0) + 1
                        deduct_flag = False
                        
                        if "연차" in ad_type or "휴가" in ad_type:
                            st.session_state.user_vacation_info[selected_target_user]["used"] += 1.0
                            deduct_flag = True
                        elif "반차" in ad_type:
                            st.session_state.user_vacation_info[selected_target_user]["used"] += 0.5
                            deduct_flag = True

                        st.session_state.schedule_requests.append({
                            "id": new_id,
                            "user_name": selected_target_user,
                            "date": date_str,
                            "type": ad_type,
                            "start_time": ad_start if "시간" in ad_type else "-",
                            "end_time": ad_end if "시간" in ad_type else "-",
                            "reason": ad_reason,
                            "status": "승인완료",
                            "deducted": deduct_flag,
                        })

                        # 2. 출퇴근 데이터에 반영
                        att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == selected_target_user), None)
                        if "시간" in ad_type:
                            in_val, out_val = ad_start, ad_end
                        else:
                            in_val, out_val = "-", "-"

                        if att:
                            att["clock_in"] = in_val
                            att["clock_out"] = out_val
                            att["note"] = ad_type
                        else:
                            st.session_state.attendance_logs.append({
                                "user_name": selected_target_user,
                                "date": date_str,
                                "clock_in": in_val,
                                "clock_out": out_val,
                                "note": ad_type
                            })

                        st.success(f"[{selected_target_user}] 님의 {date_str} 근태가 [{ad_type}] (으)로 즉시 변경 및 반영되었습니다.")
                        st.rerun()

# --- 사내 공유 일정 등록 / 수정 / 삭제 (Form 필드 정상 수정 완료) ---
with col_btn2:
    with st.popover("📌 사내 공유 일정 관리", use_container_width=True):
        st.subheader("📌 업무/미팅/회의실 일정 공유")
        
        tab_add, tab_edit = st.tabs(["➕ 일정 신규 등록", "✏️ 등록 일정 상세 수정/삭제"])
        
        with tab_add:
            with st.form("company_sched_form"):
                cs_date = st.date_input("일정 날짜", datetime.date(year, month, 1))
                cs_cat = st.selectbox("일정 카테고리", ["외부미팅", "회의실사용", "업무일정", "기타"])
                cs_time = st.text_input("시간 (예: 14:00~15:30)", value="10:00~11:00")
                cs_title = st.text_input("일정 내용/제목", placeholder="예: A상사 미팅 / 대회의실 사용")

                if st.form_submit_button("일정 공유 등록"):
                    cs_id = max([s["id"] for s in st.session_state.company_schedules], default=0) + 1
                    st.session_state.company_schedules.append({
                        "id": cs_id,
                        "creator": logged_user_name,
                        "date": str(cs_date),
                        "time": cs_time,
                        "title": cs_title,
                        "category": cs_cat
                    })
                    st.success("사내 공유 일정에 성공적으로 등록되었습니다.")
                    st.rerun()
                    
        with tab_edit:
            if not st.session_state.company_schedules:
                st.info("등록된 사내 공유 일정이 없습니다.")
            else:
                sched_options = {f"[{s['date']}] {s['creator']}: {s['title']}": s["id"] for s in st.session_state.company_schedules}
                selected_sched_label = st.selectbox("수정/삭제할 일정 선택", list(sched_options.keys()))
                target_sched_id = sched_options[selected_sched_label]
                target_sched = next(s for s in st.session_state.company_schedules if s["id"] == target_sched_id)

                if is_admin or target_sched["creator"] == logged_user_name:
                    # 일정, 내용, 시간 수정 Form 정상 배치
                    with st.form("edit_sched_detail_form"):
                        st.markdown("#### ✏️ 선택 일정 상세 수정")
                        e_date = st.date_input("일정 날짜 수정", datetime.datetime.strptime(target_sched["date"], "%Y-%m-%d").date())
                        e_cat = st.selectbox("카테고리 수정", ["외부미팅", "회의실사용", "업무일정", "기타"], index=["외부미팅", "회의실사용", "업무일정", "기타"].index(target_sched.get("category", "기타")))
                        e_time = st.text_input("시간 수정 (예: 10:00~12:00)", value=target_sched["time"])
                        e_title = st.text_input("일정 내용/제목 수정", value=target_sched["title"])

                        c_e1, c_e2 = st.columns(2)
                        with c_e1:
                            if st.form_submit_button("💾 수정사항 저장", type="primary"):
                                target_sched["date"] = str(e_date)
                                target_sched["category"] = e_cat
                                target_sched["time"] = e_time
                                target_sched["title"] = e_title
                                st.success("일정 정보가 정상적으로 수정되었습니다.")
                                st.rerun()
                        with c_e2:
                            if st.form_submit_button("🗑️ 해당 일정 삭제"):
                                st.session_state.company_schedules = [s for s in st.session_state.company_schedules if s["id"] != target_sched_id]
                                st.success("일정이 삭제되었습니다.")
                                st.rerun()
                else:
                    st.warning("⚠️ 해당 일정을 작성한 사용자 또는 관리자만 수정/삭제할 수 있습니다.")

daily_rows = []
tot_work, tot_ot, tot_tard, tot_early, tot_break, tot_sum = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

for d in range(1, last_day + 1):
    curr_date = datetime.date(year, month, d)
    date_str_full = curr_date.strftime("%Y-%m-%d")
    date_disp = f"{month}/{d}({weekdays_kr[curr_date.weekday()]})"

    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str_full and a.get("user_name") == selected_target_user), None)
    
    in_time = att["clock_in"] if att else "-"
    out_time = att["clock_out"] if att else "-"
    note_val = att.get("note", "") if att else ""

    w, ot, td, el, br, total = calculate_daily_timecard(in_time, out_time)

    req = next((r for r in st.session_state.schedule_requests if r["date"] == date_str_full and r["user_name"] == selected_target_user), None)
    req_status = f"[{req['type']}] {req['status']}" if req else "일반"

    tot_work += w
    tot_ot += ot
    tot_tard += td
    tot_early += el
    tot_break += br
    tot_sum += total

    daily_rows.append({
        "날짜": date_disp,
        "raw_date": date_str_full,
        "출근시간": in_time,
        "퇴근시간": out_time,
        "근무": f"{w:.2f}",
        "잔업": f"{ot:.2f}",
        "지각": f"{td:.2f}",
        "조퇴": f"{el:.2f}",
        "휴식": f"{br:.2f}",
        "노동합계": f"{total:.2f}",
        "신청": req_status,
        "비고/사유": note_val
    })

df_daily_display = pd.DataFrame(daily_rows)

with col_btn3:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        export_df = df_daily_display.drop(columns=["raw_date"])
        export_df.to_excel(writer, index=False, sheet_name=f"{month}월_타임카드_상세")
        summary_df = pd.DataFrame([{
            "직원명": selected_target_user,
            "조회기간": period_display,
            "총 근무시간": f"{tot_work:.2f}",
            "총 잔업시간": f"{tot_ot:.2f}",
            "총 지각시간": f"{tot_tard:.2f}",
            "총 조퇴시간": f"{tot_early:.2f}",
            "총 휴식시간": f"{tot_break:.2f}",
            "총 노동합계": f"{tot_sum:.2f}",
        }])
        summary_df.to_excel(writer, index=False, sheet_name="월별_시간집계")

    st.download_button(
        label=f"🖨️ [{selected_target_user}] 엑셀 출력 (.xlsx)",
        data=buffer.getvalue(),
        file_name=f"Timecard_{year}_{month:02d}_{selected_target_user}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 6. 관리자 전용 스케줄/휴가 승인 및 차감 처리
# ==========================================
if is_admin:
    pending_reqs = [r for r in st.session_state.schedule_requests if r["status"] == "승인대기"]
    if pending_reqs:
        with st.expander(f"⚠️ 승인 대기 중인 휴가/스케줄 신청 ({len(pending_reqs)}건)", expanded=True):
            for pr in pending_reqs:
                c1, c2, c3, c4 = st.columns([2, 3, 1, 1])
                c1.write(f"**{pr['user_name']}** ({pr['date']})")
                c2.write(f"구분: `{pr['type']}` | 사유: {pr['reason']}")
                if c3.button("✅ 승인", key=f"app_{pr['id']}"):
                    pr["status"] = "승인완료"
                    target_u = pr["user_name"]
                    if target_u not in st.session_state.user_vacation_info:
                        st.session_state.user_vacation_info[target_u] = {"granted": 15.0, "used": 0.0}
                    
                    if not pr.get("deducted", False):
                        if "연차" in pr["type"] or "휴가" in pr["type"]:
                            st.session_state.user_vacation_info[target_u]["used"] += 1.0
                            pr["deducted"] = True
                        elif "반차" in pr["type"]:
                            st.session_state.user_vacation_info[target_u]["used"] += 0.5
                            pr["deducted"] = True

                    st.success(f"[{pr['user_name']}] 님의 신청이 승인 처리되었습니다.")
                    st.rerun()

                if c4.button("❌ 반려", key=f"rej_{pr['id']}"):
                    pr["status"] = "반려"
                    st.warning(f"[{pr['user_name']}] 님의 신청이 반려되었습니다.")
                    st.rerun()


# ==========================================
# 7. 캘린더 모드 선택 (개인 캘린더 vs 사내 캘린더)
# ==========================================
st.markdown("---")
col_cal_hdr, col_cal_sel = st.columns([2, 1])
with col_cal_hdr:
    st.subheader(f"📅 [{selected_target_user}] 캘린더 관리")
with col_cal_sel:
    cal_mode = st.selectbox("캘린더 종류 선택", ["👤 개인 캘린더 (출퇴근/휴가)", "🏢 사내 캘린더 (전사 일정/공휴일)"])

if is_admin and cal_mode == "🏢 사내 캘린더 (전사 일정/공휴일)":
    with st.expander("🛠️ [관리자] 회사 재량 휴무일 추가 / 수정 / 삭제"):
        c_h1, c_h2, c_h3, c_h4 = st.columns([2, 2, 2, 1])
        with c_h1:
            ch_date = st.date_input("휴무일 날짜", datetime.date(year, month, 1))
        with c_h2:
            ch_name = st.text_input("휴무일 이름", value="회사 재량 휴무")
        with c_h3:
            ch_type = st.radio("표기 유형", ["공휴일표기", "평일표기"], horizontal=True)
        with c_h4:
            st.write(" ")
            st.write(" ")
            if st.button("휴무일 추가"):
                st.session_state.company_holidays.append({
                    "date": str(ch_date),
                    "name": ch_name,
                    "type": ch_type
                })
                st.success("재량 휴무일이 추가되었습니다.")
                st.rerun()

cal_obj = calendar.Calendar(firstweekday=6)
month_weeks = cal_obj.monthdayscalendar(year, month)

cols_hdr = st.columns(7)
day_headers = ["일", "월", "화", "수", "목", "금", "토"]
for idx, dh in enumerate(day_headers):
    color = "#e63946" if idx == 0 else ("#1d3557" if idx == 6 else "inherit")
    cols_hdr[idx].markdown(f"<h4 style='text-align: center; color: {color}; margin-bottom:4px; font-weight:bold;'>{dh}</h4>", unsafe_allow_html=True)

st.markdown("---")

for week in month_weeks:
    cols_w = st.columns(7)
    for idx, day_num in enumerate(week):
        with cols_w[idx]:
            if day_num == 0:
                st.markdown("<div style='background-color:rgba(200,200,200,0.1); height:125px; border-radius:6px; border:1px solid #444;'></div>", unsafe_allow_html=True)
            else:
                date_str = f"{year}-{month:02d}-{day_num:02d}"
                day_color = "#e63946" if idx == 0 else ("#2196f3" if idx == 6 else "#222222")

                jp_holiday = JAPAN_HOLIDAYS_2026.get(date_str)
                comp_holiday = next((h for h in st.session_state.company_holidays if h["date"] == date_str), None)
                
                if jp_holiday or (comp_holiday and comp_holiday["type"] == "공휴일표기"):
                    day_color = "#e63946"

                card_html = (
                    f"<div style='border:1px solid #ccc; border-radius:6px; padding:6px; height:125px; "
                    f"background-color:#ffffff; color:#111111; overflow-y:auto; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
                )
                card_html += f"<div style='font-weight:bold; font-size:14px; color:{day_color}; margin-bottom:3px;'>{month}/{day_num}</div>"

                if cal_mode == "👤 개인 캘린더 (출퇴근/휴가)":
                    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == selected_target_user), None)
                    req = next((r for r in st.session_state.schedule_requests if r["date"] == date_str and r["user_name"] == selected_target_user), None)

                    if att:
                        if att['clock_in'] != "-" or att['clock_out'] != "-":
                            card_html += f"<div style='font-size:11px; color:#1b5e20; font-weight:600; margin-top:2px;'>⏰ <b>출:</b> {att['clock_in']} / <b>퇴:</b> {att['clock_out']}</div>"
                        if att.get("note"):
                            card_html += f"<div style='font-size:10px; color:#c62828; font-weight:bold;'>📌 {att['note']}</div>"
                    if req:
                        bg_c = "#d4edda" if req["status"] == "승인완료" else "#fff3cd"
                        text_c = "#155724" if req["status"] == "승인완료" else "#856404"
                        card_html += (
                            f"<div style='font-size:11px; font-weight:600; background-color:{bg_c}; color:{text_c}; "
                            f"padding:2px 4px; border-radius:3px; margin-top:3px; border:1px solid {text_c};'>"
                            f"[{req['type']}] {req['status']}</div>"
                        )

                else:
                    if jp_holiday:
                        card_html += f"<div style='font-size:11px; color:#d90429; font-weight:bold; margin-top:2px;'>🇯🇵 {jp_holiday}</div>"
                    
                    if comp_holiday:
                        h_color = "#d90429" if comp_holiday["type"] == "공휴일표기" else "#4a5568"
                        card_html += f"<div style='font-size:11px; color:{h_color}; font-weight:bold; margin-top:2px;'>🏢 {comp_holiday['name']}</div>"

                    approved_vacs = [r for r in st.session_state.schedule_requests if r["date"] == date_str and r["status"] == "승인완료" and ("휴가" in r["type"] or "반차" in r["type"] or "결근" in r["type"])]
                    for av in approved_vacs:
                        card_html += (
                            f"<div style='font-size:11px; font-weight:bold; background-color:#d4edda; color:#155724; "
                            f"padding:2px 4px; border-radius:3px; margin-top:2px; border:1px solid #c3e6cb;'>"
                            f"🌴 {av['user_name']}({av['type']})</div>"
                        )

                    schedules = [s for s in st.session_state.company_schedules if s["date"] == date_str]
                    for sc in schedules:
                        card_html += (
                            f"<div style='font-size:11px; font-weight:bold; background-color:#e7f3ff; color:#004085; "
                            f"padding:2px 4px; border-radius:3px; margin-top:2px; border:1px solid #b8daff;'>"
                            f"📌 {sc['creator']}: {sc['title']} ({sc['time']})</div>"
                        )

                card_html += "</div>"
                st.markdown(card_html, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)


# ==========================================
# 8. 월별 데이터 시간집계
# ==========================================
st.subheader(f"📊 [{selected_target_user}] 님 월별 데이터 시간집계")

m1, m2, m3, m4 = st.columns(4)
m1.metric("근무 시간 (총합)", f"{tot_work:.2f} 시간")
m2.metric("잔업 시간 (18시 이후 1분단위)", f"{tot_ot:.2f} 시간")
m3.metric("지각 / 조퇴 (시간)", f"{tot_tard:.2f} / {tot_early:.2f}")
m4.metric("노동 합계 (근무+잔업)", f"{tot_sum:.2f} 시간")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 9. 일별 상세 타임카드 (직접 수정 및 비고/사유 기록)
# ==========================================
st.subheader(f"📋 [{selected_target_user}] 님 일별 상세 타임카드 ({month}월 1일 ~ {last_day}일)")

if is_admin:
    st.info("💡 **[관리자 기능]** 셀을 직접 수정(출/퇴근 시간, 비고/사유) 후 **[💾 수정사항 저장]**을 클릭하세요.")
    
    edited_df = st.data_editor(
        df_daily_display[["날짜", "출근시간", "퇴근시간", "근무", "잔업", "지각", "조퇴", "휴식", "노동합계", "신청", "비고/사유"]],
        disabled=["날짜", "근무", "잔업", "지각", "조퇴", "휴식", "노동합계", "신청"],
        column_config={
            "출근시간": st.column_config.TextColumn("출근시간 (HH:MM)", help="예: 09:00"),
            "퇴근시간": st.column_config.TextColumn("퇴근시간 (HH:MM)", help="예: 18:00"),
            "비고/사유": st.column_config.TextColumn("비고/사유 (결근, 사유 등)", help="사유 입력"),
        },
        use_container_width=True,
        height=380,
        key=f"admin_timecard_editor_{selected_target_user}_{month}"
    )

    col_save, col_del = st.columns([2, 3])
    with col_save:
        if st.button(f"💾 [{selected_target_user}] 타임카드 수정사항 저장", type="primary", use_container_width=True):
            for idx, row in edited_df.iterrows():
                raw_d = df_daily_display.loc[idx, "raw_date"]
                new_in = str(row["출근시간"]).strip()
                new_out = str(row["퇴근시간"]).strip()
                new_note = str(row["비고/사유"]).strip()

                att = next((a for a in st.session_state.attendance_logs if a["date"] == raw_d and a.get("user_name") == selected_target_user), None)
                
                if att:
                    att["clock_in"] = new_in
                    att["clock_out"] = new_out
                    att["note"] = new_note
                else:
                    if new_in != "-" or new_out != "-" or new_note != "":
                        st.session_state.attendance_logs.append({
                            "user_name": selected_target_user,
                            "date": raw_d,
                            "clock_in": new_in,
                            "clock_out": new_out,
                            "note": new_note
                        })

            st.success(f"[{selected_target_user}] 님의 타임카드 데이터가 성공적으로 저장되었습니다.")
            st.rerun()

    with col_del:
        with st.popover("🗑️ 출퇴근/근태 기록 삭제", use_container_width=True):
            st.write(f"**[{selected_target_user}] 님의 특정 날짜 근태 기록 삭제**")
            del_target_date = st.date_input("삭제할 날짜 선택", datetime.date(year, month, 1))
            if st.button("❌ 선택한 날짜 기록 삭제", type="primary"):
                del_str = str(del_target_date)
                st.session_state.attendance_logs = [
                    a for a in st.session_state.attendance_logs 
                    if not (a["date"] == del_str and a.get("user_name") == selected_target_user)
                ]
                st.success(f"[{selected_target_user}] 님의 {del_str} 근태 기록이 삭제되었습니다.")
                st.rerun()

else:
    st.dataframe(
        df_daily_display[["날짜", "출근시간", "퇴근시간", "근무", "잔업", "지각", "조퇴", "휴식", "노동합계", "신청", "비고/사유"]],
        use_container_width=True,
        height=400
    )
