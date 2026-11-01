import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# 路径配置
ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
RAW = ROOT / "data" / "raw"
TABLES = ROOT / "outputs" / "tables"
FIGS = ROOT / "outputs" / "figures"
FIGS.mkdir(parents=True, exist_ok=True)

# ---------------- 全局中文字体与样式设置 ----------------
# 兼容 Windows 系统
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font=plt.rcParams['font.sans-serif'])
# 统一配色
COLORS = sns.color_palette("Set2")


def load_data():
    print("加载数据...")
    df = pd.read_csv(CLEAN / "olist_cleaned_wide_table.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df


def fig01_sales_trend(df):
    print("1. 绘制：月度销售趋势折线图（模板复现-折线图）")
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly = df.groupby('month')['total_amount'].sum().reset_index()

    plt.figure(figsize=(10, 5), dpi=150)
    sns.lineplot(data=monthly, x='month', y='total_amount', marker='o', color='#1f77b4', linewidth=2.5)
    plt.title('2016-2018 Olist 月度销售额趋势', fontsize=16, pad=15)
    plt.xlabel('月份', fontsize=12)
    plt.ylabel('销售额 (BRL)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGS / "fig01_销售趋势折线图.png")
    plt.close()


def fig02_category_top10(df):
    print("2. 绘制：品类销售额 Top10（模板复现-条形图）")
    top_cat = df.groupby('product_category_name_english')['total_amount'].sum().nlargest(10).reset_index()

    plt.figure(figsize=(10, 6), dpi=150)
    sns.barplot(data=top_cat, y='product_category_name_english', x='total_amount', palette='viridis')
    plt.title('销售额 Top10 商品品类', fontsize=16, pad=15)
    plt.xlabel('销售额 (BRL)', fontsize=12)
    plt.ylabel('品类', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGS / "fig02_品类Top10条形图.png")
    plt.close()


def fig03_payment_pie():
    print("3. 绘制：支付方式占比环形图（模板复现-环形图）")
    payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
    pay_counts = payments['payment_type'].value_counts()

    plt.figure(figsize=(8, 8), dpi=150)
    plt.pie(pay_counts, labels=pay_counts.index, autopct='%1.1f%%', startangle=90,
            colors=COLORS, wedgeprops=dict(width=0.4, edgecolor='w'))
    plt.title('用户支付方式占比分布', fontsize=16, pad=15)
    plt.tight_layout()
    plt.savefig(FIGS / "fig03_支付方式环形图.png")
    plt.close()


def fig04_rfm_counts():
    print("4. 绘制：RFM 客群分布（业务图-柱状图）")
    rfm_counts = pd.read_csv(TABLES / "rfm_segment_counts.csv")

    plt.figure(figsize=(10, 5), dpi=150)
    sns.barplot(data=rfm_counts, x='Customer_Segment', y='Count', palette='Set3')
    plt.title('RFM 八大客群数量分布', fontsize=16, pad=15)
    plt.xlabel('客群分类', fontsize=12)
    plt.ylabel('用户数', fontsize=12)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(FIGS / "fig04_RFM客群分布图.png")
    plt.close()


def fig05_rfm_bubble():
    print("5. 绘制：RFM 散点气泡图（业务图-气泡图）")
    rfm = pd.read_csv(TABLES / "rfm_model_results.csv")
    # 为了防止画图太慢，抽样 3000 个用户展示
    rfm_sample = rfm.sample(n=min(3000, len(rfm)), random_state=42)

    plt.figure(figsize=(10, 6), dpi=150)
    sns.scatterplot(data=rfm_sample, x='R', y='F', size='M', hue='Customer_Segment',
                    sizes=(20, 200), alpha=0.6, palette='Set1')
    plt.title('用户价值分布气泡图 (R vs F, 气泡大小=M)', fontsize=16, pad=15)
    plt.xlabel('最近一次购买间隔 (天)', fontsize=12)
    plt.ylabel('购买频次', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(FIGS / "fig05_RFM气泡散点图.png")
    plt.close()


def fig06_cohort_heatmap():
    print("6. 绘制：同期群留存热力图（业务图-热力图）")
    matrix = pd.read_csv(TABLES / "cohort_retention_matrix.csv", index_col=0)
    # 取前 12 个月展示
    matrix = matrix.iloc[:12, :12]

    plt.figure(figsize=(12, 8), dpi=150)
    sns.heatmap(matrix, annot=True, fmt='.1%', cmap='Blues', cbar_kws={'label': '留存率'})
    plt.title('用户同期群留存率矩阵 (Cohort Retention)', fontsize=16, pad=15)
    plt.xlabel('首购后第 N 个月', fontsize=12)
    plt.ylabel('首购月份 (Cohort)', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGS / "fig06_同期群留存热力图.png")
    plt.close()


def fig07_pareto():
    print("7. 绘制：帕累托品类累计图（业务图-双轴图）")
    abc = pd.read_csv(TABLES / "pareto_abc_results.csv")
    abc = abc.head(30)  # 取前30个展示

    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
    ax1.bar(abc.index, abc['total_amount'], color='#1f77b4', alpha=0.7, label='品类销售额')
    ax1.set_xlabel('品类排名', fontsize=12)
    ax1.set_ylabel('销售额 (BRL)', fontsize=12)

    ax2 = ax1.twinx()
    ax2.plot(abc.index, abc['cumulative_percent'], color='crimson', marker='D', markersize=4, label='累计占比')
    ax2.axhline(0.8, color='gray', linestyle='--')
    ax2.set_ylabel('累计百分比', fontsize=12)

    plt.title('品类销售帕累托图 (ABC分类)', fontsize=16, pad=15)
    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.85))
    plt.tight_layout()
    plt.savefig(FIGS / "fig07_帕累托双轴图.png")
    plt.close()


def fig08_freight_box(df):
    print("8. 绘制：各州运费分布箱线图（模板复现-箱线图）")
    top_states = df['customer_state'].value_counts().nlargest(5).index
    df_box = df[df['customer_state'].isin(top_states)]

    plt.figure(figsize=(10, 5), dpi=150)
    sns.boxplot(data=df_box, x='customer_state', y='freight_value', palette='pastel')
    plt.title('Top5 客户所在州的运费分布 (箱线图)', fontsize=16, pad=15)
    plt.xlabel('客户州', fontsize=12)
    plt.ylabel('运费 (BRL)', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGS / "fig08_运费箱线图.png")
    plt.close()


def fig09_area_chart(df):
    print("9. 绘制：月度订单量堆积面积图（模板复现-面积图）")
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    top_5_cat = df.groupby('product_category_name_english')['total_amount'].sum().nlargest(5).index
    df_area = df[df['product_category_name_english'].isin(top_5_cat)]

    monthly_cat = df_area.groupby(['month', 'product_category_name_english'])['total_amount'].sum().unstack().fillna(0)

    plt.figure(figsize=(12, 6), dpi=150)
    plt.stackplot(monthly_cat.index, [monthly_cat[col] for col in monthly_cat.columns],
                  labels=monthly_cat.columns, alpha=0.8)
    plt.title('Top5 热门品类月度销售额堆积面积图', fontsize=16, pad=15)
    plt.xlabel('月份', fontsize=12)
    plt.ylabel('销售额 (BRL)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(FIGS / "fig09_品类堆积面积图.png")
    plt.close()


def fig10_histogram(df):
    print("10. 绘制：订单金额分布直方图（模板复现-直方图）")
    order_amt = df.groupby('order_id')['total_amount'].sum().reset_index()
    # 过滤极端值展示更好看
    order_amt = order_amt[order_amt['total_amount'] < 1000]

    plt.figure(figsize=(10, 5), dpi=150)
    sns.histplot(order_amt['total_amount'], bins=50, kde=True, color='teal')
    plt.title('用户单笔订单金额分布 (Histogram)', fontsize=16, pad=15)
    plt.xlabel('订单金额 (BRL)', fontsize=12)
    plt.ylabel('订单数量', fontsize=12)
    plt.tight_layout()
    plt.savefig(FIGS / "fig10_订单金额直方图.png")
    plt.close()


def main():
    df = load_data()
    fig01_sales_trend(df)
    fig02_category_top10(df)
    fig03_payment_pie()
    fig04_rfm_counts()
    fig05_rfm_bubble()
    fig06_cohort_heatmap()
    fig07_pareto()
    fig08_freight_box(df)
    fig09_area_chart(df)
    fig10_histogram(df)
    print(f"\n🎉 所有 10 张图表生成成功！已保存至 outputs/figures/")


if __name__ == "__main__":
    main()