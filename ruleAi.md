# ruleAi.md — AI Rules for eFMS/eTMS Automation Framework

> **Purpose:** This document is the single source of truth for any AI model (Claude, GPT, Gemini, Cursor Agent, Copilot, etc.) to **read, understand, and write** automation tests in this repository.
>
> **Language:** English (code and comments remain English).
> **Stack:** Python 3.12+, pytest, Playwright (sync API), pytest-html, pytest-reportportal, Pydantic Settings, Loguru.

---

## Table of Contents

1. [Quick Start for AI](#1-quick-start-for-ai)
2. [Repository Map](#2-repository-map)
   - [2.1 Framework Architecture & Layers](#21-framework-architecture--layers)
   - [2.2 Implemented Test Inventory](#22-implemented-test-inventory)
3. [Architecture Rules (MUST follow)](#3-architecture-rules-must-follow)
   - [3.6 Wait & Timing Strategy](#36-wait--timing-strategy-no-hard-coded-waits)
4. [Naming Conventions](#4-naming-conventions)
   - [4.1 Test Class Organization](#41-test-class-organization)
5. [Manual Test Case Sheet → Automation (CANONICAL)](#5-manual-test-case-sheet--automation-canonical)
   - [5.11 Multi-Scenario Navigation Tests](#511-multi-scenario-navigation-tests)
   - [5.12 Menu Module POM Pattern](#512-menu-module-pom-pattern)
   - [5.13 Booking Receipt CRUD (FMS_BR_001–005)](#513-booking-receipt-crud-fms_br_001005)
   - [5.14 XPath Catalog — Booking Receipt](#514-xpath-catalog--booking-receipt)
6. [How to Write a UI Test (Step-by-Step)](#6-how-to-write-a-ui-test-step-by-step)
7. [How to Write a Page Object](#7-how-to-write-a-page-object)
8. [How to Write Test Data (JSON)](#8-how-to-write-test-data-json)
9. [How to Write an API Test](#9-how-to-write-an-api-test)
10. [How to Write a DB Test](#10-how-to-write-a-db-test)
11. [Pytest Markers & Fixtures Reference](#11-pytest-markers--fixtures-reference)
12. [Run Commands](#12-run-commands)
    - [12.1 CI/CD Pipeline (Jenkins)](#121-cicd-pipeline-jenkins)
13. [Complete Examples (Copy-Paste Ready)](#13-complete-examples-copy-paste-ready)
14. [Known Issues & Do NOT Replicate](#14-known-issues--do-not-replicate)
15. [Improvement Backlog](#15-improvement-backlog)
16. [Clean Code & Reuse (DRY — No Duplication)](#16-clean-code--reuse-dry--no-duplication)
17. [AI Checklist Before Submitting Code](#17-ai-checklist-before-submitting-code)

---

## 1. Quick Start for AI

When asked to **write a new automation test from a manual test case sheet**, follow this order:

```
1. Read manual sheet columns: TC_ID, Module, Scenario, Priority, Preconditions, TestData_ID, Steps, Expected Result
2. Identify application       → efms | etms
3. Map TestData_ID            → .env credentials (see Section 5)
4. Add JSON test data         → tests/testdata/dataTest-{app}.json  (key = test function name)
5. Search existing code first   → reuse Page Object / BasePage / fixture methods (Section 16)
6. Create/update Page Object  → one @log_method per manual Step — extend existing page if possible
7. Write test file            → tests/{app}/test_{app}_{module}.py (class-based when module has 2+ TCs)
8. Add markers                → class: @pytest.mark.{app}+{suite} | method: @pytest.mark.tc_id | JSON priority → auto via DataProvider.efms_cases()
9. Run test                   → uv run pytest <file> -v --browser chrome --browser-headless false
```

When asked to **write a new automation test** (no manual sheet), follow:

```
1. Identify application  → efms | etms
2. Identify test type    → ui (api/db: add layers when needed)
3. Search existing code first           → Section 16 — reuse before creating
4. Create/update Page Object (UI only)  → src/automation/pages/{app}/ — extend existing page when possible
5. Add test data (if data-driven)       → tests/testdata/dataTest-{app}.json
6. Write test file                      → tests/{app}/test_{feature}.py
7. Register page in PageManager (only if a genuinely new page is needed)
8. Add pytest markers: @pytest.mark.{app}, @pytest.mark.{smoke|login|regression}
```

**Golden rules:**

| Rule | Description |
|------|-------------|
| **Never interact with `page` directly in tests** | Always use `pages` fixture → Page Object methods |
| **Never hardcode passwords in JSON or test files** | Use `efms_account_password` / `etms_account_password` fixture from `.env` |
| **Never hardcode URLs in tests** | Use `settings.efms_base_url` / `settings.etms_base_url` inside Page Objects |
| **Never hardcode waits (`sleep`, raw ms in code)** | Use `settings.*_timeout`, `settings.*_ms`, or condition-based waits (Section 3.6) |
| **Always decorate page/API/DB methods with `@log_method`** | Required for HTML report step logs |
| **Always use fluent interface** | Page methods return `self` for chaining |
| **One manual Step = one Page Object method** | See Section 5.3 — preferred over opaque combined methods |
| **TestData_ID → .env, business data → JSON** | Never mix secrets into JSON (Section 5.2) |
| **Selectors go in Page Object class attributes** | As `*_selectors: list[str]`, ordered by priority (Section 3.4) |
| **Follow selector priority order strictly** | data-testid → id → name → aria-label → text → xpath → contains → index (last resort) |
| **Reuse before create — no duplicate code** | Search existing methods/fixtures first; extend existing Page Object; only add new code when nothing fits (Section 16) |

---

## 2. Repository Map

```
auotmation-techub/
├── conftest.py                     # Early hooks — load .env, auto-enable ReportPortal
├── src/automation/                 # Framework package (import as `automation`)
│   ├── config/
│   │   └── settings.py             # Pydantic Settings — all env config
│   ├── logging/
│   │   ├── logger.py               # Loguru file logger
│   │   └── step_logger.py          # @log_method decorator + step logs
│   ├── pages/
│   │   ├── base_page.py            # BasePage — open_url, wait_for_visible, wait_for_page_stable
│   │   ├── page_manager.py         # PageManager — lazy page object factory
│   │   ├── efms/
│   │   │   ├── efms_login_page.py          # EfmsLoginPage
│   │   │   ├── efms_home_page.py           # EfmsHomePage — dashboard, logout
│   │   │   ├── commercial/                 # Commercial menu module
│   │   │   │   ├── commercial_menu_page.py # Base — NOT in PageManager
│   │   │   │   ├── efms_agent_page.py
│   │   │   │   ├── efms_customer_page.py
│   │   │   │   ├── efms_work_order_page.py
│   │   │   │   └── efms_booking_receipt_page.py
│   │   │   ├── logistics/                  # Logistics menu module
│   │   │   │   ├── logistics_menu_page.py  # Base — NOT in PageManager
│   │   │   │   ├── efms_job_management_page.py
│   │   │   │   ├── efms_custom_clearance_page.py
│   │   │   │   └── efms_trucking_inland_page.py
│   │   │   └── services/                   # Services menu module
│   │   │       ├── services_menu_page.py   # Base — NOT in PageManager
│   │   │       └── efms_services_documentation_page.py
│   │   └── etms/
│   │       └── etms_home_page.py
│   └── reporting/
│       └── reportportal_support.py # ReportPortal ini, display names, step logs, screenshots
│
├── tests/
│   ├── conftest.py                 # Playwright fixtures + HTML/RP report hooks
│   ├── conftest_reportportal.py    # ReportPortal pytest hooks (via pytest_plugins)
│   ├── data_provider.py            # DataProvider — load JSON + auto priority markers
│   ├── testdata/
│   │   ├── dataTest-efms.json
│   │   └── dataTest-etms.json
│   ├── efms/                       # eFMS UI tests (app-first layout)
│   │   ├── test_efms_auth.py       # TestEfmsAuth — SMK_AUTH_001/002
│   │   ├── test_efms_navigate.py   # TestEfmsNavigate — SMK_NAV_001–006
│   │   ├── test_efms_booking_receipt.py                 # FMS_BR_001–005
│   │   └── test_efms_booking_receipt_delete_debug.py    # Debug FMS_BR_005
│   └── etms/                       # eTMS UI tests
│       └── test_etms_login.py      # ETMS-LOGIN-001
│
├── reports/                        # HTML report output (gitignored)
├── test-results/                   # Screenshots (gitignored)
├── logs/                           # automation.log (gitignored)
├── Jenkinsfile                     # CI pipeline
├── pyproject.toml                  # Package metadata, pytest markers, ruff, pyright
├── uv.lock                         # Dependency lock
├── .env.example                    # Environment variable template (copy → .env)
└── README.md
```

**Test folder layout (app-first):**

| Path | Purpose |
|------|---------|
| `tests/efms/` | All eFMS UI automation tests |
| `tests/etms/` | All eTMS UI automation tests |
| `tests/testdata/` | Shared JSON test data per application |
| `tests/conftest.py` | Global Playwright fixtures + HTML/ReportPortal report hooks |
| `tests/conftest_reportportal.py` | ReportPortal configuration hooks |
| `conftest.py` (root) | Early `.env` load + auto `--reportportal` when `RP_API_KEY` is set |

> **Migration note:** Tests moved from `tests/ui/{app}/` → `tests/{app}/`. Do **not** recreate the `tests/ui/` layer.

**Applications:**

| App | Base URL setting | PageManager properties | Test data file |
|-----|-----------------|-------------------------|----------------|
| eFMS | `settings.efms_base_url` | `efms_login_page`, `efms_home_page`, commercial pages (`efms_agent_page`, `efms_customer_page`, `efms_work_order_page`, `efms_booking_receipt_page`), logistics pages (`efms_job_management_page`, `efms_custom_clearance_page`, `efms_trucking_inland_page`), `efms_services_documentation_page` | `dataTest-efms.json` |
| eTMS | `settings.etms_base_url` | `etms_home_page` | `dataTest-etms.json` |

**eFMS Page Object responsibilities:**

| Class | File | Responsibility |
|-------|------|----------------|
| `EfmsLoginPage` | `efms_login_page.py` | Open login URL, enter credentials, click login, verify login page |
| `EfmsHomePage` | `efms_home_page.py` | Dashboard ready, logout flow |
| `EfmsCommercialMenuPage` | `commercial/commercial_menu_page.py` | Base: sidebar, `open_commercial_menu()` — **internal only** |
| `EfmsAgentPage` | `commercial/efms_agent_page.py` | Agent submenu + Agent List verification |
| `EfmsCustomerPage` | `commercial/efms_customer_page.py` | Customer submenu + Customer List verification |
| `EfmsWorkOrderPage` | `commercial/efms_work_order_page.py` | Work Order submenu + list verification |
| `EfmsBookingReceiptPage` | `commercial/efms_booking_receipt_page.py` | Booking Receipt CRUD: list, create, update, delete (FMS_BR_001–005) |
| `EfmsLogisticsMenuPage` | `logistics/logistics_menu_page.py` | Base: `open_logistics_menu()` — **internal only** |
| `EfmsJobManagementPage` | `logistics/efms_job_management_page.py` | Job Management submenu + table verification |
| `EfmsCustomClearancePage` | `logistics/efms_custom_clearance_page.py` | Customs Clearance submenu + verification |
| `EfmsTruckingInlandPage` | `logistics/efms_trucking_inland_page.py` | Trucking Inland submenu + verification |
| `EfmsServicesMenuPage` | `services/services_menu_page.py` | Base: `open_services_menu()` — **internal only** |
| `EfmsServicesDocumentationPage` | `services/efms_services_documentation_page.py` | All 8 Services documentation pages (title + URL verify) |

**Default UAT URLs (settings defaults):**
- eFMS: `https://uat-efms.logtechub.com/`
- eTMS: `https://staging-itllog-etms.logtechub.com/en/#/app/default/home`

### 2.1 Framework Architecture & Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Test Layer (tests/efms/, tests/etms/)                      │
│  Assertions, orchestration, JSON data, pytest markers       │
│  NO selectors, NO page.locator(), NO hard-coded waits       │
└──────────────────────────┬──────────────────────────────────┘
                           │ pages fixture
┌──────────────────────────▼──────────────────────────────────┐
│  Page Manager (page_manager.py)                               │
│  Lazy factory — one property per screen registered in POM    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Page Objects (src/automation/pages/{app}/)                   │
│  Selectors, @log_method actions, verifications               │
│  Module bases: commercial_menu_page, logistics_menu_page,     │
│                services_menu_page (extend, not in Manager)    │
└──────────────────────────┬──────────────────────────────────┘
                           │ inherits
┌──────────────────────────▼──────────────────────────────────┐
│  BasePage (base_page.py)                                      │
│  open_url, wait_for_visible, wait_for_page_stable             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Playwright sync API + Settings (Pydantic) + Logging (Loguru) │
└─────────────────────────────────────────────────────────────┘

Supporting layers (not in UI test path):
  reporting/ → reportportal_support.py (ReportPortal) + pytest-html hooks in conftest
```

**Test pyramid (current scope):**

| Layer | Status | Location |
|-------|--------|----------|
| UI E2E | **Active** — smoke auth + navigation | `tests/efms/`, `tests/etms/` |
| ReportPortal | **Active** — auto when `RP_API_KEY` in `.env` | `reportportal_support.py`, `conftest_reportportal.py` |
| API | Not implemented | Add `src/automation/api/` + `tests/api/` when needed |
| DB | Not implemented | Add `src/automation/db/` + `tests/db/` when needed |

**Design principles (SA view):**

| Principle | Implementation |
|-----------|----------------|
| Separation of concerns | Tests orchestrate; Page Objects own selectors and actions |
| Single source of config | `settings.py` + `.env` — no magic numbers in code |
| Data-driven | JSON metadata + `DataProvider`; credentials in `.env` only |
| Observability | `@log_method` step logs → HTML report + console + `logs/automation.log` |
| Failure diagnostics | Screenshot on failure (`test-results/screenshots/`) |
| Extensibility | New menu module = base class + feature pages + PageManager registration |
| CI-ready | Jenkinsfile + headless viewport + marker-based suite selection |

### 2.2 Implemented Test Inventory

| TC_ID | Module | Priority | Test class / method | File |
|-------|--------|----------|---------------------|------|
| SMK_AUTH_001 | Login | Critical | `TestEfmsAuth.test_smk_auth_001_login_success_efms` | `tests/efms/test_efms_auth.py` |
| SMK_AUTH_002 | Login | Critical | `TestEfmsAuth.test_smk_auth_002_logout_success_efms` | `tests/efms/test_efms_auth.py` |
| SMK_NAV_001–004 | Navigation | High | `TestEfmsNavigate.test_smk_nav_verify_commercial_menu_efms` | `tests/efms/test_efms_navigate.py` |
| SMK_NAV_005 | Navigation | High | `TestEfmsNavigate.test_smk_nav_verify_logistics_menu_efms` | `tests/efms/test_efms_navigate.py` |
| SMK_NAV_006 | Navigation | High | `TestEfmsNavigate.test_smk_nav_verify_services_menu_efms` | `tests/efms/test_efms_navigate.py` |
| FMS_BR_001–005 | Booking Receipt | High | `TestEfmsBookingReceipt` | `tests/efms/test_efms_booking_receipt.py` |
| FMS_BR_005 (debug) | Booking Receipt | — | `TestEfmsBookingReceiptDeleteDebug` | `tests/efms/test_efms_booking_receipt_delete_debug.py` |
| ETMS-LOGIN-001 | Login | High | `test_login_etms` | `tests/etms/test_etms_login.py` |

**Run by priority (from JSON, auto-applied via `DataProvider.efms_cases`):**

```bash
uv run pytest -m critical -v --browser chrome --browser-headless true   # SMK_AUTH_001/002
uv run pytest -m high -v --browser chrome --browser-headless true       # navigation + ETMS-LOGIN-001
uv run pytest -m navigation -v --browser chrome --browser-headless true # SMK_NAV_001–006
uv run pytest -m login -v --browser chrome --browser-headless true      # all login/logout tests
uv run pytest -m efms -v --browser chrome --browser-headless true       # eFMS only → RP launch efms-automation
uv run pytest -m etms -v --browser chrome --browser-headless true         # eTMS only → RP launch etms-automation
```

---

## 3. Architecture Rules (MUST follow)

### 3.1 Page Object Model (POM)

```
Test File  →  pages fixture  →  PageManager  →  {App}Page  →  BasePage  →  Playwright Page
```

- **Test layer:** assertions + orchestration only
- **Page layer:** selectors, user actions, element waits
- **Base layer:** shared navigation, polling, DOM waits

### 3.2 Data-Driven Pattern

```python
# Preferred — auto-applies priority markers (critical/high/medium/low) from JSON
@pytest.mark.parametrize("data", DataProvider.efms_cases("test_smk_auth_001_login_success_efms"))
def test_smk_auth_001_login_success_efms(pages, data, efms_account_password):
    # data["test_case_id"]  → "SMK_AUTH_001"  (HTML report + pytest param id)
    # data["test_data_id"]  → "LOGIN_ADMIN"   (maps to .env credentials)
    # data["company"]       → business field from JSON
    # pytest mark critical  → auto from data["priority"] == "Critical"
    ...
```

- JSON key **must equal** the test function name exactly
- `test_case_id`, `test_data_id`, and `description` from JSON appear in HTML report
- Credentials from `TestData_ID` → `.env`, not JSON

### 3.3 Credential Pattern

```python
# CORRECT — eFMS login (skips if EFMS_ACCOUNT_PASSWORD missing)
def test_smk_auth_001_login_success_efms(pages, data, efms_account_password):
    pages.efms_login_page.open().login(
        settings.efms_username, efms_account_password, data["company"]
    )

# CORRECT — eTMS login (skips if ETMS_ACCOUNT_PASSWORD missing)
def test_login_etms(pages, data, etms_account_password):
    pages.etms_home_page.open().login(settings.etms_username, etms_account_password)

# WRONG — hardcoded password
def test_login(pages, data):
    pages.efms_login_page.open().login("user", "123456", data["company"])
```

### 3.4 Selector Priority Rules (MUST follow)

All locators **must be defined in Page Object** as `*_selectors: list[str]`.
Order selectors from **most stable → least stable**. Try priority **1 first**, only add lower priorities as fallbacks when higher ones are unavailable in the DOM.

#### Priority order (strict)

| Priority | Strategy | Playwright examples | When to use |
|----------|----------|---------------------|-------------|
| **1** | `data-testid` | `[data-testid='login-submit']` | **Best choice** — stable, test-friendly |
| **2** | `id` | `#username`, `input#password` | Unique, stable `id` on element |
| **3** | `name` | `input[name='username']`, `select[name='company']` | Form fields with `name` attribute |
| **4** | `aria-label` | `[aria-label='Logout']`, `button[aria-label='Submit']` | Accessible labels |
| **5** | `text` | `button:has-text('Sign Out')`, `text=Login` | Visible label text (exact or partial via `:has-text`) |
| **6** | Relative XPath | `xpath=//form[@id='login-form']//button[@type='submit']` | Structural XPath anchored to a stable parent |
| **7** | `contains()` | `xpath=//button[contains(@class,'submit')]`, `[class*='user-menu']` | Partial attribute/class match — less stable |
| **8** | Index / `nth` | `.first`, `.nth(0)`, `>> nth=0` | **FORBIDDEN** except special cases (see below) |

#### Rules

1. **List order in `*_selectors` must follow priority 1 → 8** (best selector first).
2. **Never start with** broad selectors like `input[type='text']`, `button`, `div`, or bare `xpath=//button`.
3. **Never use index/nth as the primary selector** — only when no other strategy works.
4. **Never put selectors in test files** — always in Page Object class attributes.
5. Use `wait_for_visible(selectors, element_name)` — framework polls the list in order.

#### Correct `*_selectors` list example

```python
class EfmsHomePage(BasePage):
    logout_selectors = [
        "[data-testid='sign-out']",                              # 1 data-testid
        "#sign-out-btn",                                         # 2 id
        "button[name='logout']",                                 # 3 name
        "[aria-label='Sign Out']",                               # 4 aria-label
        "span:has-text('Sign Out')",                             # 5 text
        "xpath=//li[contains(@class,'user-profile')]//span[normalize-space()='Sign Out']",  # 6 relative xpath
        "xpath=//a[contains(@class,'dropdown-item') and contains(.,'Sign Out')]",           # 7 contains()
        # 8 index — do NOT add unless approved special case
    ]

    username_selectors = [
        "[data-testid='username']",
        "#username",
        "input[name='username']",
        "input[autocomplete='username']",
        "[aria-label='Username']",
        "input[placeholder='Username']",
    ]
```

#### Wrong examples (DO NOT write)

```python
# WRONG — starts with index / overly broad type selector
username_selectors = [
    "input[type='text']",           # too broad, no identity
    "xpath=(//input)[1]",            # index-based — forbidden
]

# WRONG — absolute xpath with deep DOM path
submit_selectors = [
    "xpath=/html/body/div[1]/div[2]/form/button[3]",  # brittle absolute path
]

# WRONG — contains() before stable attributes
login_selectors = [
    "xpath=//button[contains(@class,'btn')]",  # should try id/name/data-testid first
    "#login-btn",
]

# WRONG — selector in test file
def test_login(pages):
    pages.page.locator("button:has-text('Login')").click()  # forbidden
```

#### Index / `nth` — allowed only in special cases

Use index **only when ALL conditions are true**:

- No `data-testid`, `id`, `name`, `aria-label`, unique text, or stable relative xpath exists
- The parent container is already scoped by a priority 1–6 selector
- You document **why** in a one-line comment above the selector
- Team has approved (or it is a known legacy UI constraint)

```python
# SPECIAL CASE: legacy table with no row id — scoped under stable parent
shipment_row_delete_selectors = [
    "xpath=//tr[@data-shipment-id='{id}']//button[@aria-label='Delete']",  # prefer this
    # "xpath=//table[@id='shipments']//tr[1]//button[2]",  # last resort only — avoid
]
```

#### XPath guidelines

| Type | Rule | Example |
|------|------|---------|
| **Relative XPath** (priority 6) | Anchor from stable parent (`id`, `data-testid`, `form`, known container) | `xpath=//form[@id='login']//input[@name='username']` |
| **contains()** (priority 7) | Use for partial class/text match when 1–6 not available | `xpath=//button[contains(@class,'submit')]` |
| **Absolute XPath** | **FORBIDDEN** | `xpath=/html/body/div[1]/...` |
| **Index in XPath** | **FORBIDDEN** (special cases only) | `xpath=(//button)[3]`, `//tr[1]/td[2]` |

#### Mapping Playwright locator strategies

```python
# Priority 1 — data-testid
"[data-testid='user-menu']"

# Priority 2 — id
"#user-menu", "input#password"

# Priority 3 — name
"select[name='companyId']"

# Priority 4 — aria-label
"[aria-label='User menu']"

# Priority 5 — text (Playwright)
"button:has-text('Sign Out')", "text=Sign Out"

# Priority 6 — relative xpath
"xpath=//li[contains(@class,'m-topbar__user-profile')]//a[contains(@class,'m-nav__link')]"

# Priority 7 — contains (attribute partial match)
"[class*='m-topbar__username']"
"xpath=//span[contains(normalize-space(),'Sign Out')]"

# Priority 8 — index (avoid)
".locator('button').nth(2)"  # only in Page Object, only as last fallback
```

#### AI: how to pick selectors for a new element

```
1. Inspect element in browser DevTools
2. Check data-testid → use if present
3. Else check unique id → use if stable (not auto-generated like ng-xxx random)
4. Else check name / aria-label
5. Else use visible text (exact label from UI)
6. Else build relative xpath from nearest stable parent
7. Else use contains() on class/attribute
8. Never use index unless special case documented
9. Add all viable selectors to *_selectors list in priority order
10. Never reference selectors in test files
```

Use `wait_for_visible(selectors, element_name)` — never raw `page.locator()` in tests.

### 3.5 Logging Pattern

Every user-facing action in Page/API/DB classes must use `@log_method`:

```python
@log_method("Login to eFMS")
def login(self, username: str, password: str, company: str) -> "EfmsHomePage":
    ...
    return self
```

### 3.6 Wait & Timing Strategy (NO hard-coded waits)

> **Rule:** Never use `time.sleep()`, never pass raw millisecond literals (e.g. `5000`, `30000`) in Page Objects or tests. All timing must come from `settings` or condition-based Playwright waits.

#### Wait priority (best → worst)

| Priority | Method | When to use |
|----------|--------|-------------|
| **1** | `wait_for_visible(selectors, name, timeout=settings.page_load_timeout)` | Element must appear (login fields, sidebar, table) |
| **2** | `page.wait_for_url(..., timeout=settings.page_load_timeout)` | After login/logout navigation |
| **3** | `page.wait_for_function(..., timeout=settings.page_load_timeout)` | Hash route change, custom DOM condition |
| **4** | `wait_for_page_stable()` | After navigation — `readyState === 'complete'` + `navigation_settle_ms` |
| **5** | `wait_for_dom_content_loaded()` | Lightweight load state only |
| **6** | `page.wait_for_timeout(settings.*_ms)` | **Last resort** — only via named settings keys |

#### Settings keys (all configurable via `.env`)

| Setting | Default | Purpose |
|---------|---------|---------|
| `browser_timeout` | `60000` | Default element wait (ms) — Playwright context default |
| `page_load_timeout` | `60000` | Navigation / post-login dashboard wait (ms) |
| `browser_slow_mo` | `0` | Playwright slow motion (ms) — debug only |
| `polling_interval` | `250` | Poll interval inside `wait_for_visible()` |
| `navigation_settle_ms` | `1000` | Extra settle after `document.readyState === 'complete'` |
| `open_url_settle_ms` | `5000` | Brief SPA settle after `goto()` in `open_url()` |
| `headless_viewport_width` / `height` | `1920` / `1080` | Headless browser viewport in `conftest.py` |
| `screenshot_dir` | `test-results/screenshots` | Failure screenshot path |

#### Correct patterns

```python
# CORRECT — condition-based + settings timeout
self.page.wait_for_url(
    lambda url: "#/home" in url and "#/login" not in url,
    timeout=settings.page_load_timeout,
)
self.wait_for_page_stable()

# CORRECT — dashboard ready (headless-safe selector)
self.wait_for_visible(
    self.dashboard_ready_selectors,
    "eFMS dashboard navigation",
    timeout=settings.page_load_timeout,
)

# CORRECT — title text without is_visible() when element has 0×0 size in headless
actual_title = (
    self.page.locator("xpath=//h3[normalize-space()='eFMS']").first.inner_text().strip()
)
```

#### Wrong patterns (DO NOT write)

```python
# WRONG — hard-coded sleep
import time
time.sleep(5)

# WRONG — raw millisecond literal
self.page.wait_for_timeout(5000)
self.page.wait_for_timeout(30000)

# WRONG — dashboard h3 only (fails headless: element exists but 0×0, is_visible() = False)
self.wait_for_visible(self.home_title_selectors, "eFMS dashboard title")

# WRONG — timeout in test file
def test_login(pages):
    pages.page.wait_for_timeout(10000)
```

#### Headless mode rules (learned from SMK_AUTH / SMK_NAV)

1. **`conftest.py`** sets viewport `1920×1080` when `--browser-headless true` (sidebar outside viewport otherwise).
2. **Dashboard verification** uses `dashboard_ready_selectors` (Commercial sidebar) — not `h3` title alone.
3. **Commercial menu click** uses `scroll_into_view_if_needed()` + `click(force=True)`.
4. **Submenu navigation** uses `click(force=True)` after `open_commercial_menu()`.
5. After login, call `wait_for_page_stable()` before dashboard assertions.

#### `open_url()` SPA settle

`BasePage.open_url()` performs: `goto` → optional `open_url_settle_ms` wait → `wait_for_dom_content_loaded()`.

Tune via `OPEN_URL_SETTLE_MS` in `.env` — do not hard-code milliseconds in Page Objects.

#### Angular grid / SPA — beyond `wait_for_page_stable()` (learned from FMS_BR_005)

`wait_for_page_stable()` only waits `document.readyState === 'complete'` + `navigation_settle_ms`.
**It does NOT guarantee:** API finished, grid re-rendered, toolbar enabled, overlay hidden.

| Symptom | Cause | Fix |
|---------|-------|-----|
| Run FAIL, debug step-by-step PASS | Race condition — automation faster than Angular | Condition-based waits (below), not `time.sleep()` |
| Delete popup never opens | Clicked **row delete** before **toolbar delete** ready | **Only toolbar delete** after row selected |
| `is_checked()` stays False | Angular checkbox state lags DOM | Verify selection via **toolbar Delete enabled** |
| Record still on grid after delete | Verified DOM before API/grid refresh | `expect_response` + toast + `wait_until_booking_absent` |

**Mandatory wait chain for grid delete (Booking Receipt):**

```
refresh_list_page()          → reload + networkidle + _wait_for_grid_ready()
search_booking(booking_no)
select_booking_row()         → poll until toolbar Delete enabled
_wait_toolbar_delete_ready() → 3 consecutive enabled checks
_click_delete_for_booking()  → toolbar only → wait delete popup
_click_delete_confirm_yes_and_wait()
  → wait popup → actionable Yes → expect_response(delete API)
  → popup closed → grid ready → toast success
wait_until_booking_absent()  → networkidle + grid ready + poll exact row match
open_list_page() + verify again (avoid transient DOM false-pass)
```

**Helper methods on `EfmsBookingReceiptPage` (reuse — do not duplicate in tests):**

| Method | Purpose |
|--------|---------|
| `_wait_for_grid_ready()` | No loading overlay + table header visible |
| `_wait_actionable(selectors, name, stable_checks=3)` | Visible + enabled for N polls |
| `_wait_toolbar_delete_ready()` | Toolbar trash enabled after row select |
| `_click_delete_for_booking()` | Toolbar delete only + wait confirm popup |
| `_click_delete_confirm_yes_and_wait()` | Yes + API + popup close + toast |
| `delete_booking_receipt_from_grid()` | **Use in tests** — full stable delete flow |
| `refresh_list_page()` | Reload list before delete (FMS_BR_005) |
| `wait_until_booking_absent()` | networkidle + poll; exact `normalize-space()` match |

**DO NOT in delete tests:**

```python
# WRONG — returns before API/popup/grid complete
br_page.click_delete(booking_no)
br_page.click_delete_confirm_yes()
assert br_page.wait_until_booking_absent(booking_no)

# WRONG — row trash opens Duplicate or no popup
row.locator("app-permission-button[@type='delete']").click()

# CORRECT — single stable flow
br_page.refresh_list_page()
br_page.delete_booking_receipt_from_grid(booking_no, data["expected_success_message"])
br_page.open_list_page()
assert br_page.wait_until_booking_absent(booking_no)
```

**CRUD ordered test class pattern (`TestEfmsBookingReceipt`):**

```python
class TestEfmsBookingReceipt:
    booking_no: str | None = None  # set in FMS_BR_002, shared by BR_003–005

    # Run in order: BR_001 → BR_002 → BR_003 → BR_004 → BR_005
    # BR_005: refresh_list_page() before delete_booking_receipt_from_grid()
```

**Debug class for FMS_BR_005 only:** `TestEfmsBookingReceiptDeleteDebug` in
`tests/efms/test_efms_booking_receipt_delete_debug.py` — set `BOOKING_NO` or env
`EFMS_DEBUG_BOOKING_NO`; run `-k step03` for single step.

---

## 4. Naming Conventions

| Artifact | Pattern | Example |
|----------|---------|---------|
| Test file | `test_{app}_{module}.py` in `tests/{app}/` | `tests/efms/test_efms_auth.py`, `tests/efms/test_efms_navigate.py` |
| Test class | `Test{App}{Module}` | `TestEfmsAuth`, `TestEfmsNavigate` |
| Test method | `test_{tc_id_lower}_{scenario_slug}_{app}` | `test_smk_auth_001_login_success_efms` |
| Page object class | `{App}{Page}Page` | `EfmsHomePage`, `EtmsHomePage` |
| Page object file | `{app}_{page}_page.py` | `efms_home_page.py` |
| Menu base class | `{module}_menu_page.py` | `commercial_menu_page.py`, `logistics_menu_page.py` |
| Selector attribute | `{element}_selectors` | `username_selectors` |
| JSON data key | **same as test method name** | `"test_smk_auth_001_login_success_efms"` |
| Test case ID (`TC_ID`) | from manual sheet | `SMK_AUTH_001` |
| Test data ID (`TestData_ID`) | from manual sheet → `.env` | `LOGIN_ADMIN` |
| Pytest marker (app) | `@pytest.mark.efms` or `@pytest.mark.etms` | not `etmss` |
| Pytest marker (suite) | `@pytest.mark.login` / `navigation` / `smoke` / `regression` | on test **class** when shared |
| Pytest marker (priority) | auto from JSON `priority` via `DataProvider.efms_cases()` | `critical`, `high`, `medium`, `low` |

### 4.1 Test Class Organization

Group related test cases in one **test class per module** when they share markers and domain:

| Module | Class | File | Methods |
|--------|-------|------|---------|
| Auth (Login/Logout) | `TestEfmsAuth` | `tests/efms/test_efms_auth.py` | `test_smk_auth_001_*`, `test_smk_auth_002_*` |
| Navigation | `TestEfmsNavigate` | `tests/efms/test_efms_navigate.py` | commercial, logistics, services nav tests |
| eTMS Login | — | `tests/etms/test_etms_login.py` | `test_login_etms` |

**Rules:**

1. **Class-level markers** — `@pytest.mark.login` + `@pytest.mark.efms` on the class (shared by all methods).
2. **Method-level markers** — `@pytest.mark.tc_id("SMK_AUTH_001")` per test case when needed for report fallback.
3. **Parametrize** — use `DataProvider.efms_cases()` / `etms_cases()` (auto priority markers from JSON).
4. **First parameter** — always `self` in class methods.
5. **Standalone tests** — single TC (e.g. `test_etms_login.py`) may remain function-based with `@pytest.mark.smoke`.

**Canonical class template:**

```python
@pytest.mark.login
@pytest.mark.efms
class TestEfmsAuth:
    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_auth_001_login_success_efms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_efms(self, pages, data, efms_account_password):
        ...
```

**When to use a class vs standalone function:**

| Situation | Use |
|-----------|-----|
| 2+ related TCs in same module (Auth, Navigation) | Test class |
| Single TC (e.g. ETMS-LOGIN-001) | Standalone function |
| New module with only 1 TC planned | Standalone function — refactor to class when 2nd TC added |

---

## 5. Manual Test Case Sheet → Automation (CANONICAL)

> **This is the primary pattern.** When a user provides a manual test case table, convert it using this section.
> Reference implementation: `SMK_AUTH_001` in `tests/efms/test_efms_auth.py` (`TestEfmsAuth`).
> Navigation reference: `SMK_NAV_001–006` in `tests/efms/test_efms_navigate.py` (`TestEfmsNavigate`).

### 5.1 Manual sheet column mapping

When you receive a test case like this:

| TC_ID | Module | Scenario | Priority | Preconditions | TestData_ID | Steps | Expected Result |
|-------|--------|----------|----------|---------------|-------------|-------|-----------------|
| SMK_AUTH_001 | Login | Login success | Critical | User active | LOGIN_ADMIN | 1. Open Login Page … | Dashboard displayed successfully |

Map each column to automation as follows:

| Manual Column | Where it goes | Example |
|---------------|---------------|---------|
| `TC_ID` | JSON `test_case_id` + `@pytest.mark.tc_id` | `SMK_AUTH_001` |
| `Module` | JSON `module` (metadata for report) | `Login` |
| `Scenario` | JSON `description` + part of test function name | `Login success` |
| `Priority` | JSON `priority` + auto marker via `DataProvider.efms_cases()` | `Critical` → `@pytest.mark.critical` |
| `Preconditions` | JSON `preconditions` (documentation only) | `User active` |
| `TestData_ID` | JSON `test_data_id` → resolves credentials from `.env` | `LOGIN_ADMIN` |
| `Steps` | One Page Object method per step + `# Step N` comment in test | see 5.3 |
| `Expected Result` | `assert` at end of test + Page Object verify method | `is_dashboard_displayed()` |

### 5.2 TestData_ID → credential mapping (NEVER put passwords in JSON)

`TestData_ID` is a **logical name** for a credential set. Credentials always come from environment variables.

| TestData_ID | Username source | Password source | .env keys |
|-------------|-----------------|-----------------|-----------|
| `LOGIN_ADMIN` (eFMS) | `settings.efms_username` | `efms_account_password` fixture | `EFMS_ACCOUNT_USERNAME`, `EFMS_ACCOUNT_PASSWORD` |
| eTMS login | `settings.etms_username` | `etms_account_password` fixture | `ETMS_ACCOUNT_USERNAME`, `ETMS_ACCOUNT_PASSWORD` |

Legacy fallback (eFMS only): `ACCOUNT_USERNAME`, `ACCOUNT_PASSWORD` when `EFMS_ACCOUNT_*` is not set.

**Rules:**
- JSON stores `test_data_id: "LOGIN_ADMIN"` as metadata only
- Test injects `efms_account_password` or `etms_account_password` — test **skips** if that product password is empty
- Username from `settings.efms_username` (eFMS) or `settings.etms_username` (eTMS)
- **Never** put `username` or `password` fields in JSON

```python
# Step 2 & 3 in test — LOGIN_ADMIN resolves to env credentials
pages.efms_login_page.enter_username(settings.efms_username)
pages.efms_login_page.enter_password(efms_account_password)
```

### 5.3 Steps → Page Object methods (1 step = 1 method)

Each manual step becomes exactly one `@log_method` in the Page Object and one call in the test.

| Manual Step | Page Object method | Test call |
|-------------|-------------------|-----------|
| 1. Open Login Page | `EfmsLoginPage.open()` | `pages.efms_login_page.open()` |
| 2. Enter Username | `EfmsLoginPage.enter_username(username)` | `pages.efms_login_page.enter_username(settings.account_username)` |
| 3. Enter Password | `EfmsLoginPage.enter_password(password)` | `pages.efms_login_page.enter_password(efms_account_password)` |
| 4. Enter Company | `EfmsLoginPage.select_company(company)` | `pages.efms_login_page.select_company(data["company"])` |
| 5. Click Login | `EfmsLoginPage.click_login()` | `pages.efms_login_page.click_login()` |
| Expected: Dashboard displayed | `EfmsHomePage.is_dashboard_displayed()` | `assert pages.efms_home_page.is_dashboard_displayed()` |

**Also provide a composite shortcut** (optional, for simple tests):

```python
# Composite — chains all step methods internally (returns EfmsLoginPage)
pages.efms_login_page.open().login(
    settings.efms_username, efms_account_password, data["company"],
)
assert pages.efms_home_page.is_dashboard_displayed()
```

### 5.4 Test function naming from TC_ID

Convert `TC_ID` to test function name:

```
TC_ID:     SMK_AUTH_001
Scenario:  Login success
App:       efms

Function:  test_smk_auth_001_login_success_efms
JSON key:  "test_smk_auth_001_login_success_efms"   ← must match method name exactly
File:      tests/efms/test_efms_auth.py          ← inside TestEfmsAuth class
```

Formula: `test_{tc_id_lowercase}_{scenario_slug}_{app}`

- `tc_id_lowercase`: `SMK_AUTH_001` → `smk_auth_001`
- `scenario_slug`: lowercase, spaces → underscores: `Login success` → `login_success`
- `app`: `efms` or `etms`

### 5.5 JSON data schema (from manual sheet)

File: `tests/testdata/dataTest-efms.json`

```json
{
    "test_smk_auth_001_login_success_efms": [
        {
            "test_case_id": "SMK_AUTH_001",
            "test_data_id": "LOGIN_ADMIN",
            "description": "Login success - Dashboard displayed successfully",
            "module": "Login",
            "priority": "Critical",
            "preconditions": "User active",
            "company": "LTH Demo JSC"
        }
    ]
}
```

| JSON field | Required | Source | Used in test |
|------------|----------|--------|--------------|
| `test_case_id` | Yes | `TC_ID` column | HTML report (auto) |
| `test_data_id` | Yes | `TestData_ID` column | documentation; maps to `.env` |
| `description` | Yes | `Scenario` + `Expected Result` | HTML report (auto) |
| `module` | Recommended | `Module` column | documentation |
| `priority` | Recommended | `Priority` column | auto marker: `critical`/`high`/`medium`/`low` via `efms_cases()` |
| `preconditions` | Recommended | `Preconditions` column | documentation |
| `{feature_fields}` | As needed | business data from steps | e.g. `company`, `expected_title` |
| `username` | **Never** | — | use `settings.account_username` |
| `password` | **Never** | — | use `efms_account_password` fixture |

### 5.6 Complete test file template (CANONICAL)

File: `tests/efms/test_efms_auth.py`

```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.login
@pytest.mark.efms
class TestEfmsAuth:
    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_auth_001_login_success_efms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_efms(self, pages, data, efms_account_password):
        # Step 1: Open Login Page
        pages.efms_login_page.open()

        # Step 2: Enter Username (LOGIN_ADMIN → settings.account_username)
        pages.efms_login_page.enter_username(settings.account_username)

        # Step 3: Enter Password (LOGIN_ADMIN → efms_account_password fixture)
        pages.efms_login_page.enter_password(efms_account_password)

        # Step 4: Enter Company (from JSON business data)
        pages.efms_login_page.select_company(data["company"])

        # Step 5: Click Login
        pages.efms_login_page.click_login()

        # Expected Result: Dashboard displayed successfully
        assert pages.efms_home_page.is_dashboard_displayed()
```

### 5.7 Page Object methods required (CANONICAL)

**Login page** — `src/automation/pages/efms/efms_login_page.py`

| Method | Purpose |
|--------|---------|
| `open()` | Navigate to eFMS login URL |
| `enter_username()`, `enter_password()`, `select_company()` | One method per manual step |
| `click_login()` | Submit + `wait_for_url(#/home)` + `wait_for_page_stable()` |
| `login()` | Composite chaining all login steps |
| `is_login_page_displayed()` | Verify logout landed on login page |

**Home page** — `src/automation/pages/efms/efms_home_page.py`

| Method | Purpose |
|--------|---------|
| `is_dashboard_displayed()` | Wait `dashboard_ready_selectors` + URL `#/home` |
| `wait_for_dashboard_ready()` | Dashboard ready + `wait_for_page_stable()` |
| `click_user_menu()`, `click_logout()`, `click_confirm_yes()` | Logout flow |

**Commercial navigation** — `src/automation/pages/efms/commercial/`

| Class | Method | Notes |
|-------|--------|-------|
| `EfmsCommercialMenuPage` | `open_commercial_menu()` | Base — scroll + `force` click toggle; **not** exposed in PageManager |
| `EfmsAgentPage` | `click_agent_menu()`, `is_agent_list_displayed()` | Extends commercial base |
| `EfmsCustomerPage` | `click_customer_menu()`, `is_customer_list_displayed()` | Same pattern |
| `EfmsWorkOrderPage` | `click_work_order_menu()`, `is_work_order_list_displayed()` | Same pattern |
| `EfmsBookingReceiptPage` | `open_list_page()`, `refresh_list_page()`, `click_add_new()`, `fill_create_form()`, `delete_booking_receipt_from_grid()`, `wait_until_booking_absent()` | FMS_BR_001–005; delete via stable flow only |

**Logistics navigation** — `src/automation/pages/efms/logistics/`

| Class | Method | Notes |
|-------|--------|-------|
| `EfmsLogisticsMenuPage` | `open_logistics_menu()` | Base — scroll + `force` click; **not** in PageManager |
| `EfmsJobManagementPage` | `click_job_management_menu()`, `is_job_management_displayed()` | Verifies `h3` + table column `Job ID` |
| `EfmsCustomClearancePage` | `click_custom_clearance_menu()`, `is_custom_clearance_displayed()` | UI label **"Customs Clearance"** |
| `EfmsTruckingInlandPage` | `click_trucking_inland_menu()`, `is_trucking_inland_displayed()` | Same pattern |

**Services navigation** — `src/automation/pages/efms/services/`

| Class | Method | Notes |
|-------|--------|-------|
| `EfmsServicesMenuPage` | `open_services_menu()` | Base — **not** in PageManager |
| `EfmsServicesDocumentationPage` | `click_*_menu()`, `is_*_displayed()` × 8 | Documentation pages: verify **title + URL** only (no stable data table) |

Each action method:
- Has `@log_method("Human readable step name")`
- Returns `self` (fluent interface) except verify methods return `bool`
- Uses `wait_for_visible(selectors, element_name)` — never raw `page.locator()` in tests
- Passes `timeout=settings.page_load_timeout` for post-navigation / dashboard waits

Key methods for login flow:

```python
# efms_login_page.py
@log_method("Click login button")
def click_login(self) -> "EfmsLoginPage":
    self.wait_for_visible(self.submit_selectors, "eFMS login button").click()
    self.page.wait_for_url(
        lambda url: "#/home" in url and "#/login" not in url,
        timeout=settings.page_load_timeout,
    )
    self.wait_for_page_stable()
    return self

# efms_home_page.py
@log_method("Verify dashboard is displayed")
def is_dashboard_displayed(self) -> bool:
    self.wait_for_visible(
        self.dashboard_ready_selectors,
        "eFMS dashboard navigation",
        timeout=settings.page_load_timeout,
    )
    return "#/home" in self.current_url
```

~~Legacy reference (removed):~~ Do **not** use `EfmsNavigationPage` or put login methods on `EfmsHomePage`.

### 5.8 Data flow diagram

```
Manual Test Case Sheet
        │
        ├─ TC_ID, Module, Scenario, Priority, Preconditions
        │       └─→ tests/testdata/dataTest-{app}.json  (metadata + business fields)
        │
        ├─ TestData_ID (e.g. LOGIN_ADMIN)
        │       └─→ .env  (EFMS_ACCOUNT_*, ETMS_ACCOUNT_*)
        │               └─→ settings.efms_username + efms_account_password fixture
        │
        ├─ Steps (1..N)
        │       └─→ Page Object methods (@log_method per step)
        │               └─→ test file with # Step N comments
        │
        └─ Expected Result
                └─→ assert pages.{page}.{verify_method}()
```

### 5.9 AI decision tree — which data goes where?

```
Is it a secret (password, token, API key)?
  YES → .env only, never JSON
  NO  ↓

Is it shared across all tests (username for LOGIN_ADMIN)?
  YES → .env (ACCOUNT_USERNAME) + settings.account_username in test
  NO  ↓

Is it test-specific business data (company name, shipment ID, expected text)?
  YES → JSON field in dataTest-{app}.json, access via data["field"]
  NO  ↓

Is it test metadata (TC_ID, module, priority)?
  YES → JSON metadata fields (test_case_id, module, priority, preconditions)
```

### 5.10 Run the test

```bash
# Headed mode (recommended for first run / debugging)
uv run pytest tests/efms/test_efms_auth.py -v \
  --browser chrome --browser-headless false -s

# Headless CI mode
uv run pytest tests/efms/test_efms_auth.py -v \
  --browser chrome --browser-headless true

# By priority (auto from JSON via DataProvider.efms_cases)
uv run pytest -m critical -v --browser chrome --browser-headless true

# By suite
uv run pytest -m "login and efms" -v --browser chrome --browser-headless false
uv run pytest -m navigation -v --browser chrome --browser-headless true
```

### 5.11 Multi-Scenario Navigation Tests

When one manual TC covers multiple submenu items (SMK_NAV_001–004, SMK_NAV_005, SMK_NAV_006), use a **single parametrized test** with `scenarios[]` in JSON:

```json
{
    "test_smk_nav_verify_logistics_menu_efms": [
        {
            "test_case_id": "SMK_NAV_005",
            "priority": "High",
            "company": "LTH Demo JSC",
            "scenarios": [
                { "step": 2, "description": "Job Management displayed", "menu_action": "job_management" },
                { "step": 3, "description": "Customs Clearance displayed", "menu_action": "custom_clearance" }
            ]
        }
    ]
}
```

**Test pattern** — `tests/efms/test_efms_navigate.py`:

```python
LOGISTICS_MENU_ACTIONS = {
    "job_management": ("efms_job_management_page", "click_job_management_menu", "is_job_management_displayed"),
}

@pytest.mark.navigation
@pytest.mark.efms
class TestEfmsNavigate:
    @pytest.mark.parametrize("data", DataProvider.efms_cases("test_smk_nav_verify_logistics_menu_efms"))
    def test_smk_nav_verify_logistics_menu_efms(self, pages, data, efms_account_password):
        pages.efms_login_page.open().login(settings.account_username, efms_account_password, data["company"])
        assert pages.efms_home_page.is_dashboard_displayed()
        pages.efms_home_page.wait_for_dashboard_ready()

        pages.efms_job_management_page.open_logistics_menu()  # parent menu once

        for scenario in data["scenarios"]:
            page_name, click_method, verify_method = LOGISTICS_MENU_ACTIONS[scenario["menu_action"]]
            action_page = getattr(pages, page_name)
            getattr(action_page, click_method)()
            assert getattr(action_page, verify_method)()
```

**Reset strategy between scenarios:**

| Menu | Reset between sub-scenarios? | Reason |
|------|------------------------------|--------|
| Commercial | **Yes** — `goto #/home` before scenario index > 0 | Work Order URL breaks Booking Receipt if not reset |
| Logistics | **No** — sequential clicks under same parent menu | Submenus share sidebar state |
| Services | **No** — sequential clicks under same parent menu | Documentation pages are independent routes |

### 5.12 Menu Module POM Pattern

For each sidebar menu group, follow this **3-layer pattern**:

```
{module}_menu_page.py     → Base: open_{module}_menu(), _click_submenu(), wait_for_sidebar
efms_{feature}_page.py    → Feature: click_{feature}_menu(), is_{feature}_displayed()
PageManager               → Register feature pages only (NOT base menu class)
```

| Module | Base class | Feature pages | Routes |
|--------|-----------|---------------|--------|
| Commercial | `EfmsCommercialMenuPage` | Agent, Customer, Work Order, Booking Receipt | `#/home/commercial/...` |
| Logistics | `EfmsLogisticsMenuPage` | Job Management, Customs Clearance, Trucking Inland | `#/home/operation/...` |
| Services | `EfmsServicesMenuPage` | `EfmsServicesDocumentationPage` (all 8 docs) | `#/home/documentation/...` |

**Base class responsibilities:**
- Sidebar toggle: `scroll_into_view_if_needed()` + `click(force=True)`
- Wait submenu visible before click
- Shared `_click_*_submenu(selectors, hash_fragment)` helper

**Verification strategy by page type:**

| Page type | Verify with | Example |
|-----------|-------------|---------|
| List page (Agent, Job Management) | `h3` title + table column header | `Job ID`, `Clearance Date` |
| Documentation page (Services) | `h3` title + URL hash fragment | `#/home/documentation/air-export` |
| Booking Receipt grid row | Exact `normalize-space()` on `span`/`a` | Never `contains()` for booking_no verify |
| Booking Receipt delete | Toolbar delete after checkbox | Never row `btn-outline-danger` (opens Duplicate) |

### 5.13 Booking Receipt CRUD (FMS_BR_001–005)

> Reference: `tests/efms/test_efms_booking_receipt.py`, `efms_booking_receipt_page.py`,
> `tests/testdata/dataTest-efms.json` keys `test_fms_br_001_*` … `test_fms_br_005_*`.

| TC_ID | Scenario | Key Page methods |
|-------|----------|------------------|
| FMS_BR_001 | Open Add New — Air Export | `open_list_page()`, `click_add_new()`, `click_add_new_option()`, `is_add_form_displayed()` |
| FMS_BR_002 | Create + capture `booking_no` | `fill_create_form()`, `click_save()`, `click_confirm_yes()`, `get_booking_no_from_grid_row_containing()` |
| FMS_BR_003 | Open detail | `search_booking()`, `click_booking_no()`, `is_detail_displayed()` |
| FMS_BR_004 | Update (stay Draft) | `fill_update_form()`, `click_save()`, `get_booking_status_in_grid()` == `Draft` |
| FMS_BR_005 | Delete Draft record | `refresh_list_page()`, `delete_booking_receipt_from_grid()`, verify absent after reload |

**FMS_BR_005 test template (canonical):**

```python
booking_no = TestEfmsBookingReceipt.booking_no
if not booking_no:
    pytest.skip("Requires booking_no from FMS_BR_002")

br_page.open_list_page()
br_page.refresh_list_page()
br_page.delete_booking_receipt_from_grid(
    booking_no,
    data["expected_success_message"],
)
br_page.open_list_page()
assert br_page.wait_until_booking_absent(booking_no)
```

**Expected success message (JSON):** `Delete Booking Receipt Success!`

**Run full CRUD flow:**

```bash
uv run pytest tests/efms/test_efms_booking_receipt.py -v \
  --browser chrome --browser-headless false

# Debug delete only (existing Draft record)
$env:EFMS_DEBUG_BOOKING_NO="BKAE26060007"
uv run pytest tests/efms/test_efms_booking_receipt_delete_debug.py -k step03 -v \
  --browser chrome --browser-headless false
```

### 5.14 XPath Catalog — Booking Receipt

> All selectors live in `EfmsBookingReceiptPage` class attributes.
> Dynamic `{booking_no}` — always use **exact** `normalize-space()='{booking_no}'` for verify;
> avoid `contains(., booking_no)` (false positives).

#### Navigation & list page

| Element | XPath / selector (priority order in POM) |
|---------|------------------------------------------|
| Menu | `xpath=//div[contains(@class,'m-menu__submenu')]//a[contains(@href,'commercial/booking-receipt')]` |
| List title | `xpath=//h3[normalize-space()='Booking Receipt']` |
| Table header | `xpath=//th[normalize-space()='Booking No']` |
| List URL | `{efms_base_url}en/#/home/commercial/booking-receipt` |

#### Create / detail

| Element | XPath / selector |
|---------|------------------|
| Add new | `button:has-text('Add new')` |
| Add form title | `xpath=//h3[contains(normalize-space(),'Add New Booking Receipt')]` |
| Detail title | `xpath=//h3[contains(normalize-space(),'Detail Booking Receipt')]` |
| Save | `button:has-text('Save')` |
| Generic Yes (save confirm) | `.swal2-confirm`, `xpath=//button[normalize-space()='Yes']` |

#### Grid — search & row (parameterized `{booking_no}`)

| Element | XPath |
|---------|-------|
| Booking no in grid | `xpath=//span[normalize-space()='{booking_no}']` |
| Row | `xpath=//tr[.//span[normalize-space()='{booking_no}']]` |
| Row checkbox | `xpath=//tr[.//span[normalize-space()='{booking_no}']]//input[@type='checkbox']` |
| Row absent verify | `xpath=//table//tbody//tr[.//span[normalize-space()='{booking_no}'] or .//a[normalize-space()='{booking_no}']]` → `count() == 0` |

#### Delete — toolbar (PREFERRED after row select)

| Element | XPath |
|---------|-------|
| Toolbar Delete | `xpath=//*[contains(@class,'m-portlet__head')]//button[contains(@class,'btn-outline-danger') and .//i[contains(@class,'la-trash')]]` |

#### Delete — row action (reference only — do NOT use in automation delete flow)

| Element | XPath | Note |
|---------|-------|------|
| Row delete permission | `xpath=//tr[.//span[normalize-space()='{booking_no}']]//app-permission-button[@type='delete']` | May not open Delete popup when run fast |
| Row delete (alt) | `xpath=//span[normalize-space()='{booking_no}']//preceding::td//app-permission-button[@type='delete']` | Same |
| Row trash button | `xpath=//tr[...]//button[contains(@class,'btn-outline-danger')]` | Opens **Duplicate** popup — forbidden |

#### Delete confirm popup (SweetAlert2)

| Element | XPath |
|---------|-------|
| Popup container | `xpath=//h5[text()='Delete Booking Receipt ']//ancestor::div` |
| Popup (swal2) | `xpath=//div[contains(@class,'swal2-popup') and .//h2[contains(.,'Delete Booking Receipt')]]` |
| Yes button | `xpath=//h5[text()='Delete Booking Receipt ']//ancestor::div//span[text()=' Yes ']` |
| Yes (swal2 confirm) | `xpath=//div[contains(@class,'swal2-popup') and .//h2[contains(.,'Delete Booking Receipt')]]//button[contains(@class,'swal2-confirm')]` |

#### Loading / overlay (wait before grid actions)

| Element | Selector |
|---------|----------|
| Block UI | `.m-blockui`, `.block-ui-wrapper.block-ui-active` |
| Loading mask | `xpath=//div[contains(@class,'loading-mask')]` |

#### Toast / system message

| Element | Selector |
|---------|----------|
| Success toast | `#toast-container .toast-message:has-text('Delete Booking Receipt Success!')` |
| Popup closed check | `() => !document.querySelector('.swal2-popup')` |

#### Delete API (`expect_response` matcher)

```python
# URL contains bookingreceipt (with or without hyphen) AND:
#   DELETE → status 200/204
#   POST/PUT → status 200/204 AND "delete" in URL
def _is_booking_receipt_delete_response(response) -> bool: ...
```

---

## 6. How to Write a UI Test (Step-by-Step)

### Step 1 — Add test data (if data-driven)

File: `tests/testdata/dataTest-efms.json`

```json
{
    "test_create_shipment_efms": [
        {
            "test_case_id": "EFMS-SHIP-001",
            "description": "Create shipment successfully",
            "origin": "Ho Chi Minh",
            "destination": "Ha Noi",
            "expected_status": "Created"
        }
    ]
}
```

### Step 2 — Search existing code, then create or extend Page Object

**Before writing any new method**, follow [Section 16](#16-clean-code--reuse-dry--no-duplication):

1. Search `src/automation/pages/` for an existing method that already does the action
2. If the action belongs to an existing page (e.g. login on `EfmsHomePage`) → **add method there**, do not create a duplicate page
3. Only create a new Page Object file when the feature is a distinct screen/module with its own selectors

File: `src/automation/pages/efms/efms_shipment_page.py` (only if no existing page fits)

(See [Section 7](#7-how-to-write-a-page-object) for full template)

### Step 3 — Register in PageManager

File: `src/automation/pages/page_manager.py` — add lazy property.

### Step 4 — Write the test

File: `tests/efms/test_efms_shipment.py` (eFMS UI) or `tests/etms/test_etms_{feature}.py` (eTMS UI)

(See [Section 13](#13-complete-examples-copy-paste-ready) for full template)

### Step 5 — Run and verify

```bash
uv run pytest tests/efms/test_efms_shipment.py -v --browser chrome --browser-headless true
```

---

## 7. How to Write a Page Object

### Template

```python
from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EfmsShipmentPage(BasePage):
    # --- Selectors: priority order data-testid → id → name → aria-label → text → xpath → contains ---
    create_button_selectors = [
        "[data-testid='create-shipment']",
        "#create-shipment",
        "button[name='create-shipment']",
        "[aria-label='Create Shipment']",
        "button:has-text('Create Shipment')",
        "xpath=//div[@id='shipment-toolbar']//button[@type='button']",
    ]
    origin_input_selectors = [
        "input[formcontrolname='origin']",
        "input[placeholder*='Origin']",
    ]
    status_label_selectors = [
        "span.shipment-status",
        "xpath=//span[contains(@class,'status')]",
    ]

    # --- Navigation ---
    @log_method("Open eFMS shipment page")
    def open(self) -> "EfmsShipmentPage":
        self.open_url(f"{settings.efms_base_url}#/shipment")
        return self

    # --- Actions (fluent — return self) ---
    @log_method("Click create shipment button")
    def click_create(self) -> "EfmsShipmentPage":
        self.wait_for_visible(self.create_button_selectors, "Create button").click()
        return self

    @log_method("Fill origin field")
    def fill_origin(self, origin: str) -> "EfmsShipmentPage":
        self.wait_for_visible(self.origin_input_selectors, "Origin input").fill(origin)
        return self

    # --- Verifications (return bool or raise AssertionError) ---
    @log_method("Get shipment status text")
    def get_status(self) -> str:
        return (
            self.wait_for_visible(self.status_label_selectors, "Status label")
            .inner_text()
            .strip()
        )
```

### BasePage methods available

| Method | Usage |
|--------|-------|
| `open_url(url)` | Navigate + optional `open_url_settle_ms` + `wait_for_dom_content_loaded()` |
| `wait_for_visible(selectors, name, timeout?)` | Poll until element visible; default timeout = `settings.browser_timeout` |
| `find_visible(selectors)` | Single-check, returns `Locator \| None` |
| `wait_for_dom_content_loaded()` | Wait for `domcontentloaded` |
| `wait_for_page_stable()` | `readyState === 'complete'` + `navigation_settle_ms` |
| `current_url` (property) | Current page URL string |

---

## 8. How to Write Test Data (JSON)

> **For manual test case sheets, use [Section 5.5](#55-json-data-schema-from-manual-sheet) as the canonical schema.**

### File location

```
tests/testdata/dataTest-{app}.json
```

### Schema per test case (from manual sheet)

```json
{
    "test_smk_auth_001_login_success_efms": [
        {
            "test_case_id": "SMK_AUTH_001",
            "test_data_id": "LOGIN_ADMIN",
            "description": "Login success - Dashboard displayed successfully",
            "module": "Login",
            "priority": "Critical",
            "preconditions": "User active",
            "company": "LTH Demo JSC"
        }
    ]
}
```

### Schema per test case (generic)

```json
{
    "test_{tc_id}_{scenario}_{app}": [
        {
            "test_case_id": "TC_ID_FROM_SHEET",
            "test_data_id": "TESTDATA_ID_FROM_SHEET",
            "description": "Scenario - Expected result",
            "module": "Module name",
            "priority": "Critical|High|Medium|Low",
            "preconditions": "Precondition text",
            "...": "feature-specific business fields only — NO passwords"
        }
    ]
}
```

### Rules

- JSON key **must equal** the test function name exactly
- `test_case_id` and `description` are **required** for HTML report
- `test_data_id` documents which credential set to use — resolved via `.env`, not JSON
- Do **not** put `password` or `username` in JSON — use `TestData_ID` → `.env` pattern (Section 5.2)
- `module`, `priority`, `preconditions` are metadata for documentation and reports
- Multiple objects in array = multiple parametrized test runs

### Load in test

```python
from tests.data_provider import DataProvider

# Always use *_cases() — auto priority markers from JSON
@pytest.mark.parametrize("data", DataProvider.efms_cases("test_smk_auth_001_login_success_efms"))
@pytest.mark.parametrize("data", DataProvider.etms_cases("test_login_etms"))
```

---

## 9. How to Write an API Test

> **Status:** Not implemented. When needed, add `src/automation/api/` (e.g. httpx client) and `tests/api/`. Follow `@log_method` and settings-based timeouts.

---

## 10. How to Write a DB Test

> **Status:** Not implemented. When needed, add `src/automation/db/` (e.g. psycopg) and `tests/db/`. Keep credentials in `.env` only.

---

## 11. Pytest Markers & Fixtures Reference

### Fixtures (from `tests/conftest.py`)

| Fixture | Scope | Inject into test | Description |
|---------|-------|-----------------|-------------|
| `playwright_instance` | session | rarely | Raw Playwright instance |
| `browser` | function | rarely | Launched Chrome/Edge browser |
| `context` | function | rarely | Browser context; headless → fixed viewport from settings |
| `page` | function | **avoid in tests** | Raw Playwright Page |
| `pages` | function | **always use this** | `PageManager` instance |
| `efms_account_password` | function | eFMS login tests — skips if `EFMS_ACCOUNT_PASSWORD` missing |
| `etms_account_password` | function | eTMS login tests — skips if `ETMS_ACCOUNT_PASSWORD` missing |

### Markers — two sources

| Source | Markers | When |
|--------|---------|------|
| **Test class / method** (manual) | `@pytest.mark.efms`, `@pytest.mark.login`, `@pytest.mark.navigation`, `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.tc_id(...)` | Suite filtering, report fallback |
| **JSON `priority`** (auto) | `@pytest.mark.critical`, `high`, `medium`, `low` | Via `DataProvider.efms_cases()` / `etms_cases()` only |

```python
@pytest.mark.login          # eFMS login/logout suite
@pytest.mark.navigation     # eFMS menu navigation suite
@pytest.mark.efms           # eFMS application
@pytest.mark.etms           # eTMS application (NOT etmss)
@pytest.mark.smoke          # smoke suite (manual — e.g. test_etms_login.py)
@pytest.mark.regression     # regression suite
@pytest.mark.tc_id("SMK_AUTH_001")       # fallback when JSON tc_id absent
@pytest.mark.description("Login eFMS Successfully")  # fallback description
```

**Marker execution matrix:**

| Command | Collects |
|---------|----------|
| `-m critical` | SMK_AUTH_001, SMK_AUTH_002 |
| `-m high` | SMK_NAV_001–006, ETMS-LOGIN-001 |
| `-m login` | SMK_AUTH_001/002 + ETMS-LOGIN-001 |
| `-m navigation` | SMK_NAV commercial/logistics/services |
| `-m "login and efms"` | eFMS auth tests only |
| `-m efms` / `-m etms` | All tests for one app; ReportPortal uses separate launch name |
| `-m smoke` | Tests with explicit `@pytest.mark.smoke` |

### HTML report hooks (`conftest.py`)

| Hook | Behavior |
|------|----------|
| `pytest_html_report_title` | Report title: "Automation Report" |
| `pytest_runtest_makereport` | Enriches report: TC_ID, description, method logs, failure screenshot |
| `pytest_html_results_table_*` | Custom "Test Case" column (not raw nodeid) |
| Multi-scenario tests | Shows `test_case_ids[]` + per-scenario breakdown in extras |

**Report outputs:**
- HTML: `reports/report.html` (via `--html=... --self-contained-html`)
- Screenshots on failure: `test-results/screenshots/`
- Step logs: embedded in HTML report + console `[STEP START/PASS]`
- File log: `logs/automation.log`

### ReportPortal integration

| Item | Behavior |
|------|----------|
| Auto-enable | When `RP_API_KEY` is set in `.env` — no `--reportportal` flag needed |
| Early load | Root `conftest.py` → `pytest_load_initial_conftests` |
| Config hook | `tests/conftest_reportportal.py` → inject ini + `rp_enabled=True` |
| Display name | `{test_case_id} - {description}` from JSON via `@pytest.mark.name` |
| Launch name | `-m efms` → `efms-automation`; `-m etms` → `etms-automation`; else `RP_LAUNCH` |
| Step logs | `log_step_lines()` → ReportPortal on test finish |
| Failure screenshot | `attach_failure_screenshot()` → full-page PNG |
| View results | `{RP_ENDPOINT}/ui/#{RP_PROJECT}/launches/all` |

**Dashboard tip:** Create separate dashboards filtering launch name `efms-automation` vs `etms-automation`, or filter test attribute `efms` / `etms`.

### CLI options

```bash
--browser chrome|edge
--browser-headless true|false
```

## 12. Run Commands

```bash
# Install dependencies
uv sync --extra dev
uv run playwright install --with-deps chrome msedge

# Setup env (once)
copy .env.example .env   # Windows
# Fill EFMS_ACCOUNT_*, ETMS_ACCOUNT_*, RP_API_KEY

# Run all login tests (both apps)
uv run pytest -m login --browser chrome --browser-headless true

# Run eFMS only (ReportPortal launch: efms-automation)
uv run pytest -m efms --browser chrome --browser-headless true

# Run eTMS only (ReportPortal launch: etms-automation)
uv run pytest -m etms --browser edge --browser-headless true

# Run by priority (from JSON)
uv run pytest -m critical --browser chrome --browser-headless true
uv run pytest -m high --browser chrome --browser-headless true

# Run navigation suite
uv run pytest tests/efms/test_efms_navigate.py -v --browser chrome --browser-headless true

# Run auth class
uv run pytest tests/efms/test_efms_auth.py -v --browser chrome --browser-headless true

# Run with HTML report
uv run pytest -m login --browser chrome --browser-headless true \
  --html=reports/report.html --self-contained-html

# Headed mode (visible browser)
uv run pytest -m login --browser chrome --browser-headless false -s

# Code quality
uv run ruff check .
uv run ruff format .
uv run pyright
```

### 12.1 CI/CD Pipeline (Jenkins)

File: `Jenkinsfile`

| Parameter | Choices | Purpose |
|-----------|---------|---------|
| `ENV` | UAT | Target environment |
| `BROWSER` | chrome, edge | Browser channel |
| `HEADLESS` | true, false | Headless mode |
| `MARKER` | critical, high, login, navigation, smoke, regression | Pytest marker filter |
| `PYTEST_ARGS` | free text | Extra pytest args (e.g. `-m critical`, file path) |

**Pipeline stages:** Checkout → Install (`uv sync`, Playwright browsers) → Quality (`ruff`, `pyright`) → Run Tests → Archive artifacts.

**Credentials:** Jenkins injects `EFMS_ACCOUNT_PASSWORD`, `ETMS_ACCOUNT_PASSWORD` (or map from credential store).

**Artifacts archived:** `reports/`, `test-results/`, `logs/`

```bash
# Example: run Critical tests in CI via parameter or PYTEST_ARGS
MARKER=critical
# or
PYTEST_ARGS='tests/efms/test_efms_auth.py --browser chrome --browser-headless true'
```

**Parallel execution (optional, dev deps installed):**

```bash
uv run pytest -m login -n auto --browser chrome --browser-headless true  # pytest-xdist
uv run pytest --reruns 2 --reruns-delay 3 ...                          # pytest-rerunfailures
```

---

## 13. Complete Examples (Copy-Paste Ready)

### Example A — SMK_AUTH_001 Manual Sheet → Automation ✅ CANONICAL (use this first)

**Manual test case:**

| TC_ID | Module | Scenario | Priority | Preconditions | TestData_ID | Steps | Expected Result |
|-------|--------|----------|----------|---------------|-------------|-------|-----------------|
| SMK_AUTH_001 | Login | Login success | Critical | User active | LOGIN_ADMIN | 1. Open Login Page 2. Enter Username 3. Enter Password 4. Enter Company 5. Click Login | Dashboard displayed successfully |

**Test data** — `tests/testdata/dataTest-efms.json`:
```json
{
    "test_smk_auth_001_login_success_efms": [
        {
            "test_case_id": "SMK_AUTH_001",
            "test_data_id": "LOGIN_ADMIN",
            "description": "Login success - Dashboard displayed successfully",
            "module": "Login",
            "priority": "Critical",
            "preconditions": "User active",
            "company": "LTH Demo JSC"
        }
    ]
}
```

**Test file** — `tests/efms/test_efms_auth.py`:
```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.login
@pytest.mark.efms
class TestEfmsAuth:
    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_smk_auth_001_login_success_efms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_efms(self, pages, data, efms_account_password):
        pages.efms_login_page.open()
        pages.efms_login_page.enter_username(settings.efms_username)
        pages.efms_login_page.enter_password(efms_account_password)
        pages.efms_login_page.select_company(data["company"])
        pages.efms_login_page.click_login()
        assert pages.efms_home_page.is_dashboard_displayed()
```

**Run:**
```bash
uv run pytest tests/efms/test_efms_auth.py -v \
  --browser chrome --browser-headless false -s
```

---

### Example B — eTMS Login Test ✅ Current Pattern

**Test data** — `tests/testdata/dataTest-etms.json`:
```json
{
    "test_login_etms": [
        {
            "test_case_id": "ETMS-LOGIN-001",
            "description": "Login eTMS successfully",
            "priority": "High",
            "expected_url_contains": "staging-itllog-etms.logtechub.com"
        }
    ]
}
```

**Test file** — `tests/etms/test_etms_login.py`:
```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.parametrize("data", DataProvider.etms_cases("test_login_etms"))
@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.etms
def test_login_etms(pages, data, etms_account_password):
    pages.etms_home_page.open().login(
        settings.etms_username,
        etms_account_password,
    )

    assert not pages.etms_home_page.is_password_field_visible()
    assert data["expected_url_contains"] in pages.etms_home_page.current_url
```

---

### Example C — eFMS Negative Login Test (New Test — template)

**Test data** — add to `tests/testdata/dataTest-efms.json`:
```json
{
    "test_login_efms_invalid_company": [
        {
            "test_case_id": "EFMS-LOGIN-003",
            "description": "Login eFMS fails with invalid company",
            "company": "NonExistent Company",
            "expected_error": "Invalid company"
        }
    ]
}
```

**Page object** — add method to `efms_login_page.py`:
```python
@log_method("Get login error message")
def get_login_error(self) -> str:
    error_selectors = [
        "div.error-message",
        "span[class*='error']",
        "div[role='alert']",
    ]
    locator = self.wait_for_visible(error_selectors, "Login error message")
    return locator.inner_text().strip()
```

**Test file** — `tests/efms/test_efms_login_negative.py`:
```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.parametrize("data", DataProvider.efms_cases("test_login_efms_invalid_company"))
@pytest.mark.login
@pytest.mark.regression
@pytest.mark.efms
def test_login_efms_invalid_company(pages, data, efms_account_password):
    pages.efms_login_page.open().login(
        settings.account_username,
        efms_account_password,
        data["company"],
    )

    error = pages.efms_login_page.get_login_error()
    assert data["expected_error"] in error
```

---

### Example E — eTMS Data-Driven Login ✅ IMPLEMENTED (same as Example C)

**Test data** — `tests/testdata/dataTest-etms.json`:
```json
{
    "test_login_etms": [
        {
            "test_case_id": "ETMS-LOGIN-001",
            "description": "Login eTMS successfully",
            "priority": "High",
            "expected_url_contains": "staging-itllog-etms.logtechub.com"
        }
    ]
}
```

**Test file** — `tests/etms/test_etms_login.py`:
```python
@pytest.mark.parametrize("data", DataProvider.etms_cases("test_login_etms"))
```

---

### Example F — New Page Object + PageManager Registration

**New page** — `src/automation/pages/efms/efms_bay_page.py`:
```python
from automation.config import settings
from automation.logging import log_method
from automation.pages.base_page import BasePage


class EfmsBayPage(BasePage):
    bay_button_selectors = [
        "button:has-text('Bay')",
        "a:has-text('Bay Management')",
    ]
    page_title_selectors = [
        "h1:has-text('Bay Management')",
        "xpath=//h1[contains(text(),'Bay')]",
    ]

    @log_method("Open eFMS Bay page")
    def open(self) -> "EfmsBayPage":
        self.open_url(f"{settings.efms_base_url}")
        return self

    @log_method("Click Bay button")
    def click_bay_button(self) -> "EfmsBayPage":
        self.wait_for_visible(self.bay_button_selectors, "Bay button").click()
        self.wait_for_dom_content_loaded()
        return self

    @log_method("Verify Bay page title")
    def verify_page_title(self, expected: str) -> bool:
        actual = (
            self.wait_for_visible(self.page_title_selectors, "Bay page title")
            .inner_text()
            .strip()
        )
        return actual == expected
```

**Register in PageManager** — `src/automation/pages/page_manager.py`:
```python
from automation.pages.efms.efms_bay_page import EfmsBayPage

class PageManager:
    def __init__(self, page: Page):
        self.page = page
        self._efms_home_page: EfmsHomePage | None = None
        self._etms_home_page: EtmsHomePage | None = None
        self._efms_bay_page: EfmsBayPage | None = None

    @property
    def efms_bay_page(self) -> EfmsBayPage:
        if self._efms_bay_page is None:
            self._efms_bay_page = EfmsBayPage(self.page)
        return self._efms_bay_page
```

**Test data** — `tests/testdata/dataTest-efms.json`:
```json
{
    "test_click_bay_button_efms": [
        {
            "test_case_id": "EFMS-BAY-001",
            "description": "Navigate to Bay Management page",
            "button_name": "Bay",
            "expected_page": "Bay Management"
        }
    ]
}
```

**Test file** — `tests/efms/test_efms_bay.py`:
```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.parametrize("data", DataProvider.efms_cases("test_click_bay_button_efms"))
@pytest.mark.smoke
@pytest.mark.efms
def test_click_bay_button_efms(pages, data, efms_account_password):
    # Precondition: login first
    pages.efms_login_page.open().login(
        settings.account_username,
        efms_account_password,
        "LTH Demo JSC",
    )
    assert pages.efms_home_page.is_dashboard_displayed()

    # Action: navigate to Bay page
    pages.efms_bay_page.click_bay_button()

    # Assert
    assert pages.efms_bay_page.verify_page_title(data["expected_page"])
```

---

### Example G — API Test (future template)

> Add `src/automation/api/` when first API test is needed. Use httpx (or similar), `@log_method`, settings-based timeouts, and `tests/api/{app}/`.

---

## 14. Known Issues & Do NOT Replicate

| # | Issue | Impact | AI should |
|---|-------|--------|-----------|
| 1 | Dashboard `h3` "eFMS" only for `is_visible()` | Fails headless (0×0 element) | Use `dashboard_ready_selectors` + `inner_text()` for title |
| 2 | Headless with `no_viewport=True` | Sidebar click "outside viewport" | Headless uses `headless_viewport_width/height` in conftest |
| 3 | `@pytest.mark.etmss` typo | Marker filter `-m etms` won't match | Always use `@pytest.mark.etms` |
| 4 | Login tests without `efms_account_password` fixture | Tests fail instead of skip | Always inject `efms_account_password` fixture |
| 5 | `dataTest-etms.json` wrong key / hardcoded password | DataProvider fails or security risk | **Fixed** — `test_login_etms` + no credentials in JSON |
| 6 | `open_url()` settle wait + reload | Every navigation is slow | Tune via `settings.open_url_settle_ms` — do not hardcode ms |
| 7 | Jenkins `MARKER` dropdown missing `critical`/`navigation` | CI cannot select by priority from UI | **Fixed** — MARKER includes critical, high, navigation |
| 8 | `EfmsNavigationPage` removed | Old docs reference deleted class | Use module-specific pages under `commercial/`, `logistics/`, `services/` |
| 9 | Commercial scenarios without dashboard reset | Booking Receipt fails after Work Order | `goto #/home` between commercial scenarios (index > 0) |
| 10 | Services pages have no stable data table | Table-based verify fails | Verify title + URL hash only |
| 11 | Row delete / row trash on Booking Receipt | Wrong popup (Duplicate) or no popup | **Toolbar delete only** after row select + `_wait_toolbar_delete_ready()` |
| 12 | `click_delete` + `click_delete_confirm_yes` without wait chain | Run FAIL / debug PASS race | Use `delete_booking_receipt_from_grid()` |
| 13 | `is_checked()` on grid checkbox | False while Angular syncing | Verify via toolbar Delete **enabled** |
| 14 | `wait_until_booking_absent` with `contains()` | False pass / wrong row match | Exact `normalize-space()='{booking_no}'` on span/a |
| 15 | Delete verify immediately after Yes click | DOM stale — record still visible | Wait API + toast + grid ready + reload verify |

**Fixed — do not re-introduce:**

| Issue | Status |
|-------|--------|
| Missing `pyproject.toml` | ✅ Fixed |
| `_build_wait_error` missing in BasePage | ✅ Fixed |
| Duplicate `model_config` in settings | ✅ Fixed |
| Hardcoded waits in Page Objects | ✅ Fixed — settings-based timing (Section 3.6) |
| Hardcoded `5000` in open_url | ✅ Fixed — uses `settings.open_url_settle_ms` |
| `browser_timeout` 30s too short for headless login | ✅ Fixed — default 60s |

---

## 15. Improvement Backlog

### P0 — Critical ✅ DONE

- [x] Add `pyproject.toml`, fix BasePage wait errors, fix etmss typo
- [x] `efms_account_password` fixture in all login tests
- [x] Register all markers in `pytest_configure`
- [x] Headless viewport + dashboard_ready_selectors
- [x] Remove hard-coded waits — settings-based timing (Section 3.6)
- [x] SMK_AUTH_001/002, SMK_NAV_001–006 implemented
- [x] Test class organization (`TestEfmsAuth`, `TestEfmsNavigate`)

### P1 — High (consistency)

- [x] **Fix `dataTest-etms.json`** — rename key to `test_login_etms`, remove hardcoded password, add `priority`
- [x] **Migrate login tests** to `DataProvider.*_cases()` + product password fixtures
- [x] **ReportPortal integration** — auto-enable, display names, per-app launches
- [x] **Update Jenkinsfile** — add `critical`, `navigation`, `high` to MARKER choices
- [ ] **Add API/DB layers** when first API or DB test is required (not scaffolded in repo)
- [x] **Restructure tests** — `tests/ui/{app}/` → `tests/{app}/` (app-first layout)
- [x] **Update README** to match current structure

### P2 — Medium (developer experience)

- [ ] **Playwright trace on failure** (optional — add `trace_dir` to settings when needed)
- [ ] **Shared `conftest.py` per app** (`tests/efms/conftest.py`) for login precondition fixture
- [ ] **Extract `MENU_ACTIONS` dicts** to shared module if duplicated across new nav tests
- [ ] **AGENTS.md** reference to this `ruleAi.md`
- [ ] **Tighten fallback selectors** — remove overly broad `input[type='text']` where possible

### P3 — Low (nice to have)

- [ ] **Configure `pytest-xdist`** in Jenkins for parallel UI runs (careful: shared UAT env)
- [ ] **Configure `pytest-rerunfailures`** for flaky test retry in CI
- [ ] **ReportPortal dashboards** — eFMS / eTMS widgets on CI (optional)
- [ ] **Visual regression** (Playwright screenshot compare) for critical pages
- [ ] **Allure report** as alternative to pytest-html

---

## 16. Clean Code & Reuse (DRY — No Duplication)

> **Core rule:** Before writing any new function, method, fixture, or Page Object — **search the codebase first**. If something already exists that does the same job (or can be extended with minimal change), **reuse it**. Only create new code when nothing suitable exists.

### 16.1 Mandatory search-before-create workflow

When implementing a new test or Page Object method, run this checklist **in order**:

```
1. Search Page Objects     → src/automation/pages/{efms|etms}/
2. Search BasePage         → src/automation/pages/base_page.py
3. Search PageManager      → src/automation/pages/page_manager.py
4. Search existing tests   → tests/{app}/  (see how similar flows are done)
5. Search fixtures         → tests/conftest.py
6. Search utilities        → src/automation/{logging,reporting}/
7. Search test data        → tests/testdata/dataTest-{app}.json
```

**Only after steps 1–7 return no match** → write a new method or file.

### 16.2 Where to look (reuse map)

| Need | Search here first | Reuse example |
|------|-------------------|---------------|
| Login | `EfmsLoginPage` | `open()`, `login()`, `click_login()`, `is_login_page_displayed()` |
| Logout / dashboard | `EfmsHomePage` | `is_dashboard_displayed()`, `wait_for_dashboard_ready()`, `click_logout()` |
| Commercial navigation | `EfmsAgentPage`, `EfmsCustomerPage`, … | `click_*_menu()`, `is_*_displayed()` — extend `EfmsCommercialMenuPage` |
| Commercial menu base | `commercial_menu_page.py` | `open_commercial_menu()`, `wait_for_sidebar_ready()` — extend, do not duplicate |
| Logistics navigation | `EfmsJobManagementPage`, `EfmsCustomClearancePage`, `EfmsTruckingInlandPage` | Same pattern — extend `EfmsLogisticsMenuPage` |
| Logistics menu base | `logistics_menu_page.py` | `open_logistics_menu()` — extend, do not duplicate |
| Services navigation | `EfmsServicesDocumentationPage` | All 8 doc pages — extend `EfmsServicesMenuPage` |
| Services menu base | `services_menu_page.py` | `open_services_menu()` — extend, do not duplicate |
| eTMS login | `EtmsHomePage` | `open()`, `login()` |
| Wait for element | `BasePage` | `wait_for_visible()`, `wait_for_page_stable()`, `wait_for_dom_content_loaded()` |
| Open URL + reload | `BasePage` | `open_url()` — tune `open_url_settle_ms`, do not copy wait logic |
| Credentials | `conftest.py` + `settings` | `efms_account_password` / `etms_account_password`, `settings.efms_username` |
| Test data loading | `DataProvider` | `DataProvider.efms_cases("test_...")` / `etms_cases("test_...")` |
| Step logging | `step_logger.py` | `@log_method` decorator |
| Page access in test | `PageManager` | `pages.efms_login_page`, `pages.efms_home_page`, `pages.efms_agent_page`, … |

### 16.3 Reuse rules (DO)

| Situation | Correct action |
|-----------|----------------|
| Precondition is "Login success" | `pages.efms_login_page.open().login(...)` then `pages.efms_home_page.is_dashboard_displayed()` |
| Same action in multiple tests | One Page Object method — all tests call it |
| Composite + step methods needed | `EfmsLoginPage.login()` calls step methods internally |
| New test in same module (Login, Navigation) | **Extend** `EfmsLoginPage` or `efms/commercial/*` — not monolithic navigation page |
| Multi TC in one test (SMK_NAV_001–004) | JSON `test_case_ids[]` + `scenarios[]`; `goto #/home` between commercial scenarios |
| Multi step in one TC (SMK_NAV_005/006) | JSON `scenarios[]` + `menu_action` dict in test file; open parent menu once |
| Similar selector on same page | Add to existing `*_selectors` list — do not duplicate selector arrays |
| Same JSON company / metadata | Reuse existing JSON fields — do not duplicate rows with identical data |

### 16.4 Anti-patterns (DO NOT)

```python
# WRONG — duplicate login logic in test instead of reusing login()
def test_nav(pages, data, efms_account_password):
    pages.efms_login_page.open()
    pages.efms_login_page.enter_username(settings.account_username)
    pages.efms_login_page.enter_password(efms_account_password)
    pages.efms_login_page.select_company(data["company"])
    pages.efms_login_page.click_login()
    # ... navigation steps

# CORRECT — reuse composite login on EfmsLoginPage
def test_nav(pages, data, efms_account_password):
    pages.efms_login_page.open().login(
        settings.efms_username, efms_account_password, data["company"],
    )
    assert pages.efms_home_page.is_dashboard_displayed()
    pages.efms_home_page.wait_for_dashboard_ready()
    # ... navigation via pages.efms_agent_page.click_agent_menu()
```

```python
# WRONG — copy-paste wait_for_visible polling into new page
class EfmsNewPage(BasePage):
    def click_button(self):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            ...

# CORRECT — reuse BasePage.wait_for_visible()
class EfmsNewPage(BasePage):
    def click_button(self):
        self.wait_for_visible(self.button_selectors, "Submit button").click()
        return self
```

```python
# WRONG — new Page Object file for one method that belongs on existing page
# efms_login_helper_page.py with enter_username() when EfmsHomePage already has it

# WRONG — duplicate selector list across two page classes
# efms_home_page.py and efms_auth_page.py both define username_selectors

# WRONG — new PageManager property + new class when EfmsHomePage can be extended
```

### 16.5 When to create NEW code (allowed)

Create a **new method** when:
- The action/step does not exist in any Page Object yet
- The method name matches a manual test step and has distinct selectors/behavior

Create a **new Page Object file** when:
- The feature is a **different screen or module** (e.g. `EfmsAgentPage` vs `EfmsLoginPage`)
- Selectors and actions are grouped by UI area, not by test case

Create a **new fixture** when:
- No existing fixture in `conftest.py` provides the same setup/teardown
- The setup is shared by **multiple test files** (not one-off inline code)

**Do NOT create** a new helper for:
- One-liner wrappers around existing BasePage methods
- Logic already available as a composite method (`login()` covers full login flow)
- Copy of an existing method with a different name but same behavior

### 16.6 Extend vs new file — decision tree

```
Does an Page Object for this app + screen already exist?
  YES → Add method(s) to that file
  NO  ↓

Is the action part of an existing flow (login, top bar, sidebar)?
  YES → Login: `EfmsLoginPage` | Dashboard/logout: `EfmsHomePage` | Commercial: `efms/commercial/*`
  NO  ↓

Is it a new distinct screen with its own URL/selectors?
  YES → Create new {App}{Feature}Page under `efms/` or `efms/commercial/` + register in PageManager
  NO  → Add to the closest existing Page Object
```

**Do NOT register base menu classes in PageManager** — `EfmsCommercialMenuPage`, `EfmsLogisticsMenuPage`, `EfmsServicesMenuPage` are internal bases only.

### 16.7 AI search commands (recommended)

Before implementing, search the repo:

```bash
# Find existing page methods
rg "def (login|open|click_|enter_|is_|verify_)" src/automation/pages/

# Find existing selectors for an element
rg "username_selectors|logout_selectors|commercial" src/automation/pages/

# Find how other tests handle the same precondition
rg "login\(|is_dashboard_displayed" tests/efms/

# Find existing fixtures
rg "@pytest.fixture" tests/conftest.py
```

---

## 17. AI Checklist Before Submitting Code

Before finishing any automation task, verify:

```
[ ] Searched existing Page Objects / BasePage / fixtures — reused before creating (Section 16)
[ ] No hard-coded waits — all timing from settings or condition-based waits (Section 3.6)
[ ] Dashboard verify uses dashboard_ready_selectors (headless-safe), not h3 is_visible alone
[ ] Login on EfmsLoginPage, dashboard/logout on EfmsHomePage — not mixed on one page
[ ] No duplicate login, wait, or selector logic — composite methods call step methods
[ ] New Page Object file only when existing page cannot own the feature
[ ] Read manual test case sheet and mapped all columns (Section 5.1)
[ ] Test function name follows: test_{tc_id_lower}_{scenario_slug}_{app}
[ ] JSON key matches test function name exactly
[ ] test_case_id, test_data_id, description present in JSON
[ ] TestData_ID credentials via .env — no username/password in JSON
[ ] efms_account_password / etms_account_password fixture for login tests
[ ] One Page Object @log_method per manual Step
[ ] Test has # Step N comments matching manual Steps
[ ] Expected Result has assert + verify method with wait_for_visible
[ ] Test class used when 2+ related TCs in same module (Section 4.1)
[ ] DataProvider.efms_cases() used when JSON has priority field
[ ] Test file path: tests/{app}/test_{app}_{module}.py
[ ] Uses pages fixture — no direct page.locator() in test
[ ] Markers: class-level @pytest.mark.{efms|etms}+{login|navigation} | JSON priority auto-markers
[ ] New page objects registered in PageManager (only if genuinely new page)
[ ] Selectors follow priority order: data-testid → id → name → aria-label → text → xpath → contains → index (Section 3.4)
[ ] No index/nth selectors unless documented special case
[ ] No selectors in test files — only in Page Object *_selectors lists
[ ] Did not replicate known issues from Section 14
[ ] Booking Receipt delete uses delete_booking_receipt_from_grid() — not raw click_delete chain (Section 3.6 / 5.13)
[ ] Grid verify uses exact normalize-space() for booking_no — not contains()
[ ] Toolbar delete only after row select — never row btn-outline-danger for delete
```

---

## Appendix B — Cursor Rules (`.cursor/rules/`)

Project AI rules are maintained in **`ruleAi.md`** (this file). For Cursor IDE, scoped rules mirror key sections:

| File | Scope | Content |
|------|-------|---------|
| `efms-playwright-waits.mdc` | `src/automation/pages/**/*.py`, `tests/**/*.py` | Wait strategy, no sleep, grid/delete race conditions |
| `efms-booking-receipt-xpath.mdc` | `**/efms_booking_receipt*.py` | XPath catalog Section 5.14, delete flow Section 5.13 |

When updating Booking Receipt automation, update **both** `ruleAi.md` and the matching `.cursor/rules/*.mdc` files.

---

## Appendix — Environment Variables

Copy `.env.example` → `.env` and fill credentials. **Never commit `.env` to Git.**

### Runtime

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `UAT` | Environment name (HTML metadata + RP attribute) |

### Browser

| Variable | Default | Description |
|----------|---------|-------------|
| `BROWSER` | `chrome` | `chrome` or `edge` |
| `BROWSER_HEADLESS` | `false` | Headless mode |
| `BROWSER_TIMEOUT` | `60000` | Element timeout (ms) |
| `BROWSER_SLOW_MO` | `0` | Playwright slow motion (ms) |
| `PAGE_LOAD_TIMEOUT` | `60000` | Navigation / dashboard wait (ms) |
| `POLLING_INTERVAL` | `250` | `wait_for_visible` poll interval (ms) |
| `NAVIGATION_SETTLE_MS` | `1000` | Post-navigation settle (ms) |
| `OPEN_URL_SETTLE_MS` | `5000` | `open_url()` SPA settle (ms) |
| `HEADLESS_VIEWPORT_WIDTH` | `1920` | Headless browser width |
| `HEADLESS_VIEWPORT_HEIGHT` | `1080` | Headless browser height |

### Application URLs

| Variable | Default | Description |
|----------|---------|-------------|
| `EFMS_BASE_URL` | `https://uat-efms.logtechub.com/` | eFMS entry point |
| `ETMS_BASE_URL` | staging eTMS home URL | eTMS entry point |

### Credentials (required for login tests)

| Variable | Description |
|----------|-------------|
| `EFMS_ACCOUNT_USERNAME` | eFMS login username |
| `EFMS_ACCOUNT_PASSWORD` | eFMS login password |
| `ETMS_ACCOUNT_USERNAME` | eTMS login username |
| `ETMS_ACCOUNT_PASSWORD` | eTMS login password |

Legacy fallback in code (`settings.account_username` / `settings.account_password`) still works if `EFMS_ACCOUNT_*` is unset — prefer product-specific keys.

### ReportPortal

| Variable | Default | Description |
|----------|---------|-------------|
| `RP_ENDPOINT` | `http://localhost:8080` | ReportPortal server |
| `RP_PROJECT` | `default_personal` | Project slug in UI URL |
| `RP_API_KEY` | — | API key from Profile → API Keys; **auto-enables reporting** |
| `RP_LAUNCH` | `efms-etms-automation` | Launch name (full suite) |
| `RP_LAUNCH_DESCRIPTION` | eFMS/eTMS UI automation | Launch description |
| `RP_VERIFY_SSL` | `false` | SSL verify for local Docker |
| `RP_LAUNCH_EFMS` | `efms-automation` | Launch when `pytest -m efms` |
| `RP_LAUNCH_ETMS` | `etms-automation` | Launch when `pytest -m etms` |
| `RP_LAUNCH_DESCRIPTION_EFMS` | eFMS UI automation | eFMS launch description |
| `RP_LAUNCH_DESCRIPTION_ETMS` | eTMS UI automation | eTMS launch description |

**View launches:** `{RP_ENDPOINT}/ui/#{RP_PROJECT}/launches/all`

---

*Last updated: 2026-06-16 | Framework: efms-etms-automation 1.0.0 | Tests: SMK_AUTH_001/002, SMK_NAV_001–006, FMS_BR_001–005, ETMS-LOGIN-001 | ReportPortal: auto-enabled*
