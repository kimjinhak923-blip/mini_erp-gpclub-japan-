import streamlit as st
from views import master_data, sales, inventory, invoice

st.set_page_config(page_title="통합 ERP 시스템", layout="wide")

st.sidebar.title("🏢 통합 ERP 시스템")
menu = st.sidebar.radio(
    "메뉴 선택",
    ["마스터 데이터", "영업 및 배송", "재고 관리", "청구 및 정산"]
)

if menu == "마스터 데이터":
    master_data.render()
elif menu == "영업 및 배송":
    sales.render()
elif menu == "재고 관리":
    inventory.render()
elif menu == "청구 및 정산":
    invoice.render()
