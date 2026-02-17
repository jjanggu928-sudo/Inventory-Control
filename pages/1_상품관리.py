"""
상품관리 페이지
"""
import streamlit as st
from utils.auth import require_auth
from utils.database import get_products, create_product, update_product, delete_product, get_product_by_id
from utils.helpers import show_success, show_error, format_currency, validate_non_negative_number, create_dataframe, export_to_csv
from utils.barcode import scan_barcode_ui, get_product_by_barcode
from utils.styles import apply_global_styles, page_header, sidebar_brand

st.set_page_config(page_title="상품관리 - 재고마스터", page_icon="📦", layout="wide")
apply_global_styles()
require_auth()

with st.sidebar:
    sidebar_brand()

page_header("📦 상품관리", "상품을 등록하고 재고를 관리하세요")

if 'scanned_sku' not in st.session_state:
    st.session_state['scanned_sku'] = ''

tab1, tab2, tab3 = st.tabs(["📋  상품 목록", "➕  상품 등록", "✏️  상품 수정"])
user_id = st.session_state['user_id']

CATEGORIES = ["식품", "음료", "생활용품", "전자제품", "의류", "기타"]
UNITS = ["개", "박스", "kg", "L", "세트"]

# ===== 탭 1: 상품 목록 =====
with tab1:
    products = get_products(user_id)

    if products:
        col1, col2, col3 = st.columns(3)
        total_value = sum(p['current_stock'] * p['unit_price'] for p in products)
        low_stock = sum(1 for p in products if p['current_stock'] < p['min_stock'])

        with col1:
            st.markdown(f"""<div style="background:#e3f2fd;border-radius:10px;padding:1rem 1.2rem;border-left:4px solid #1976D2;">
                <div style="color:#1565C0;font-size:0.8rem;font-weight:600;">총 상품 수</div>
                <div style="font-size:1.6rem;font-weight:700;color:#212529;">{len(products)}개</div></div>""",
                unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div style="background:#e8f5e9;border-radius:10px;padding:1rem 1.2rem;border-left:4px solid #388E3C;">
                <div style="color:#2E7D32;font-size:0.8rem;font-weight:600;">총 재고 가치</div>
                <div style="font-size:1.6rem;font-weight:700;color:#212529;">{format_currency(total_value)}</div></div>""",
                unsafe_allow_html=True)
        with col3:
            bg = "#fff3e0" if low_stock > 0 else "#e8f5e9"
            bc = "#F57C00" if low_stock > 0 else "#388E3C"
            tc = "#E65100" if low_stock > 0 else "#2E7D32"
            st.markdown(f"""<div style="background:{bg};border-radius:10px;padding:1rem 1.2rem;border-left:4px solid {bc};">
                <div style="color:{tc};font-size:0.8rem;font-weight:600;">재고 부족 상품</div>
                <div style="font-size:1.6rem;font-weight:700;color:#212529;">{low_stock}개</div></div>""",
                unsafe_allow_html=True)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        search = st.text_input("🔍 상품명 또는 코드 검색", placeholder="검색어 입력...", label_visibility="collapsed")
        if search:
            products = [p for p in products if
                        search.lower() in p['name'].lower() or
                        search.lower() in (p.get('sku') or '').lower()]

        df = create_dataframe(products)
        if not df.empty:
            display_df = df[['name', 'sku', 'category', 'unit', 'unit_price', 'current_stock', 'min_stock']].copy()
            display_df.columns = ['상품명', '상품코드', '카테고리', '단위', '단가', '현재재고', '최소재고']
            display_df['재고상태'] = display_df.apply(
                lambda r: '⚠️ 부족' if r['현재재고'] < r['최소재고'] else '✅ 정상', axis=1)
            display_df['단가'] = display_df['단가'].apply(format_currency)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            export_to_csv(display_df, "상품목록.csv")
    else:
        st.markdown("""<div style="text-align:center;padding:3rem;background:#f8f9fa;border-radius:14px;border:2px dashed #dee2e6;">
            <div style="font-size:3rem;margin-bottom:0.5rem;">📦</div>
            <div style="font-weight:600;color:#495057;margin-bottom:0.3rem;">등록된 상품이 없습니다</div>
            <div style="color:#adb5bd;font-size:0.9rem;">'상품 등록' 탭에서 첫 번째 상품을 추가해보세요</div></div>""",
            unsafe_allow_html=True)

# ===== 탭 2: 상품 등록 =====
with tab2:
    st.markdown("#### 새 상품 등록")

    with st.expander("📷  바코드 스캔으로 상품코드 자동 입력", expanded=False):
        scanned = scan_barcode_ui(key_prefix="register")
        if scanned:
            st.session_state['scanned_sku'] = scanned
            existing = get_product_by_barcode(user_id, scanned)
            if existing:
                st.warning(f"⚠️ 이미 등록된 상품: **{existing['name']}** (재고: {existing['current_stock']})")
            else:
                st.info("새 상품코드입니다. 아래 양식을 작성해주세요.")

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("상품명 *", placeholder="예: 콜라 500ml")
            sku = st.text_input("상품코드 (SKU/바코드)",
                                value=st.session_state.get('scanned_sku', ''),
                                placeholder="예: 8801234567890")
            category = st.selectbox("카테고리 *", CATEGORIES)
        with col2:
            unit = st.selectbox("단위 *", UNITS)
            unit_price = st.number_input("단가 *", min_value=0, step=100, format="%d")
            min_stock = st.number_input("최소 재고 *", min_value=0, value=10)
        current_stock = st.number_input("초기 재고", min_value=0, value=0)
        submitted = st.form_submit_button("✅  상품 등록", use_container_width=True, type="primary")

        if submitted:
            if not name:
                show_error("상품명을 입력해주세요.")
            elif not validate_non_negative_number(unit_price, "단가"):
                pass
            else:
                result = create_product(user_id, {
                    'name': name, 'sku': sku or None, 'category': category,
                    'unit': unit, 'unit_price': unit_price,
                    'current_stock': current_stock, 'min_stock': min_stock
                })
                if result:
                    st.session_state['scanned_sku'] = ''
                    show_success(f"'{name}' 상품이 등록되었습니다!")
                    st.rerun()
                else:
                    show_error("상품 등록에 실패했습니다.")

# ===== 탭 3: 상품 수정 =====
with tab3:
    st.markdown("#### 상품 정보 수정")
    products = get_products(user_id)

    if products:
        product_options = {f"{p['name']}  ({p.get('sku') or 'SKU 없음'})": p['id'] for p in products}
        selected = st.selectbox("수정할 상품 선택", list(product_options.keys()))

        if selected:
            product = get_product_by_id(product_options[selected])
            if product:
                stock_color = "#dc3545" if product['current_stock'] < product['min_stock'] else "#28a745"
                st.markdown(f"""
                <div style="background:#f8f9fa;border-radius:10px;padding:0.8rem 1.2rem;
                            border-left:4px solid {stock_color};margin-bottom:1rem;display:flex;align-items:center;gap:8px;">
                    <span style="font-weight:600;">현재 재고:</span>
                    <span style="color:{stock_color};font-weight:700;">{product['current_stock']} {product['unit']}</span>
                    <span style="color:#6c757d;font-size:0.85rem;">(최소: {product['min_stock']} {product['unit']})</span>
                    <span style="color:#adb5bd;font-size:0.8rem;margin-left:auto;">재고는 입출고 관리에서 변경하세요</span>
                </div>""", unsafe_allow_html=True)

                with st.form("update_product_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("상품명 *", value=product['name'])
                        sku = st.text_input("상품코드 (SKU/바코드)", value=product.get('sku') or '')
                        cat_idx = CATEGORIES.index(product['category']) if product['category'] in CATEGORIES else 5
                        category = st.selectbox("카테고리 *", CATEGORIES, index=cat_idx)
                    with col2:
                        unit_idx = UNITS.index(product['unit']) if product['unit'] in UNITS else 0
                        unit = st.selectbox("단위 *", UNITS, index=unit_idx)
                        unit_price = st.number_input("단가 *", min_value=0, value=int(product['unit_price']), step=100)
                        min_stock = st.number_input("최소 재고 *", min_value=0, value=product['min_stock'])

                    col_btn1, col_btn2 = st.columns([3, 1])
                    with col_btn1:
                        update_btn = st.form_submit_button("💾  수정 저장", use_container_width=True, type="primary")
                    with col_btn2:
                        delete_btn = st.form_submit_button("🗑️  삭제", use_container_width=True)

                    if update_btn:
                        if not name:
                            show_error("상품명을 입력해주세요.")
                        else:
                            result = update_product(product_options[selected], {
                                'name': name, 'sku': sku or None, 'category': category,
                                'unit': unit, 'unit_price': unit_price, 'min_stock': min_stock
                            })
                            if result:
                                show_success("상품 정보가 수정되었습니다!")
                                st.rerun()
                            else:
                                show_error("상품 수정에 실패했습니다.")

                    if delete_btn:
                        if delete_product(product_options[selected]):
                            show_success("상품이 삭제되었습니다.")
                            st.rerun()
                        else:
                            show_error("상품 삭제에 실패했습니다.")
    else:
        st.info("등록된 상품이 없습니다.")
