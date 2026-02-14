"""
상품관리 페이지
"""
import streamlit as st
from utils.auth import require_auth
from utils.database import (
    get_products, create_product, update_product,
    delete_product, get_product_by_id
)
from utils.helpers import (
    show_success, show_error, format_currency,
    validate_positive_number, validate_non_negative_number,
    create_dataframe, export_to_csv
)
from utils.barcode import scan_barcode_ui, get_product_by_barcode
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="상품관리 - 재고마스터", page_icon="📦", layout="wide")

# 인증 확인
require_auth()

st.title("📦 상품관리")

# 세션 상태 초기화
if 'scanned_sku' not in st.session_state:
    st.session_state['scanned_sku'] = ''

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📋 상품 목록", "➕ 상품 등록", "✏️ 상품 수정"])

user_id = st.session_state['user_id']

# ===== 탭 1: 상품 목록 =====
with tab1:
    st.subheader("등록된 상품 목록")

    # 상품 조회
    products = get_products(user_id)

    if products:
        # DataFrame 생성
        df = create_dataframe(products)

        # 필요한 컬럼만 선택 및 이름 변경
        display_df = df[['name', 'sku', 'category', 'unit', 'unit_price', 'current_stock', 'min_stock']].copy()
        display_df.columns = ['상품명', '상품코드', '카테고리', '단위', '단가', '현재재고', '최소재고']

        # 재고 상태 표시
        display_df['재고상태'] = display_df.apply(
            lambda row: '⚠️ 부족' if row['현재재고'] < row['최소재고'] else '✅ 정상',
            axis=1
        )

        # 단가 포맷
        display_df['단가'] = display_df['단가'].apply(lambda x: format_currency(x))

        # 테이블 표시
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # CSV 다운로드
        export_to_csv(display_df, "상품목록.csv")

        # 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 상품 수", len(products))
        with col2:
            total_value = sum(p['current_stock'] * p['unit_price'] for p in products)
            st.metric("총 재고 가치", format_currency(total_value))
        with col3:
            low_stock = sum(1 for p in products if p['current_stock'] < p['min_stock'])
            st.metric("재고 부족 상품", low_stock)
    else:
        st.info("등록된 상품이 없습니다. '상품 등록' 탭에서 새 상품을 추가하세요.")

# ===== 탭 2: 상품 등록 =====
with tab2:
    st.subheader("새 상품 등록")

    # 바코드 스캔 섹션
    with st.expander("📷 바코드 스캔으로 상품코드 입력", expanded=False):
        scanned = scan_barcode_ui(key_prefix="register")
        if scanned:
            st.session_state['scanned_sku'] = scanned
            # 이미 등록된 상품인지 확인
            existing = get_product_by_barcode(user_id, scanned)
            if existing:
                st.warning(f"⚠️ 이미 등록된 상품입니다: **{existing['name']}** (재고: {existing['current_stock']})")
            else:
                st.info(f"새 상품코드입니다. 아래 양식에서 상품 정보를 입력하세요.")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("상품명*", placeholder="예: 콜라 500ml")
            sku = st.text_input(
                "상품코드 (SKU/바코드)",
                value=st.session_state.get('scanned_sku', ''),
                placeholder="예: 8801234567890"
            )
            category = st.selectbox(
                "카테고리*",
                ["식품", "음료", "생활용품", "전자제품", "의류", "기타"]
            )

        with col2:
            unit = st.selectbox("단위*", ["개", "박스", "kg", "L", "세트"])
            unit_price = st.number_input("단가*", min_value=0, step=100)
            min_stock = st.number_input("최소 재고*", min_value=0, value=10)

        current_stock = st.number_input("초기 재고", min_value=0, value=0)

        submit = st.form_submit_button("상품 등록", use_container_width=True)

        if submit:
            if not name:
                show_error("상품명을 입력해주세요.")
            elif not validate_non_negative_number(unit_price, "단가"):
                pass
            elif not validate_non_negative_number(current_stock, "재고"):
                pass
            else:
                product_data = {
                    'name': name,
                    'sku': sku if sku else None,
                    'category': category,
                    'unit': unit,
                    'unit_price': unit_price,
                    'current_stock': current_stock,
                    'min_stock': min_stock
                }

                result = create_product(user_id, product_data)

                if result:
                    st.session_state['scanned_sku'] = ''
                    show_success(f"'{name}' 상품이 등록되었습니다!")
                    st.rerun()
                else:
                    show_error("상품 등록에 실패했습니다.")

# ===== 탭 3: 상품 수정 =====
with tab3:
    st.subheader("상품 정보 수정")

    products = get_products(user_id)

    if products:
        # 상품 선택
        product_options = {f"{p['name']} ({p.get('sku', 'SKU 없음')})": p['id'] for p in products}
        selected_product = st.selectbox(
            "수정할 상품 선택",
            options=list(product_options.keys())
        )

        if selected_product:
            product_id = product_options[selected_product]
            product = get_product_by_id(product_id)

            if product:
                with st.form("update_product_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        name = st.text_input("상품명*", value=product['name'])
                        sku = st.text_input("상품코드 (SKU/바코드)", value=product.get('sku', ''))
                        category = st.selectbox(
                            "카테고리*",
                            ["식품", "음료", "생활용품", "전자제품", "의류", "기타"],
                            index=["식품", "음료", "생활용품", "전자제품", "의류", "기타"].index(product['category']) if product['category'] in ["식품", "음료", "생활용품", "전자제품", "의류", "기타"] else 5
                        )

                    with col2:
                        unit = st.selectbox(
                            "단위*",
                            ["개", "박스", "kg", "L", "세트"],
                            index=["개", "박스", "kg", "L", "세트"].index(product['unit']) if product['unit'] in ["개", "박스", "kg", "L", "세트"] else 0
                        )
                        unit_price = st.number_input("단가*", min_value=0, value=int(product['unit_price']), step=100)
                        min_stock = st.number_input("최소 재고*", min_value=0, value=product['min_stock'])

                    st.info(f"현재 재고: {product['current_stock']} {product['unit']} (입출고 관리에서 변경 가능)")

                    col_btn1, col_btn2 = st.columns(2)

                    with col_btn1:
                        update_btn = st.form_submit_button("수정 저장", use_container_width=True, type="primary")

                    with col_btn2:
                        delete_btn = st.form_submit_button("상품 삭제", use_container_width=True)

                    if update_btn:
                        if not name:
                            show_error("상품명을 입력해주세요.")
                        elif not validate_non_negative_number(unit_price, "단가"):
                            pass
                        else:
                            update_data = {
                                'name': name,
                                'sku': sku if sku else None,
                                'category': category,
                                'unit': unit,
                                'unit_price': unit_price,
                                'min_stock': min_stock
                            }

                            result = update_product(product_id, update_data)

                            if result:
                                show_success("상품 정보가 수정되었습니다!")
                                st.rerun()
                            else:
                                show_error("상품 수정에 실패했습니다.")

                    if delete_btn:
                        if delete_product(product_id):
                            show_success("상품이 삭제되었습니다.")
                            st.rerun()
                        else:
                            show_error("상품 삭제에 실패했습니다.")
    else:
        st.info("등록된 상품이 없습니다.")
