import pandas as pd

from .utils import parse_datetime, parse_numeric, require_columns


def _score(series: pd.Series, high_is_good: bool = True) -> pd.Series:
    percentile = series.rank(method="average", pct=True)
    score = percentile.mul(5).clip(upper=4.9999).astype(int).add(1)
    return score if high_is_good else 6 - score


def _segment(row: pd.Series) -> str:
    if row["R"] >= 4 and row["F"] >= 4:
        return "Loyal Customers"
    if row["R"] >= 4 and row["F"] <= 2:
        return "New Customers"
    if row["R"] <= 2 and row["F"] >= 4:
        return "At Risk"
    if row["R"] <= 2 and row["F"] <= 2:
        return "Lost Customers"
    return "Potential Loyalists"


def calculate_rfm(
    data_frame: pd.DataFrame,
    customer_id_col: str,
    date_col: str,
    invoice_id_col: str,
    amount_col: str | None = None,
) -> tuple[dict, list[dict], pd.DataFrame]:
    required = [customer_id_col, date_col, invoice_id_col]
    require_columns(data_frame, required + ([amount_col] if amount_col else []))
    frame = data_frame[required + ([amount_col] if amount_col else [])].dropna(subset=required).copy()
    frame[date_col] = parse_datetime(frame[date_col], date_col)
    if amount_col:
        frame[amount_col] = parse_numeric(frame[amount_col], amount_col)

    snapshot_date = frame[date_col].max() + pd.Timedelta(days=1)
    aggregation = {
        "recency": (date_col, lambda values: (snapshot_date - values.max()).days),
        "frequency": (invoice_id_col, "nunique"),
    }
    if amount_col:
        aggregation["monetary"] = (amount_col, "sum")
    rfm = frame.groupby(customer_id_col).agg(**aggregation).reset_index()
    if not amount_col:
        rfm["monetary"] = rfm["frequency"].astype(float)
    rfm["R"] = _score(rfm["recency"], high_is_good=False)
    rfm["F"] = _score(rfm["frequency"])
    rfm["M"] = _score(rfm["monetary"])
    rfm["rfm_score"] = rfm[["R", "F", "M"]].astype(str).agg("".join, axis=1)
    rfm["segment"] = rfm.apply(_segment, axis=1)

    counts = rfm["segment"].value_counts()
    total = len(rfm)
    chart_data = [
        {"segment": segment, "count": int(count), "percentage": round(count * 100 / total, 2)}
        for segment, count in counts.items()
    ]
    churn_count = int(rfm["segment"].isin(("At Risk", "Lost Customers")).sum())
    summary = {
        "total_customers": total,
        "churn_rate_percentage": round(churn_count * 100 / total, 2),
        "repeat_buyer_percentage": round((rfm["frequency"] > 1).mean() * 100, 2),
    }
    return summary, chart_data, rfm
