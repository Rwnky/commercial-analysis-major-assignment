import pandas as pd
import numpy as np
from pathlib import Path

# 路径配置
ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
TABLES = ROOT / "outputs" / "tables"
TABLES.mkdir(parents=True, exist_ok=True)


def load_clean_data():
    print("1. 正在加载清洗后的宽表...")
    df = pd.read_csv(CLEAN / "olist_cleaned_wide_table.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df


def rfm_model(df):
    print("2. 正在计算 RFM 模型...")
    # 提取订单级别去重，避免同一个订单多个商品导致计算偏差
    order_df = df.drop_duplicates(subset=['order_id'])

    # 计算订单总金额 (宽表中的 total_amount 是 item 级别的，需要按订单聚合)
    order_amt = df.groupby('order_id')['total_amount'].sum().reset_index()
    order_df = order_df.merge(order_amt, on='order_id', suffixes=('', '_corrected'))

    # 观察日期：数据集最后一天 + 1天
    snapshot_date = order_df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    # 按用户聚合 R, F, M
    rfm = order_df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'total_amount_corrected': 'sum'  # Monetary
    }).reset_index()

    rfm.rename(columns={
        'order_purchase_timestamp': 'R',
        'order_id': 'F',
        'total_amount_corrected': 'M'
    }, inplace=True)

    # 根据中位数划分高低（中位数比均值更稳健，不受极端大客户影响）
    r_median = rfm['R'].median()
    f_median = rfm['F'].median()
    m_median = rfm['M'].median()

    def classify_rfm(row):
        # R 越小说明最近买过，属于高 R
        is_high_r = row['R'] <= r_median
        is_high_f = row['F'] >= f_median
        is_high_m = row['M'] >= m_median

        if is_high_r and is_high_f and is_high_m:
            return '重要价值客户'
        elif not is_high_r and is_high_f and is_high_m:
            return '重要保持客户'
        elif is_high_r and not is_high_f and is_high_m:
            return '重要发展客户'
        elif not is_high_r and not is_high_f and is_high_m:
            return '重要挽留客户'
        elif is_high_r and is_high_f and not is_high_m:
            return '一般价值客户'
        elif not is_high_r and is_high_f and not is_high_m:
            return '一般保持客户'
        elif is_high_r and not is_high_f and not is_high_m:
            return '一般发展客户'
        else:
            return '一般挽留客户'

    rfm['Customer_Segment'] = rfm.apply(classify_rfm, axis=1)

    # 保存用户明细和分类统计
    rfm.to_csv(TABLES / "rfm_model_results.csv", index=False)
    segment_counts = rfm['Customer_Segment'].value_counts().reset_index()
    segment_counts.columns = ['Customer_Segment', 'Count']
    segment_counts.to_csv(TABLES / "rfm_segment_counts.csv", index=False)
    print("✅ RFM 模型计算完成！")


def cohort_model(df):
    print("3. 正在计算 同期群(Cohort) 留存模型...")
    cohort_df = df[['customer_unique_id', 'order_purchase_timestamp']].drop_duplicates()
    cohort_df['OrderMonth'] = cohort_df['order_purchase_timestamp'].dt.to_period('M')

    # 获取每个用户的首购月份
    cohort_df['CohortMonth'] = cohort_df.groupby('customer_unique_id')['OrderMonth'].transform('min')

    # 计算距离首购的月份差 (CohortIndex)
    order_year, order_month = cohort_df['OrderMonth'].dt.year, cohort_df['OrderMonth'].dt.month
    cohort_year, cohort_month = cohort_df['CohortMonth'].dt.year, cohort_df['CohortMonth'].dt.month

    years_diff = order_year - cohort_year
    months_diff = order_month - cohort_month
    cohort_df['CohortIndex'] = years_diff * 12 + months_diff + 1

    # 透视表与留存率计算
    cohort_data = cohort_df.groupby(['CohortMonth', 'CohortIndex'])['customer_unique_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortIndex', values='customer_unique_id')

    cohort_size = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_size, axis=0)

    retention_matrix.to_csv(TABLES / "cohort_retention_matrix.csv")
    print("✅ 同期群模型计算完成！")


def pareto_model(df):
    print("4. 正在计算 帕累托(ABC) 品类模型...")
    cat_sales = df.groupby('product_category_name_english')['total_amount'].sum().reset_index()
    cat_sales = cat_sales.sort_values(by='total_amount', ascending=False).reset_index(drop=True)

    # 计算累计占比
    cat_sales['cumulative_sum'] = cat_sales['total_amount'].cumsum()
    cat_sales['cumulative_percent'] = cat_sales['cumulative_sum'] / cat_sales['total_amount'].sum()

    def abc_class(pct):
        if pct <= 0.80:
            return 'A类 (核心品类)'
        elif pct <= 0.95:
            return 'B类 (腰部品类)'
        else:
            return 'C类 (长尾品类)'

    cat_sales['ABC_Class'] = cat_sales['cumulative_percent'].apply(abc_class)
    cat_sales.to_csv(TABLES / "pareto_abc_results.csv", index=False)
    print("✅ 帕累托模型计算完成！")


def main():
    df = load_clean_data()
    rfm_model(df)
    cohort_model(df)
    pareto_model(df)
    print("\n🎉 所有商业模型分析计算完毕！表格已存入 outputs/tables/")


if __name__ == "__main__":
    main()