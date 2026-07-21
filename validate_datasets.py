from itertools import permutations
from pathlib import Path
import pandas as pd

ROOT = Path("mlaas_test_datasets")
SPECS = {
 "rfm_transactions.csv": (["customer_id","invoice_date","invoice_id","total_amount"],["invoice_date"],["total_amount"]),
 "market_basket_transactions.csv": (["invoice_id","product_name"],[],["quantity"]),
 "customer_churn.csv": (["customer_id","last_purchase_date","first_purchase_date","purchase_count","total_spend","average_order_value","days_since_last_purchase","support_ticket_count","returned_order_count","email_engagement_rate","churned"],["last_purchase_date","first_purchase_date"],["purchase_count","total_spend","average_order_value","days_since_last_purchase","support_ticket_count","returned_order_count","email_engagement_rate","churned"]),
 "customer_lifetime_value.csv": (["customer_id","invoice_id","invoice_date","total_amount","product_category","acquisition_channel"],["invoice_date"],["total_amount"]),
 "product_share.csv": (["invoice_id","invoice_date","product_id","product_name","product_category","quantity","unit_price","total_amount"],["invoice_date"],["quantity","unit_price","total_amount"]),
 "purchase_propensity.csv": (["customer_id","invoice_date","invoice_amount"],["invoice_date"],["invoice_amount"]),
 "sales_anomalies.csv": (["invoice_id","invoice_date","total_amount"],["invoice_date"],["total_amount","quantity"]),
 "demand_forecast.csv": (["date","product_id","product_name","product_category","units_sold","unit_price","inventory_level","promotion_active","holiday","stockout"],["date"],["units_sold","unit_price","inventory_level","promotion_active","holiday","stockout"]),
 "product_recommendations.csv": (["customer_id","product_id","product_name","product_category","interaction_type","interaction_date","quantity"],["interaction_date"],["quantity","rating"]),
 "price_optimization.csv": (["date","product_id","product_name","product_category","unit_price","units_sold","unit_cost","competitor_price","promotion_active","inventory_level"],["date"],["unit_price","units_sold","unit_cost","competitor_price","promotion_active","inventory_level"]),
}

for name,(required,dates,numerics) in SPECS.items():
    df=pd.read_csv(ROOT/name,dtype={c:"string" for c in required if c.endswith("_id")})
    assert set(required)<=set(df.columns), (name,"columns")
    assert not df[required].isna().any().any(), (name,"required null")
    for c in dates: pd.to_datetime(df[c],errors="raise")
    for c in numerics:
        if c=="rating": pd.to_numeric(df[c].dropna(),errors="raise")
        else: pd.to_numeric(df[c],errors="raise")
    print(f"{name}: rows={len(df):,}; columns={list(df.columns)}; missing={int(df.isna().sum().sum()):,}; duplicates={int(df.duplicated().sum()):,}")

b=pd.read_csv(ROOT/"market_basket_transactions.csv")
sets=b.groupby("invoice_id").product_name.agg(set); sizes=b.groupby("invoice_id").size(); singles={}; pairs={}
for basket in sets:
    for a in basket: singles[a]=singles.get(a,0)+1
    for a,c in permutations(basket,2): pairs[a,c]=pairs.get((a,c),0)+1
rules=[(a,c,n/len(sets),n/singles[a]) for (a,c),n in pairs.items() if n/len(sets)>=.002 and n/singles[a]>=.30]
assert len(rules)>=10
print(f"Basket: invoices={len(sets):,}; avg_products={sizes.mean():.4f}; invoices_2plus={(sizes.ge(2).mean()*100):.2f}%; qualifying_rules={len(rules)}")
