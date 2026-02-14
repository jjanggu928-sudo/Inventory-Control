"""
재고마스터 - 메인 앱
"""
import streamlit as st
from utils.auth import sign_in, sign_up, sign_out, is_authenticated, get_current_user
from utils.helpers import show_success, show_error, show_info

# 페이지 설정
st.set_page_config(
    page_title="재고마스터",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None


def show_login_page():
    """로그인 페이지"""
    st.title("📦 재고마스터")
    st.markdown("### 소상공인을 위한 간편한 재고관리 시스템")
    
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            email = st.text_input("이메일", placeholder="example@email.com")
            password = st.text_input("비밀번호", type="password")
            submit = st.form_submit_button("로그인", use_container_width=True)
            
            if submit:
                if not email or not password:
                    show_error("이메일과 비밀번호를 입력해주세요.")
                else:
                    response = sign_in(email, password)
                    if response and response.user:
                        st.session_state['user_id'] = response.user.id
                        st.session_state['user_email'] = response.user.email
                        show_success("로그인 성공!")
                        st.rerun()
                    else:
                        show_error("로그인 실패. 이메일과 비밀번호를 확인해주세요.")
    
    with tab2:
        st.subheader("회원가입")
        with st.form("signup_form"):
            new_email = st.text_input("이메일", placeholder="example@email.com", key="signup_email")
            new_password = st.text_input("비밀번호", type="password", key="signup_password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            submit = st.form_submit_button("회원가입", use_container_width=True)
            
            if submit:
                if not new_email or not new_password:
                    show_error("모든 필드를 입력해주세요.")
                elif new_password != confirm_password:
                    show_error("비밀번호가 일치하지 않습니다.")
                elif len(new_password) < 6:
                    show_error("비밀번호는 최소 6자 이상이어야 합니다.")
                else:
                    response = sign_up(new_email, new_password)
                    if response and response.user:
                        show_success("회원가입 성공! 이메일을 확인해주세요.")
                        show_info("이메일 인증 후 로그인할 수 있습니다.")
                    else:
                        show_error("회원가입 실패. 다시 시도해주세요.")


def show_main_page():
    """메인 페이지 (로그인 후)"""
    # 사이드바
    with st.sidebar:
        st.title("📦 재고마스터")
        st.write(f"👤 {st.session_state.get('user_email', 'User')}")
        st.divider()
        
        if st.button("🚪 로그아웃", use_container_width=True):
            sign_out()
            show_success("로그아웃되었습니다.")
            st.rerun()
    
    # 메인 컨텐츠
    st.title("🏠 대시보드")
    
    # 안내 메시지
    st.info("""
    👈 왼쪽 사이드바에서 메뉴를 선택하세요.
    
    - **상품관리**: 상품 등록, 조회, 수정, 삭제
    - **입출고관리**: 입고/출고 기록 및 조회
    - **대시보드**: 재고 현황 및 통계
    """)
    
    # 간단한 통계 표시
    from utils.database import get_inventory_summary
    
    summary = get_inventory_summary(st.session_state['user_id'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📦 총 상품 수",
            value=summary['total_products']
        )
    
    with col2:
        st.metric(
            label="💰 총 재고 가치",
            value=f"₩{summary['total_stock_value']:,.0f}"
        )
    
    with col3:
        st.metric(
            label="⚠️ 재고 부족 상품",
            value=summary['low_stock_count'],
            delta="주의 필요" if summary['low_stock_count'] > 0 else None
        )
    
    st.divider()
    
    # 최근 활동
    st.subheader("📊 최근 활동")
    from utils.database import get_transactions
    
    recent_transactions = get_transactions(st.session_state['user_id'], limit=5)
    
    if recent_transactions:
        for trans in recent_transactions:
            trans_type = trans.get('type', '')
            quantity = trans.get('quantity', 0)
            product_name = trans.get('products', {}).get('name', '알 수 없음')
            date = trans.get('transaction_date', '')
            
            icon = "📥" if trans_type == "입고" else "📤"
            st.write(f"{icon} **{product_name}** - {trans_type} {quantity}개 ({date[:10]})")
    else:
        st.write("아직 입출고 내역이 없습니다.")


def main():
    """메인 함수"""
    if is_authenticated():
        show_main_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
