import streamlit as st
import sqlite3
import os

def create_sales_views(conn):
    """
    기존 로직을 바탕으로 DB 내에 2개의 View를 생성합니다.
    """
    cursor = conn.cursor()

    # 1. 판매계획 전처리 (매출리스트 컬럼명에 맞춤)
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_plan")
    cursor.execute("""
        CREATE VIEW view_cleaned_plan AS
        SELECT 
            strftime('%Y-%m', 계획년월) AS 기준월,
            매출처명,
            품명 AS 품목명,
            판매수량 AS 수량,
            판매금액 AS 장부금액
        FROM sales_plan_data
    """)

    # 2. 매출리스트 전처리 (필요한 컬럼만 선별)
    # 수정한 점: '품목명' 뒤에 누락되었던 콤마(,) 추가
    cursor.execute("DROP VIEW IF EXISTS view_cleaned_actual")
    cursor.execute("""
        CREATE VIEW view_cleaned_actual AS
        SELECT 
            strftime('%Y-%m', 매출일) AS 기준월,
            매출처명,
            품목명,
            수량,
            장부금액
        FROM sales_actual_data
    """)

    conn.commit()

def main():
    st.title("판매 데이터 DB View 생성기")

    # 1. 사이드바에서 DB 파일 업로드
    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.file_uploader("SQLite DB 파일을 업로드하세요", type=["db", "sqlite", "sqlite3"])

    if uploaded_file is not None:
        # 임시 파일로 저장하여 sqlite3에서 읽을 수 있게 함
        temp_db_path = "temp_sales_data.db"
        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # DB 연결
            conn = sqlite3.connect(temp_db_path)
            
            # 2. View 생성 버튼
            if st.button("전처리 View 생성 시작"):
                create_sales_views(conn)
                st.success("✅ 'view_cleaned_plan' 및 'view_cleaned_actual' 생성이 완료되었습니다!")
                
                # 생성된 View 확인 (선택 사항)
                st.info("DB 내 View가 성공적으로 구성되었습니다.")
            
            conn.close()
        except Exception as e:
            st.error(f"오류 발생: {e}")
        finally:
            # 작업 완료 후 임시 파일 삭제 여부는 운영 환경에 따라 결정
            pass
    else:
        st.info("사이드바에서 DB 파일을 먼저 업로드해 주세요.")

if __name__ == "__main__":
    main()
