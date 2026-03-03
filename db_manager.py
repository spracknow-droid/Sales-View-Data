# db_manager.py
import sqlite3
from config import COLUMN_MAP

def create_integrated_sales_view(conn):
    cursor = conn.cursor()
    
    plan_cols_list = []
    actual_cols_list = []

    for std, plan_orig, actual_orig in COLUMN_MAP:
        # 1. 날짜 처리
        if std == "매출연월":
            plan_cols_list.append(f"STRFTIME('%Y-%m', P.{plan_orig}) AS {std}")
            actual_cols_list.append(f"STRFTIME('%Y-%m', A.{actual_orig}) AS {std}")
        
        # 2. 고객그룹 처리 (두 테이블 모두 마스터에서 가져오도록 통일)
        elif std == "고객그룹":
            plan_cols_list.append(f"M.고객그룹 AS {std}")
            actual_cols_list.append(f"M.고객그룹 AS {std}")
            
        # 3. 기타 컬럼
        else:
            plan_cols_list.append(f"P.{plan_orig} AS {std}")
            actual_cols_list.append(f"A.{actual_orig} AS {std}")

    plan_cols = ", ".join(plan_cols_list)
    actual_cols = ", ".join(actual_cols_list)

    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    
    # 판매계획(P)과 판매실적(A) 모두 마스터 테이블(M)과 JOIN 합니다.
    sql = f"""
        CREATE VIEW view_integrated_sales AS
        SELECT '판매계획' AS 데이터구분, {plan_cols} 
        FROM sales_plan_data AS P
        LEFT JOIN customer_master AS M ON P.매출처 = M.매출처
        
        UNION ALL
        
        SELECT '판매실적' AS 데이터구분, {actual_cols} 
        FROM sales_actual_data AS A
        LEFT JOIN customer_master AS M ON A.매출처 = M.매출처
    """
    
    cursor.execute(sql)
    conn.commit()
