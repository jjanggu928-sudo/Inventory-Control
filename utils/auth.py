"""
Supabase 인증 관련 함수
"""
import streamlit as st
from .database import get_supabase_client

supabase = get_supabase_client()


def sign_up(email: str, password: str):
    """회원가입"""
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "email_redirect_to": "http://localhost:8501"
            }
        })
        return response
    except Exception as e:
        st.error(f"회원가입 오류: {e}")
        return None


def sign_in(email: str, password: str):
    """로그인"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        st.error(f"로그인 오류: {e}")
        return None


def sign_out():
    """로그아웃"""
    try:
        supabase.auth.sign_out()
        if 'user' in st.session_state:
            del st.session_state['user']
        if 'user_id' in st.session_state:
            del st.session_state['user_id']
        if 'user_email' in st.session_state:
            del st.session_state['user_email']
        return True
    except Exception as e:
        st.error(f"로그아웃 오류: {e}")
        return False


def get_current_user():
    """현재 로그인한 사용자 정보"""
    try:
        user = supabase.auth.get_user()
        return user
    except Exception as e:
        return None


def is_authenticated():
    """인증 상태 확인"""
    return 'user_id' in st.session_state and st.session_state['user_id'] is not None


def require_auth():
    """인증 필수 데코레이터 함수 역할"""
    if not is_authenticated():
        st.warning("⚠️ 로그인이 필요합니다.")
        st.stop()
