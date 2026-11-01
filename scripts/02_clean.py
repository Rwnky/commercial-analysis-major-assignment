from pathlib import Path
import pandas as pd
import numpy as np
import sqlite3
import json

# 路径配置
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)


def load_data():
    print("1. 正在加载原始数据...")
    orders = pd.read_csv(RAW / "olist_orders_dataset.csv")
    items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
    customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
    products = pd.read_csv(RAW / "olist_products_dataset.csv")
    payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
    translation = pd.read_csv(RAW / "product_category_name_translation.csv")

    # 核心：只保留已送达的订单（做用户分析和留存预测，需要确定完成的订单）
    print(f"清洗前订单数: {len(orders)}")
    orders = orders[orders['order_status'] == 'delivered'].copy()
    print(f"筛选已送达(delivered)订单数: {len(orders)}")
    return orders, items, customers, products, payments, translation


def clean_and_merge(orders, items, customers, products, payments, translation):
    print("2. 正在清洗数据并转换类型...")

    # --- 清洗订单表 ---
    date_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])

    # 剔除没有送达时间的异常订单
    orders = orders.dropna(subset=['order_delivered_customer_date'])

    # --- 清洗商品表 ---
    # 填补缺失的品类名称
    products['product_category_name'] = products['product_category_name'].fillna('unknown')
    # 合并英文品类名称
    products = products.merge(translation, on='product_category_name', how='left')
    products['product_category_name_english'] = products['product_category_name_english'].fillna('unknown')

    # --- 多表关联（构建宽表） ---
    print("3. 正在执行多表主外键对齐...")
    # items 和 orders 关联
    df = items.merge(orders, on='order_id', how='inner')
    # 关联商品信息
    df = df.merge(products[['product_id', 'product_category_name_english']], on='product_id', how='left')
    # 关联用户信息
    df = df.merge(customers[['customer_id', 'customer_unique_id', 'customer_state', 'customer_city']], on='customer_id',
                  how='left')

    # 关联支付信息（因为一个订单可能有多笔支付，我们求和汇总）
    pay_agg = payments.groupby('order_id')['payment_value'].sum().reset_index()
    df = df.merge(pay_agg, on='order_id', how='left')

    # --- 指标派生 ---
    # 计算总金额 = 商品价格 + 运费
    df['total_amount'] = df['price'] + df['freight_value']
    # 提取订单年月，用于后续同期群分析
    df['order_year_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    df['order_year'] = df['order_purchase_timestamp'].dt.year

    print(f"宽表构建完成，记录数: {len(df)}")
    return df


def export_data(df):
    print("4. 正在导出清洗后的数据...")

    # 1. 导出为 CSV
    csv_path = CLEAN / "olist_cleaned_wide_table.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"CSV 导出成功: {csv_path.name}")

    # 2. 导出为 JSON (取前1000条即可，主要用于验证)
    json_path = CLEAN / "olist_sample.json"
    df.head(1000).to_json(json_path, orient='records', force_ascii=False, indent=2)
    print(f"JSON 导出成功: {json_path.name}")

    # 3. 导出为 SQLite
    db_path = CLEAN / "olist.db"
    conn = sqlite3.connect(db_path)
    df.to_sql('orders_wide', conn, if_exists='replace', index=False)
    conn.close()
    print(f"SQLite 导出成功: {db_path.name}")


def main():
    orders, items, customers, products, payments, translation = load_data()
    df = clean_and_merge(orders, items, customers, products, payments, translation)
    export_data(df)
    print("\n✅ 数据清洗与治理全部完成！")


if __name__ == "__main__":
    main()