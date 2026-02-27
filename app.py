import streamlit as st
import sqlite3
import pandas as pd
import os

def create_integrated_sales_view(conn):
    """
    서로 다른 형식의 계획과 실적 테이블을 표준화하여 하나의 통합 View로 생성합니다.
    '데이터구분' 값을 '판매계획'과 '판매실적'으로 설정합니다.
    """
    cursor = conn.cursor()

    # 기존 View 정리
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_plan")
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_actual")
    
    # 통합 View 생성 (수정: 데이터구분 명칭 변경)
    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    cursor.execute("""
        CREATE VIEW view_integrated_sales AS
        /* 1. 판매계획 데이터 표준화 */
        SELECT 
            '판매계획' AS 데이터구분,
            strftime('%Y-%m', 계획년월) AS 매출연월,
            매출처명,
            품명 AS 품목명,
            판매수량 AS 수량,
            판매금액 AS 장부금액
        FROM sales_plan_data
        
        UNION ALL
        
        /* 2. 매출실적 데이터 표준화 */
        SELECT 
            '판매실적' AS 데이터구분,
            strftime('%Y-%m', 매출일) AS 매출연월,
            매출처명,
            품목명,
            수량,
            장부금액
        FROM sales_actual_data
    """)

    conn.commit()

def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    st.title("📊 판매 데이터 표준화 통합 뷰")

    # 1. 사이드바에서 DB 파일 업로드
    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.file_uploader("SQLite DB 파일을 업로드하세요", type=["db", "sqlite", "sqlite3"])

    if uploaded_file is not None:
        # 임시 파일 저장
        temp_db_path = "temp_sales_data.db"
        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # DB 연결
            conn = sqlite3.connect(temp_db_path)
            
            # 업로드 즉시 View 생성
            create_integrated_sales_view(conn)
            st.sidebar.success("✅ 통합 View 생성 완료")

            # 결과 출력
            st.subheader("📋 통합 판매 데이터 (view_integrated_sales)")
            
            try:
                df_integrated = pd.read_sql_query("SELECT * FROM view_integrated_sales", conn)
                
                if not df_integrated.empty:
                    # 데이터프레임 출력
                    st.dataframe(df_integrated, use_container_width=True)
                    
                    # 요약 정보
                    st.write(f"총 데이터: {len(df_integrated)} 건")
                else:
                    st.info("데이터가 존재하지 않습니다.")
                    
            except Exception as e:
                st.warning(f"View를 조회할 수 없습니다. 테이블 구조를 확인하세요. ({e})")
            
            conn.close()

        except Exception as e:
            st.error(f"DB 연결 오류: {e}")
    else:
        st.info("왼쪽 사이드바에서 DB 파일을 업로드하면 '판매계획'과 '판매실적'이 통합된 View가 생성됩니다.")

if __name__ == "__main__":
    main()
