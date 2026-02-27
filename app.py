import streamlit as st
import sqlite3
import os
import io
import pandas as pd
from database import create_integrated_sales_view, get_view_data

def convert_df_to_excel(df):
    """데이터프레임을 엑셀 바이트로 변환"""
    output = io.BytesIO()
    # xlsxwriter 엔진을 사용하여 엑셀 파일 생성
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    st.title("판매 데이터 통합 View")

    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.file_uploader("SQLite DB 파일을 업로드하세요", type=["db", "sqlite", "sqlite3"])

    if uploaded_file is not None:
        temp_db_path = "temp_sales_data.db"
        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            conn = sqlite3.connect(temp_db_path)
            
            # 1. View 생성
            create_integrated_sales_view(conn)
            st.sidebar.success("✅ 통합 View 생성 완료")

            # 2. 데이터 가져오기 및 출력
            st.subheader("📋 판매 분석을 위한 View Table")
            df = get_view_data(conn)
            
            if not df.empty:
                # [수정] 데이터프레임을 먼저 화면에 뿌려줍니다 (사용자 대기 시간 감소)
                st.dataframe(df, use_container_width=True)
                st.write(f"총 데이터: {len(df)} 건")

                # [수정] 엑셀 변환 및 다운로드 버튼 배치 (데이터 아래쪽)
                excel_data = convert_df_to_excel(df)
                
                st.download_button(
                    label="📂 엑셀 파일로 다운로드",
                    data=excel_data,
                    file_name="integrated_sales_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='download-excel' # 버튼을 고유하게 식별하기 위한 키 추가
                )
            else:
                st.info("데이터가 존재하지 않습니다.")
            
            conn.close()
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.info("사이드바에서 DB 파일을 업로드해주세요.")

if __name__ == "__main__":
    main()
