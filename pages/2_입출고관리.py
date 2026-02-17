"""
입출고관리 페이지
"""
import streamlit as st
from datetime import datetime
from utils.auth import require_auth
from utils.database import get_products, get_transactions, create_transaction, get_product_by_id
from utils.helpers import show_success, show_error, format_currency, validate_positive_number, create_dataframe, export_to_csv
from utils.barcode import scan_barcode_ui, get_product_by_barcode
from utils.styles import apply_global_styles, page_header, sidebar_brand

st.set_page_config(page_title="입출고관리 - 재고마스터", page_icon="📥", layout="wide")
apply_global_styles()
require_auth()

with st.sidebar:
    sidebar_brand()

page_header("📥 입출고관리", "입고·출고를 등록하고 내역을 확인하세요")

if 'barcode_product_index' not in st.session_state:
    st.session_state['barcode_product_index'] = 0

tab1, tab2 = st.tabs(["➕  입출고 등록", "📋  입출고 내역"])
user_id = st.session_state['user_id']

# ===== 탭 1: 입출고 등록 =====
with tab1:
    products = get_products(user_id)

    if not products:
        st.markdown("""<div style="text-align:center;padding:3rem;background:#fff3e0;border-radius:14px;border:2px dashed #ffcc02;">
            <div style="font-size:3rem;margin-bottom:0.5rem;">⚠️</div>
            <div style="font-weight:600;color:#E65100;">등록된 상품이 없습니다</div>
            <div style="color:#adb5bd;font-size:0.9rem;margin-top:0.3rem;">먼저 상품관리에서 상품을 등록해주세요</div></div>""",
            unsafe_allow_html=True)
        st.stop()

    # 바코드 스캔
    with st.expander("📷  바코드 스캔으로 상품 빠른 선택", expanded=False):
        scanned = scan_barcode_ui(key_prefix="transaction")
        if scanned:
            found = get_product_by_barcode(user_id, scanned)
            if found:
                st.success(f"✅ **{found['name']}** 선택됨 · 현재 재고: **{found['current_stock']}{found['unit']}**")
                for i, p in enumerate(products):
                    if p['id'] == found['id']:
                        st.session_state['barcode_product_index'] = i
                        break
            else:
                st.error(f"❌ 바코드 **{scanned}** 에 해당하는 상품이 없습니다. 먼저 상품을 등록해주세요.")

    with st.form("transaction_form"):
        # 입/출고 선택 (눈에 띄게)
        trans_type = st.radio("거래 유형", ["📥  입고", "📤  출고"], horizontal=True)
        trans_type_value = "입고" if "입고" in trans_type else "출고"

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            product_keys = [f"{p['name']}  (재고: {p['current_stock']}{p['unit']})" for p in products]
            product_ids = [p['id'] for p in products]
            default_idx = min(st.session_state.get('barcode_product_index', 0), len(product_keys) - 1)
            selected_label = st.selectbox("상품 *", product_keys, index=default_idx)
            selected_idx = product_keys.index(selected_label)
            product_id = product_ids[selected_idx]
            quantity = st.number_input("수량 *", min_value=1, value=1)

        with col2:
            unit_price = st.number_input("단가 *", min_value=0, step=100, format="%d")
            transaction_date = st.date_input("거래 날짜", value=datetime.now())

        memo = st.text_area("메모 (선택)", placeholder="거래처, 특이사항 등을 입력하세요")

        submitted = st.form_submit_button("✅  등록", use_container_width=True, type="primary")

        if submitted:
            product = get_product_by_id(product_id)
            if trans_type_value == "출고" and product['current_stock'] < quantity:
                show_error(f"재고 부족! 현재 재고: {product['current_stock']}{product['unit']}")
                st.stop()
            elif not validate_positive_number(quantity, "수량"):
                pass
            elif not validate_positive_number(unit_price, "단가"):
                pass
            else:
                result = create_transaction(user_id, {
                    'product_id': product_id,
                    'type': trans_type_value,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': quantity * unit_price,
                    'memo': memo or None,
                    'transaction_date': transaction_date.isoformat()
                })
                if result:
                    updated = get_product_by_id(product_id)
                    show_success(f"{trans_type_value} {quantity}{product['unit']} 등록 완료!")
                    color = "#28a745" if trans_type_value == "입고" else "#dc3545"
                    st.markdown(f"""
                    <div style="background:#f8f9fa;border-radius:10px;padding:0.8rem 1.2rem;border-left:4px solid {color};">
                        📦 <strong>{product['name']}</strong> 업데이트된 재고:
                        <strong style="color:{color};">{updated['current_stock']}{updated['unit']}</strong>
                    </div>""", unsafe_allow_html=True)
                    st.session_state['barcode_product_index'] = 0
                    st.rerun()
                else:
                    show_error("입출고 등록에 실패했습니다.")

# ===== 탭 2: 입출고 내역 =====
with tab2:
    products = get_products(user_id)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        filter_opts = ["전체"] + [f"{p['name']} ({p.get('sku', '')})" for p in products]
        selected_filter = st.selectbox("상품 필터", filter_opts, label_visibility="collapsed")
    with col2:
        type_filter = st.selectbox("유형", ["전체", "입고", "출고"], label_visibility="collapsed")
    with col3:
        limit = st.number_input("표시 개수", min_value=10, max_value=500, value=100, step=10, label_visibility="collapsed")

    # 내역 조회
    if selected_filter == "전체":
        transactions = get_transactions(user_id, limit=limit)
    else:
        product_name = selected_filter.split(" (")[0]
        pid = next((p['id'] for p in products if p['name'] == product_name), None)
        transactions = get_transactions(user_id, product_id=pid, limit=limit)

    if type_filter != "전체":
        transactions = [t for t in transactions if t['type'] == type_filter]

    if transactions:
        # 요약 통계 배너
        total_in_qty = sum(t['quantity'] for t in transactions if t['type'] == '입고')
        total_out_qty = sum(t['quantity'] for t in transactions if t['type'] == '출고')
        total_in_val = sum(t['total_price'] for t in transactions if t['type'] == '입고')
        total_out_val = sum(t['total_price'] for t in transactions if t['type'] == '출고')

        c1, c2, c3, c4 = st.columns(4)
        for col, label, val, color in [
            (c1, "📥 총 입고 수량", f"{total_in_qty}개", "#28a745"),
            (c2, "📤 총 출고 수량", f"{total_out_qty}개", "#dc3545"),
            (c3, "💚 입고 금액", format_currency(total_in_val), "#28a745"),
            (c4, "💸 출고 금액", format_currency(total_out_val), "#dc3545"),
        ]:
            with col:
                st.markdown(f"""<div style="background:#f8f9fa;border-radius:10px;padding:0.8rem 1rem;border-left:3px solid {color};margin-bottom:0.5rem;">
                    <div style="font-size:0.78rem;color:#6c757d;">{label}</div>
                    <div style="font-size:1.2rem;font-weight:700;color:{color};">{val}</div></div>""",
                    unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # 테이블
        trans_list = [{
            '날짜': t['transaction_date'][:10],
            '상품명': t.get('products', {}).get('name', '알 수 없음'),
            '상품코드': t.get('products', {}).get('sku') or '-',
            '유형': t['type'],
            '수량': t['quantity'],
            '단가': format_currency(t['unit_price']),
            '합계': format_currency(t['total_price']),
            '메모': t.get('memo') or '-'
        } for t in transactions]

        df = create_dataframe(trans_list)

        def highlight_type(row):
            color = '#e8f5e9' if row['유형'] == '입고' else '#ffebee'
            return [f'background-color: {color}'] * len(row)

        st.dataframe(df.style.apply(highlight_type, axis=1), use_container_width=True, hide_index=True)
        export_to_csv(df, "입출고내역.csv")
    else:
        st.markdown("""<div style="text-align:center;padding:3rem;background:#f8f9fa;border-radius:14px;border:2px dashed #dee2e6;">
            <div style="font-size:3rem;margin-bottom:0.5rem;">📋</div>
            <div style="font-weight:600;color:#495057;">입출고 내역이 없습니다</div></div>""",
            unsafe_allow_html=True)
