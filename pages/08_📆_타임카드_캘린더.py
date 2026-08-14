import calendar
import datetime
import io
import pandas as pd
import streamlit as st

# 사이드바 예외 처리
try:
    from sidebar_menu import render_sidebar
    render_sidebar()
except Exception:
    pass

st.set_page_config(page_title="타임카드 및 캘린더", layout="wide")
st.title("📅 타임카드 관리 및 스케줄/사내 캘린더")
st.markdown("---")

# ==========================================
# 1. 세션 상태 초기화
# ==========================================
if "tc_year" not in st.session_state:
    st.session_state.tc_year = 2026
if "tc_month" not in st.session_state:
    st.session_state.tc_month = 8

if "users" not in st.session_state:
    st.session_state.users = [
        {"name": "관리자", "role": "admin"},
        {"name": "김사원", "role": "user"},
        {"name": "이대리", "role": "user"},
    ]

# 관리자 선택 상태를 보장하기 위한 세션 키
if "selected_target_user" not in st.session_state:
    st.session_state.selected_target_user = "관리자"

user = st.session_state.get("logged_in_user", {"name": "관리자", "role": "admin"})
is_admin = (user.get("role") == "admin")

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
        {"user_name": "김사원", "date": "2026-08-03", "clock_in": "09:00", "clock_out": "18:00", "note": ""},
        {"user_name": "김사원", "date": "2026-08-05", "clock_in": "14:00", "clock_out": "15:30", "note": "외근"},
        {"user_name": "이대리", "date": "2026-08-04", "clock_in": "08:45", "clock_out": "19:15", "note": ""},
    ]

if "company_schedules" not in st.session_state:
    st.session_state.company_schedules = [
        {"id": 1, "creator": "김사원", "date": "2026-08-05", "time": "14:00~15:30", "title": "A상사 외부 미팅", "category": "외부미팅"},
        {"id": 2, "creator": "이대리", "date": "2026-08-12", "time": "10:00~11:00", "title": "대회의실 신제품 회의", "category": "회의실사용"},
    ]

# ==========================================
# 2. 관리자 직원 선택 드롭다운 (상태 동기화 수정)
# ==========================================
user_list = [u["name"] for u in st.session_state.users]

def on_user_change():
    st.session_state.selected_target_user = st.session_state.sel_user_key

if is_admin:
    col_adm1, col_adm2 = st.columns([2, 3])
    with col_adm1:
        current_idx = user_list.index(st.session_state.selected_target_user) if st.session_state.selected_target_user in user_list else 0
        selected_target_user = st.selectbox(
            "👤 [관리자] 조회 및 관리 대상 직원 선택", 
            user_list, 
            index=current_idx,
            key="sel_user_key",
            on_change=on_user_change
        )
    with col_adm2:
        st.info(f"🔑 관리자 권한: 현재 **[{st.session_state.selected_target_user}]** 님의 근태 및 타임카드를 관리 중입니다.")
else:
    st.session_state.selected_target_user = user["name"]

target_user = st.session_state.selected_target_user

if target_user not in st.session_state.user_vacation_info:
    st.session_state.user_vacation_info[target_user] = {"granted": 15.0, "used": 0.0}

v_info = st.session_state.user_vacation_info[target_user]
rem_vacation = v_info["granted"] - v_info["used"]

st.markdown(
    f"💡 **[{target_user}] 님의 연차 현황:** 부여 `{v_info['granted']}일` | 사용 `{v_info['used']}일` | **잔여 `{rem_vacation}일`**"
)

year = st.session_state.tc_year
month = st.session_state.tc_month
weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
_, last_day = calendar.monthrange(year, month)

# ==========================================
# 3. 관리자 대리 수정 & 사내공유일정 수정/삭제 (팝업 UI)
# ==========================================
col_b1, col_b2 = st.columns([1.5, 1.5])

with col_b1:
    with st.popover(f"⚡ [{target_user}] 근태/휴가 즉시 수정 및 대리 등록", use_container_width=True):
        st.subheader(f"🛠️ [{target_user}] 근태/휴가 관리자 수정")
        st.caption("당일 개인사정 휴가/결근 등 직원이 직접 신청하지 못한 경우 관리자가 즉시 처리합니다.")
        
        with st.form("admin_direct_fix_form"):
            fix_date = st.date_input("대상 날짜", datetime.date.today())
            fix_type = st.selectbox("항목 선택", ["연차/휴가", "오전반차", "오후반차", "출/퇴근시간 직접수정", "결근 처리", "공가/조퇴"])
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                fix_in = st.text_input("출근시간 (HH:MM)", value="09:00")
            with c_f2:
                fix_out = st.text_input("퇴근시간 (HH:MM)", value="18:00")
                
            fix_reason = st.text_area("수정/대리 입력 사유", value="관리자 대리 수정 (개인 사정 당일 휴가 등)")

            if st.form_submit_button("⚡ 즉시 변경 반영", type="primary"):
                f_date_str = str(fix_date)
                
                # 연차 차감 로직
                if "연차" in fix_type or "휴가" in fix_type:
                    st.session_state.user_vacation_info[target_user]["used"] += 1.0
                elif "반차" in fix_type:
                    st.session_state.user_vacation_info[target_user]["used"] += 0.5

                # 출퇴근 데이터 수정/추가
                att = next((a for a in st.session_state.attendance_logs if a["date"] == f_date_str and a.get("user_name") == target_user), None)
                in_val = fix_in if "시간" in fix_type else "-"
                out_val = fix_out if "시간" in fix_type else "-"

                if att:
                    att["clock_in"] = in_val
                    att["clock_out"] = out_val
                    att["note"] = f"{fix_type} ({fix_reason})"
                else:
                    st.session_state.attendance_logs.append({
                        "user_name": target_user,
                        "date": f_date_str,
                        "clock_in": in_val,
                        "clock_out": out_val,
                        "note": f"{fix_type} ({fix_reason})"
                    })

                st.success(f"[{target_user}] 님의 {f_date_str} 근태가 정상 수정되었습니다.")
                st.rerun()

with col_b2:
    with st.popover("📌 사내 공유 일정 수정 / 삭제 / 등록", use_container_width=True):
        st.subheader("📌 사내 공유 일정 관리")
        tab_c1, tab_c2 = st.tabs(["✏️ 일정 상세 수정 / 삭제", "➕ 신규 일정 등록"])

        with tab_c1:
            if not st.session_state.company_schedules:
                st.info("등록된 사내 공유 일정이 없습니다.")
            else:
                sched_map = {f"[{s['date']}] {s['creator']}: {s['title']}": s["id"] for s in st.session_state.company_schedules}
                sel_label = st.selectbox("수정/삭제할 일정 선택", list(sched_map.keys()))
                target_id = sched_map[sel_label]
                target_item = next(s for s in st.session_state.company_schedules if s["id"] == target_id)

                # 날짜 변환 에러 안전 처리
                try:
                    init_date = datetime.datetime.strptime(target_item["date"], "%Y-%m-%d").date()
                except Exception:
                    init_date = datetime.date.today()

                # 날짜, 카테고리, 시간, 내용 수정 Form
                with st.form("edit_cs_form"):
                    st.markdown("**👇 아래 항목을 수정 후 [💾 수정사항 저장]을 누르세요.**")
                    e_date = st.date_input("일정 날짜 수정", init_date)
                    e_cat = st.selectbox("카테고리 수정", ["외부미팅", "회의실사용", "업무일정", "기타"])
                    e_time = st.text_input("시간 수정 (예: 10:00~12:00)", value=target_item["time"])
                    e_title = st.text_input("일정 내용 / 제목 수정", value=target_item["title"])

                    col_save, col_del = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 수정사항 저장", type="primary"):
                            target_item["date"] = str(e_date)
                            target_item["category"] = e_cat
                            target_item["time"] = e_time
                            target_item["title"] = e_title
                            st.success("일정이 정상적으로 수정되었습니다.")
                            st.rerun()
                    with col_del:
                        if st.form_submit_button("🗑️ 해당 일정 삭제"):
                            st.session_state.company_schedules = [s for s in st.session_state.company_schedules if s["id"] != target_id]
                            st.success("일정이 삭제되었습니다.")
                            st.rerun()

        with tab_c2:
            with st.form("add_cs_form"):
                n_date = st.date_input("날짜", datetime.date.today())
                n_cat = st.selectbox("구분", ["외부미팅", "회의실사용", "업무일정", "기타"])
                n_time = st.text_input("시간", "14:00~15:00")
                n_title = st.text_input("제목")
                if st.form_submit_button("등록"):
                    new_id = max([s["id"] for s in st.session_state.company_schedules], default=0) + 1
                    st.session_state.company_schedules.append({
                        "id": new_id, "creator": user["name"], "date": str(n_date),
                        "time": n_time, "title": n_title, "category": n_cat
                    })
                    st.success("새 일정이 등록되었습니다.")
                    st.rerun()

# ==========================================
# 4. 일별 타임카드 데이터 매핑 및 테이블 수정
# ==========================================
st.markdown("---")
st.subheader(f"📋 [{target_user}] 님 타임카드 상세 (수정 및 삭제)")

daily_rows = []
for d in range(1, last_day + 1):
    curr_date = datetime.date(year, month, d)
    date_str = curr_date.strftime("%Y-%m-%d")
    date_disp = f"{month}/{d}({weekdays_kr[curr_date.weekday()]})"

    att = next((a for a in st.session_state.attendance_logs if a["date"] == date_str and a.get("user_name") == target_user), None)
    
    in_time = att["clock_in"] if att else "-"
    out_time = att["clock_out"] if att else "-"
    note_val = att.get("note", "") if att else ""

    daily_rows.append({
        "raw_date": date_str,
        "날짜": date_disp,
        "출근시간": in_time,
        "퇴근시간": out_time,
        "비고/사유": note_val
    })

df_daily = pd.DataFrame(daily_rows)

if is_admin:
    st.caption("💡 출/퇴근시간 및 비고/사유 수정 후 아래 **[💾 수정사항 저장]** 버튼을 누르세요.")
    
    # data_editor 수정 버그 방지를 위해 key 동적 생성
    edited_df = st.data_editor(
        df_daily[["날짜", "출근시간", "퇴근시간", "비고/사유"]],
        use_container_width=True,
        height=350,
        key=f"editor_{target_user}_{year}_{month}"
    )

    if st.button(f"💾 [{target_user}] 타임카드 수정사항 저장", type="primary"):
        for idx, row in edited_df.iterrows():
            raw_d = df_daily.loc[idx, "raw_date"]
            new_in = str(row["출근시간"]).strip()
            new_out = str(row["퇴근시간"]).strip()
            new_note = str(row["비고/사유"]).strip()

            att = next((a for a in st.session_state.attendance_logs if a["date"] == raw_d and a.get("user_name") == target_user), None)
            if att:
                att["clock_in"] = new_in
                att["clock_out"] = new_out
                att["note"] = new_note
            else:
                if new_in != "-" or new_out != "-" or new_note != "":
                    st.session_state.attendance_logs.append({
                        "user_name": target_user,
                        "date": raw_d,
                        "clock_in": new_in,
                        "clock_out": new_out,
                        "note": new_note
                    })
        st.success(f"[{target_user}] 님의 근태 데이터가 정상적으로 저장되었습니다!")
        st.rerun()
else:
    st.dataframe(df_daily[["날짜", "출근시간", "퇴근시간", "비고/사유"]], use_container_width=True)
