"""
커스텀 CSS 스타일 및 UI 유틸리티
"""
import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests


def apply_global_styles():
    """전역 커스텀 CSS 적용"""
    st.markdown("""
    <style>
    /* ===== 폰트 ===== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    /* ===== 메인 컨테이너 ===== */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* ===== 사이드바 ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #e0e0e0;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.1);
    }

    /* ===== 메트릭 카드 ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #6c757d !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #212529 !important;
    }

    /* ===== 버튼 ===== */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        border: none;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
    }

    /* ===== 폼 ===== */
    [data-testid="stForm"] {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
    }

    /* ===== 입력 필드 ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1.5px solid #dee2e6;
        transition: border-color 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1976D2;
        box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
    }

    /* ===== 탭 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* ===== Expander ===== */
    .streamlit-expanderHeader {
        font-weight: 500;
        font-size: 1rem;
        border-radius: 8px;
    }

    /* ===== 데이터프레임 ===== */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    }

    /* ===== 알림 메시지 ===== */
    .stAlert {
        border-radius: 10px;
    }

    /* ===== 구분선 ===== */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #dee2e6, transparent);
        margin: 1.5rem 0;
    }

    /* ===== 스크롤바 ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #a1a1a1;
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, icon: str = "", delta: str = None):
    """커스텀 메트릭 카드"""
    delta_html = ""
    if delta:
        delta_color = "#28a745" if "정상" in delta else "#dc3545"
        delta_html = f'<div style="font-size:0.8rem; color:{delta_color}; margin-top:4px;">{delta}</div>'

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #e9ecef;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transition: transform 0.2s ease;
    ">
        <div style="font-size:0.85rem; color:#6c757d; font-weight:500; margin-bottom:6px;">
            {icon} {label}
        </div>
        <div style="font-size:1.8rem; font-weight:700; color:#212529;">
            {value}
        </div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """페이지 헤더"""
    sub_html = f'<p style="color:#6c757d; font-size:1rem; margin-top:4px;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="
            font-size: 2rem;
            font-weight: 700;
            color: #212529;
            margin-bottom: 0;
            letter-spacing: -0.5px;
        ">{title}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def sidebar_brand():
    """사이드바 브랜드 영역"""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.3rem;">📦</div>
        <div style="
            font-size: 1.4rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
        ">재고마스터</div>
        <div style="
            font-size: 0.75rem;
            color: rgba(255,255,255,0.5);
            margin-top: 2px;
        ">Inventory Control System</div>
    </div>
    """, unsafe_allow_html=True)


def load_lottie_url(url: str):
    """Lottie 애니메이션 URL에서 로드"""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# 자주 사용하는 Lottie 애니메이션 URL
LOTTIE_URLS = {
    "inventory": "https://lottie.host/e4e9a523-3a5f-4742-a853-aff6e32a5a04/oXpmIlYFjN.json",
    "loading":   "https://lottie.host/4db68bbd-31f6-4cd8-84eb-189de235dcc2/6aFDMJOfMt.json",
    "empty":     "https://lottie.host/2639b394-c2db-4a5a-a42b-7098e18c5af6/BjRrJikXul.json",
}
