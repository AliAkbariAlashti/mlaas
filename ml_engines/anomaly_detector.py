import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .utils import parse_datetime, parse_numeric, require_columns


def calculate_anomalies(
    data_frame: pd.DataFrame,
    invoice_id_col: str,
    date_col: str,
    amount_col: str,
    contamination: float = 0.01,
) -> tuple[dict, list[dict], pd.DataFrame]:
    require_columns(data_frame, [invoice_id_col, date_col, amount_col])
    frame = data_frame[[invoice_id_col, date_col, amount_col]].dropna().copy()
    frame[date_col] = parse_datetime(frame[date_col], date_col)
    frame[amount_col] = parse_numeric(frame[amount_col], amount_col)
    if len(frame) < 10:
        raise ValueError("Anomaly analysis requires at least ten complete transactions.")

    model_features = pd.DataFrame({
        "amount": frame[amount_col],
        "hour": frame[date_col].dt.hour,
        "day_of_week": frame[date_col].dt.dayofweek,
    }, index=frame.index)
    scaled_features = StandardScaler().fit_transform(model_features)
    model = IsolationForest(contamination=contamination, random_state=42)
    prediction = model.fit_predict(scaled_features)
    frame["anomaly_score"] = model.decision_function(scaled_features)
    frame["is_anomaly"] = prediction == -1
    anomalies = frame[frame["is_anomaly"]].sort_values("anomaly_score")
    anomalies_list = [{
        "row_index": int(index),
        "invoice_id": str(row[invoice_id_col]),
        "amount": float(row[amount_col]),
        "date": row[date_col].isoformat(),
        "anomaly_score": round(float(row["anomaly_score"]), 6),
    } for index, row in anomalies.iterrows()]
    summary = {"total_checked": len(frame), "anomalies_found": len(anomalies)}
    return summary, anomalies_list, frame
