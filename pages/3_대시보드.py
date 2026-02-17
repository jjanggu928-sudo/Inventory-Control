"""
대시보드 페이지
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.auth import require_auth
from utils.database import get_products, get_transactions, get_low_stock_products, get_inventory_summary
from utils.helpers import format_currency
from utils.styles import apply_global_styles, page_header, sidebar_brand

st.set_page_config(page_title="대시보드 - 재고마스터", page_icon="📊", layout="wide")
apply_global_styles()
require_auth()

with st.sidebar:
    sidebar_brand()

page_header("📊 재고 대시보드", "전체 재고 현황과 통계를 확인하세요")

user_id = st.session_state['user_id']
summary = get_inventory_summary(user_id)

# ===== KPI 카드 =====
col1, col2, col3 = st.columns(3)
kpis = [
    ("📦 총 상품 수", f"{summary['total_products']}개", "#1976D2", "#e3f2fd"),
    ("💰 총 재고 가치", f"₩{summary['total_stock_value']:,.0f}", "#388E3C", "#e8f5e9"),
    ("⚠️ 재고 부족", f"{summary['low_stock_count']}개",
     "#F57C00" if summary['low_stock_count'] > 0 else "#388E3C",
     "#fff3e0" if summary['low_stock_count'] > 0 else "#e8f5e9"),
]
for col, (label, val, color, bg) in zip([col1, col2, col3], kpis):
    with col:
        st.markdown(f"""
        <div style="background:{bg};border-radius:14px;padding:1.4rem 1.6rem;border-left:4px solid {color};
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-size:0.85rem;color:{color};font-weight:600;margin-bottom:6px;">{label}</div>
            <div style="font-size:2rem;font-weight:700;color:#212529;">{val}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ===== 재고 부족 알림 =====
low_stock_products = get_low_stock_products(user_id)
if low_stock_products:
    with st.expander(f"⚠️  재고 부족 상품 {len(low_stock_products)}개 — 클릭하여 확인", expanded=True):
        for p in low_stock_products:
            pct = int(p['current_stock'] / max(p['min_stock'], 1) * 100)
            color = "#dc3545" if pct < 50 else "#fd7e14"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;padding:0.6rem 1rem;
                        background:#fff5f5;border-radius:8px;margin-bottom:0.4rem;border-left:3px solid {color};">
                <span style="font-weight:600;flex:1;color:#212529;">{p['name']}</span>
                <span style="color:{color};font-weight:700;">{p['current_stock']}{p['unit']}</span>
                <span style="color:#adb5bd;font-size:0.85rem;">/ 최소 {p['min_stock']}{p['unit']}</span>
                <span style="background:{color};color:#fff;font-size:0.75rem;
                             padding:2px 8px;border-radius:20px;font-weight:600;">{pct}%</span>
            </div>""", unsafe_allow_html=True)

st.divider()

# ===== 차트 영역 =====
products = get_products(user_id)
transactions = get_transactions(user_id, limit=200)

if products:
    col1, col2 = st.columns(2)

    # 카테고리별 파이 차트
    with col1:
        st.markdown("##### 📦 카테고리별 상품 분포")
        cat_counts = {}
        for p in products:
            c = p.get('category', '기타')
            cat_counts[c] = cat_counts.get(c, 0) + 1

        fig = px.pie(
            values=list(cat_counts.values()),
            names=list(cat_counts.keys()),
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
            height=320,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

    # 상품별 재고 가치 바 차트
    with col2:
        st.markdown("##### 💰 상품별 재고 가치 Top 10")
        product_values = sorted(
            [{'상품명': p['name'], '재고가치': p['current_stock'] * p['unit_price']} for p in products],
            key=lambda x: x['재고가치'], reverse=True
        )[:10]

        if product_values:
            df_v = pd.DataFrame(product_values)
            fig2 = px.bar(
                df_v, x='재고가치', y='상품명', orientation='h',
                color='재고가치', color_continuous_scale='Blues',
                text='재고가치'
            )
            fig2.update_traces(texttemplate='₩%{text:,.0f}', textposition='outside')
            fig2.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(t=10, b=10, l=10, r=80),
                coloraxis_showscale=False,
                height=320,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # 입출고 추이 라인 차트
    if transactions:
        st.markdown("##### 📈 입출고 추이")
        trans_by_date: dict = {}
        for t in transactions:
            date = t['transaction_date'][:10]
            if date not in trans_by_date:
                trans_by_date[date] = {'입고': 0, '출고': 0}
            trans_by_date[date][t['type']] += t['quantity']

        df_trend = pd.DataFrame([
            {'날짜': d, '입고': v['입고'], '출고': v['출고']}
            for d, v in sorted(trans_by_date.items())
        ])

        if not df_trend.empty:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df_trend['날짜'], y=df_trend['입고'],
                mode='lines+markers', name='입고',
                line=dict(color='#28a745', width=2.5),
                marker=dict(size=7, color='#28a745'),
                fill='tozeroy', fillcolor='rgba(40,167,69,0.08)'
            ))
            fig3.add_trace(go.Scatter(
                x=df_trend['날짜'], y=df_trend['출고'],
                mode='lines+markers', name='출고',
                line=dict(color='#dc3545', width=2.5),
                marker=dict(size=7, color='#dc3545'),
                fill='tozeroy', fillcolor='rgba(220,53,69,0.08)'
            ))
            fig3.update_layout(
                hovermode='x unified',
                xaxis_title="날짜", yaxis_title="수량",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                margin=dict(t=30, b=10, l=10, r=10),
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
                yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            )
            st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # 전체 재고 현황 테이블
    st.markdown("##### 📋 전체 재고 현황")
    inventory_data = [{
        '상품명': p['name'],
        '카테고리': p['category'],
        '현재재고': f"{p['current_stock']} {p['unit']}",
        '최소재고': f"{p['min_stock']} {p['unit']}",
        '단가': format_currency(p['unit_price']),
        '재고가치': format_currency(p['current_stock'] * p['unit_price']),
        '상태': '⚠️ 부족' if p['current_stock'] < p['min_stock'] else '✅ 정상'
    } for p in products]

    st.dataframe(pd.DataFrame(inventory_data), use_container_width=True, hide_index=True)

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem;background:#f8f9fa;border-radius:14px;border:2px dashed #dee2e6;">
        <div style="font-size:3.5rem;margin-bottom:0.8rem;">📊</div>
        <div style="font-weight:700;font-size:1.1rem;color:#495057;margin-bottom:0.4rem;">데이터가 없습니다</div>
        <div style="color:#adb5bd;font-size:0.9rem;">상품관리에서 상품을 등록하면 차트가 표시됩니다</div>
    </div>
    """, unsafe_allow_html=True)
