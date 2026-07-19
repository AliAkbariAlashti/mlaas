from unittest import TestCase

import pandas as pd

from .anomaly_detector import calculate_anomalies
from .market_basket import calculate_market_basket
from .propensity_scorer import calculate_propensity
from .rfm_segmenter import calculate_rfm


class RFMEngineTests(TestCase):
    def test_calculates_customer_segments(self):
        frame = pd.DataFrame({
            "customer": ["A", "A", "B", "C"],
            "date": ["2026-01-01", "2026-02-01", "2025-01-01", "2026-02-02"],
            "invoice": [1, 2, 3, 4],
            "amount": [10, 20, 5, 30],
        })
        summary, chart_data, output = calculate_rfm(frame, "customer", "date", "invoice", "amount")
        self.assertEqual(summary["total_customers"], 3)
        self.assertTrue(chart_data)
        self.assertIn("segment", output.columns)


class MarketBasketEngineTests(TestCase):
    def test_finds_association_rules(self):
        frame = pd.DataFrame({
            "invoice": [1, 1, 2, 2, 3, 3, 4],
            "product": ["A", "B", "A", "B", "A", "B", "C"],
        })
        rules = calculate_market_basket(frame, "invoice", "product", min_support=0.2)
        self.assertTrue(any(rule["antecedent"] == "A" and rule["consequent"] == "B" for rule in rules))


class PropensityEngineTests(TestCase):
    def test_scores_customers(self):
        frame = pd.DataFrame({
            "customer": ["A", "B", "A", "C", "B", "D", "A", "B", "C", "D"],
            "date": pd.date_range("2026-01-01", periods=10, freq="D"),
            "amount": [10, 20, 15, 8, 25, 12, 30, 35, 9, 14],
        })
        metrics, scores, output = calculate_propensity(frame, "customer", "date", "amount")
        self.assertEqual(metrics["customers_scored"], 4)
        self.assertTrue(scores)
        self.assertIn("propensity_score", output.columns)


class AnomalyEngineTests(TestCase):
    def test_detects_anomalies(self):
        frame = pd.DataFrame({
            "invoice": range(20),
            "date": pd.date_range("2026-01-01", periods=20, freq="h"),
            "amount": [10] * 19 + [10000],
        })
        summary, anomalies, output = calculate_anomalies(frame, "invoice", "date", "amount", contamination=0.05)
        self.assertEqual(summary["total_checked"], 20)
        self.assertEqual(summary["anomalies_found"], 1)
        self.assertTrue(anomalies)
        self.assertIn("is_anomaly", output.columns)
