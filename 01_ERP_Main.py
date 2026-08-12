import streamlit as st
from utils.auth import require_auth
from utils.i18n import t, render_sidebar

st.set_page_config(page_title=t("title"), page_icon="🏢", layout="wide")
require_auth()
render_sidebar()

st.title("🏢 통합 ERP 시스템")
st.success("환영합니다! 좌측 메뉴를 통해 원하는 기능으로 이동해 주세요.")

c1, c2, c3, c4 = st.columns(4)
c1.info("📊 **메인 대시보드**\n\n월별 및 기간별 매출 조회")
c2.info("⚙️ **마스터 관리**\n\n제품/거래처/공급가 등록")
c3.info("📦 **출고/납품 작성**\n\n최대 30개 품목 발주 처리")
c4.info("🏢 **재고 및 위탁**\n\n3개 창고 & 大吉商事 평가액")
