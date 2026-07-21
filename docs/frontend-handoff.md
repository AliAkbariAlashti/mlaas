# Frontend Handoff: Pages, ML Workflow, URLs, and APIs

## 1. Scope and terminology

This document is the implementation contract for the InsightFlow frontend.

- Local frontend: `http://localhost:5173`
- Local backend: `http://localhost:8000`
- API base URL: `http://localhost:8000/api/v1` (or `/api/v1` through the Vite proxy)
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`
- Uploaded/generated media base: `http://localhost:8000/media/`

### MLflow clarification

There is currently **no MLflow tracking-server integration, MLflow experiment page, run ID, or MLflow URL in this repository**. “ML flow” in this product means the customer-facing machine-learning workflow described below: choose a service, upload data, map columns, start processing, poll status, and view a report. Do not add an iframe or link to an MLflow server unless the backend later provides a tracking URL and access policy.

The ML workflow pages requested from the frontend are:

| Page | Frontend URL |
| --- | --- |
| Analytics products | `/app/products` |
| Upload and column mapping | `/app/run/{service_code}` |
| Processing status | `/app/project/{project_id}/{service_code}` |
| Result report | `/app/report/{project_id}/{service_code}` |
| Analysis history | `/app/history` |
| Completed reports | `/app/reports` |

Supported active service codes are `RFM`, `MARKET_BASKET`, `PROPENSITY`, and `ANOMALY`.

## 2. Global frontend requirements

- Support English/LTR and Persian/RTL throughout the public site and workspace.
- Support light and dark themes.
- Public content endpoints require no token. Workspace endpoints require `Authorization: Bearer <access_token>`.
- The OTP endpoints also require no token.
- If an authenticated request returns `401`, refresh once, retry once, then sign the user out if refresh fails.
- Keep access token, refresh token, selected service, project ID, detected columns, and mapping state.
- Never persist the raw file contents in browser storage.
- Raw uploads are deleted by the backend after 48 hours.

## 3. Required pages and sections

### 3.1 Public website

#### Home — `/`

Sections:

1. Global header: brand, dynamic navigation, language, theme, sign-in/get-started action.
2. Hero: value proposition, “Get started”, and “View products”.
3. Product rail: active and private-beta services.
4. Why InsightFlow: product benefits.
5. Three-step workflow: log in, upload/select service, receive reports.
6. FAQ accordion.
7. Latest blog posts.
8. Get involved: LinkedIn, GitHub, and API documentation.
9. Footer: product/component links, blog, legal placeholders, social links.
10. Authentication modal: phone entry, OTP entry, then onboarding if required.

#### Component/category detail — `/components/{slug}`

Sections: category hero, description/media, related product rail. Current slugs are `customer-analytics` and `product-analytics`; navigation data remains authoritative.

#### Service marketing detail — `/services/{slug}`

Sections: hero, service availability, CTA, three “next steps”, and final CTA. Current slugs are generated from service codes, for example `/services/rfm` and `/services/market-basket`. Use the product API rather than hard-coding the list.

#### Blog list and detail

- List: `/blog`
- Detail: `/blog/{slug}`
- List sections: title/introduction and article cards.
- Detail sections: back link, title, excerpt, publish date, and content.

### 3.2 Authentication and onboarding

Authentication is a modal on the public site, not a separate route. It contains:

1. Phone number input.
2. Six-digit OTP input with resend countdown.
3. Business profile onboarding: company name, industry, commerce platform.

After success, route to `/app`. The development OTP is `123456` and expires in 120 seconds.

### 3.3 Authenticated workspace

#### Overview — `/app`

Sections: page heading/new analysis CTA, KPI cards, recent activity, usage-over-time chart, active-service quick launch, and help card.

#### Products — `/app/products`

Sections: service list, active/private-beta badge, number of required mapping fields, and Start/Request Access CTA.

#### Run analysis — `/app/run/{service_code}`

Sections and states:

1. Upload: project title and `.csv`, `.xls`, or `.xlsx` file.
2. Mapping: one selector for every required/optional key returned by the service catalog.
3. Submit: “Run analysis” for active services; “Join private beta” for inactive services.
4. Inline validation/error state.

Do not hard-code mappings. The `GET /services/` response is authoritative.

#### Processing — `/app/project/{project_id}/{service_code}`

Sections/states: processing spinner and status, success CTA to report, or failed message and new-upload CTA. Poll every 2–3 seconds and stop on `SUCCESS`, `FAILED`, `401`, or `404`.

#### Report — `/app/report/{project_id}/{service_code}`

Sections: report heading, Excel download when supplied, summary KPI cards, and detailed output table/chart. RFM, basket, propensity, and anomaly have different response shapes (see below).

#### History — `/app/history`

Sections: search, status filter, paginated project table, status badge, and links to processing/report pages.

#### Reports — `/app/reports`

Same core layout as history, filtered to projects for which `has_report` is true.

#### Credits — `/app/credits`

Sections: available balance, rules explaining credit use, and contact/support CTA. `/app/wallet` is currently an alias.

#### Business profile — `/app/profile`

Sections: account summary, read-only phone number, editable company/industry/platform, save confirmation/error.

#### Support — `/app/support`

Sections: mapping guidance, report guidance, and contact form/success state.

## 4. ML workflow and page/API mapping

```text
/app/products
  -> select service
/app/run/{service_code}
  -> POST upload
  -> map returned detected_columns
  -> POST start (active) OR POST waitlist (inactive)
/app/project/{project_id}/{service_code}
  -> poll GET status
  -> on SUCCESS
/app/report/{project_id}/{service_code}
  -> GET the result endpoint selected by service code
```

Result endpoint mapping:

| Service code | Result API |
| --- | --- |
| `RFM` | `/projects/{id}/rfm-results/` |
| `MARKET_BASKET` | `/projects/{id}/basket-results/` |
| `PROPENSITY` | `/projects/{id}/predictive-results/` |
| `ANOMALY` | `/projects/{id}/predictive-results/` |

Project status values are `PENDING`, `PROCESSING`, `SUCCESS`, and `FAILED`.

## 5. API reference with sample responses

Unless marked Public, requests require the bearer token. JSON is used except for file upload.

### Authentication

#### `POST /auth/send-otp/` — Public

Request:

```json
{"phone_number":"09123456789"}
```

Response `200`:

```json
{"message":"OTP verification code sent successfully.","expires_in_seconds":120}
```

#### `POST /auth/verify-otp/` — Public

Request:

```json
{"phone_number":"09123456789","otp_code":"123456"}
```

Response `200`:

```json
{"access_token":"eyJ...","refresh_token":"eyJ...","is_profile_complete":false}
```

Invalid/expired OTP `400`:

```json
{"detail":"Invalid or expired OTP code."}
```

#### `POST /auth/token/refresh/` — Public

Request and response:

```json
{"refresh":"eyJ..."}
```

```json
{"access":"eyJ..."}
```

### User profile

#### `GET /user/profile/`

Response `200`:

```json
{
  "id": 12,
  "phone_number": "09123456789",
  "company_name": "Chic Boutiques",
  "industry": "fashion",
  "platform": "woocommerce",
  "credit_limit": 9,
  "date_joined": "2026-07-21T09:30:00+03:30",
  "is_profile_complete": true
}
```

#### `PUT /user/profile/`

Request:

```json
{"company_name":"Chic Boutiques","industry":"fashion","platform":"woocommerce"}
```

Response `200`:

```json
{"status":"success"}
```

### Workspace and service catalog

#### `GET /services/`

Response `200` (array):

```json
[
  {
    "code": "RFM",
    "name_en": "RFM Segmentation",
    "name_fa": "بخش‌بندی هوشمند مشتریان",
    "is_active": true,
    "result_kind": "RFM",
    "required_mapping_fields": ["customer_id_column","date_column","invoice_id_column"],
    "optional_mapping_fields": ["amount_column"]
  }
]
```

#### `GET /dashboard/`

Response `200`:

```json
{
  "credits_remaining": 9,
  "total_projects": 5,
  "successful_projects": 3,
  "processing_projects": 1,
  "failed_projects": 1,
  "waitlist_requests": 0,
  "recent_projects": []
}
```

#### `GET /projects/`

Response `200` (array):

```json
[
  {
    "id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
    "title": "June customer analysis",
    "analysis_type": "RFM",
    "service_name_en": "RFM Segmentation",
    "service_name_fa": "بخش‌بندی هوشمند مشتریان",
    "status": "SUCCESS",
    "error_log": null,
    "has_report": true,
    "created_at": "2026-07-21T09:30:00+03:30"
  }
]
```

### Upload, mapping, and processing

#### `POST /projects/upload/`

Content type: `multipart/form-data`. Fields: `file`, `title` (max 100 characters), and `analysis_type` (service code).

Response `201`:

```json
{
  "project_id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
  "analysis_type": "RFM",
  "detected_columns": ["User ID","Invoice Date","Order Total","Invoice Number"]
}
```

Unsupported/invalid file `400` example:

```json
{"file":["Only CSV, XLS, and XLSX files are supported."]}
```

#### `POST /projects/{project_id}/start/`

Request (mapping values must exactly match detected column names):

```json
{
  "mapping": {
    "customer_id_column": "User ID",
    "date_column": "Invoice Date",
    "invoice_id_column": "Invoice Number",
    "amount_column": "Order Total"
  }
}
```

Response `202`:

```json
{
  "project_id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
  "status": "PROCESSING",
  "message": "Data ingestion complete. Analysis added to Celery queue."
}
```

Important errors: `402 {"detail":"No analysis credits remain."}`, `409` for an inactive/already-submitted project, and `400` for missing mappings.

#### `GET /projects/{project_id}/status/`

Responses:

```json
{"status":"PROCESSING"}
```

```json
{"status":"SUCCESS"}
```

```json
{"status":"FAILED","error":"Datetime format in column 'Invoice Date' cannot be parsed."}
```

#### `POST /projects/{project_id}/join-waitlist/`

No request body. Response `200`:

```json
{
  "status": "waitlisted",
  "message": "Your request for this automated engine has been registered. Our accounts team will contact you shortly to run an isolated private-beta trial on your raw data."
}
```

### Result APIs

#### `GET /projects/{project_id}/rfm-results/`

```json
{
  "summary": {"total_customers":12450,"churn_rate_percentage":18.4,"repeat_buyer_percentage":42.7},
  "chart_data": [{"segment":"Loyal Customers","count":1450,"percentage":11.6}],
  "actionable_insights": [{"segment":"Loyal Customers","recommendation":"Offer early access to new products."}],
  "download_excel_url": "downloads/rfm_out_8f3b89b4.xlsx"
}
```

#### `GET /projects/{project_id}/basket-results/`

```json
{
  "rules": [
    {"antecedent":"Wireless Headphones","consequent":"Carrying Case","support":0.12,"confidence":0.82,"lift":3.4}
  ]
}
```

#### `GET /projects/{project_id}/predictive-results/` — Propensity

```json
{
  "analysis_type": "PROPENSITY",
  "summary": {"customers_scored":4000,"training_accuracy":0.81,"training_roc_auc":0.84,"result_file_path":"downloads/propensity_out_8f3b89b4.xlsx"},
  "scores": [{"customer_id":"C-120","propensity_score":92.5}]
}
```

#### `GET /projects/{project_id}/predictive-results/` — Anomaly

```json
{
  "analysis_type": "ANOMALY",
  "summary": {"total_checked":45000,"anomalies_found":12,"result_file_path":"downloads/anomaly_out_8f3b89b4.xlsx"},
  "anomalies_list": [{"row_index":1402,"invoice_id":"INV-9921","amount":980000.0,"date":"2026-06-20T03:00:00+00:00","anomaly_score":-0.113245}]
}
```

Resolve relative download paths against `/media/`. Anomalies are review candidates, not confirmed fraud.

### Public website APIs

#### `GET /website/navigation/` — Public

```json
[
  {"id":1,"title_en":"Components","title_fa":"اجزا","href":"#","children":[{"id":2,"title_en":"Customer Analytics","title_fa":"تحلیل مشتری","href":"/components/customer-analytics","children":[]}]}
]
```

#### `GET /website/components/` and `GET /website/components/{slug}/` — Public

List returns an array; detail returns one object:

```json
{"slug":"customer-analytics","title_en":"Customer Analytics","title_fa":"تحلیل مشتری","description_en":"Understand customer behavior, value, and purchase intent.","description_fa":"رفتار، ارزش و قصد خرید مشتری را بهتر بشناسید.","hero_media_url":""}
```

#### `GET /website/products/` and `GET /website/products/{slug}/` — Public

List returns an array; detail returns one object:

```json
{
  "slug":"rfm",
  "code":"RFM",
  "is_active":true,
  "doc_id":"DOC-RFM-001",
  "title_en":"RFM Segmentation",
  "title_fa":"بخش‌بندی هوشمند مشتریان",
  "description_en":"Group customers by recency, frequency, and value to focus retention actions.",
  "description_fa":"با بخش‌بندی هوشمند مشتریان داده تراکنش را به تصمیم عملی تبدیل کنید.",
  "image_url":"",
  "hero_title_en":"Understand every customer relationship",
  "hero_title_fa":"هر رابطه با مشتری را بشناسید",
  "hero_media_url":"",
  "get_started_title_en":"Get started",
  "get_started_title_fa":"شروع کنید",
  "steps":[{"title_en":"Map transaction data","title_fa":"نگاشت داده تراکنش","description_en":"Upload a familiar export and connect its columns to the required business fields.","description_fa":"یک خروجی آشنا بارگذاری و ستون‌ها را به فیلدهای موردنیاز متصل کنید.","image_url":"","display_order":1}]
}
```

#### `GET /website/blog/` and `GET /website/blog/{slug}/` — Public

List returns an array; detail returns one object:

```json
{"slug":"customer-segmentation-guide","title_en":"A practical guide to customer segmentation","title_fa":"راهنمای عملی بخش‌بندی مشتری","excerpt_en":"Turn transaction history into customer groups your team can act on.","excerpt_fa":"تاریخچه تراکنش را به گروه‌های قابل اقدام مشتری تبدیل کنید.","content_en":"Article content...","content_fa":"محتوای مقاله...","published_at":"2026-07-21T09:30:00+03:30"}
```

#### `POST /website/contact/` — Public

Request:

```json
{"name":"Sara Ahmadi","email":"sara@example.com","phone_number":"09123456789","company_name":"Chic Boutiques","subject":"Mapping review","message":"Please help us validate our export."}
```

Response `201`:

```json
{"status":"received","message":"Thank you. Our team will contact you shortly."}
```

## 6. Error and UX contract

| HTTP status | Meaning | Frontend action |
| --- | --- | --- |
| `400` | Invalid OTP, payload, mapping, or file | Show field/API message; preserve user input |
| `401` | Missing/expired access token | Refresh once; otherwise sign out |
| `402` | No credits | Show credit state and support CTA |
| `404` | Missing/not-owned project or content | Return to the appropriate list page |
| `409` | Inactive service or project already submitted | Show private-beta/existing-run state |
| `500` | Unexpected backend error | Keep the project ID and offer retry/support |

The API may return DRF field errors such as `{"field":["message"]}` or a general `{"detail":"message"}`. The frontend should support both.

## 7. Implementation acceptance checklist

- All listed routes work on direct navigation and browser refresh.
- Public content is API-driven and has loading, empty, and error states.
- Auth token refresh retries at most once.
- Profile-incomplete users complete onboarding before using the workspace.
- Service availability and mapping fields come from `/services/`.
- Upload uses multipart data and stores the returned project ID.
- Processing polling is cleaned up when the view unmounts.
- Each service code opens the correct report endpoint.
- Relative report download paths resolve through `/media/`.
- English/Persian direction, content, dates, and controls are correct.
- Responsive behavior covers mobile, tablet, and desktop.
- No MLflow UI/link is shown until an actual MLflow integration is delivered.
