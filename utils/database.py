"""
Supabase 데이터베이스 연결 및 쿼리 함수
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 초기화
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL과 SUPABASE_KEY를 .env 파일에 설정해주세요.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase_client() -> Client:
    """Supabase 클라이언트 반환"""
    return supabase


# ===== 상품 관리 함수 =====

def get_products(user_id: str):
    """사용자의 모든 상품 조회"""
    try:
        response = supabase.table('products')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        return response.data
    except Exception as e:
        print(f"상품 조회 오류: {e}")
        return []


def get_product_by_id(product_id: str):
    """특정 상품 조회"""
    try:
        response = supabase.table('products')\
            .select('*')\
            .eq('id', product_id)\
            .single()\
            .execute()
        return response.data
    except Exception as e:
        print(f"상품 조회 오류: {e}")
        return None


def create_product(user_id: str, product_data: dict):
    """새 상품 등록"""
    try:
        product_data['user_id'] = user_id
        response = supabase.table('products').insert(product_data).execute()
        return response.data
    except Exception as e:
        print(f"상품 등록 오류: {e}")
        return None


def update_product(product_id: str, product_data: dict):
    """상품 정보 수정"""
    try:
        response = supabase.table('products')\
            .update(product_data)\
            .eq('id', product_id)\
            .execute()
        return response.data
    except Exception as e:
        print(f"상품 수정 오류: {e}")
        return None


def delete_product(product_id: str):
    """상품 삭제"""
    try:
        response = supabase.table('products')\
            .delete()\
            .eq('id', product_id)\
            .execute()
        return True
    except Exception as e:
        print(f"상품 삭제 오류: {e}")
        return False


# ===== 입출고 관리 함수 =====

def get_transactions(user_id: str, product_id: str = None, limit: int = 100):
    """입출고 내역 조회"""
    try:
        query = supabase.table('transactions')\
            .select('*, products(name, sku)')\
            .eq('user_id', user_id)\
            .order('transaction_date', desc=True)\
            .limit(limit)
        
        if product_id:
            query = query.eq('product_id', product_id)
        
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"입출고 내역 조회 오류: {e}")
        return []


def create_transaction(user_id: str, transaction_data: dict):
    """입출고 등록 및 재고 업데이트"""
    try:
        # 입출고 기록 추가
        transaction_data['user_id'] = user_id
        trans_response = supabase.table('transactions').insert(transaction_data).execute()
        
        # 재고 업데이트
        product_id = transaction_data['product_id']
        quantity = transaction_data['quantity']
        trans_type = transaction_data['type']
        
        # 현재 재고 조회
        product = get_product_by_id(product_id)
        if product:
            current_stock = product.get('current_stock', 0)
            
            # 입고면 +, 출고면 -
            if trans_type == '입고':
                new_stock = current_stock + quantity
            else:  # 출고
                new_stock = current_stock - quantity
            
            # 재고 업데이트
            update_product(product_id, {'current_stock': new_stock})
        
        return trans_response.data
    except Exception as e:
        print(f"입출고 등록 오류: {e}")
        return None


def get_low_stock_products(user_id: str):
    """재고 부족 상품 조회 (현재재고 < 최소재고)"""
    try:
        # Supabase에서는 computed column을 사용하거나 클라이언트에서 필터링
        products = get_products(user_id)
        low_stock = [
            p for p in products 
            if p.get('current_stock', 0) < p.get('min_stock', 0)
        ]
        return low_stock
    except Exception as e:
        print(f"재고 부족 상품 조회 오류: {e}")
        return []


# ===== 통계 함수 =====

def get_inventory_summary(user_id: str):
    """재고 요약 통계"""
    try:
        products = get_products(user_id)
        
        total_products = len(products)
        total_stock_value = sum(
            p.get('current_stock', 0) * p.get('unit_price', 0) 
            for p in products
        )
        low_stock_count = len(get_low_stock_products(user_id))
        
        return {
            'total_products': total_products,
            'total_stock_value': total_stock_value,
            'low_stock_count': low_stock_count
        }
    except Exception as e:
        print(f"통계 조회 오류: {e}")
        return {
            'total_products': 0,
            'total_stock_value': 0,
            'low_stock_count': 0
        }
