"""
재고마스터 - 메인 앱
"""
import streamlit as st
from utils.auth import sign_in, sign_up, sign_out, is_authenticated
from utils.helpers import show_success, show_error, show_info
from utils.styles import apply_global_styles, sidebar_brand, page_header, metric_card, load_lottie_url

# 페이지 설정
st.set_page_config(
    page_title="재고마스터",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 전역 스타일 적용
apply_global_styles()

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None


def show_login_page():
    """로그인 페이지"""
    col_l, col_c, col_r = st.columns([1, 1.6, 1])

    with col_c:
        # 브랜드 헤더
        st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1.5rem 0;">
            <div style="font-size:4rem; margin-bottom:0.5rem;">📦</div>
            <h1 style="
                font-size:2.2rem; font-weight:700;
                color:#212529; margin:0; letter-spacing:-1px;
            ">재고마스터</h1>
            <p style="color:#6c757d; margin-top:6px; font-size:1rem;">
                소상공인을 위한 스마트 재고관리 시스템
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 로그인 / 회원가입 탭
        tab1, tab2 = st.tabs(["🔑  로그인", "✏️  회원가입"])

        with tab1:
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("이메일", placeholder="example@email.com")
                password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("로그인", use_container_width=True, type="primary")

                if submit:
                    if not email or not password:
                        show_error("이메일과 비밀번호를 입력해주세요.")
                    else:
                        with st.spinner("로그인 중..."):
                            response = sign_in(email, password)
                        if response and response.user:
                            st.session_state['user_id'] = response.user.id
                            st.session_state['user_email'] = response.user.email
                            show_success("로그인 성공!")
                            st.rerun()
                        else:
                            show_error("이메일 또는 비밀번호가 올바르지 않습니다.")

        with tab2:
            with st.form("signup_form", clear_on_submit=False):
                new_email = st.text_input("이메일", placeholder="example@email.com", key="signup_email")
                new_password = st.text_input("비밀번호", type="password", placeholder="6자 이상", key="signup_password")
                confirm_password = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호 재입력")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("회원가입", use_container_width=True, type="primary")

                if submit:
                    if not new_email or not new_password:
                        show_error("모든 필드를 입력해주세요.")
                    elif new_password != confirm_password:
                        show_error("비밀번호가 일치하지 않습니다.")
                    elif len(new_password) < 6:
                        show_error("비밀번호는 최소 6자 이상이어야 합니다.")
                    else:
                        with st.spinner("계정 생성 중..."):
                            response = sign_up(new_email, new_password)
                        if response and response.user:
                            show_success("회원가입 성공!")
                            show_info("이메일 인증 후 로그인하실 수 있습니다.")
                        else:
                            show_error("회원가입에 실패했습니다. 다시 시도해주세요.")

        st.markdown("""
        <div style="text-align:center; margin-top:2rem; color:#adb5bd; font-size:0.8rem;">
            © 2025 재고마스터 · Powered by Supabase &amp; Streamlit
        </div>
        """, unsafe_allow_html=True)


def show_main_page():
    """메인 페이지 (로그인 후)"""
    with st.sidebar:
        sidebar_brand()
        st.markdown(
            "<div style='color:rgba(255,255,255,0.5); font-size:0.8rem; padding: 0 1rem;'>로그인 계정</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='color:#e0e0e0; font-size:0.9rem; padding: 4px 1rem 1rem 1rem; font-weight:500;'>"
            f"👤 {st.session_state.get('user_email','')}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.1); margin: 0 0 1rem 0;'>",
            unsafe_allow_html=True
        )
        if st.button("🚪  로그아웃", use_container_width=True):
            sign_out()
            st.rerun()

    # 헤더
    page_header("🏠 대시보드", "재고 현황을 한눈에 확인하세요")

    # 통계 카드
    from utils.database import get_inventory_summary, get_transactions
    summary = get_inventory_summary(st.session_state['user_id'])

    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card("총 상품 수", f"{summary['total_products']}개", "📦")
    with col2:
        metric_card("총 재고 가치", f"₩{summary['total_stock_value']:,.0f}", "💰")
    with col3:
        delta = "⚠️ 주의 필요" if summary['low_stock_count'] > 0 else "✅ 정상"
        metric_card("재고 부족 상품", f"{summary['low_stock_count']}개", "⚠️", delta)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # 메뉴 안내 카드
    col_a, col_b, col_c = st.columns(3)
    cards = [
        ("📦", "상품관리", "상품 등록·수정·삭제\n바코드 스캔 지원", "#1976D2"),
        ("📥", "입출고관리", "입고·출고 등록\n재고 자동 업데이트", "#0288D1"),
        ("📊", "대시보드", "재고 현황 차트\n통계 분석", "#0097A7"),
    ]
    for col, (icon, title, desc, color) in zip([col_a, col_b, col_c], cards):
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}18 0%, {color}08 100%);
                border: 1px solid {color}40;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 1.2rem 1.4rem;
            ">
                <div style="font-size:1.8rem; margin-bottom:0.4rem;">{icon}</div>
                <div style="font-weight:700; font-size:1rem; color:#212529; margin-bottom:0.3rem;">{title}</div>
                <div style="font-size:0.82rem; color:#6c757d; white-space:pre-line;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 최근 입출고 내역
    st.markdown("#### 📋 최근 입출고 내역")
    recent = get_transactions(st.session_state['user_id'], limit=5)

    if recent:
        for t in recent:
            icon = "📥" if t.get('type') == '입고' else "📤"
            color = "#28a745" if t.get('type') == '입고' else "#dc3545"
            name = t.get('products', {}).get('name', '알 수 없음')
            date = t.get('transaction_date', '')[:10]
            qty = t.get('quantity', 0)
            t_type = t.get('type', '')
            st.markdown(f"""
            <div style="
                display:flex; align-items:center; gap:1rem;
                padding: 0.7rem 1rem;
                background:#ffffff; border:1px solid #e9ecef;
                border-radius:10px; margin-bottom:0.5rem;
            ">
                <span style="font-size:1.3rem;">{icon}</span>
                <span style="font-weight:600; flex:1; color:#212529;">{name}</span>
                <span style="color:{color}; font-weight:600;">{t_type} {qty}개</span>
                <span style="color:#adb5bd; font-size:0.85rem;">{date}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:2rem; color:#adb5bd;">
            아직 입출고 내역이 없습니다.<br>
            <span style="font-size:0.9rem;">사이드바에서 입출고관리를 선택하세요.</span>
        </div>
        """, unsafe_allow_html=True)


def main():
    if is_authenticated():
        show_main_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
