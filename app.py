import streamlit as st
import sqlite3
import os
import io
import pandas as pd
from database import create_integrated_sales_view, get_view_data

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
            
            # 1. View 생성 (리스트 기반 로직 실행)
            create_integrated_sales_view(conn)
            st.sidebar.success("✅ 통합 View 생성 완료")

            # 2. 데이터 가져오기 및 출력
            st.subheader("📋 판매 분석을 위한 View Table")
            df = get_view_data(conn)
            
            if not df.empty:
                # 엑셀 다운로드 로직 준비
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                excel_data = output.getvalue()

                # 다운로드 버튼 추가
                st.download_button(
                    label="📂 엑셀 파일로 다운로드",
                    data=excel_data,
                    file_name="integrated_sales_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # 데이터프레임 화면 표시
                st.dataframe(df, use_container_width=True)
                st.write(f"총 데이터: {len(df)} 건")
            else:
                st.info("데이터가 존재하지 않습니다.")
            
            conn.close()
        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.info("사이드바에서 DB 파일을 업로드해주세요.")

if __name__ == "__main__":
    main()
