This is the final, comprehensive, and production-ready **Product Requirement Document (PRD)** for your MLaaS platform. It integrates the business mechanics, data models, API schemas, dual-language capabilities, and the "Coming Soon" marketing psychologies into a single master engineering source of truth.

---

# 📝 Product Requirement Document (PRD)

## 📌 1. Document Control & Overview

| Project Name | AI-Analytics (Working Title) |
| --- | --- |
| **Product Version** | v1.0.0 (MVP) |
| **Target Audience** | B2B E-commerce Managers, Growth Marketers, Shop Operators |
| **Core Architecture** | Django Core API + Celery Worker Core + React Single-Page App |
| **Languages Supported** | English (LTR) & Persian/Farsi (RTL) |

### 1.1 Executive Summary

AI-Analytics is a low-friction, cloud-based Machine Learning as a Service (MLaaS) platform that allows e-commerce operators to upload transactional raw data (`.csv` or `.xlsx`) and automatically apply advanced data science algorithms to optimize revenue, track loyalty, and detect anomalies.

The MVP strategy intentionally displays a highly robust catalog of **10 strategic products**: **4 features are fully operational**, while **6 features are deployed as "Coming Soon" engines** featuring functional onboarding loops to capture high-intent enterprise pipeline leads before writing core engine code.

---

## 🎯 2. The 10-Product Functional Scope Matrix

The application splits its technical offerings into two explicit categories.

### 2.1 Suite A: Data Analytics Suite (توتیف و تحلیل داده‌ها)

*Focuses on diagnostic analytics, behavior segmentation, and looking at historic transactional realities to yield quick marketing actions.*

| # | Product Name (EN) | Product Name (FA) | Type | Variable Matrix Required |
| --- | --- | --- | --- | --- |
| **01** | **RFM Segmentation** | **بخش‌بندی هوشمند مشتریان** | 🟢 **Active** | **Req:** `customer_id`, `invoice_date`, `invoice_id`<br>

<br>**Opt:** `total_amount` |
| **02** | **Market Basket Analysis** | **تحلیل سبد خرید و اقلام هم‌نشین** | 🟢 **Active** | **Req:** `invoice_id`, `product_name`<br>

<br>**Opt:** `product_category`, `quantity` |
| **03** | Customer Churn Audit | آنالیز ریزش لحظه‌ای مشتریان | 🟡 *Coming Soon* | *Waitlisted* |
| **04** | Customer Lifetime Value | گزارش ارزش طول عمر مشتری | 🟡 *Coming Soon* | *Waitlisted* |
| **05** | Product Share Matrix | تحلیل سهم بازار کالاها | 🟡 *Coming Soon* | *Waitlisted* |

### 2.2 Suite B: Predictive AI Engine (هوش مصنوعی پیش‌بین)

*Utilizes advanced predictive modeling to infer future consumer behaviors and system anomalies.*

| # | Product Name (EN) | Product Name (FA) | Type | Variable Matrix Required |
| --- | --- | --- | --- | --- |
| **06** | **Purchase Propensity Score** | **پیش‌بینی احتمال خرید آتی** | 🟢 **Active** | **Req:** `customer_id`, `invoice_date`, `invoice_amount`<br>

<br>**Opt:** None |
| **07** | **Sales Anomaly Detection** | **تشخیص آنومالی و رفتارهای مشکوک** | 🟢 **Active** | **Req:** `invoice_id`, `invoice_date`, `total_amount`<br>

<br>**Opt:** None |
| **08** | Demand Forecasting AI | پیش‌بینی پویای تقاضا و انبار | 🟡 *Coming Soon* | *Waitlisted* |
| **09** | Personalized Recommender | موتور توصیه‌گر شخصی‌سازی شده | 🟡 *Coming Soon* | *Waitlisted* |
| **10** | Price Optimization Engine | مدل‌سازی حساسیت قیمت و سود | 🟡 *Coming Soon* | *Waitlisted* |

---

## 🎨 3. User Experience & Multilingual Workflow Rules

### 3.1 Localization Mechanics

1. **The Global State Switcher:** The top navigation header houses a explicit `EN | FA` toggle switch accessible at all historical points of execution.
2. **Dynamic Bi-Directional Layout Shifting:**
* Selecting `FA` wraps the application view matrix in HTML directional property tags: `dir="rtl"`. Fonts dynamically substitute to Persian typography assets (e.g., *Vazirmatn* or *IRANSans*). Layout components, navigation lists, and form icons invert seamlessly from right-to-left.
* Selecting `EN` triggers `dir="ltr"` utilizing standard modern sans-serif fonts (e.g., *Inter* or *Roboto*).


3. **Internal Parsing Integrity:** All components, graph titles, legend keys, column configurations, error summaries, and tooltips must change dynamically depending on the global localization flag.

### 3.2 The Core User Persona Path

```
[Landing Page (EN/FA)] ➔ [Simulated OTP Verification Modal] ➔ [3-Field Business Onboarding Form]
                                                                          │
 ┌───────────────────────────────────◀────────────────────────────────────┘
 ▼
[Main Dashboard Workspace]
 │
 ├─► Select 🟢 Active Tool ────► [Upload Area] ➔ [Drag & Drop Mapping] ➔ [Celery Simulation] ➔ [Interactive Graphs Report]
 │
 └─► Select 🟡 Inactive Tool ──► [Tool Specs] ➔ [Upload Area] ➔ [Drag & Drop Mapping] ➔ [Waitlist Intercept Modal]

```

---

## 🛠️ 4. Detailed Component & System Specifications

### 4.1 Global Sidebar & Structural Layout

* **Sidebar:** Houses the primary brand logo and functional navigation routes matching the 10 products structured under their respective category headers (*Data Analytics Suite* & *Predictive AI Engine*). Includes links for *Analysis History* and *Business Profile*.
* **Top Header:** Persistent display containing:
* Multilingual Language Switcher Toggle (`EN` / `FA`).
* User State Block: Initially displays a clear "Sign In / Register" CTA button. Upon successful verification simulation, switches to an interactive profile badge displaying the user's phone record and a distinct visual chip: `"3 Free Credits Left" / "۳ اعتبار رایگان باقی‌مانده"`.



### 4.2 The "IKEA Effect" Schema Mapper Component (Core Interaction)

When any product detail view is initiated, the UI exposes a 3-step procedural workspace:

#### Step 1: Secure Data Dropzone

An attractive, standardized multi-format uploading hub supporting `.csv`, `.xls`, and `.xlsx`. Dragging or locating a file triggers an immediate, simulated client-side ingestion phase (~1s loop progress line). The UI extracts the structural header array out of the test sheet file.

* *Standard English Upload Sandbox Array:* `["User ID", "Invoice Date", "Order Total", "Product Title", "Invoice Number"]`
* *Standard Persian Upload Sandbox Array:* `["کد کاربر", "تاریخ فاکتور", "مبلغ کل", "نام کالا", "شماره خرید"]`

#### Step 2: The Drag & Drop Variable Mapping Canvas

The workspace changes into a two-column structural transformation matrix:

* **Draggable Column:** The list of user-extracted headers formatted as draggable token cards.
* **Droppable Drop-Zones:** The target data collection schema fields needed by the chosen machine learning tool (e.g., RFM requires `Customer ID Identifier`, `Invoice Datetime String`, and `Unique Invoice Key`).
* **Validation Engine Constraints:** Required drop-zones must reflect clear semantic warnings (Red asterisk notation). The primary action execution button, `"Run Machine Learning Engine" / "اجرای موتور هوش مصنوعی"`, must remain structurally disabled until all mandatory target drop-zones have had a token successfully dropped onto them.

#### Step 3: Asynchronous Process Loader Simulation

Clicking the engine submission action kicks off a stylized loading module simulating the background server orchestration architecture (Django + Celery + Redis). The interface blocks background navigation and walks the customer through real-time state flags over 4 seconds:

1. `PENDING (Enqueuing Data Engine)` ➔ `در انتظار (صف پردازش داده‌ها)`
2. `PROCESSING (Running Scikit-Learn/Apriori Pipelines...)` ➔ `در حال پردازش (اجرای خط لوله هوش مصنوعی...)`
3. `SUCCESS (Rendering Comprehensive Graphics)` ➔ `موفقیت‌آمیز (تولید گزارش‌های نهایی)`

### 4.3 Data Visualization & Analytical Dashboards

Upon successful pipeline processing, step 3 resolves into clean visual data reports:

* **RFM Engine:** A grid consisting of high-level KPIs (Total Unique Base, Churn Risk Ratio, Repeat Buyer Frequency), backed by an interactive Recharts Pie/Donut layout demonstrating segment size volume, alongside clear text cards outlining actionable business tips for each tier.
* **Market Basket Rules Engine:** A professional analytical database table parsing the transactional rules found via computational algorithms: `[Antecedent Product] ➔ [Consequent Product] | Confidence Factor % | Lift Value`.
* **Predictive Engines:** Charts demonstrating custom scores (0-100 propensity models) or timeline tables highlighting exact data index positions where anomalies were successfully isolated.

### 4.4 Coming Soon Conversion Funnel Hook

When a operator initiates a **Coming Soon** product card:

1. The platform displays high-end graphic design mockups of the upcoming analytics layout, but overlays an active documentation frame explaining the machine learning formulas planned for deployment (e.g., Time-Series, XGBoost modeling variants).
2. The platform *forces* the user to walk through the exact same File Upload and Drag-and-Drop Mapping UI layouts as the operational tools. This creates deep psychological investment.
3. Upon clicking the final button, instead of a calculation progress engine, a high-end, premium modal window appears: **"Join Enterprise Private Beta / عضویت در بتای اختصاصی"**. Clicking the registration confirmation button triggers a mock tracking endpoint logging the user's account details to your sales database as an enterprise consultation candidate, updating the workspace with a confirmation state:

> *"You have been added to the Private Beta. Our accounts team will contact you shortly to run an isolated private-beta trial on your raw data structure."*

---

## 🏗️ 5. Technical & Engineering Specs (The Contract)

### 5.1 Architecture Diagram

```
                  ┌──────────────────────────────────────────────┐
                  │          REACT FRONT-END (SPA)               │
                  │   - i18n Layout (EN: LTR / FA: RTL)          │
                  │   - Interactive Drag & Drop Mapper Component  │
                  └──────┬──────────────────────────────▲────────┘
                         │                              │
             (1) Upload File & Map JSON        (4) Polling Engine State
                         │                              │
                         ▼                              │
                  ┌─────────────────────────────────────┴────────┐
                  │          DJANGO REST BACKEND (API)           │
                  └──────┬───────────────────────────────────────┘
                         │
              (2) Ingest Task Payload
                         │
                         ▼
                  ┌──────────────┐
                  │ REDIS BROKER │
                  └──────┬───────┘
                         │
              (3) Dequeue Ingestion
                         │
                         ▼
                  ┌──────────────────────────────────────────────┐
                  │              CELERY ASYNC WORKER             │
                  │   Engine Modules: Pandas, Sklearn, MLXtend   │
                  └──────────────────────┬───────────────────────┘
                                         │
                                 (5) Write Schema Result
                                         │
                                         ▼
                                ┌────────────────┐
                                │ POSTGRESQL DB  │
                                └────────────────┘

```

### 5.2 Core PostgreSQL Schema Definition

```sql
-- Core User Account Extensions
CREATE TABLE users_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    company_name VARCHAR(100) NULL,
    industry VARCHAR(50) NULL,
    platform VARCHAR(30) NULL,
    credit_limit INT DEFAULT 3,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Central Project Processing Tracker
CREATE TABLE analytics_project (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users_user(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    analysis_type VARCHAR(20) NOT NULL, -- 'RFM', 'MARKET_BASKET', 'CHURN', etc.
    status VARCHAR(15) DEFAULT 'PENDING', -- 'PENDING', 'PROCESSING', 'SUCCESS', 'FAILED'
    raw_file_path VARCHAR(255) NOT NULL,
    data_mapping JSONB NOT NULL,
    error_log TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

```

### 5.3 Core API Production Contract Matrix

All analytical paths assume a valid JWT Header sequence: `Authorization: Bearer <token>`.

#### Endpoint 1: Schema File Extractor

* **Method & Route:** `POST /api/v1/projects/upload/`
* **Payload Format:** `multipart/form-data` containing parameters `file` (Excel/CSV payload), `title` (String descriptor), and `analysis_type` (Enum lookup key).
* **JSON Output Model (201 Created):**

```json
{
  "project_id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
  "analysis_type": "RFM",
  "detected_columns": ["User ID", "Invoice Date", "Order Total", "Product Title", "Invoice Number"]
}

```

#### Endpoint 2: Submit Column Configuration Schema

* **Method & Route:** `POST /api/v1/projects/{project_id}/start/`
* **JSON Input Model:**

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

* **JSON Output Model (202 Accepted):**

```json
{
  "project_id": "8f3b89b4-3d68-4a68-96bf-11a5113f8999",
  "status": "PROCESSING",
  "message": "Data pipeline successfully initialized inside processing workers."
}

```

#### Endpoint 3: Processing Pipeline Polling Monitor

* **Method & Route:** `GET /api/v1/projects/{project_id}/status/`
* **JSON Output Model Options (200 OK):**
* *Processing Loop State:* `{"status": "PROCESSING"}`
* *Fatal Execution Failure State:* `{"status": "FAILED", "error": "Datetime formats within parsed row records could not be resolved."}`
* *Operational Success Resolution:* `{"status": "SUCCESS"}`



#### Endpoint 4: Fetch Output Reports (Example: RFM Tool Variant)

* **Method & Route:** `GET /api/v1/projects/{project_id}/rfm-results/`
* **JSON Output Model (200 OK):**

```json
{
  "summary": {
    "total_customers": 12450,
    "churn_rate_percentage": 18.4
  },
  "chart_data": [
    { "segment": "Loyal Customers", "count": 1450, "percentage": 11.6 },
    { "segment": "At Risk", "count": 3100, "percentage": 24.8 }
  ],
  "actionable_insights": [
    {
      "segment": "At Risk",
      "tips": "Targeted cohort volume has passed safe parameters. Export the data tracking file and execute immediate customer re-engagement campaigns."
    }
  ],
  "download_excel_url": "/media/downloads/rfm_out_8f3b.xlsx"
}

```

#### Endpoint 5: Enterprise Lead Conversion Tracking Node

* **Method & Route:** `POST /api/v1/projects/{project_id}/join-waitlist/`
* **JSON Output Model (200 OK):**

```json
{
  "status": "waitlisted",
  "message": "Account tracking flag successfully recorded for the selected private beta product engine."
}

```

---

## 📈 6. Key Performance Indicators (KPIs) & Target Goals

1. **User Activation Metric:** Greater than 45% of registered users successfully map a mock or production spreadsheet through one of the 4 operational toolsets within their initial 48 hours.
2. **Product Validation Pipeline Capture:** Over 25% of all users onboarding data pipeline configurations choose to trigger the Waitlist flow on at least one **Coming Soon** product, providing a clear data-driven roadmap for feature development.
3. **Data Localization Retention Optimization:** Achieving zero statistical dropout discrepancies between users utilizing the English interface layout vs the Persian interface layout during the Drag & Drop schema configuration step.