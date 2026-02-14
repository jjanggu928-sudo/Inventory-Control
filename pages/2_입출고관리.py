"""
입출고관리 페이지
"""
import streamlit as st
from datetime import datetime
from utils.auth import require_auth
from utils.database import (
    get_products, get_transactions, create_transaction, get_product_by_id
)
from utils.helpers import (
    show_success, show_error, show_warning, format_currency,
    format_date, validate_positive_number, create_dataframe, export_to_csv
)
from utils.barcode import scan_barcode_ui, get_product_by_barcode

# 페이지 설정
st.set_page_config(page_title="입출고관리 - 재고마스터", page_icon="📦", layout="wide")

# 인증 확인
require_auth()

st.title("📦 입출고관리")

# 세션 상태 초기화
if 'barcode_product_index' not in st.session_state:
    st.session_state['barcode_product_index'] = 0

# 탭 생성
tab1, tab2 = st.tabs(["➕ 입출고 등록", "📋 입출고 내역"])

user_id = st.session_state['user_id']

# ===== 탭 1: 입출고 등록 =====
with tab1:
    st.subheader("입출고 등록")

    # 상품 목록 조회
    products = get_products(user_id)

    if not products:
        st.warning("⚠️ 등록된 상품이 없습니다. 먼저 상품을 등록해주세요.")
        st.stop()

    # 바코드 스캔으로 상품 선택
    with st.expander("📷 바코드 스캔으로 상품 선택", expanded=False):
        scanned = scan_barcode_ui(key_prefix="transaction")
        if scanned:
            found_product = get_product_by_barcode(user_id, scanned)
            if found_product:
                st.success(f"✅ **{found_product['name']}** 선택됨 (현재 재고: {found_product['current_stock']}{found_product['unit']})")
                # 상품 목록에서 해당 상품의 인덱스 찾기
                for i, p in enumerate(products):
                    if p['id'] == found_product['id']:
                        st.session_state['barcode_product_index'] = i
                        break
            else:
                st.error(f"❌ 바코드 '{scanned}'에 해당하는 상품이 없습니다. 먼저 상품을 등록해주세요.")

    with st.form("transaction_form"):
        # 입출고 유형 선택
        trans_type = st.radio("유형", ["입고", "출고"], horizontal=True)

        col1, col2 = st.columns(2)

        with col1:
            # 상품 선택
            product_options = {f"{p['name']} (현재: {p['current_stock']}{p['unit']})": p['id'] for p in products}
            product_keys = list(product_options.keys())
            default_index = st.session_state.get('barcode_product_index', 0)
            if default_index >= len(product_keys):
                default_index = 0
            selected_product = st.selectbox(
                "상품*",
                options=product_keys,
                index=default_index
            )

            # 수량
            quantity = st.number_input("수량*", min_value=1, value=1)

        with col2:
            # 단가
            unit_price = st.number_input("단가*", min_value=0, step=100)

            # 거래 날짜
            transaction_date = st.date_input("날짜", value=datetime.now())

        # 메모
        memo = st.text_area("메모 (선택사항)", placeholder="거래처, 특이사항 등")

        submit = st.form_submit_button("등록", use_container_width=True, type="primary")

        if submit:
            product_id = product_options[selected_product]
            product = get_product_by_id(product_id)

            # 출고 시 재고 확인
            if trans_type == "출고":
                if product['current_stock'] < quantity:
                    show_error(f"재고 부족! 현재 재고: {product['current_stock']}{product['unit']}")
                    st.stop()

            if not validate_positive_number(quantity, "수량"):
                pass
            elif not validate_positive_number(unit_price, "단가"):
                pass
            else:
                transaction_data = {
                    'product_id': product_id,
                    'type': trans_type,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': quantity * unit_price,
                    'memo': memo if memo else None,
                    'transaction_date': transaction_date.isoformat()
                }

                result = create_transaction(user_id, transaction_data)

                if result:
                    show_success(f"{trans_type} {quantity}{product['unit']}이(가) 등록되었습니다!")

                    # 업데이트된 재고 표시
                    updated_product = get_product_by_id(product_id)
                    st.info(f"📦 업데이트된 재고: {updated_product['current_stock']}{updated_product['unit']}")
                    st.session_state['barcode_product_index'] = 0
                    st.rerun()
                else:
                    show_error("입출고 등록에 실패했습니다.")

# ===== 탭 2: 입출고 내역 =====
with tab2:
    st.subheader("입출고 내역")

    # 필터
    col1, col2 = st.columns([3, 1])

    with col1:
        # 상품 필터
        products = get_products(user_id)
        product_filter_options = ["전체"] + [f"{p['name']} ({p.get('sku', '')})" for p in products]
        selected_filter = st.selectbox("상품 필터", product_filter_options)

    with col2:
        limit = st.number_input("표시 개수", min_value=10, max_value=500, value=100, step=10)

    # 입출고 내역 조회
    if selected_filter == "전체":
        transactions = get_transactions(user_id, limit=limit)
    else:
        # 선택된 상품의 ID 찾기
        product_name = selected_filter.split(" (")[0]
        selected_product_id = next((p['id'] for p in products if p['name'] == product_name), None)
        transactions = get_transactions(user_id, product_id=selected_product_id, limit=limit)

    if transactions:
        # DataFrame 생성
        trans_list = []
        for trans in transactions:
            trans_list.append({
                '날짜': trans['transaction_date'][:10],
                '상품명': trans.get('products', {}).get('name', '알 수 없음'),
                '상품코드': trans.get('products', {}).get('sku', '-'),
                '유형': trans['type'],
                '수량': trans['quantity'],
                '단가': format_currency(trans['unit_price']),
                '합계': format_currency(trans['total_price']),
                '메모': trans.get('memo', '-')
            })

        df = create_dataframe(trans_list)

        # 유형별 색상 구분을 위한 스타일링
        def highlight_type(row):
            if row['유형'] == '입고':
                return ['background-color: #e8f5e9'] * len(row)
            else:
                return ['background-color: #ffebee'] * len(row)

        styled_df = df.style.apply(highlight_type, axis=1)

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

        # CSV 다운로드
        export_to_csv(df, "입출고내역.csv")

        # 통계
        st.divider()
        st.subheader("📊 통계")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_in = sum(t['quantity'] for t in transactions if t['type'] == '입고')
            st.metric("총 입고", f"{total_in}건")

        with col2:
            total_out = sum(t['quantity'] for t in transactions if t['type'] == '출고')
            st.metric("총 출고", f"{total_out}건")

        with col3:
            total_in_value = sum(t['total_price'] for t in transactions if t['type'] == '입고')
            st.metric("입고 금액", format_currency(total_in_value))

        with col4:
            total_out_value = sum(t['total_price'] for t in transactions if t['type'] == '출고')
            st.metric("출고 금액", format_currency(total_out_value))

    else:
        st.info("입출고 내역이 없습니다.")
