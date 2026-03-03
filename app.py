# app.py
import streamlit as st
import os
import sqlite3
from config import TEMP_DB_PATH
from db_manager import create_integrated_sales_view
from data_processor import fetch_integrated_data
from utils import convert_df_to_excel

def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    
    st.title("🚀 판매 데이터 통합 시스템")
    
    # 사이드바 설정
    st.sidebar.header("설정")
    uploaded_file = st.sidebar.file_uploader("DB 파일을 업로드하세요 (.db)", type="db")

    # [수정] 업로드 전 화면 구성
    if not uploaded_file:
        st.info("왼쪽 사이드바에서 SQLite DB 파일(.db)을 업로드해 주세요.")
        st.write("판매계획, 판매실적, 고객마스터를 통합하여 VIEW를 생성합니다.")
        return # 업로드 전에는 아래 로직 실행 안 함

    # 파일 저장 로직
    with open(TEMP_DB_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # 1. 뷰 생성 (DB 매니저 호출)
        with sqlite3.connect(TEMP_DB_PATH) as conn:
            create_integrated_sales_view(conn)
        
        # 2. 데이터 조회 (데이터 프로세서 호출)
        df = fetch_integrated_data(TEMP_DB_PATH)

        # 3. 화면 표시
        st.subheader("📊 통합 판매 데이터 미리보기")
        st.dataframe(df, use_container_width=True)
        
        # [추가] 다운로드 섹션
        st.divider()
        st.subheader("📥 데이터 다운로드")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1) 통합 뷰가 포함된 DB 파일 다운로드
            with open(TEMP_DB_PATH, "rb") as db_file:
                st.download_button(
                    label="💾 통합 DB 파일 다운로드 (.db)",
                    data=db_file,
                    file_name="integrated_sales_data.db",
                    mime="application/octet-stream",
                    help="고객그룹 뷰가 포함된 전체 DB 파일을 다운로드합니다."
                )
        
        with col2:
            # 2) 검증용 엑셀 파일 다운로드 (df를 엑셀로 변환)
            excel_data = convert_df_to_excel(df)
            st.download_button(
                label="xlsx 검증용 엑셀 다운로드 (.xlsx)",
                data=excel_data,
                file_name="sales_verification.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="현재 화면에 보이는 데이터를 엑셀로 저장합니다."
            )

    except Exception as e:
        st.error(f"오류 발생: {e}")
        st.exception(e) # 자세한 에러 로그 출력

if __name__ == "__main__":
    main()
