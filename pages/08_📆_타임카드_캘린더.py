import streamlit as st

st.set_page_config(page_title="타임카드 캘린더", page_layout="wide")

import pandas as pd
from sidebar_menu import render_sidebar

render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("📅 휴가 신청 및 달력/공휴일 관리")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(
    ["🏖️ 휴가 신청", "📋 휴가 승인 관리 (관리자)", "🎌 회사 휴무일/공휴일 설정"]
)

with tab1:
    st.subheader("휴가(연차) 신청하기")
    with st.form("leave_request_form"):
        leave_type = st.selectbox("휴가 종류", ["연차", "반차", "경조사", "병가"])
        leave_date = st.date_input("휴가 예정일")
        reason = st.text_area("사유")
        submit_leave = st.form_submit_button("신청서 제출")

        if submit_leave:
            st.session_state.leave_records.append({
                "user_id": user["id"],
                "name": user["name"],
                "type": leave_type,
                "date": str(leave_date),
                "reason": reason,
                "status": "대기중",
            })
            st.success("휴가 신청이 완료되었습니다.")

    st.markdown("---")
    st.subheader("내 휴가 신청 이력")
    my_leaves = [
        l for l in st.session_state.leave_records if l["user_id"] == user["id"]
    ]
    if my_leaves:
        st.dataframe(pd.DataFrame(my_leaves), use_container_width=True)

with tab2:
    st.subheader("휴가 신청 승인 / 반려")
    if "관리자" not in user.get("role", ""):
        st.warning("관리자만 접근할 수 있습니다.")
    else:
        if not st.session_state.leave_records:
            st.info("신청된 휴가 내역이 없습니다.")
        else:
            for idx, l in enumerate(st.session_state.leave_records):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(
                        f"**[{l['status']}]** {l['name']} ({l['date']}) - {l['type']} : {l['reason']}"
                    )
                with col2:
                    if st.button("승인", key=f"app_{idx}"):
                        l["status"] = "승인"
                        st.rerun()
                with col3:
                    if st.button("반려", key=f"rej_{idx}"):
                        l["status"] = "반려"
                        st.rerun()

with tab3:
    st.subheader("회사 휴무일 등록")
    with st.form("holiday_form"):
        h_date = st.date_input("휴무일 날짜")
        h_name = st.text_input("휴무일 명칭 (예: 창립기념일)")
        if st.form_submit_button("휴무일 추가"):
            st.session_state.company_holidays.append(
                {"date": str(h_date), "name": h_name}
            )
            st.success("휴무일이 등록되었습니다.")

    st.write("📋 **등록된 휴무일 목록**")
    if st.session_state.company_holidays:
        st.dataframe(
            pd.DataFrame(st.session_state.company_holidays),
            use_container_width=True,
        )
