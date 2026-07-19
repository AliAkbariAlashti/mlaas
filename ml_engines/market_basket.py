import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

from .utils import parse_numeric, require_columns


def calculate_market_basket(
    data_frame: pd.DataFrame,
    invoice_id_col: str,
    product_name_col: str,
    quantity_col: str | None = None,
    min_support: float = 0.01,
    min_confidence: float = 0.3,
) -> list[dict]:
    columns = [invoice_id_col, product_name_col] + ([quantity_col] if quantity_col else [])
    require_columns(data_frame, columns)
    frame = data_frame[columns].dropna(subset=[invoice_id_col, product_name_col]).copy()
    frame[product_name_col] = frame[product_name_col].astype(str).str.strip()
    if quantity_col:
        frame[quantity_col] = parse_numeric(frame[quantity_col], quantity_col)
        frame = frame[frame[quantity_col] > 0]
        basket = frame.pivot_table(index=invoice_id_col, columns=product_name_col, values=quantity_col, aggfunc="sum", fill_value=0)
    else:
        basket = pd.crosstab(frame[invoice_id_col], frame[product_name_col])
    basket = basket.gt(0)
    if len(basket) < 2 or basket.shape[1] < 2:
        return []
    itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    if itemsets.empty:
        return []
    rules = association_rules(itemsets, metric="confidence", min_threshold=min_confidence)
    rules = rules[rules["antecedents"].map(len).eq(1) & rules["consequents"].map(len).eq(1)]
    rules = rules.sort_values(["lift", "confidence"], ascending=False).head(100)
    return [{
        "antecedent": str(next(iter(row.antecedents))),
        "consequent": str(next(iter(row.consequents))),
        "support": round(float(row.support), 4),
        "confidence": round(float(row.confidence), 4),
        "lift": round(float(row.lift), 4),
    } for row in rules.itertuples()]
