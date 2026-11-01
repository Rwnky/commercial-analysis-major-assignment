# Olist 电商用户价值与留存商业数据分析

## 项目简介
本项目基于 Kaggle 上的 Olist 巴西电商公开数据集，使用纯 Python 技术栈（Pandas, Matplotlib, Seaborn, Plotly, Streamlit）完成了从数据获取、清洗治理、模型分析、可视化复现到交互式大屏搭建的端到端全流程。最终提炼出可落地的商业洞察。

## 数据来源合规声明
- **数据源名称**：Brazilian E-Commerce Public Dataset by Olist
- **获取方式**：Kaggle 官网 ZIP 手动下载（白名单方式，非爬虫）
- **获取日期**：2026-10-31
- **授权/License**：CC BY-NC-SA 4.0
- **数据规模**：主表记录数 99,441 条。本项目使用全量数据，未抽样。
- **非爬虫声明**：未使用 Scrapy、Selenium、requests 网页解析等网页抓取方式。

## 目录结构
```text
.
├── data/
│   ├── raw/            # 原始数据 CSV
│   └── clean/          # 清洗后导出的 CSV / JSON / SQLite
├── docs/
│   └── 数据来源合规声明.md
│   └── 期末大论文.docx
├── outputs/
│   ├── figures/        # 10 张高清可视化图表 (150dpi)
│   └── tables/         # 模型输出数据表 (RFM, Cohort, ABC)
├── scripts/
│   ├── 01_load.py      # 数据加载测试
│   ├── 02_clean.py     # 数据清洗与多表关联
│   ├── 03_analysis.py  # RFM/同期群/帕累托模型计算
│   ├── 04_visuals.py   # 10 张图表绘制
│   └── 05_dashboard.py # Streamlit 交互式大屏
├── requirements.txt    # 依赖列表
├── run_all.py          # 一键复现入口
└── README.md