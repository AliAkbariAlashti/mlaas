# E-commerce MLaaS Test Datasets

This directory contains ten deterministic, synthetic UTF-8 CSV datasets for testing e-commerce analytics services. Data is fictional and uses a fixed random seed. CSVs have no index column, required fields are populated, dates use ISO format, and monetary/quantity fields are numeric.

## Dataset guide

| File | Rows | Purpose and embedded patterns | Expected analytical findings | Recommended MLAAS mapping |
|---|---:|---|---|---|
| `rfm_transactions.csv` | 12,666 | RFM segmentation over two years; loyal, new, at-risk, lost, and potential-loyalist behavior with varied spend | Recent/frequent loyal cohort, one-order newcomers, stale formerly frequent customers, low-frequency lost cohort | Customer ID=`customer_id`; Date=`invoice_date`; Invoice ID=`invoice_id`; Amount=`total_amount` |
| `market_basket_transactions.csv` | 32,822 | Multi-line baskets with seven deliberately recurring product pairs plus background products | Strong bidirectional rules for coffee/filters, laptop/sleeve, smartphone/case, printer/paper, shampoo/conditioner, pasta/sauce, console/controller | Invoice ID=`invoice_id`; Product name=`product_name`; Product category=`product_category`; Quantity=`quantity` |
| `customer_churn.csv` | 7,000 | Customer-level churn audit with 28% churn, correlated inactivity, engagement, returns, and support burden; 13% noisy edge cases | Inactivity and low engagement lead prediction; service problems add risk without making labels trivial | Entity ID=`customer_id`; Target=`churned`; Dates=`first_purchase_date`,`last_purchase_date`; remaining numeric columns as features |
| `customer_lifetime_value.csv` | 17,632 | Two years of transactions for 2,200 customers: high-value, one-time, seasonal, recent, rising, and declining cohorts | High-frequency/high-spend customers dominate CLV; seasonal and trajectory cohorts remain distinguishable | Customer ID=`customer_id`; Invoice ID=`invoice_id`; Date=`invoice_date`; Amount=`total_amount`; dimensions=`product_category`,`acquisition_channel` |
| `product_share.csv` | 28,000 | Zipf-like product demand across 180 products and 12 categories, seasonal lifts, exact line totals | A few products dominate, followed by a medium tier and long tail; Toys/Electronics rise late-year and Garden rises in spring | Invoice ID=`invoice_id`; Date=`invoice_date`; Product ID=`product_id`; Product/category dimensions; Quantity, unit price, amount measures |
| `purchase_propensity.csv` | 19,494 | Two-year histories for 2,500 customers with regular, one-time, accelerating, and inactive behavior | Recent/frequent and accelerating customers are likelier to buy in the final 20%; inactive and one-time customers less likely | Customer ID=`customer_id`; Date=`invoice_date`; Amount=`invoice_amount` |
| `sales_anomalies.csv` | 12,000 | Mostly normal sales with exactly 240 injected anomaly records (2%): extreme, tiny/negative, quantity mismatch, odd-hour, burst, and repeated-ID activity | Multiple anomaly types should surface without treating every legitimate high-value sale as anomalous | Invoice ID=`invoice_id`; Date=`invoice_date`; Amount=`total_amount`; other columns as explanatory features |
| `demand_forecast.csv` | 43,860 | Daily product series for 60 products across 731 days with weekly/monthly cycles, trends, holidays, promotions, category seasonality, and stockouts | Weekend, promotion and holiday lifts; category-specific seasonality; censored sales during stockouts | Time=`date`; Series ID=`product_id`; Target=`units_sold`; price/inventory and binary event columns as regressors |
| `product_recommendations.csv` | 60,000 | Interactions among 6,000 customers and 700 products with customer category preference, popularity tiers, niche/cold-start items, and view→cart→purchase imbalance | Collaborative overlap and category affinities; popular and niche items; sparse purchase ratings | User ID=`customer_id`; Item ID=`product_id`; Interaction=`interaction_type`; Date=`interaction_date`; Rating=`rating`; Quantity=`quantity` |
| `price_optimization.csv` | 36,500 | Daily observations for 100 products over one year with heterogeneous elasticity, promotions, competitor effects, margins and seasonality | Units generally fall with relative price, rise on promotion, and respond to competitor price; elasticity varies by product | Date=`date`; Product ID=`product_id`; Price=`unit_price`; Demand=`units_sold`; Cost/competitor/promotion/inventory as features |

## Validation report

All files open successfully with pandas. Required columns exist and have no nulls. All date columns parse, numeric columns coerce successfully, and identifier columns load consistently as strings. The only missing values are 55,761 intentionally blank `rating` values on non-purchase or unrated recommendation interactions; `rating` is optional by specification. No file contains duplicate full rows.

| File | Rows | Columns | Missing values | Duplicate rows |
|---|---:|---:|---:|---:|
| `rfm_transactions.csv` | 12,666 | 4 | 0 | 0 |
| `market_basket_transactions.csv` | 32,822 | 4 | 0 | 0 |
| `customer_churn.csv` | 7,000 | 11 | 0 | 0 |
| `customer_lifetime_value.csv` | 17,632 | 6 | 0 | 0 |
| `product_share.csv` | 28,000 | 8 | 0 | 0 |
| `purchase_propensity.csv` | 19,494 | 3 | 0 | 0 |
| `sales_anomalies.csv` | 12,000 | 7 | 0 | 0 |
| `demand_forecast.csv` | 43,860 | 10 | 0 | 0 |
| `product_recommendations.csv` | 60,000 | 8 | 55,761 | 0 |
| `price_optimization.csv` | 36,500 | 10 | 0 | 0 |

Market-basket validation: 8,000 unique invoices, 4.1028 average product lines per invoice, and 100% of invoices contain at least two products. A direct pairwise association check at minimum support 0.002 and confidence 0.30 produces 14 qualifying rules. The seven intended pairs each produce both directional rules, with support around 9.6–10.6% and confidence around 84–87%.

Additional integrity checks: `product_share.total_amount` equals `quantity * unit_price` after currency rounding; binary flags contain only 0/1; recommendation interaction types contain only `view`, `cart`, or `purchase`; ratings are within 1–5; churn prevalence is 27.99%; all optimized prices are positive and costs are normally below prices.
