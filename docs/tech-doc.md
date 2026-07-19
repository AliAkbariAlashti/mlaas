Here is the complete, production-ready **Final Technical Documentation (Architecture & API Spec)** translated into English. You can hand this directly to your Front-end developer as the formal technical contract.

---

# 🏗️ 1. System Architecture & Data Flow

The system is designed around an **Asynchronous Event-Driven Architecture** to ensure that heavy Pandas operations and Machine Learning modeling do not block Django's main Request-Response cycle.

```
                  ┌──────────────────────────────────────────────┐
                  │                 FRONT-END                    │
                  └──────┬──────────────────────────────▲────────┘
                         │                              │
                (1) Upload File & Map JSON       (4) Polling Status
                         │                              │
                         ▼                              │
                  ┌─────────────────────────────────────┴────────┐
                  │             DJANGO BACKEND (API)             │
                  └──────┬───────────────────────────────────────┘
                         │
                (2) Push Task to Queue
                         │
                         ▼
                  ┌──────────────┐
                  │ REDIS BROKER │
                  └──────┬───────┘
                         │
                (3) Pop Task
                         │
                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               CELERY WORKER                  │
                  │  ┌────────────────────────────────────────┐  │
                  │  │          CORE ML ENGINE (Python)       │  │
                  │  │  - Pandas/Sklearn / XGBoost / MLXtend  │  │
                  │  └───────────────────┬────────────────────┘  │
                  └──────────────────────│───────────────────────┘
                                         │
                                (5) Write Results
                                         │
                                         ▼
                                ┌────────────────┐
                                │ POSTGRESQL DB  │
                                └────────────────┘

```

---

# 🗄️ 2. Database Schema (PostgreSQL)

To comply with data privacy and resource constraints, raw uploaded files are automatically purged via a scheduled `Celery Beat Task` after 48 hours, while the computed analytical metadata is preserved permanently.

### `users_user`

| Field Name | Type | Attributes | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary Key | Unique User ID |
| `phone_number` | VARCHAR(15) | Unique, Index | User's mobile number (used for OTP Login) |
| `company_name` | VARCHAR(100) | Nullable | Name of the business/company |
| `industry` | VARCHAR(50) | Nullable | Business vertical (e.g., fashion, electronics) |
| `platform` | VARCHAR(30) | Nullable | Current e-commerce platform (WooCommerce, Shopify) |
| `credit_limit` | INT | Default: 3 | Number of remaining free analysis credits |
| `date_joined` | TIMESTAMP | Auto Now Add | User registration timestamp |

### `analytics_project`

| Field Name | Type | Attributes | Description |
| --- | --- | --- | --- |
| `id` | UUID | Primary Key | Unique Project/Analysis ID |
| `user_id` | UUID | ForeignKey | References `users_user.id` |
| `title` | VARCHAR(100) |  | User-defined title for this batch/file |
| `analysis_type` | VARCHAR(20) | Choices (10 Types) | Selected product (RFM, ANOMALY, PROPENSITY, etc.) |
| `status` | VARCHAR(15) | PENDING/PROCESSING/SUCCESS/FAILED | Live state of the asynchronous worker pipeline |
| `raw_file_path` | VARCHAR(255) |  | Temporary file system/S3 path of the uploaded file |
| `data_mapping` | JSONB |  | Column mapping layout mapped by the user in UI |
| `error_log` | TEXT | Nullable | Exception trace if the Celery task fails |
| `created_at` | TIMESTAMP | Auto Now Add | Request timestamp |

### `analytics_rfmresult` (One-to-One with Project)

* `project_id` (UUID - PK, FK)
* `summary` (JSONB): High-level aggregates `{"total_customers": 4000, "active_rate": 75}`
* `chart_data` (JSONB): Clean segment distribution optimized for charts `[{"name": "Loyal", "count": 200}]`
* `result_file_path` (VARCHAR): Download link for the final processed, segmented Excel file.

### `analytics_basketresult` (One-to-One with Project)

* `project_id` (UUID - PK, FK)
* `rules` (JSONB): Extracted association rules `[{"antecedent": "A", "consequent": "B", "confidence": 0.85}]`

### `analytics_mlresult` (One-to-One with Project)

*Stores inference data for Predictive AI products like Propensity Scoring and Anomaly Detection*

* `project_id` (UUID - PK, FK)
* `metrics` (JSONB): Overall model accuracy/performance stats
* `visualization_data` (JSONB): Targeted anomaly lists or histogram distribution values for UI charts.

---

# 🔌 3. API Contract Spec (Endpoints)

All endpoints—excluding the Landing Page stats and Authentication workflows—stricly require an `Authorization: Bearer <token>` Header.

---

## 🔐 Section 1: Authentication (OTP-Based)

### 1. Request OTP

* **Endpoint:** `POST /api/v1/auth/send-otp/`
* **Payload (Front-end ➔ Back-end):**

```json
{
  "phone_number": "09123456789"
}

```

* **Response (Back-end ➔ Front-end):** `200 OK`

```json
{
  "message": "OTP verification code sent successfully.",
  "expires_in_seconds": 120
}

```

### 2. Verify OTP & Authenticate

* **Endpoint:** `POST /api/v1/auth/verify-otp/`
* **Payload (Front-end ➔ Back-end):**

```json
{
  "phone_number": "09123456789",
  "otp_code": "5849"
}

```

* **Response (Back-end ➔ Front-end):** `200 OK`

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "is_profile_complete": false
}

```

---

## 📊 Section 2: Project & Onboarding Management

### 3. Complete Business Profile

* **Endpoint:** `PUT /api/v1/user/profile/`
* **Payload (Front-end ➔ Back-end):**

```json
{
  "company_name": "Chic Boutiques",
  "industry": "fashion",
  "platform": "woocommerce"
}

```

* **Response:** `200 OK` `{ "status": "success" }`

### 4. Initial File Upload (Schema Extractor)

* **Endpoint:** `POST /api/v1/projects/upload/`
* **Payload:** `multipart/form-data` containing the file field `file`, alongside string parameters `title` and `analysis_type`.
* **Response:** `201 Created`

```json
{
  "project_id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
  "analysis_type": "RFM",
  "detected_columns": ["User ID", "Invoice Date", "Order Total", "Product Title", "Invoice Number"]
}

```

*(Note: The backend executes no computation here; it merely reads the headers of the file and returns them instantly to trigger the Drag & Drop schema-mapper UI).*

---

## 🧠 Section 3: Data Pipeline & Task Ingestion

### 5. Submit Column Mapping & Trigger Engine

* **Endpoint:** `POST /api/v1/projects/{project_id}/start/`
* **Payload (Front-end ➔ Back-end):**

```json
{
  "mapping": {
    "customer_id_column": "User ID",
    "date_column": "Invoice Date",
    "amount_column": "Order Total",
    "invoice_id_column": "Invoice Number",
    "product_name_column": null 
  }
}

```

*(Note: Unmapped optional columns are explicitly submitted as `null`).*

* **Response:** `202 Accepted`

```json
{
  "project_id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
  "status": "PROCESSING",
  "message": "Data ingestion complete. Analysis added to Celery queue."
}

```

### 6. Process Status Check (Polling)

* **Endpoint:** `GET /api/v1/projects/{project_id}/status/`
* **Response:** `200 OK`
* **Scenario A (Active Execution):** `{ "status": "PROCESSING" }`
* **Scenario B (Data Science/Parsing Error):** `{ "status": "FAILED", "error": "Datetime format in column 'Invoice Date' cannot be parsed." }`
* **Scenario C (Execution Finished):** `{ "status": "SUCCESS" }`

---

## 📈 Section 4: Analytics Result Delivery

Once polling resolves to `SUCCESS`, the Front-end triggers the specific fetch API matching the `analysis_type`:

### 7. Fetch RFM Results

* **Endpoint:** `GET /api/v1/projects/{project_id}/rfm-results/`
* **Response:** `200 OK`

```json
{
  "summary": {
    "total_customers": 12450,
    "churn_rate_percentage": 18.4
  },
  "chart_data": [
    { "segment": "Loyal Customers", "count": 1450, "percentage": 11.6 },
    { "segment": "At Risk", "count": 3100, "percentage": 24.8 },
    { "segment": "Sleeping Heroes", "count": 890, "percentage": 7.1 }
  ],
  "actionable_insights": [
    {
      "segment": "At Risk",
      "tips": "This segment hasn't bought anything for 60+ days but was highly profitable before. Download their phone lists and send an urgent, localized SMS offer."
    }
  ],
  "download_excel_url": "/media/downloads/rfm_out_8f3b.xlsx"
}

```

### 8. Fetch Market Basket Rules

* **Endpoint:** `GET /api/v1/projects/{project_id}/basket-results/`
* **Response:** `200 OK`

```json
{
  "rules": [
    {
      "antecedent": "Wireless Headphones",
      "consequent": "Silicon Carrying Case",
      "confidence": 0.82,
      "lift": 3.4,
      "actionable_tip": "Highly bound correlation. Feature these items together as an up-sell bundle on the checkout page."
    }
  ]
}

```

### 9. Fetch Predictive ML Results (Propensity / Anomaly)

* **Endpoint:** `GET /api/v1/projects/{project_id}/predictive-results/`
* **Response:** `200 OK`

```json
{
  "analysis_type": "ANOMALY",
  "summary": { "total_checked": 45000, "anomalies_found": 12 },
  "anomalies_list": [
    { "row_index": 1402, "invoice_id": "INV-9921", "reason": "System flagged a zero-amount transaction with bulk quantities executed at 03:00 AM." }
  ]
}

```

---

## ⏳ Section 5: Monetizing the "Coming Soon" Products

For the 6 inactive products, the full UI flow (Documentation and Drag & Drop file structure verification) executes identically to make the platform feel robust. However, upon submitting the final mapping, the Front-end intercepts the action and sends it here:

### 10. Enroll User in Private Beta Waitlist

* **Endpoint:** `POST /api/v1/projects/{project_id}/join-waitlist/`
* **Response:** `200 OK`

```json
{
  "status": "waitlisted",
  "message": "Your request for this automated engine has been registered. Our accounts team will contact you shortly to run an isolated private-beta trial on your raw data."
}

```

*(Product Design Tip: This logs a high-intent B2B lead in your admin panel, allowing you to manually upsell enterprise analytical consulting contracts before you write a single line of backend production code).*