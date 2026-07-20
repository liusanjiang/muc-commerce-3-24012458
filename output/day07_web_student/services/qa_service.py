from pathlib import Path
import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"

    # ---- 读取数据 ----
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    seg_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
    cat_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")

    # 基础指标字典（严格来自 overall_metrics.csv）
    m = dict(zip(metrics_df["指标"].str.strip(), metrics_df["数值"]))

    # 归一化问题，忽略空格和大小写
    q = question.replace(" ", "").lower()

    # 1️⃣ 用户数
    if any(k in q for k in ["多少用户", "用户数", "总人数"]):
        return f"数据集共有 **{int(float(m['用户数'])):,}** 名用户。"

    # 2️⃣ 流失率
    elif any(k in q for k in ["流失率", "流失比例", "流失了"]):
        return (
            f"总体流失率为 **{float(m['流失率']):.2%}**，"
            f"对应流失人数为 **{int(float(m['流失人数'])):,}** 人。"
        )

    # 3️⃣ 订单情况
    elif any(k in q for k in ["订单", "买了几次", "购买频次"]):
        return (
            f"用户平均订单数为 **{float(m['平均订单数']):.2f}** 单，"
            f"订单数中位数为 **{float(m['订单数中位数']):.1f}** 单，"
            f"说明多数用户仅完成过 2 单。"
        )

    # 4️⃣ 生命周期风险（严格引用 segment_analysis.csv 已算好的指标）
    elif any(k in q for k in ["生命周期", "哪个阶段", "风险最高", "留存"]):
        seg_df["流失率"] = seg_df["流失率"].astype(float)
        top = seg_df.loc[seg_df["流失率"].idxmax()]
        return (
            f"生命周期为「**{top['TenureGroup']}**」的阶段流失风险最高，"
            f"流失率达 **{top['流失率']:.1%}**，远高于整体均值，需重点关注新用户激活。"
        )

    # 5️⃣ 偏好品类（严格引用 category_analysis.csv）
    elif any(k in q for k in ["偏好", "品类", "类别", "喜欢买"]):
        # 按用户数排序找最多的
        cat_df_sorted = cat_df.sort_values("用户数", ascending=False)
        top_cat = cat_df_sorted.iloc[0]
        return (
            f"用户占比最高的偏好品类是「**{top_cat['PreferedOrderCat']}**」，"
            f"该品类用户平均订单数为 **{top_cat['平均订单数']:.2f}**，"
            f"流失率为 **{top_cat['流失率']:.1%}**。"
        )

    # 兜底回复
    return (
        "抱歉，我还不能理解这个问题。\n"
        "你可以试试问我：\n"
        "• 系统一共有多少用户？\n"
        "• 总体流失率是多少？\n"
        "• 用户平均订单数是多少？\n"
        "• 哪个生命周期阶段风险最高？\n"
        "• 用户最喜欢哪个品类？"
    )