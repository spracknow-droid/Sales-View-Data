import sqlite3

# 표준화할 컬럼 리스트 정의 (나중에 여기만 수정하면 됨)
# 형식: (표준컬럼명, 판매계획원본컬럼, 판매실적원본컬럼)
COLUMN_MAP = [
    ("매출연월", "계획년월", "매출일"),
    ("매출처명", "매출처명", "매출처명"),
    ("품목명", "품명", "품목명"),
    ("수량", "판매수량", "수량"),
    ("장부금액", "판매금액", "장부금액")
]

def create_integrated_sales_view(conn):
    """
    COLUMN_MAP에 정의된 리스트를 바탕으로 통합 View를 생성합니다.
    """
    cursor = conn.cursor()

    # 1. 판매계획 쿼리 구성
    plan_cols = ", ".join([f"strftime('%Y-%m', {orig}) AS {std}" if std == "매출연월" 
                           else f"{orig} AS {std}" for std, orig, _ in COLUMN_MAP])
    
    # 2. 판매실적 쿼리 구성
    actual_cols = ", ".join([f"strftime('%Y-%m', {orig}) AS {std}" if std == "매출연월" 
                             else f"{orig} AS {std}" for std, _, orig in COLUMN_MAP])

    # 통합 View 생성
    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    sql = f"""
        CREATE VIEW view_integrated_sales AS
        SELECT '판매계획' AS 데이터구분, {plan_cols}
        FROM sales_plan_data
        UNION ALL
        SELECT '판매실적' AS 데이터구분, {actual_cols}
        FROM sales_actual_data
    """
    
    cursor.execute(sql)
    conn.commit()

def get_view_data(conn):
    """
    생성된 View의 데이터를 가져오는 함수
    """
    import pandas as pd
    return pd.read_sql_query("SELECT * FROM view_integrated_sales", conn)
