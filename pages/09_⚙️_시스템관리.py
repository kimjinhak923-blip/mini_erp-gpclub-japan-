import pandas as pd
import streamlit as st
from sidebar_menu import render_sidebar
from utils.i18n import txt

st.set_page_config(page_title="시스템관리", layout="wide")
render_sidebar()

user = st.session_state.get("logged_in_user")

st.title("⚙️ 시스템 및 사용자 관리")
st.markdown("---")

# 세션 내 연차 신청 내역 초기화 (테스트용/기존데이터 없을 경우)
if "vacation_requests" not in st.session_state:
    st.session_state.vacation_requests = []

if not user or "관리자" not in user.get("role", ""):
    st.error("관리자(CEO)만 접근할 수 있는 메뉴입니다.")
else:
    # 탭 구성: 사용자 관리 / 연차 승인 관리 / 공통 코드
    tab1, tab2, tab3 = st.tabs(
        [
            "👤 사용자 승인 및 권한 관리",
            "🌴 연차 신청 승인 관리",
            "🏢 공통 코드 관리",
        ]
    )

    # -------------------------------------------------------------------------
    # TAB 1: 사용자 승인 및 권한 (직원별 연차 수동 수정 가능)
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("전체 사용자 및 연차 관리")
        if "users" in st.session_state and st.session_state.users:
            df_users = pd.DataFrame(st.session_state.users)

            # remaining_leave 컬럼 세팅
            if "remaining_leave" not in df_users.columns:
                df_users["remaining_leave"] = 0.0

            edited_users = st.data_editor(
                df_users,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "id": st.column_config.TextColumn("아이디", disabled=True),
                    "name": st.column_config.TextColumn("이름"),
                    "role": st.column_config.TextColumn("권한"),
                    "department": st.column_config.TextColumn("부서"),
                    "position": st.column_config.TextColumn("직급"),
                    "remaining_leave": st.column_config.NumberColumn(
                        "부여/잔여 연차 (일)",
                        help="직원의 현재 부여/잔여 연차 일수입니다.",
                        min_value=0.0,
                        max_value=40.0,
                        step=0.5,
                        format="%.1f 일",
                    ),
                },
            )

            if st.button("💾 사용자 설정 저장", type="primary"):
                updated_list = edited_users.to_dict("records")
                st.session_state.users = updated_list

                # 현재 로그인 유저 세션 동기화
                for u in updated_list:
                    if u.get("id") == user.get("id"):
                        st.session_state.logged_in_user = u
                        break

                st.success("사용자 정보 및 연차가 저장되었습니다.")
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: 연차 신청 승인 (승인 시 1일/신청일수 자동 차감)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("📋 연차 신청 승인 및 자동 차감")

        v_requests = st.session_state.get("vacation_requests", [])

        if not v_requests:
            st.info("현재 대기 중이거나 등록된 연차 신청 내역이 없습니다.")
        else:
            for idx, req in enumerate(v_requests):
                user_id = req.get("user_id") or req.get("user_name", "-")
                user_name = req.get("user_name") or req.get("name", user_id)
                req_date = req.get("date", "-")
                req_days = float(req.get("days", 1.0))  # 기본 1일 차감
                status = req.get("status", "대기")
                is_deducted = req.get("deducted", False)

                col_info, col_btn = st.columns([3, 1])

                with col_info:
                    st.write(
                        f"**[{status}]** **{user_name}** ({user_id}) - "
                        f"신청일: `{req_date}` | 차감 예정: `{req_days}일`"
                    )
                    if req.get("reason"):
                        st.caption(f"사유: {req.get('reason')}")

                with col_btn:
                    if status == "대기":
                        btn_approve, btn_reject = st.columns(2)

                        # [승인] 클릭 시 연차 자동 차감
                        if btn_approve.button(
                            "승인", key=f"app_{idx}", type="primary"
                        ):
                            # 1. users 목록에서 사용자 연차 차감
                            user_found = False
                            for u in st.session_state.get("users", []):
                                if (
                                    u.get("id") == user_id
                                    or u.get("name") == user_name
                                ):
                                    current_val = float(
                                        u.get("remaining_leave", 15.0)
                                    )
                                    # 연차 차감 (최소 0일)
                                    u["remaining_leave"] = max(
                                        0.0, current_val - req_days
                                    )
                                    user_found = True

                                    # 로그인한 본인 데이터면 세션도 업데이트
                                    if user.get("id") == u.get("id"):
                                        st.session_state.logged_in_user[
                                            "remaining_leave"
                                        ] = u["remaining_leave"]
                                    break

                            # 2. 신청 상태 변경 및 중복 차감 방지 플래그 설정
                            req["status"] = "승인"
                            req["deducted"] = True

                            st.success(
                                f"{user_name}님의 연차가 승인되었으며 {req_days}일이 차감되었습니다!"
                            )
                            st.rerun()

                        if btn_reject.button("반려", key=f"rej_{idx}"):
                            req["status"] = "반려"
                            st.warning(f"{user_name}님의 연차 신청이 반려되었습니다.")
                            st.rerun()

                    elif status == "승인":
                        st.success("✅ 승인완료 (차감됨)")
                    elif status == "반려":
                        st.error("❌ 반려됨")

                st.markdown("---")

    # -------------------------------------------------------------------------
    # TAB 3: 공통 코드 관리 (창고/직급)
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("창고 / 직급 목록 관리")
        col1, col2 = st.columns(2)
        with col1:
            st.write("📋 **현재 창고 목록**")
            st.write(st.session_state.get("warehouses", []))
            new_wh = st.text_input("새 창고 추가")
            if st.button("창고 추가"):
                if "warehouses" not in st.session_state:
                    st.session_state.warehouses = []
                if new_wh and new_wh not in st.session_state.warehouses:
                    st.session_state.warehouses.append(new_wh)
                    st.success("창고가 추가되었습니다.")
                    st.rerun()

        with col2:
            st.write("📋 **현재 직급 목록**")
            st.write(st.session_state.get("positions", []))
            new_pos = st.text_input("새 직급 추가")
            if st.button("직급 추가"):
                if "positions" not in st.session_state:
                    st.session_state.positions = []
                if new_pos and new_pos not in st.session_state.positions:
                    st.session_state.positions.append(new_pos)
                    st.success("직급이 추가되었습니다.")
                    st.rerun()
