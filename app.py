import streamlit as st
import sqlite3
import os
import io
import pandas as pd
from database import create_integrated_sales_view, get_view_data


def convert_df_to_excel(df):
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output) as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()
    except Exception as e:
        return str(e)


def main():
    st.set_page_config(page_title="Sales Data Integrator", layout="wide")
    st.title("판매 데이터 통합 View")

    uploaded_file = st.sidebar.file_uploader(
        "SQLite DB 파일 업로드",
        type=["db", "sqlite", "sqlite3"]
    )

    if uploaded_file:

        temp_db_path = "temp_sales_data.db"

        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

        with open(temp_db_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            conn = sqlite3.connect(temp_db_path)

            st.write("① DB 연결 성공")

            create_integrated_sales_view(conn)
            st.write("② View 생성 성공")

            df = get_view_data(conn)
            st.write("③ 데이터 로드 성공")

            st.write("📊 DF shape:", df.shape)
            st.write("📊 DF empty:", df.empty)

            # ✅ 버튼을 조건 없이 항상 표시
            excel_data = convert_df_to_excel(df)

            st.write("④ 엑셀 변환 타입:", type(excel_data))

            if isinstance(excel_data, bytes):
                st.download_button(
                    "📂 엑셀 다운로드",
                    data=excel_data,
                    file_name="integrated_sales_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.write("⑤ 다운로드 버튼 생성 완료")
            else:
                st.error(f"엑셀 변환 실패: {excel_data}")

            st.dataframe(df, use_container_width=True)

            conn.close()

        except Exception as e:
            st.error(f"🔥 실행 중 오류 발생: {e}")

    else:
        st.info("DB 파일을 업로드하세요.")


if __name__ == "__main__":
    main()
