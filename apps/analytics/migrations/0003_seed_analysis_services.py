from django.db import migrations


SERVICES = (
    ("RFM", "RFM Segmentation", "بخش‌بندی هوشمند مشتریان", True, "RFM", ["customer_id_column", "date_column", "invoice_id_column"], ["amount_column"]),
    ("MARKET_BASKET", "Market Basket Analysis", "تحلیل سبد خرید و اقلام هم‌نشین", True, "BASKET", ["invoice_id_column", "product_name_column"], ["product_category_column", "quantity_column"]),
    ("CHURN", "Customer Churn Audit", "آنالیز ریزش لحظه‌ای مشتریان", False, "PREDICTIVE", [], []),
    ("CLV", "Customer Lifetime Value", "گزارش ارزش طول عمر مشتری", False, "PREDICTIVE", [], []),
    ("PRODUCT_SHARE", "Product Share Matrix", "تحلیل سهم بازار کالاها", False, "PREDICTIVE", [], []),
    ("PROPENSITY", "Purchase Propensity Score", "پیش‌بینی احتمال خرید آتی", True, "PREDICTIVE", ["customer_id_column", "date_column", "amount_column"], []),
    ("ANOMALY", "Sales Anomaly Detection", "تشخیص آنومالی و رفتارهای مشکوک", True, "PREDICTIVE", ["invoice_id_column", "date_column", "amount_column"], []),
    ("DEMAND_FORECAST", "Demand Forecasting AI", "پیش‌بینی پویای تقاضا و انبار", False, "PREDICTIVE", [], []),
    ("RECOMMENDER", "Personalized Recommender", "موتور توصیه‌گر شخصی‌سازی شده", False, "PREDICTIVE", [], []),
    ("PRICE_OPTIMIZATION", "Price Optimization Engine", "مدل‌سازی حساسیت قیمت و سود", False, "PREDICTIVE", [], []),
)


def seed_services(apps, schema_editor):
    service_model = apps.get_model("analytics", "AnalysisService")
    for order, service in enumerate(SERVICES, start=1):
        code, name_en, name_fa, is_active, result_kind, required, optional = service
        service_model.objects.update_or_create(code=code, defaults={
            "name_en": name_en,
            "name_fa": name_fa,
            "is_active": is_active,
            "result_kind": result_kind,
            "required_mapping_fields": required,
            "optional_mapping_fields": optional,
            "display_order": order,
        })


class Migration(migrations.Migration):
    dependencies = [("analytics", "0002_initial")]
    operations = [migrations.RunPython(seed_services, migrations.RunPython.noop)]
