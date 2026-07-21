from django.db import migrations


MAPPINGS = {
    "rfm-segmentation": '''{
  "mapping": {
    "customer_id_column": "customer_id",
    "date_column": "invoice_date",
    "invoice_id_column": "invoice_id",
    "amount_column": "total_amount"
  }
}''',
    "market-basket": '''{
  "mapping": {
    "invoice_id_column": "invoice_id",
    "product_name_column": "product_name",
    "product_category_column": "product_category",
    "quantity_column": "quantity"
  }
}''',
    "purchase-propensity": '''{
  "mapping": {
    "customer_id_column": "customer_id",
    "date_column": "invoice_date",
    "amount_column": "invoice_amount"
  }
}''',
    "sales-anomaly": '''{
  "mapping": {
    "invoice_id_column": "invoice_id",
    "date_column": "invoice_date",
    "amount_column": "total_amount"
  }
}''',
}


def add_mapping_examples(apps, schema_editor):
    Page = apps.get_model("developer_api", "DocumentationPage")
    for slug, payload in MAPPINGS.items():
        page = Page.objects.filter(slug=slug).first()
        if not page:
            continue
        block = page.blocks.filter(kind="CODE", heading_en="Start through the API").first()
        if block:
            prefix = block.code.split("# Then start the returned project")[0]
            block.code = (
                prefix
                + "# Then start the returned project\n"
                + "curl -X POST http://localhost:8000/api/v1/projects/$PROJECT_ID/start/ \\\n"
                + '  -H "X-API-Key: $MLAAS_API_KEY" \\\n'
                + '  -H "Content-Type: application/json" \\\n'
                + f"  -d '{payload}'"
            )
            block.save(update_fields=("code",))


class Migration(migrations.Migration):
    dependencies = [("developer_api", "0004_seed_documentation")]
    operations = [migrations.RunPython(add_mapping_examples, migrations.RunPython.noop)]
