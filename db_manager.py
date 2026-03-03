# db_manager.py
import sqlite3
from config import COLUMN_MAP

def create_integrated_sales_view(conn):
    cursor = conn.cursor()
    
    # 1. 계획(Plan)용 컬럼 구성
    plan_cols_list = []
    for std, plan_orig, _ in COLUMN_MAP:
        if std == "매출연월":
            plan_cols_list.append(f"STRFTIME('%Y-%m', P.{plan_orig}) AS {std}")
        else:
            plan_cols_list.append(f"P.{plan_orig} AS {std}")

    # 2. 실적(Actual)용 컬럼 구성
    actual_cols_list = []
    for std, _, actual_orig in COLUMN_MAP:
        if std == "매출연월":
            actual_cols_list.append(f"STRFTIME('%Y-%m', A.{actual_orig}) AS {std}")
        elif std == "고객그룹":
            # 실적 테이블에 없으므로 마스터 테이블(M)에서 가져옴
            actual_cols_list.append(f"M.고객그룹 AS {std}")
        else:
            actual_cols_list.append(f"A.{actual_orig} AS {std}")

    plan_cols = ", ".join(plan_cols_list)
    actual_cols = ", ".join(actual_cols_list)

    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    
    # SQL 수정: 실적 데이터 조회 시 customer_master와 JOIN
    sql = f"""
        CREATE VIEW view_integrated_sales AS
        SELECT '판매계획' AS 데이터구분, {plan_cols} 
        FROM sales_plan_data AS P
        
        UNION ALL
        
        SELECT '판매실적' AS 데이터구분, {actual_cols} 
        FROM sales_actual_data AS A
        LEFT JOIN customer_master AS M ON A.매출처 = M.매출처
    """
    
    cursor.execute(sql)
    conn.commit()
