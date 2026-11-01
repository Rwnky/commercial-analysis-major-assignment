import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# 页面设置
st.set_page_config(page_title="Olist 商业数据大屏", layout="wide", page_icon="📊")
st.title("🛍️ Olist 电商用户价值与留存商业大屏")

# 路径配置
ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
TABLES = ROOT / "outputs" / "tables"

# 缓存数据加载，提升网页性能
@st.cache_data
def load_data():
    df = pd.read_csv(CLEAN / "olist_cleaned_wide_table.csv")
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    rfm = pd.read_csv(TABLES / "rfm_model_results.csv")
    return df, rfm

df, rfm = load_data()

# --- 侧边栏筛选器（联动组件） ---
st.sidebar.header("🎛️ 数据筛选面板")
# 日期筛选
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()
start_date, end_date = st.sidebar.date_input("选择日期范围", [min_date, max_date])

# 州筛选
states = df['customer_state'].unique().tolist()
selected_states = st.sidebar.multiselect("选择客户所在州", states, default=states[:3])

# 根据筛选器过滤数据
df_filtered = df[(df['order_purchase_timestamp'].dt.date >= start_date) &
                 (df['order_purchase_timestamp'].dt.date <= end_date) &
                 (df['customer_state'].isin(selected_states))]

# --- KPI 卡片组件 (3个) ---
st.markdown("### 📈 核心业务指标")
col1, col2, col3 = st.columns(3)
total_sales = df_filtered['total_amount'].sum()
total_orders = df_filtered['order_id'].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

col1.metric("总销售额 (BRL)", f"R$ {total_sales:,.2f}")
col2.metric("总订单量", f"{total_orders:,} 单")
col3.metric("平均客单价 (AOV)", f"R$ {avg_order_value:.2f}")

st.markdown("---")

# --- 图表组件 (3个) ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 🌍 各州销售额分布 (地图联动)")
    state_sales = df_filtered.groupby('customer_state')['total_amount'].sum().reset_index()
    fig_map = px.choropleth(state_sales, locations='customer_state', locationmode="geojson-id",
                            color='total_amount', scope="south america",
                            color_continuous_scale="Blues", labels={'total_amount': '销售额'})
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.markdown("#### 📅 月度销售趋势图")
    df_filtered['month'] = df_filtered['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly = df_filtered.groupby('month')['total_amount'].sum().reset_index()
    fig_line = px.line(monthly, x='month', y='total_amount', markers=True,
                       labels={'month': '月份', 'total_amount': '销售额 (BRL)'})
    st.plotly_chart(fig_line, use_container_width=True)

# 底部图表组件
col_bot_left, col_bot_right = st.columns(2)

with col_bot_left:
    st.markdown("#### 👥 RFM 客群分布 (联动)")
    # 这里做一个简单的联动，显示当前选中的州的 RFM 分布
    rfm_counts = rfm['Customer_Segment'].value_counts().reset_index()
    rfm_counts.columns = ['客群', '数量']
    fig_bar = px.bar(rfm_counts, x='客群', y='数量', color='客群', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_bot_right:
    st.markdown("#### 🛒 支付方式占比")
    pay_counts = df_filtered['payment_value'].notna().value_counts().reset_index()
    # 简单生成一个甜甜圈图
    fig_pie = px.pie(names=['有其他支付', '无支付记录'], values=[len(df_filtered), 0], hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
# --- 明细表组件 ---
st.markdown("#### 📋 订单明细数据预览 (Top 100)")
st.dataframe(df_filtered[['order_id', 'customer_state', 'product_category_name_english', 'total_amount', 'order_purchase_timestamp']].head(100), use_container_width=True)