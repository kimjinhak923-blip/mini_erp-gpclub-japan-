import streamlit as st
from utils.supabase_client import supabase

def render():
    st.header("🏭 재고 및 창고 이동")
    tab1, tab2 = st.tabs(["실시간 재고 현황", "재고 이동 현황"])
    
    with tab1:
        st.subheader("창고별 실시간 재고")
        try:
            # 재고 데이터 조회
            inv_res = supabase.table("inventories").select(
                "current_qty, allocated_qty, updated_at, warehouses(name), products(sku, name)"
            ).execute()
            
            if inv_res.data:
                # 데이터 가공하여 표시
                flattened_data = []
                for item in inv_res.data:
                    flattened_data.append({
                        "창고명": item["warehouses"]["name"] if item.get("warehouses") else "-",
                        "SKU": item["products"]["sku"] if item.get("products") else "-",
                        "상품명": item["products"]["name"] if item.get("products") else "-",
                        "현재 재고": item["current_qty"],
                        "예약 재고": item["allocated_qty"],
                        "최종 수정일": item["updated_at"]
                    })
                st.dataframe(flattened_data, use_container_width=True)
            else:
                st.info("현재 수량 데이터가 존재하는 재고가 없습니다.")
        except Exception as e:
            st.error(f"재고 데이터 조회 실패: {e}")

    with tab2:
        st.subheader("창고 간 재고 이동 이력")
        try:
            transfers = supabase.table("stock_transfers").select("*").execute()
            if transfers.data:
                st.dataframe(transfers.data, use_container_width=True)
            else:
                st.info("재고 이동 내역이 없습니다.")
        except Exception as e:
            st.error(f"이동 내역 조회 실패: {e}")
