"""
헬퍼 함수 모음
"""
import streamlit as st
from datetime import datetime
import pandas as pd


def format_currency(amount: float) -> str:
    """금액 포맷 (원화)"""
    return f"₩{amount:,.0f}"


def format_date(date_str: str) -> str:
    """날짜 포맷"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str


def show_success(message: str):
    """성공 메시지 표시"""
    st.success(f"✅ {message}")


def show_error(message: str):
    """에러 메시지 표시"""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """경고 메시지 표시"""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """정보 메시지 표시"""
    st.info(f"ℹ️ {message}")


def validate_positive_number(value, field_name: str) -> bool:
    """양수 검증"""
    if value <= 0:
        show_error(f"{field_name}은(는) 0보다 커야 합니다.")
        return False
    return True


def validate_non_negative_number(value, field_name: str) -> bool:
    """음수 아닌 값 검증"""
    if value < 0:
        show_error(f"{field_name}은(는) 0 이상이어야 합니다.")
        return False
    return True


def create_dataframe(data: list) -> pd.DataFrame:
    """리스트를 DataFrame으로 변환"""
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def export_to_csv(df: pd.DataFrame, filename: str):
    """DataFrame을 CSV로 내보내기"""
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )
