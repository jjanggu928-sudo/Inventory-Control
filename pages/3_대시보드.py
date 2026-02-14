"""
대시보드 페이지
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.auth import require_auth
from utils.database import (
    get_products, get_transactions, get_low_stock_products,
    get_inventory_summary
)
from utils.helpers import format_currency

# 페이지 설정
st.set_page_config(page_title="대시보드 - 재고마스터", page_icon="📊", layout="wide")

# 인증 확인
require_auth()

st.title("📊 재고 현황 대시보드")

user_id = st.session_state['user_id']

# ===== 주요 지표 =====
summary = get_inventory_summary(user_id)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📦 총 상품 수",
        value=summary['total_products']
    )

with col2:
    st.metric(
        label="💰 총 재고 가치",
        value=format_currency(summary['total_stock_value'])
    )

with col3:
    st.metric(
        label="⚠️ 재고 부족 상품",
        value=summary['low_stock_count'],
        delta="주의 필요" if summary['low_stock_count'] > 0 else "정상",
        delta_color="inverse"
    )

st.divider()

# ===== 재고 부족 알림 =====
low_stock_products = get_low_stock_products(user_id)

if low_stock_products:
    with st.expander("⚠️ 재고 부족 상품 알림", expanded=True):
        for product in low_stock_products:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{product['name']}**")
            with col2:
                st.write(f"현재: {product['current_stock']}{product['unit']}")
            with col3:
                st.write(f"최소: {product['min_stock']}{product['unit']}")

st.divider()

# ===== 차트 영역 =====
products = get_products(user_id)
transactions = get_transactions(user_id, limit=100)

if products:
    # 2개 컬럼으로 차트 배치
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 카테고리별 상품 분포")
        
        # 카테고리별 집계
        category_counts = {}
        for p in products:
            category = p.get('category', '기타')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            fig_category = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                hole=0.4
            )
            fig_category.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
    
    with col2:
        st.subheader("💰 상품별 재고 가치")
        
        # 상품별 재고 가치 계산
        product_values = []
        for p in products:
            value = p['current_stock'] * p['unit_price']
            product_values.append({
                '상품명': p['name'],
                '재고가치': value
            })
        
        if product_values:
            df_values = pd.DataFrame(product_values).sort_values('재고가치', ascending=False).head(10)
            
            fig_value = px.bar(
                df_values,
                x='재고가치',
                y='상품명',
                orientation='h',
                text='재고가치'
            )
            fig_value.update_traces(texttemplate='₩%{text:,.0f}', textposition='outside')
            fig_value.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_value, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
    
    st.divider()
    
    # 입출고 추이
    if transactions:
        st.subheader("📈 입출고 추이 (최근 30일)")
        
        # 날짜별 입출고 집계
        trans_by_date = {}
        for trans in transactions:
            date = trans['transaction_date'][:10]
            trans_type = trans['type']
            
            if date not in trans_by_date:
                trans_by_date[date] = {'입고': 0, '출고': 0}
            
            trans_by_date[date][trans_type] += trans['quantity']
        
        # DataFrame 생성
        df_trend = pd.DataFrame([
            {'날짜': date, '입고': values['입고'], '출고': values['출고']}
            for date, values in sorted(trans_by_date.items())
        ])
        
        if not df_trend.empty:
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['날짜'],
                y=df_trend['입고'],
                mode='lines+markers',
                name='입고',
                line=dict(color='green', width=2)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=df_trend['날짜'],
                y=df_trend['출고'],
                mode='lines+markers',
                name='출고',
                line=dict(color='red', width=2)
            ))
            
            fig_trend.update_layout(
                xaxis_title="날짜",
                yaxis_title="수량",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
    
    st.divider()
    
    # 재고 현황 테이블
    st.subheader("📋 전체 재고 현황")
    
    # DataFrame 생성
    inventory_data = []
    for p in products:
        stock_status = '⚠️ 부족' if p['current_stock'] < p['min_stock'] else '✅ 정상'
        stock_value = p['current_stock'] * p['unit_price']
        
        inventory_data.append({
            '상품명': p['name'],
            '카테고리': p['category'],
            '현재재고': f"{p['current_stock']} {p['unit']}",
            '최소재고': f"{p['min_stock']} {p['unit']}",
            '단가': format_currency(p['unit_price']),
            '재고가치': format_currency(stock_value),
            '상태': stock_status
        })
    
    df_inventory = pd.DataFrame(inventory_data)
    
    st.dataframe(
        df_inventory,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("등록된 상품이 없습니다. '상품관리' 메뉴에서 상품을 먼저 등록해주세요.")
