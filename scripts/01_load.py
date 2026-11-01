from pathlib import Path
import pandas as pd

# 获取当前项目根目录
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def main():
    print("开始检查数据...")
    for name, filename in FILES.items():
        path = RAW / filename
        if not path.exists():
            print(f"[缺失] 找不到文件: {filename}")
            continue
        # 只读取前几行看结构，加快速度
        df = pd.read_csv(path, nrows=3)
        print(f"\n[{name}] 读取成功！")
        print("字段:", list(df.columns))


if __name__ == "__main__":
    main()