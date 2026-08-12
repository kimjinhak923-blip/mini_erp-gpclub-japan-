import calendar
import datetime
import pytz
import pandas as pd
import streamlit as st

st.set_page_config(page_title="타임카드 & 캘린더", page_layout="wide")
st.markdown("<style>.main .block-container { max-width: 98% !important; }</style>", unsafe_allow_html=True)

if st.session_state.get("logged_in_user") is None:
    st.warning("로그인이 필요합니다.")
    st.stop()

user = st.session_state.logged_in_user
is_admin = user.get("role") == "관리자" or user["id"] == "admin"
is_visitor = user.get("role") == "방문자"

def get_tokyo_time():
    return datetime.datetime.now(pytz.timezone("Asia/Tokyo"))

st.header("📆 타임카드 (일본 기준 캘린더 & 일정 관리)")
tokyo_now = get_tokyo_time()

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("📝 휴가 / 일정 신청")
    with st.form("leave_request_form"):
        l_type = st.selectbox("신청 유형", ["연차", "반차", "병가", "경조사", "출장"])
        l_start = st.date_input("시작일")
        l_end = st.date_input("종료일")
        l_reason = st.text_area("사유")

        if st.form_submit_button("신청 제출", disabled=is_visitor):
            st.session_state.leave_records.append({
                "applicant": user["name"],
                "type": l_type,
                "start_date": str(l_start),
                "end_date": str(l_end),
                "reason": l_reason,
                "status": "승인 대기",
            })
            st.success("신청 완료!")
            st.rerun()

    st.subheader("📋 신청 및 결재 현황")
    if is_admin and st.session_state.leave_records:
        with st.expander("👑 [관리자] 휴가 승인/반려"):
            idx_l = st.selectbox("항목 선택", range(len(st.session_state.leave_records)))
            b_a, b_r = st.columns(2)
            if b_a.button("✅ 승인"):
                st.session_state.leave_records[idx_l]["status"] = "승인 완료"
                st.success("승인 처리되었습니다.")
                st.rerun()
            if b_r.button("❌ 반려"):
                st.session_state.leave_records[idx_l]["status"] = "반려"
                st.error("반려 처리되었습니다.")
                st.rerun()

    if st.session_state.leave_records:
        st.dataframe(pd.DataFrame(st.session_state.leave_records), use_container_width=True)

with c2:
    st.subheader("🇯🇵 일본 기준 월별 캘린더 & 휴무일 관리")

    if is_admin:
        with st.expander("👑 [관리자] 일본 공휴일/회사 휴무일 등록·수정·삭제"):
            tab_h1, tab_h2 = st.tabs(["➕ 휴무일 등록", "🛠️ 휴무일 수정/삭제"])

            with tab_h1:
                with st.form("add_holiday_form"):
                    hd_date = st.date_input("날짜")
                    hd_title = st.text_input("휴무일 명칭 (예: 夏休み)")
                    hd_type = st.selectbox("구분", ["일본 공휴일", "회사 휴무", "전체 월차"])

                    if st.form_submit_button("휴무일 추가"):
                        new_h_id = len(st.session_state.company_holidays) + 1
                        st.session_state.company_holidays.append({
                            "id": new_h_id,
                            "date": str(hd_date),
                            "title": hd_title,
                            "type": hd_type,
                        })
                        st.success("휴무일이 등록되었습니다.")
                        st.rerun()

            with tab_h2:
                if st.session_state.company_holidays:
                    h_options = [f"[{h['date']}] {h['title']}" for h in st.session_state.company_holidays]
                    sel_h_opt = st.selectbox("수정/삭제할 휴무일 선택", h_options)
                    sel_h_idx = h_options.index(sel_h_opt)
                    target_h = st.session_state.company_holidays[sel_h_idx]

                    e_h_title = st.text_input("휴무명 수정", value=target_h["title"])
                    e_h_type = st.selectbox("구분 수정", ["일본 공휴일", "회사 휴무", "전체 월차"], index=["일본 공휴일", "회사 휴무", "전체 월차"].index(target_h.get("type", "일본 공휴일")))

                    hb1, hb2 = st.columns(2)
                    if hb1.button("휴무일 저장"):
                        target_h["title"] = e_h_title
                        target_h["type"] = e_h_type
                        st.success("수정 완료")
                        st.rerun()

                    if hb2.button("❌ 휴무일 삭제"):
                        del st.session_state.company_holidays[sel_h_idx]
                        st.success("삭제 완료")
                        st.rerun()

    cy_col, cm_col = st.columns(2)
    sel_y = cy_col.number_input("연도", min_value=2020, max_value=2030, value=tokyo_now.year)
    sel_m = cm_col.number_input("월", min_value=1, max_value=12, value=tokyo_now.month)

    st.write(f"### 📅 {sel_y}年 {sel_m}月 Calendar")
    cal = calendar.monthcalendar(int(sel_y), int(sel_m))
    st.dataframe(pd.DataFrame(cal, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]), use_container_width=True)

    st.markdown("**📍 이 달의 일본 공휴일 및 회사 휴무:**")
    m_prefix = f"{sel_y}-{int(sel_m):02d}"

    for h in st.session_state.company_holidays:
        if h["date"].startswith(m_prefix):
            st.write(f"🔴 **[{h['date']}]** {h['title']} ({h['type']})")
