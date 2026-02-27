import streamlit as st
import sqlite3
import os
import io
import pandas as pd
from database import create_integrated_sales_view, get_view_data

# 엑셀 변환 로직을 캐싱하여 중복 연산을 방지합니다.
@st.cache_data
def convert_df_to_excel(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue()
    except Exception as e:
        return e

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

            # 2. 데이터 가져오기
            df = get_view_data(conn)
            
            if not df.empty:
                st.subheader("📋 판매 분석을 위한 View Table")
                
                # [강력 조치] 버튼을 데이터프레임보다 위에 배치하고 레이아웃을 분리합니다.
                menu_col1, menu_col2 = st.columns([1, 4])
                
                with menu_col1:
                    # 엑셀 변환 시도
                    excel_data = convert_df_to_excel(df)
                    
                    if isinstance(excel_data, bytes):
                        st.download_button(
                            label="📂 엑셀 다운로드",
                            data=excel_data,
                            file_name="integrated_sales_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key='btn_download_excel'
                        )
                    else:
                        st.error("엑셀 변환 실패")
                
                with menu_col2:
                    st.write(f"📊 총 {len(df)}건의 데이터가 로드되었습니다.")

                # 데이터프레임 표시
                st.dataframe(df, use_container_width=True)
                
            else:
                st.info("데이터가 존재하지 않습니다.")
            
            conn.close()
        except Exception as e:
            st.error(f"실행 중 오류 발생: {e}")
    else:
        st.info("사이드바에서 DB 파일을 업로드해주세요.")

if __name__ == "__main__":
    main()
