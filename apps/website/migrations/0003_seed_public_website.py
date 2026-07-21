from django.db import migrations
from django.utils.text import slugify
from django.utils import timezone


SERVICE_COPY = {
    "RFM": ("Understand every customer relationship", "هر رابطه با مشتری را بشناسید", "Group customers by recency, frequency, and value to focus retention actions."),
    "MARKET_BASKET": ("Discover what customers buy together", "کالاهای هم‌خرید را کشف کنید", "Find meaningful product relationships and build evidence-led bundles."),
    "PROPENSITY": ("Know who is ready to buy again", "مشتریان آماده خرید مجدد را بشناسید", "Score repeat-purchase likelihood and prioritize customer outreach."),
    "ANOMALY": ("Surface unusual sales activity", "فعالیت غیرعادی فروش را آشکار کنید", "Detect unusual transaction patterns and focus operational review."),
}


def seed_website(apps, schema_editor):
    Service = apps.get_model("analytics", "AnalysisService")
    Component = apps.get_model("website", "ComponentPage")
    Menu = apps.get_model("website", "HeaderMenuItem")
    Page = apps.get_model("website", "ServicePage")
    Step = apps.get_model("website", "ServiceStep")
    Blog = apps.get_model("website", "BlogPost")

    customer = Component.objects.create(slug="customer-analytics", title_en="Customer Analytics", title_fa="تحلیل مشتری", description_en="Understand customer behavior, value, and purchase intent.", description_fa="رفتار، ارزش و قصد خرید مشتری را بهتر بشناسید.", display_order=1)
    product = Component.objects.create(slug="product-analytics", title_en="Product Analytics", title_fa="تحلیل محصول", description_en="Understand product relationships, demand, and commercial performance.", description_fa="روابط محصول، تقاضا و عملکرد تجاری را تحلیل کنید.", display_order=2)
    root = Menu.objects.create(title_en="Components", title_fa="اجزا", display_order=1)
    customer_menu = Menu.objects.create(title_en=customer.title_en, title_fa=customer.title_fa, parent=root, component=customer, display_order=1)
    product_menu = Menu.objects.create(title_en=product.title_en, title_fa=product.title_fa, parent=root, component=product, display_order=2)

    for order, service in enumerate(Service.objects.all(), start=1):
        hero_en, hero_fa, description_en = SERVICE_COPY.get(service.code, (service.name_en, service.name_fa, f"Use {service.name_en} to turn transaction data into practical business decisions."))
        page = Page.objects.create(
            service=service,
            slug=slugify(service.code.replace("_", "-")),
            doc_id=f"DOC-{service.code.replace('_', '-')}-001",
            title_en=service.name_en,
            title_fa=service.name_fa,
            description_en=description_en,
            description_fa=f"با {service.name_fa} داده تراکنش را به تصمیم عملی تبدیل کنید.",
            hero_title_en=hero_en,
            hero_title_fa=hero_fa,
        )
        component_menu = customer_menu if service.code in {"RFM", "CHURN", "CLV", "PROPENSITY"} else product_menu
        Menu.objects.create(title_en=service.name_en, title_fa=service.name_fa, parent=component_menu, service=service, display_order=order)
        steps = (
            ("Map transaction data", "نگاشت داده تراکنش", "Upload a familiar export and connect its columns to the required business fields.", "یک خروجی آشنا بارگذاری و ستون‌ها را به فیلدهای موردنیاز متصل کنید."),
            ("Run the analytics engine", "اجرای موتور تحلیل", "InsightFlow validates the data and runs the selected service in a background worker.", "InsightFlow داده را اعتبارسنجی و سرویس انتخابی را در پردازشگر پس‌زمینه اجرا می‌کند."),
            ("Activate your report", "استفاده از گزارش", "Review clear results, download the output, and decide the next customer action.", "نتایج را بررسی، خروجی را دانلود و اقدام بعدی را انتخاب کنید."),
        )
        for step_order, values in enumerate(steps, start=1):
            Step.objects.create(page=page, title_en=values[0], title_fa=values[1], description_en=values[2], description_fa=values[3], display_order=step_order)

    Menu.objects.create(title_en="Blog", title_fa="وبلاگ", url="/blog", display_order=2)
    Menu.objects.create(title_en="Documentation", title_fa="مستندات", url="/api/docs/", display_order=3)
    posts = (
        ("customer-segmentation-guide", "A practical guide to customer segmentation", "راهنمای عملی بخش‌بندی مشتری", "Turn transaction history into customer groups your team can act on.", "تاریخچه تراکنش را به گروه‌های قابل اقدام مشتری تبدیل کنید."),
        ("basket-analysis-decisions", "From basket rules to better product decisions", "از قوانین سبد تا تصمیم بهتر محصول", "Use confidence and lift responsibly when planning bundles and merchandising.", "برای برنامه‌ریزی بسته‌های فروش از اطمینان و لیفت به‌درستی استفاده کنید."),
        ("analytics-data-quality", "The data quality checks every analytics team needs", "کنترل‌های کیفیت داده برای هر تیم تحلیل", "Catch identifier, date, and amount issues before they affect a report.", "مشکلات شناسه، تاریخ و مبلغ را پیش از اثرگذاری بر گزارش پیدا کنید."),
    )
    for slug, title_en, title_fa, excerpt_en, excerpt_fa in posts:
        Blog.objects.get_or_create(slug=slug, defaults={"title_en": title_en, "title_fa": title_fa, "excerpt_en": excerpt_en, "excerpt_fa": excerpt_fa, "content_en": excerpt_en, "content_fa": excerpt_fa, "is_published": True, "published_at": timezone.now()})


class Migration(migrations.Migration):
    dependencies = [("website", "0002_componentpage_headermenuitem_servicepage_servicestep")]
    operations = [migrations.RunPython(seed_website, migrations.RunPython.noop)]
