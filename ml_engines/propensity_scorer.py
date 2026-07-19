import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

from .utils import parse_datetime, parse_numeric, require_columns


def calculate_propensity(
    data_frame: pd.DataFrame,
    customer_id_col: str,
    date_col: str,
    amount_col: str,
) -> tuple[dict, list[dict], pd.DataFrame]:
    require_columns(data_frame, [customer_id_col, date_col, amount_col])
    frame = data_frame[[customer_id_col, date_col, amount_col]].dropna().copy()
    frame[date_col] = parse_datetime(frame[date_col], date_col)
    frame[amount_col] = parse_numeric(frame[amount_col], amount_col)
    if frame[customer_id_col].nunique() < 2 or len(frame) < 4:
        raise ValueError("Propensity analysis requires at least four transactions across two customers.")

    cutoff = frame[date_col].quantile(0.8)
    history = frame[frame[date_col] <= cutoff]
    future_customers = set(frame.loc[frame[date_col] > cutoff, customer_id_col])
    features = history.groupby(customer_id_col).agg(
        recency=(date_col, lambda values: (cutoff - values.max()).days),
        frequency=(date_col, "size"),
        monetary=(amount_col, "sum"),
        average_order=(amount_col, "mean"),
    ).reset_index()
    features["target"] = features[customer_id_col].isin(future_customers).astype(int)
    feature_columns = ["recency", "frequency", "monetary", "average_order"]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features[feature_columns])

    if features["target"].nunique() == 2:
        model = LogisticRegression(random_state=42, class_weight="balanced")
        model.fit(scaled, features["target"])
        probability = model.predict_proba(scaled)[:, 1]
        prediction = model.predict(scaled)
        metrics = {
            "customers_scored": len(features),
            "training_accuracy": round(float(accuracy_score(features["target"], prediction)), 4),
            "training_roc_auc": round(float(roc_auc_score(features["target"], probability)), 4),
        }
    else:
        recency = 1 - features["recency"].rank(pct=True)
        frequency = features["frequency"].rank(pct=True)
        monetary = features["monetary"].rank(pct=True)
        probability = np.asarray((recency + frequency + monetary) / 3)
        metrics = {"customers_scored": len(features), "training_accuracy": None, "training_roc_auc": None}

    features["propensity_score"] = np.round(probability * 100, 2)
    scored = features.sort_values("propensity_score", ascending=False)
    visualization_data = scored[[customer_id_col, "propensity_score"]].head(100).rename(
        columns={customer_id_col: "customer_id"}
    ).to_dict("records")
    return metrics, visualization_data, scored
