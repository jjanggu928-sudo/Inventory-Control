"""
바코드 스캔 유틸리티
- 카메라로 촬영한 이미지에서 바코드/QR코드 디코딩
"""
import streamlit as st
from PIL import Image
import zxingcpp


def decode_barcode(image: Image.Image) -> list:
    """이미지에서 바코드/QR코드 디코딩"""
    try:
        results = zxingcpp.read_barcodes(image)
        return results
    except Exception as e:
        st.error(f"바코드 인식 오류: {e}")
        return []


def scan_barcode_ui(key_prefix: str = "barcode") -> str | None:
    """바코드 스캔 UI 컴포넌트 (카메라 촬영 방식)

    Returns:
        디코딩된 바코드 문자열 또는 None
    """
    camera_image = st.camera_input(
        "📷 바코드를 카메라에 비춰주세요",
        key=f"{key_prefix}_camera"
    )

    if camera_image is not None:
        image = Image.open(camera_image)
        results = decode_barcode(image)

        if results:
            barcode_value = results[0].text
            barcode_format = results[0].format.name if hasattr(results[0].format, 'name') else str(results[0].format)
            st.success(f"✅ 바코드 인식 성공! [{barcode_format}] **{barcode_value}**")
            return barcode_value
        else:
            st.warning("⚠️ 바코드를 인식하지 못했습니다. 다시 촬영해주세요.")
            st.caption("💡 팁: 바코드가 선명하게 보이도록 가까이에서 촬영하세요.")

    return None


def get_product_by_barcode(user_id: str, barcode: str):
    """바코드(SKU)로 상품 조회"""
    from .database import supabase
    try:
        response = supabase.table('products')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('sku', barcode)\
            .execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"상품 조회 오류: {e}")
        return None
