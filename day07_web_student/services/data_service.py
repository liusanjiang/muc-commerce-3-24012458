from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    """读取 utf-8-sig 编码的 csv，防止 BOM 头引起列名异常"""
    return pd.read_csv(path, encoding="utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"

    # ---- 1. 读取数据 ----
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    # 转成 dict 方便取数，并处理科学计数法或浮点格式
    metric_map = dict(zip(metrics_df["指标"].str.strip(), metrics_df["数值"]))

    # ---- 2. 顶部指标卡（补全总体流失率 & 平均订单数）----
    total_users = int(float(metric_map.get("用户数", 0)))
    churn_users = int(float(metric_map.get("流失人数", 0)))
    churn_rate = float(metric_map.get("流失率", 0))
    avg_orders = float(metric_map.get("平均订单数", 0))

    metrics = [
        {"label": "总用户数", "value": f"{total_users:,}", "note": "人"},
        {"label": "流失用户", "value": f"{churn_users:,}", "note": "人"},
        {"label": "总体流失率", "value": f"{churn_rate:.2%}", "note": ""},
        {"label": "平均订单数", "value": f"{avg_orders:.2f}", "note": "单"},
    ]

    # ---- 3. 品类下拉选项 & 表格数据 ----
    # 去重拿到所有品类，拼上"全部"
    all_categories = category_df["PreferedOrderCat"].dropna().unique().tolist()
    categories = ["全部", *all_categories]

    # TODO 3-1 补全：根据前端选择的品类做筛选
    table_df = category_df.copy()
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category].copy()

    # 格式化输出列
    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )
    table_df = table_df[["偏好品类", "用户数", "流失率", "平均订单数"]]

    # 百分比和小数格式化
    table_df["流失率"] = table_df["流失率"].apply(lambda x: f"{float(x):.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].apply(lambda x: f"{float(x):.2f}")

    # ---- 4. 生命周期风险观察（基于 segment_analysis.csv）----
    # 找出流失率最高的阶段
    segment_df["流失率"] = segment_df["流失率"].astype(float)
    max_idx = segment_df["流失率"].idxmax()
    top_risk_stage = segment_df.loc[max_idx, "TenureGroup"]
    top_risk_rate = segment_df.loc[max_idx, "流失率"]

    insight = (
        f"📉 数据观察：生命周期为「{top_risk_stage}」的用户流失率高达 {top_risk_rate:.1%}，"
        f"远超整体均值（{churn_rate:.1%}），建议立即介入新用户激活与首单引导策略。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict(orient="records"),
        "insight": insight,
    }
