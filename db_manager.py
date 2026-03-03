# db_manager.py
import sqlite3
from config import COLUMN_MAP

def create_integrated_sales_view(conn):
    cursor = conn.cursor()
    plan_cols_list = []
    actual_cols_list = []

    for std, plan_orig, actual_orig in COLUMN_MAP:
        if std == "매출연월":
            plan_cols_list.append(f"STRFTIME('%Y-%m', {plan_orig}) AS {std}")
            actual_cols_list.append(f"STRFTIME('%Y-%m', {actual_orig}) AS {std}")
        else:
            plan_cols_list.append(f"{plan_orig} AS {std}")
            actual_cols_list.append(f"{actual_orig} AS {std}")

    plan_cols = ", ".join(plan_cols_list)
    actual_cols = ", ".join(actual_cols_list)

    cursor.execute("DROP VIEW IF EXISTS view_integrated_sales")
    
    sql = f"""
        CREATE VIEW view_integrated_sales AS
        SELECT '판매계획' AS 데이터구분, {plan_cols} FROM sales_plan_data
        UNION ALL
        SELECT '판매실적' AS 데이터구분, {actual_cols} FROM sales_actual_data
    """
    cursor.execute(sql)
    conn.commit()
