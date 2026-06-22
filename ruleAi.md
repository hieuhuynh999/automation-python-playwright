# ruleAi.md — AI Rules for eFMS/eTMS Automation Framework

> **Purpose:** This document is the **only file** any AI model (Claude, GPT, Gemini, Cursor Agent, Copilot, etc.) must read to **write correct automation tests** in this repository — no other docs required.
>
> **Start here:** [Section 0 — AI Master Playbook](#0-ai-master-playbook--read-this-first) → then follow the pipeline for your test type.
>
> **Language:** English (code and comments remain English).
> **Stack:** Python 3.12+, pytest, Playwright (sync API), pytest-html, pytest-reportportal, Pydantic Settings, Loguru.

---

## Table of Contents

0. [AI Master Playbook — Read This First](#0-ai-master-playbook--read-this-first)
   - [0.3 Eight-Step Pipeline](#03-mandatory-eight-step-pipeline)
   - [0.4 Test Type → Reference Pattern](#04-test-type--reference-pattern)
   - [0.5 User Input Formats](#05-user-input-formats-ai-must-parse)
   - [0.6 AI Response Template](#06-ai-response-template-when-user-asks-automate-tc_xxx)
   - [0.7 Copy-Paste Skeletons](#07-copy-paste-skeletons-minimum-viable-code)
1. [Quick Start for AI](#1-quick-start-for-ai)
2. [Repository Map](#2-repository-map)
   - [2.1 Framework Architecture & Layers](#21-framework-architecture--layers)
   - [2.2 Implemented Test Inventory](#22-implemented-test-inventory)
3. [Architecture Rules (MUST follow)](#3-architecture-rules-must-follow)
   - [3.6 Wait & Timing Strategy](#36-wait--timing-strategy-no-hard-coded-waits)
   - [3.7 Assertions (Tests Only)](#37-assertions-tests-only)
   - [3.8 Test Data Generation](#38-test-data-generation)
   - [3.9 Locator Verification Checklist](#39-locator-verification-checklist-before-commit)
   - [3.10 Playwright Development Workflow](#310-playwright-development-workflow)
   - [3.11 Code Quality Before Delivery](#311-code-quality-before-delivery)
4. [Naming Conventions](#4-naming-conventions)
   - [4.1 Test Class Organization](#41-test-class-organization)
5. [Manual Test Case Sheet → Automation (CANONICAL)](#5-manual-test-case-sheet--automation-canonical)
   - [5.11 Multi-Scenario Navigation Tests](#511-multi-scenario-navigation-tests)
   - [5.12 Menu Module POM Pattern](#512-menu-module-pom-pattern)
   - [5.13 Booking Receipt CRUD (FMS_BR_001–005)](#513-booking-receipt-crud-fms_br_001005)
   - [5.14 XPath Catalog — Booking Receipt](#514-xpath-catalog--booking-receipt)
   - [5.15 Cost Of Route CRUD (COR_LP_001)](#515-cost-of-route-crud-cor_lp_001)
   - [5.15 End-to-End Walkthrough](#515-end-to-end-walkthrough--one-new-tc-from-scratch)
6. [How to Write a UI Test (Step-by-Step)](#6-how-to-write-a-ui-test-step-by-step)
7. [How to Write a Page Object](#7-how-to-write-a-page-object)
   - [7.1 Common Components & Utils](#71-common-components--utils-when-to-use-what)
8. [How to Write Test Data (JSON)](#8-how-to-write-test-data-json)
9. [How to Write an API Test](#9-how-to-write-an-api-test)
10. [How to Write a DB Test](#10-how-to-write-a-db-test)
11. [Pytest Markers & Fixtures Reference](#11-pytest-markers--fixtures-reference)
12. [Run Commands](#12-run-commands)
    - [12.1 CI/CD Pipeline (GitHub Actions + Jenkins)](#121-cicd-pipeline-github-actions--jenkins)
13. [Complete Examples (Copy-Paste Ready)](#13-complete-examples-copy-paste-ready)
14. [Known Issues & Do NOT Replicate](#14-known-issues--do-not-replicate)
15. [Improvement Backlog](#15-improvement-backlog)
16. [Clean Code & Reuse (DRY — No Duplication)](#16-clean-code--reuse-dry--no-duplication)
17. [AI Checklist Before Submitting Code](#17-ai-checklist-before-submitting-code)
18. [Flaky Test Diagnosis & Fix](#18-flaky-test-diagnosis--fix)
19. [Framework Architect Quick Reference](#19-framework-architect-quick-reference)

---

## 0. AI Master Playbook — Read This First

> **Contract:** If you are an AI asked to automate a manual test case, read **this section end-to-end**, then jump to the referenced section for your test type. Do **not** invent patterns outside this repo. Do **not** put selectors or `page.locator()` in test files.

### 0.1 What this repo automates

| App | URL setting | Test folder | Test data | Page objects |
|-----|-------------|-------------|-----------|--------------|
| **eFMS** | `settings.efms_base_url` | `tests/efms/` | `tests/testdata/dataTest-efms.json` | `src/automation/pages/efms/` |
| **eTMS** | `settings.etms_base_url` | `tests/etms/` | `tests/testdata/dataTest-etms.json` | `src/automation/pages/etms/` |

**Architecture in one line:** `Test → pages fixture → PageManager → {App}Page → Common Components (composed) → BasePage → Playwright`

**Pure helpers (no browser):** `src/automation/utils/` — string/date/file helpers used by Page Objects or tests.

**Layers NOT implemented yet:** API tests, DB tests — do not scaffold unless explicitly requested (Section 9–10).

### 0.2 Golden rules (non-negotiable)

| # | Rule |
|---|------|
| 1 | Tests use **`pages` fixture only** — never `page.locator()` in tests |
| 2 | **Passwords in `.env` only** — inject `efms_account_password` / `etms_account_password` fixture |
| 3 | **URLs in Page Objects only** — via `settings.efms_base_url` / `settings.etms_base_url` |
| 4 | **One manual Step = one `@log_method` Page Object method** + `# Step N` comment in test |
| 5 | **JSON key = test function name exactly** (e.g. `"test_smk_auth_001_login_success_efms"`) |
| 6 | **Search existing code first** — extend Page Objects before creating new files (Section 16) |
| 7 | **No hard-coded waits** — use `settings.*_timeout`, `wait_for_visible`, condition waits (Section 3.6) |
| 8 | **Selectors in Page Object `*_selectors` lists** — priority order Section 3.4 |
| 9 | **Reuse UI widgets via `pages/common/`** — ng-select, native select, SweetAlert; do not duplicate in each Page Object (Section 7.1) |
| 10 | **Assertions in test files only** — Page Objects return `bool` / raise wait errors; use `assert` with messages in tests (Section 3.7) |
| 11 | **Verify locators from live DOM** before committing new selectors — never guess (Section 3.9–3.10) |

### 0.3 Mandatory eight-step pipeline

Use this **every time** you automate a new manual test case:

```
Step 1  PARSE manual sheet
        → Extract: TC_ID, Module, Scenario, Priority, Preconditions, TestData_ID, Steps[], Expected Result
        → Identify app: efms | etms (from module, URL, or user hint)

Step 2  CLASSIFY test type
        → See Section 0.5 — pick reference implementation to copy

Step 3  SEARCH codebase (Section 16.1)
        → rg existing Page methods, fixtures, similar tests

Step 4  ADD JSON test data
        → File: tests/testdata/dataTest-{app}.json
        → Key: test function name (derive from TC_ID — Section 5.4)
        → Include: test_case_id, test_data_id, description, module, priority, preconditions + business fields
        → NEVER: username, password in JSON

Step 5  CREATE / EXTEND Page Object
        → File: src/automation/pages/{app}/... (Section 7)
        → Add *_selectors + @log_method per manual step + verify method for Expected Result
        → Reuse pages/common/ for ng-select, native select, SweetAlert (Section 7.1)
        → Reuse utils/ for pure helpers (text normalize, dates) — no Playwright in utils

Step 6  REGISTER in PageManager (only if new page class)
        → src/automation/pages/page_manager.py — lazy @property

Step 7  WRITE test file
        → tests/{app}/test_{app}_{module}.py (Section 4, 5.6)
        → Class if 2+ TCs in same module; parametrize via DataProvider.{app}_cases("test_...")
        → Markers: @pytest.mark.{efms|etms}, suite marker, @pytest.mark.tc_id("TC_ID")

Step 8  RUN & verify
        → uv run pytest tests/{app}/test_{app}_{module}.py -v --browser chrome --browser-headless false
        → Fix failures using Section 14 (Known Issues)
        → Run: uv run ruff check . && uv run ruff format .
```

### 0.4 Test type → reference pattern

| Test type | When to use | Copy from | Key pattern |
|-----------|-------------|-----------|-------------|
| **A — Login / Logout** | Auth flows, preconditions | `TestEfmsAuth` — Section 5.6, Example A | Step-by-step or `open().login()` composite |
| **B — Menu navigation** | Multiple submenu items in one TC | `TestEfmsNavigate` — Section 5.11 | JSON `scenarios[]` + `MENU_ACTIONS` dict |
| **C — CRUD ordered flow** | Create → read → update → delete same record | `TestEfmsBookingReceipt` — Section 5.13 | Class variable `booking_no`; run tests in order |
| **D — Single form / action** | One screen, fill + save + verify | FMS_BR_001/002 patterns | `fill_*_form(data)`, assert message |
| **E — eTMS auth (login + branch)** | eTMS login / branch / home | `TestEtmsAuth` — Example B, Section 4.1 | `EtmsLoginPage` + `EtmsHomePage`; `NgSelectComponent` for branch |
| **G — eTMS create + delete (single TC)** | One record create then delete same run | `TestEtmsCostOfRoute` — Section 5.15 | `login_etms` fixture; menu search; `action-btn` → Delete on row |
| **F — New module page** | New sidebar screen | Example F — Section 13 | New POM + PageManager + extend menu base if under Commercial/Logistics/Services |

**Precondition "Login success" (all eFMS tests except auth):**

```python
pages.efms_login_page.open().login(
    settings.efms_username, efms_account_password, data["company"],
)
assert pages.efms_home_page.is_dashboard_displayed()
pages.efms_home_page.wait_for_dashboard_ready()
```

**Precondition "Login success" (eTMS tests that need home dashboard):**

```python
# Preferred — reuse fixture in tests/etms/conftest.py
login_etms(data["branch"])

# Or inline (same steps as login_etms fixture)
pages.etms_login_page.open().login(
    settings.etms_username, etms_account_password,
)
pages.etms_login_page.select_branch(data["branch"])
pages.etms_login_page.click_select_branch()
assert pages.etms_home_page.is_dashboard_displayed()
```

### 0.5 User input formats AI must parse

Users may paste test cases in any of these shapes — extract the same fields:

**Format 1 — Table (preferred):**

| TC_ID | Module | Scenario | Priority | Preconditions | TestData_ID | Steps | Expected Result |
|-------|--------|----------|----------|---------------|-------------|-------|-----------------|

**Format 2 — Bullet list:**

```
TC_ID: FMS_XX_001
Steps:
1. Open Booking Receipt page
2. Click Add new
Expected: Form displayed
TestData_ID: LOGIN_ADMIN
```

**Format 3 — Free text:** Parse TC_ID, numbered steps, and expected result; ask user only if app (efms/etms) is ambiguous.

**Column → code mapping (canonical):** Section 5.1

| Manual column | Code destination |
|---------------|------------------|
| `TC_ID` | JSON `test_case_id` + `@pytest.mark.tc_id("...")` |
| `TestData_ID` | JSON `test_data_id` → `.env` credentials (Section 5.2) |
| `Steps` | Page Object methods + `# Step N` in test |
| `Expected Result` | `assert pages.*.is_*()` or `assert pages.*.is_message_displayed(...)` |
| Business values in steps | JSON fields → `data["field"]` |

### 0.6 AI response template (when user asks "automate TC_XXX")

Structure your answer in this order so any reviewer (human or AI) can apply the change:

```markdown
## 1. Classification
- App: efms | etms
- Type: A|B|C|D|E|F (Section 0.4)
- Reference: {existing test file to mirror}

## 2. Files to create/modify
- [ ] tests/testdata/dataTest-{app}.json — add key `test_...`
- [ ] src/automation/pages/... — add/extend methods
- [ ] src/automation/pages/page_manager.py — if new page
- [ ] tests/{app}/test_{app}_{module}.py — add test method

## 3. JSON entry
{full JSON block}

## 4. Page Object methods
{methods with @log_method and *_selectors}

## 5. Test method
{full test with markers, parametrize, steps, asserts}

## 6. Run command
uv run pytest ... -v --browser chrome --browser-headless false
```

### 0.7 Copy-paste skeletons (minimum viable code)

**Test method skeleton (eFMS, data-driven):**

```python
@pytest.mark.parametrize(
    "data",
    DataProvider.efms_cases("test_{tc_id_lower}_{scenario_slug}_efms"),
)
@pytest.mark.tc_id("{TC_ID}")
def test_{tc_id_lower}_{scenario_slug}_efms(self, pages, data, efms_account_password):
    # Precondition: Login (skip if auth test — call steps directly)
    pages.efms_login_page.open().login(
        settings.efms_username, efms_account_password, data["company"],
    )
    assert pages.efms_home_page.is_dashboard_displayed()

    # Step 1: {description}
    pages.{page}.{method}()

    # Expected: {expected result}
    assert pages.{page}.{verify_method}()
```

**JSON row skeleton:**

```json
"test_{tc_id_lower}_{scenario_slug}_efms": [
    {
        "test_case_id": "{TC_ID}",
        "test_data_id": "LOGIN_ADMIN",
        "description": "{Scenario} - {Expected Result short}",
        "module": "{Module}",
        "priority": "Critical|High|Medium|Low",
        "preconditions": "{Preconditions}",
        "company": "LTH Demo JSC"
    }
]
```

**Page Object action skeleton:**

```python
@log_method("{Human-readable step name}")
def {action_method}(self, value: str = "") -> "{ClassName}":
    self.wait_for_visible(self.{element}_selectors, "{Element name}").fill(value)
    return self

@log_method("Verify {expected state}")
def is_{state}_displayed(self) -> bool:
    self.wait_for_visible(self.{element}_selectors, "{Element name}", timeout=settings.page_load_timeout)
    return True
```

**Naming formula (Section 5.4):**

```
TC_ID:     FMS_BR_002
Scenario:  Create Booking Receipt
App:       efms

Function:  test_fms_br_002_create_booking_receipt_efms
JSON key:  "test_fms_br_002_create_booking_receipt_efms"
File:      tests/efms/test_efms_booking_receipt.py
Class:     TestEfmsBookingReceipt
```

### 0.8 Extend vs create — decision in 30 seconds

```
Same screen/module already has a Page Object?
  YES → Add methods to that file (preferred)
  NO  ↓

Under Commercial / Logistics / Services sidebar?
  YES → Extend {module}_menu_page.py base + new efms_{feature}_page.py + PageManager
  NO  ↓

New top-level eFMS screen?
  YES → New efms_{feature}_page.py + PageManager
  NO  → Add to closest existing page
```

**Never register** `EfmsCommercialMenuPage`, `EfmsLogisticsMenuPage`, `EfmsServicesMenuPage` in PageManager — bases only.

### 0.9 Validation before finishing

```bash
# Collect only (no browser)
uv run pytest tests/{app}/test_{file}.py --collect-only -q

# Run headed (debug)
uv run pytest tests/{app}/test_{file}.py -v --browser chrome --browser-headless false

# Lint
uv run ruff check . && uv run ruff format .
```

Complete checklist: [Section 17](#17-ai-checklist-before-submitting-code)

---

## 1. Quick Start for AI

> **Already read Section 0?** Use this section as a short reminder. Full rules are in Sections 3–17.

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
│   │   ├── settings.py             # Pydantic Settings — all env config
│   │   └── secret_redaction.py     # Redact passwords in pytest/RP failure output
│   ├── logging/
│   │   ├── logger.py               # Loguru file logger
│   │   └── step_logger.py          # @log_method decorator + step logs
│   ├── pages/
│   │   ├── base_page.py            # BasePage — open_url, wait_for_visible, wait_for_page_stable
│   │   ├── page_manager.py         # PageManager — lazy page object factory
│   │   ├── common/                 # Reusable UI components (NOT in PageManager)
│   │   │   ├── base_component.py   # BaseComponent — compose inside Page Objects
│   │   │   ├── ng_select_component.py
│   │   │   ├── native_select_component.py
│   │   │   └── swal_modal_component.py
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
│   │       ├── etms_login_page.py
│   │       └── etms_home_page.py
│   ├── utils/                      # Pure helpers — no Playwright, no selectors
│   │   └── text_utils.py           # normalize_text, text_contains_any
│   └── reporting/
│       ├── reportportal_support.py # ReportPortal ini, patches, step logs, screenshots
│       ├── rerun_support.py        # pytest-rerunfailures config (TEST_RERUNS)
│       └── metadata_support.py     # HTML report Base URL per app (eFMS / eTMS)
│
├── tests/
│   ├── conftest.py                 # Playwright fixtures + HTML/RP report hooks
│   ├── conftest_reportportal.py    # ReportPortal pytest hooks (via pytest_plugins)
│   ├── data_provider.py            # DataProvider — load JSON + auto priority markers
│   ├── test_text_utils.py          # Unit tests for utils/text_utils
│   ├── test_reporting_support.py   # Unit tests — retry + secret redaction
│   ├── testdata/
│   │   ├── dataTest-efms.json
│   │   └── dataTest-etms.json
│   ├── efms/                       # eFMS UI tests (app-first layout)
│   │   ├── test_efms_auth.py       # TestEfmsAuth — SMK_AUTH_001/002
│   │   ├── test_efms_navigate.py   # TestEfmsNavigate — SMK_NAV_001–006
│   │   └── test_efms_booking_receipt.py                 # FMS_BR_001–005
│   └── etms/                       # eTMS UI tests
│       ├── conftest.py             # login_etms fixture
│       ├── test_etms_auth.py       # TestEtmsAuth — SMK_AUTH_001/002
│       └── test_etms_cost_of_route.py  # COR_LP_001
│
├── reports/                        # HTML report output (gitignored)
├── test-results/                   # Screenshots (gitignored)
├── logs/                           # automation.log (gitignored)
├── scripts/
│   └── ci-run-tests.sh             # Shared pytest runner for CI
├── .github/workflows/
│   └── ci.yml                      # GitHub Actions — quality + UI tests
├── Jenkinsfile                     # Jenkins pipeline
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
| `conftest.py` (root) | Early `.env` load + auto `--reportportal` on **test execution** only (not `--collect-only`) |

> **Migration note:** Tests moved from `tests/ui/{app}/` → `tests/{app}/`. Do **not** recreate the `tests/ui/` layer.

**Applications:**

| App | Base URL setting | PageManager properties | Test data file |
|-----|-----------------|-------------------------|----------------|
| eFMS | `settings.efms_base_url` | `efms_login_page`, `efms_home_page`, commercial pages (`efms_agent_page`, `efms_customer_page`, `efms_work_order_page`, `efms_booking_receipt_page`), logistics pages (`efms_job_management_page`, `efms_custom_clearance_page`, `efms_trucking_inland_page`), `efms_services_documentation_page` | `dataTest-efms.json` |
| eTMS | `settings.etms_base_url` | `etms_login_page`, `etms_home_page`, `etms_cost_of_route_page` | `dataTest-etms.json` |

**eFMS Page Object responsibilities:**

| Class | File | Responsibility |
|-------|------|----------------|
| `EfmsLoginPage` | `efms_login_page.py` | Open login URL, credentials, company select (`NativeSelectComponent`), verify login page |
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

**eTMS Page Object responsibilities:**

| Class | File | Responsibility |
|-------|------|----------------|
| `EtmsLoginPage` | `etms/etms_login_page.py` | Login form, branch/hub picker (`NgSelectComponent`), branch verify |
| `EtmsHomePage` | `etms/etms_home_page.py` | Home URL + dashboard after branch select |
| `EtmsCostOfRoutePage` | `etms/etms_cost_of_route_page.py` | Cost Of Route: menu search, Choose Route popup, surcharge generate, save, delete (COR_LP_001) |

**Common Components (compose inside Page Objects — not in PageManager):**

| Class | File | Widget |
|-------|------|--------|
| `NgSelectComponent` | `common/ng_select_component.py` | Angular `ng-select` |
| `NativeSelectComponent` | `common/native_select_component.py` | HTML `<select>` |
| `SwalModalComponent` | `common/swal_modal_component.py` | SweetAlert2 popup |

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
│  Compose Common Components for repeated widgets (ng-select)   │
│  Module bases: commercial_menu_page, logistics_menu_page,     │
│                services_menu_page (extend, not in Manager)    │
└──────────────────────────┬──────────────────────────────────┘
                           │ composes + inherits
┌──────────────────────────▼──────────────────────────────────┐
│  Common Components (pages/common/) — NOT in PageManager       │
│  NgSelectComponent, NativeSelectComponent, SwalModalComponent │
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
  utils/     → pure helpers (text, dates) — no browser
  reporting/ → reportportal_support.py + metadata_support.py (ReportPortal) + pytest-html hooks in conftest
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
| Reusable widgets | Shared UI in `pages/common/`; pure logic in `utils/` |
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
| SMK_AUTH_001 | Login | Critical | `TestEtmsAuth.test_smk_auth_001_login_success_etms` | `tests/etms/test_etms_auth.py` |
| SMK_AUTH_002 | Login | Critical | `TestEtmsAuth.test_smk_auth_002_select_branch_etms` | `tests/etms/test_etms_auth.py` |
| COR_LP_001 | Cost Of Route | High | `TestEtmsCostOfRoute.test_cor_lp_001_create_cost_of_route_etms` | `tests/etms/test_etms_cost_of_route.py` |

**Run by priority (auto-applied via `DataProvider.*_cases()`):**

```bash
uv run pytest -m critical -v --browser chrome --browser-headless true   # SMK_AUTH_001/002 (eFMS + eTMS)
uv run pytest -m high -v --browser chrome --browser-headless true       # SMK_NAV_001–006, FMS_BR_001–005, COR_LP_001
uv run pytest -m navigation -v --browser chrome --browser-headless true # SMK_NAV_001–006
uv run pytest -m login -v --browser chrome --browser-headless true      # all login/logout tests
uv run pytest -m efms -v --browser chrome --browser-headless true       # eFMS only → RP launch efms-automation
uv run pytest -m etms -v --browser chrome --browser-headless true         # eTMS only → RP launch etms-automation
```

---

## 3. Architecture Rules (MUST follow)

### 3.1 Page Object Model (POM)

```
Test File  →  pages fixture  →  PageManager  →  {App}Page  →  Common Components  →  BasePage  →  Playwright Page
```

- **Test layer:** assertions + orchestration only
- **Page layer:** selectors, user actions, element waits; compose shared widgets from `pages/common/`
- **Component layer:** reusable UI widgets (ng-select, `<select>`, SweetAlert) — **not** in PageManager
- **Util layer:** pure Python helpers in `utils/` — no selectors, no Playwright
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
def test_smk_auth_001_login_success_etms(pages, data, etms_account_password):
    pages.etms_login_page.open()
    pages.etms_login_page.enter_username(settings.etms_username)
    pages.etms_login_page.enter_password(etms_account_password)
    pages.etms_login_page.click_login()
    assert pages.etms_login_page.is_branch_hub_selection_displayed()

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

#### Timeout tiers (semantic — map to `settings`, never hardcode ms)

| Tier | Setting | Default | Use for |
|------|---------|---------|---------|
| Poll / retry gap | `polling_interval` | `250` | Inside `wait_for_visible()` loops |
| SPA settle | `navigation_settle_ms` | `1000` | After `readyState === complete` |
| Post-goto settle | `open_url_settle_ms` | `5000` | `open_url()` SPA bootstrap |
| Standard UI | `browser_timeout` | `60000` | Element visible, grid rows, shipment items |
| Navigation / login | `page_load_timeout` | `60000` | `wait_for_url`, dashboard, delete API |

Override per call: `wait_for_visible(..., timeout=settings.page_load_timeout)` — never `timeout=5000` literals.

#### BasePage interaction helpers

| Method | When to use |
|--------|-------------|
| `wait_for_visible(selectors, name, timeout=...)` | Element must appear |
| `click_when_ready(selectors, name, timeout=..., force=False)` | Visible **and enabled**, then click |
| `find_visible(selectors)` | Non-blocking probe inside components |

```python
# CORRECT — enabled + click via BasePage
self.click_when_ready(self.save_button_selectors, "Save button")

# WRONG — click without visibility/enabled guarantee
self.page.locator("button").click()
```

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

### 3.7 Assertions (Tests Only)

| Layer | Allowed | Pattern |
|-------|---------|---------|
| **Test class** | **Yes** — primary place for assertions | `assert pages.efms_home_page.is_dashboard_displayed()` |
| **Page Object** | **No business assertions** | Use `wait_for_visible()` → raises on failure |
| **Page Object** | `is_*_displayed() -> bool` | Test calls `assert page.is_*_displayed(), "message"` |
| **Page Object** | Composite flow guards | Rare — e.g. `refresh_list_page()` asserts list loaded before delete continues |

**Rules:**

1. Every test **must end with at least one assertion** (or explicit `pytest.skip`).
2. Use `assert` with a **descriptive message** so HTML/ReportPortal shows context:

```python
# CORRECT
assert pages.efms_agent_page.is_agent_list_displayed(), (
    f"Step {step}: Agent list with grid data — verification failed"
)

# WRONG — no context on failure
assert result
```

3. Use `pytest.skip(reason)` when a runtime precondition cannot be met — **not** `assert False`:

```python
if not TestEfmsBookingReceipt.booking_no:
    pytest.skip("Requires booking_no from FMS_BR_002")
```

4. **Never** put `assert expected == actual` for business rules inside Page Objects — keep verification methods returning `bool` or raising via waits.

### 3.8 Test Data Generation

| Data type | Source | Rule |
|-----------|--------|------|
| Credentials | `.env` → `settings` + `efms_account_password` fixture | **Never** in JSON or test files |
| Static business data | `tests/testdata/dataTest-{app}.json` | Company name, expected messages, menu actions |
| **Unique / disposable fields** | Generated at runtime | **Never hardcode** values that must be unique per run |

Generate unique data for create flows (booking no captured from UI, emails, display names):

```python
from datetime import datetime
import uuid

suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_ref = f"AUTO_{suffix}_{uuid.uuid4().hex[:6]}"
```

**Parallel-safe:** each test method that creates records should use its own generated data — do not share hardcoded unique strings across tests.

**Ordered CRUD** (Booking Receipt): use class variable `booking_no` set in create test, consumed by later tests — see Section 3.6 / 5.13.

### 3.9 Locator Verification Checklist (Before Commit)

Before adding a locator to `*_selectors`, verify on **live UAT** (headed browser or Playwright MCP):

| # | Check |
|---|--------|
| 1 | Matches **exactly one** interactive target in scope (portlet, open submenu, form) — not zero, not many |
| 2 | Target is the element the **user actually clicks/types** — not overlay, spinner, or hidden clone |
| 3 | Still resolves after **reload / navigate away and back** |
| 4 | Stable across page states: loading → loaded → with data (and empty state if applicable) |

**Core principle (semantic over styling):** build locators on `data-testid`, `name`, `aria-*`, `href`, `formcontrolname`, visible label text — **not** on layout/theme classes (`m-menu__*`, `m-portlet__*`) as primary strategy.

**eFMS / eTMS Angular priority** (when `data-testid` absent — common on legacy screens):

1. `aria-label`, `role`, `getByRole` / `getByLabel` (when they resolve)
2. `data-testid`, `data-qa`, `data-test`
3. Stable `id`, `name`, `formcontrolname`
4. Visible text (`:has-text`, `normalize-space()`)
5. Scoped CSS (`select[formcontrolname='companyId']`)
6. Relative XPath anchored to stable parent (`href`, `h3`, `th`)
7. `contains(@class, ...)` — **fallback only**

**FORBIDDEN:**

- Dynamic/hashed classes (`css-1n2xyz`, random `ng-*` ids)
- Absolute positional XPath (`/html/body/div[3]/...`, `//div[3]/button[2]`)
- `nth-child` / index as primary selector
- Overly broad selectors (`input[type='text']`, bare `button`) unless documented last-resort fallback

### 3.10 Playwright Development Workflow

**Stack:** `playwright.sync_api` via pytest `browser` / `page` fixtures in `tests/conftest.py` — use `pages` fixture in tests, not raw `page` for actions.

| Rule | Detail |
|------|--------|
| **Headed first** | Develop and debug with `--browser-headless false` until stable |
| **Headless CI** | Only after headed pass, or in CI with viewport fix below |
| **Viewport** | Headless uses `1920×1080` via `settings.headless_viewport_width/height` — required for sidebar/menu |
| **Never guess locators** | Inspect live DOM; do not copy from memory or old code without re-verifying |
| **Never blind copy** | Selectors from other products (ExtJS, etc.) do not apply to Angular eFMS |

**Recommended order when inspecting UI (Playwright MCP / browser tools):**

```
1. Navigate to URL (login if needed)
2. Set viewport 1920×1080 (mandatory for menu/sidebar)
3. Snapshot / pick locator from live DOM
4. Confirm unique + interactable
5. Add to Page Object *_selectors in priority order (Section 3.4, 3.9)
```

### 3.11 Code Quality Before Delivery

Before finishing any automation task:

- Remove debug `print()` — use `automation.logging.logger` / `@log_method`
- Remove commented-out code and unused `*_selectors`
- Remove temporary probe scripts (`scripts/probe_*.py`, `_probe_*.py`) unless user asked to keep
- **Do not delete** source files without explicit user confirmation
- Check directory structure before creating files — extend existing Page Object when possible (Section 16)
- Run `uv run ruff check . && uv run ruff format .` before commit

**Security:** never hardcode credentials, tokens, or API keys — `.env` only via `settings` (gitignored).

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
| Auth (Login + Branch) | `TestEtmsAuth` | `tests/etms/test_etms_auth.py` | `test_smk_auth_001_*`, `test_smk_auth_002_*` |

**Rules:**

1. **Class-level markers** — `@pytest.mark.login` + `@pytest.mark.efms` on the class (shared by all methods).
2. **Method-level markers** — `@pytest.mark.tc_id("SMK_AUTH_001")` per test case when needed for report fallback.
3. **Parametrize** — use `DataProvider.efms_cases()` / `etms_cases()` (auto priority markers from JSON).
4. **First parameter** — always `self` in class methods.

**Canonical class template (eFMS):**

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
| Single TC in a new module | Standalone function — refactor to class when 2nd TC added |

**eTMS auth class template:**

```python
@pytest.mark.login
@pytest.mark.etms
class TestEtmsAuth:
    @pytest.mark.parametrize(
        "data", DataProvider.etms_cases("test_smk_auth_001_login_success_etms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_etms(self, pages, data, etms_account_password):
        ...
```

---

## 5. Manual Test Case Sheet → Automation (CANONICAL)

> **AI entry point:** [Section 0](#0-ai-master-playbook--read-this-first) first, then this section for column mapping and templates.
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
| 2. Enter Username | `EfmsLoginPage.enter_username(username)` | `pages.efms_login_page.enter_username(settings.efms_username)` |
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
| `username` | **Never** | — | use `settings.efms_username` / `settings.etms_username` |
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

        # Step 2: Enter Username (LOGIN_ADMIN → settings.efms_username)
        pages.efms_login_page.enter_username(settings.efms_username)

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
  YES → .env (`EFMS_ACCOUNT_USERNAME` / `ETMS_ACCOUNT_USERNAME`) + `settings.efms_username` in test
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
        pages.efms_login_page.open().login(settings.efms_username, efms_account_password, data["company"])
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
| List page (Agent, Job Management) | `h3` + grid columns + **data rows** via `EfmsNavigateVerifyMixin` | `Partner ID`, `Name ABBR` |
| Services documentation | `h3` + **`shipment-item-wrapper`** cards with content | `efms_services_documentation_page.py` |
| Documentation page (legacy note) | — | Prefer shipment list over title-only |
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
```

### 5.15 Cost Of Route CRUD (COR_LP_001)

> Reference: `tests/etms/test_etms_cost_of_route.py`, `etms_cost_of_route_page.py`,
> `tests/etms/conftest.py` (`login_etms` fixture),
> `tests/testdata/dataTest-etms.json` key `test_cor_lp_001_create_cost_of_route_etms`.

| Step | Action | Key Page methods |
|------|--------|------------------|
| 1 | Menu search → Cost Of Route list | `open_via_menu_search()`, `is_list_page_displayed()` |
| 2 | Add New → Choose Route popup | `click_add_new()`, `is_choose_route_popup_displayed()` |
| 3 | Filter Code, tick row, Choose | `choose_route(route_code)` |
| 4 | Vehicle / Container / Weight Range | `fill_route_mapping_fields(data)` — `search-field` ng-select pattern |
| 5 | Generate + verify Total (Price) | `click_generate_surcharge()`, `is_total_price_displayed()` |
| 6 | Save + success toast | `click_save()`, `wait_for_add_modal_closed()`, `is_success_message_displayed()` |
| 7 | Delete same record | `ensure_list_page_displayed()`, `click_row_action_btn()`, `click_row_delete_button()`, confirm OK |

**Delete flow (step 7 — mandatory order):**

1. Click row `action-btn` — reveals Delete button on row
2. Click Delete: `a.btn-ftl-icon.text-danger[title='Delete']` or `a[id*='btnButtonRowDelete']`
3. Confirm SweetAlert **"Do you want delete?"** → OK
4. Verify toast **"Data delete success"**

**Do NOT** filter Route Code on list before delete when record was just created in the same test run.

**COR_LP_001 test template (canonical):**

```python
login_etms(data["branch"])
cor_page = pages.etms_cost_of_route_page

cor_page.open_via_menu_search(data["menu_search"])
cor_page.click_add_new()
cor_page.choose_route(data["route_code"])
cor_page.fill_route_mapping_fields(data)
cor_page.click_generate_surcharge()
cor_page.click_save()
cor_page.wait_for_add_modal_closed()

cor_page.ensure_list_page_displayed(data["menu_search"])
cor_page.click_row_action_btn(data["route_code"], data["vehicle_type"])
cor_page.click_row_delete_button(data["route_code"], data["vehicle_type"])
cor_page.click_delete_confirm_ok()
assert cor_page.is_success_message_displayed(data["expected_delete_message"])
```

**Run:**

```bash
uv run pytest tests/etms/test_etms_cost_of_route.py -v \
  --browser chrome --browser-headless false --reportportal
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

### 5.15 End-to-end walkthrough — one new TC from scratch

> **Use this when Section 0 is not enough detail.** Follow every file touch in order.

**User gives:**

| TC_ID | Module | Scenario | Priority | Preconditions | TestData_ID | Steps | Expected Result |
|-------|--------|----------|----------|---------------|-------------|-------|-----------------|
| FMS_WO_001 | Work Order | Open Work Order list | High | Login success | LOGIN_ADMIN | 1. Open Commercial menu 2. Click Work Order | Work Order list displayed |

**Step-by-step file changes:**

| # | File | Action |
|---|------|--------|
| 1 | `tests/testdata/dataTest-efms.json` | Add key `"test_fms_wo_001_open_work_order_list_efms"` with metadata + `"company": "LTH Demo JSC"` |
| 2 | `src/automation/pages/efms/commercial/efms_work_order_page.py` | Reuse existing `click_work_order_menu()`, `is_work_order_list_displayed()` — add method only if step is new |
| 3 | `tests/efms/test_efms_work_order.py` | New file OR add method to existing class |
| 4 | PageManager | Skip — `efms_work_order_page` already registered |

**Test file (minimal):**

```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.regression
@pytest.mark.efms
class TestEfmsWorkOrder:
    @pytest.mark.parametrize(
        "data",
        DataProvider.efms_cases("test_fms_wo_001_open_work_order_list_efms"),
    )
    @pytest.mark.tc_id("FMS_WO_001")
    def test_fms_wo_001_open_work_order_list_efms(self, pages, data, efms_account_password):
        pages.efms_login_page.open().login(
            settings.efms_username, efms_account_password, data["company"],
        )
        assert pages.efms_home_page.is_dashboard_displayed()
        pages.efms_home_page.wait_for_dashboard_ready()

        pages.efms_work_order_page.open_commercial_menu()  # Step 1
        pages.efms_work_order_page.click_work_order_menu()  # Step 2

        assert pages.efms_work_order_page.is_work_order_list_displayed()  # Expected
```

**Run:**

```bash
uv run pytest tests/efms/test_efms_work_order.py -v --browser chrome --browser-headless false
```

**If Steps include form fill / save / delete:** switch to Type C or D (Section 0.4) — use `TestEfmsBookingReceipt` as CRUD reference.

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

### 7.1 Common Components & Utils (when to use what)

| Layer | Location | Register in PageManager? | Use when |
|-------|----------|--------------------------|----------|
| **Page Object** | `pages/{app}/` | Yes (screens) | Full screen / route — login, home, booking receipt |
| **Module base** | `pages/{app}/commercial/` etc. | No | Shared navigation within one menu module |
| **Common Component** | `pages/common/` | No | Same UI widget on multiple pages — `ng-select`, `<select>`, SweetAlert |
| **Util** | `utils/` | N/A | Pure Python — normalize text, dates, file paths; **no selectors, no Playwright** |
| **BasePage** | `base_page.py` | N/A | Low-level wait/navigation primitives every page inherits |

**Compose components inside Page Objects** — selectors stay on the Page Object; pass `self` as owner:

```python
from automation.pages.common.ng_select_component import NgSelectComponent

@property
def _branch_select(self) -> NgSelectComponent:
    return NgSelectComponent(self, self.branch_hub_selectors, "eTMS Branch/Hub dropdown")

@log_method("Select branch")
def select_branch(self, branch_code: str) -> "EtmsLoginPage":
    self._branch_select.select_option_by_text(branch_code)
    return self
```

**Available components:**

| Class | Widget | Used by |
|-------|--------|---------|
| `NgSelectComponent` | Angular `ng-select` | eTMS branch picker; migrate eFMS form fields when touching those pages |
| `NativeSelectComponent` | HTML `<select>` | eFMS company dropdown |
| `SwalModalComponent` | SweetAlert2 popup | eFMS confirm/delete — use in new code; `efms_booking_receipt_page` can migrate incrementally |

**Do NOT** put `page.locator()` in tests or utils. **Do NOT** register components in `PageManager`.

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
@pytest.mark.parametrize("data", DataProvider.etms_cases("test_smk_auth_001_login_success_etms"))
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
| `login_etms` | function | `tests/etms/conftest.py` — login + branch + dashboard ready; call `login_etms(data["branch"])` |

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
@pytest.mark.smoke          # smoke suite (manual — optional on specific tests)
@pytest.mark.regression     # regression suite
@pytest.mark.tc_id("SMK_AUTH_001")       # fallback when JSON tc_id absent
@pytest.mark.description("Login eFMS Successfully")  # fallback description
```

**Marker execution matrix:**

| Command | Collects |
|---------|----------|
| `-m critical` | SMK_AUTH_001/002 (eFMS + eTMS) |
| `-m high` | SMK_NAV_001–006, FMS_BR_001–005, COR_LP_001 |
| `-m login` | All auth tests (`TestEfmsAuth`, `TestEtmsAuth`) |
| `-m navigation` | SMK_NAV commercial/logistics/services |
| `-m "login and efms"` | eFMS auth tests only |
| `-m efms` / `-m etms` | All tests for one app; ReportPortal uses separate launch name |
| `-m smoke` | Tests with explicit `@pytest.mark.smoke` |

### HTML report hooks (`conftest.py`)

| Hook | Behavior |
|------|----------|
| `pytest_configure` | Report metadata: Environment, Browser, Headless, Timeout, **Base URL** (initial guess) |
| `pytest_collection_modifyitems` | Refine **Base URL** from collected tests (accurate per run) |
| `pytest_html_report_title` | Report title: "Automation Report" |
| `pytest_runtest_makereport` | Enriches report: TC_ID, description, method logs, failure screenshot |
| `pytest_html_results_table_*` | Custom "Test Case" column (not raw nodeid) |
| Multi-scenario tests | Shows `test_case_ids[]` + per-scenario breakdown in extras |

**HTML metadata `Base URL`** (`metadata_support.resolve_report_base_url`):

| Run scope | `Base URL` value |
|-----------|------------------|
| `pytest -m efms` or `tests/efms/` only | `settings.efms_base_url` |
| `pytest -m etms` or `tests/etms/` only | `settings.etms_base_url` |
| Mixed suite (both apps) or unit tests only | `eFMS: {efms_base_url} \| eTMS: {etms_base_url}` |

Priority: collected test paths → CLI paths → `-m` marker expression.

**Report outputs:**
- HTML: `reports/report.html` (via `--html=... --self-contained-html`)
- Screenshots on failure: `test-results/screenshots/`
- Step logs: embedded in HTML report + console `[STEP START/PASS]`
- File log: `logs/automation.log`

### ReportPortal integration

| Item | Behavior |
|------|----------|
| Auto-enable | `RP_API_KEY` in `.env` + **real test run** (not `--collect-only` / IDE discovery) |
| Skip RP | `--no-reportportal` or no `RP_API_KEY` — log: `ReportPortal SKIPPED: <reason>` |
| Enabled log | `ReportPortal ENABLED: efms-automation (test execution with RP_API_KEY)` |
| Early load | Root `conftest.py` → `pytest_load_initial_conftests` |
| Config hook | `tests/conftest_reportportal.py` → detect app → inject ini |
| App detection | `-m efms` / `-m etms` → marker; `tests/efms/` path → efms; collected test markers → fallback |
| Launch name | eFMS only → `efms-automation`; eTMS only → `etms-automation` |
| No combined launch | Do **not** use `efms-etms-automation` — run apps separately: `pytest -m efms` / `pytest -m etms` |
| Mixed suite | `pytest` without app filter → RP disabled + warning in log |
| Display name | `{test_case_id} - {description}` from JSON via `@pytest.mark.name` |
| Step logs | `log_step_lines()` → ReportPortal on test finish |
| Failure screenshot | `attach_failure_screenshot()` → full-page PNG |
| Test retry | `pytest-rerunfailures` — default **1** retry via `TEST_RERUNS`; pytest logs every attempt, ReportPortal only final pass/fail |
| Secret redaction | `secret_redaction.sanitize_test_report()` + `apply_reportportal_patches()` — che password trong traceback/HTML/ReportPortal |
| View results | `{RP_ENDPOINT}/ui/#{RP_PROJECT}/launches/all` |

**Env vars (per-app launches only):**

| Variable | Default | When used |
|----------|---------|-----------|
| `RP_LAUNCH_EFMS` | `efms-automation` | `pytest -m efms` or `tests/efms/` |
| `RP_LAUNCH_ETMS` | `etms-automation` | `pytest -m etms` or `tests/etms/` |
| `RP_LAUNCH_DESCRIPTION_EFMS` | eFMS UI automation | eFMS launch |
| `RP_LAUNCH_DESCRIPTION_ETMS` | eTMS UI automation | eTMS launch |

**Dashboard tip:** Filter launch name `efms-automation` vs `etms-automation`, or filter test attribute `Application:efms` / `Application:etms`.

### Test retry (pytest-rerunfailures)

| Item | Behavior |
|------|----------|
| Default | `TEST_RERUNS=1`, `TEST_RERUNS_DELAY=2` in `.env` (via `settings.test_reruns`) |
| Configure | `tests/conftest_reportportal.py` → `configure_pytest_reruns()` in `pytest_configure` |
| Pytest terminal | Both attempts logged — `[RERUN attempt N]` then `[PASSED]` / `[FAILED]` |
| ReportPortal | `apply_reportportal_patches()` skips `outcome=="rerun"` — portal shows **one** test with final status |
| Disable | `TEST_RERUNS=0` or CLI `--reruns 0` |
| Override | CLI `--reruns N --reruns-delay S` overrides `.env` if passed explicitly |

### Secret redaction (passwords in failure output)

| Item | Behavior |
|------|----------|
| Problem | Pytest in fixture/locals khi test fail: `efms_account_password = '...'` |
| Module | `src/automation/config/secret_redaction.py` — `redact_secrets()`, `sanitize_test_report()` |
| Pytest HTML | `tests/conftest.py` → `pytest_runtest_makereport` gọi `sanitize_test_report()` khi failed |
| ReportPortal | `reportportal_support.apply_reportportal_patches()` patch `process_results` + `post_log` |
| Password source | Vẫn đọc từ `.env` (`EFMS_ACCOUNT_PASSWORD`) — chỉ **che output lỗi**, không hardcode |
| Pattern che | `efms_account_password`, `etms_account_password`, `password = '...'`, `EFMS_ACCOUNT_PASSWORD=...` |

> **Không** log password trong step logger. Fixture password là `str` thuần từ `.env`; đổi pass trong `.env` không cần sửa code.

```bash
# Default: 1 retry from .env
uv run pytest -m efms --browser chrome --browser-headless true

# Override retry count
uv run pytest -m efms --reruns 2 --reruns-delay 3 --browser chrome --browser-headless true
```

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
# Local without ReportPortal (even when RP_API_KEY is in .env)
uv run pytest tests/etms/ -m etms -v --no-reportportal

# Local with ReportPortal (auto when RP_API_KEY set)
uv run pytest tests/etms/ -m etms -v

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

### 12.1 CI/CD Pipeline (GitHub Actions + Jenkins)

> **Step-by-step setup:** follow the checklist below. Shared test script: `scripts/ci-run-tests.sh`.

#### CI/CD architecture

```
Push / PR / Manual trigger
        │
        ├─► GitHub Actions (.github/workflows/ci.yml)
        │     Job 1: quality  → ruff + pyright (every push/PR)
        │     Job 2: ui-tests → Playwright + pytest (push main + manual)
        │
        └─► Jenkins (Jenkinsfile)
              Checkout → Install → Quality → Run Tests → Archive artifacts
```

#### Step 1 — Prerequisites (both platforms)

| Requirement | Notes |
|-------------|-------|
| Python 3.12+ | GitHub Actions: `astral-sh/setup-uv@v5` |
| `uv` | Installed in CI automatically |
| Linux agent | Playwright `--with-deps` needs Ubuntu/Debian (Jenkins agent or `ubuntu-latest`) |
| UAT reachable | CI runner must reach `EFMS_BASE_URL` / `ETMS_BASE_URL` |
| Credentials | Username + password per app — **never commit** |

#### Step 2 — GitHub Actions setup

1. **Files in repo** (already committed):
   - `.github/workflows/ci.yml` — pipeline definition
   - `scripts/ci-run-tests.sh` — shared pytest runner

2. **Add repository secrets** (GitHub → Settings → Secrets and variables → Actions):

| Secret | Required | Description |
|--------|----------|-------------|
| `EFMS_ACCOUNT_USERNAME` | Yes (for eFMS runs) | eFMS login user |
| `EFMS_ACCOUNT_PASSWORD` | Yes | eFMS login password |
| `ETMS_ACCOUNT_USERNAME` | Yes (for eTMS runs) | eTMS login user |
| `ETMS_ACCOUNT_PASSWORD` | Yes | eTMS login password |
| `RP_API_KEY` | No | ReportPortal — auto-enables when set |
| `RP_ENDPOINT` | No | e.g. `http://your-rp-server:8080` |
| `RP_PROJECT` | No | e.g. `automation-techub` |

3. **Trigger behavior:**

| Event | What runs |
|-------|-----------|
| Pull Request | **quality** only (lint + typecheck) |
| Push to `main` | quality + **ui-tests** (default: `APP=efms`, `MARKER=critical`) |
| Manual (`workflow_dispatch`) | Choose APP, MARKER, BROWSER, HEADLESS |

4. **Manual run:** GitHub → Actions → **CI** → Run workflow.

5. **Download report:** Actions run → Artifacts → `pytest-report-{app}-{marker}`.

#### Step 3 — Jenkins setup

1. **Create Pipeline job** → Pipeline script from SCM → point to repo `Jenkinsfile`.

2. **Add credentials** (Manage Jenkins → Credentials):

| Credential ID | Type | Maps to |
|---------------|------|---------|
| `automation-efms-account-password` | Secret text | `EFMS_ACCOUNT_PASSWORD` |
| `automation-etms-account-password` | Secret text | `ETMS_ACCOUNT_PASSWORD` |

3. **Pipeline parameters** (build with parameters):

| Parameter | Choices | Purpose |
|-----------|---------|---------|
| `ENV` | UAT | Target environment |
| `APP` | efms, etms, all | Application filter |
| `BROWSER` | chrome, edge | Browser channel |
| `HEADLESS` | true, false | Headless mode |
| `MARKER` | critical, high, login, navigation, smoke, regression, **efms**, **etms** | Pytest filter |
| `EFMS_ACCOUNT_USERNAME` | string | eFMS user (default `QCTest`) |
| `ETMS_ACCOUNT_USERNAME` | string | eTMS user |
| `PYTEST_ARGS` | string | Extra args |

4. **Stages:** Checkout → Install (`uv sync`, Playwright) → Quality → Run Tests → Archive artifacts.

5. **Artifacts:** `reports/`, `test-results/`, `logs/` — download from Jenkins build page.

#### Step 4 — Marker + app matrix (how pytest is invoked)

Script `scripts/ci-run-tests.sh` builds the marker expression:

| APP | MARKER | pytest filter |
|-----|--------|---------------|
| `efms` | `critical` | `-m "critical and efms"` |
| `efms` | `efms` | `-m efms` (full eFMS suite) |
| `etms` | `high` | `-m "high and etms"` |
| `all` | `login` | `-m login` (both apps) |

Always passes: `--browser {BROWSER} --browser-headless {HEADLESS} --html=reports/report.html`.

**ReportPortal in CI:** set `RP_API_KEY` (+ endpoint/project) in GitHub Secrets or Jenkins env → launch `efms-automation` / `etms-automation` per Section 11.

#### Step 5 — Recommended CI schedules

| Pipeline | When | Suggested params |
|----------|------|------------------|
| Smoke (fast) | Every PR | quality only (automatic) |
| Critical | Push main / nightly | `APP=efms`, `MARKER=critical` |
| Regression | Weekly manual | `APP=efms`, `MARKER=regression`, `HEADLESS=true` |
| Full eFMS | Before release | `APP=efms`, `MARKER=efms` |
| eTMS smoke | After eTMS changes | `APP=etms`, `MARKER=etms` |

#### Step 6 — Verify CI locally (same as pipeline)

```bash
# Quality gate (matches CI job 1)
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pyright

# UI tests (matches CI job 2 / Jenkins)
export APP=efms MARKER=critical BROWSER=chrome HEADLESS=true
export EFMS_ACCOUNT_USERNAME=QCTest EFMS_ACCOUNT_PASSWORD=***
bash scripts/ci-run-tests.sh
```

#### Step 7 — Troubleshooting

| Symptom | Fix |
|---------|-----|
| Login tests skipped | Set `EFMS_ACCOUNT_PASSWORD` / `ETMS_ACCOUNT_PASSWORD` in CI secrets |
| Headless sidebar fail | CI uses `HEADLESS=true` + viewport 1920×1080 in `conftest.py` |
| Playwright browser missing | Run `uv run playwright install --with-deps chrome` in Install stage |
| ReportPortal 3 launches | Run `-m efms` or `-m etms` separately — Section 11 |
| Jenkins `sh` fails on Windows agent | Use Linux agent label or convert script to PowerShell |

**Parallel execution (optional, dev deps):**

```bash
uv run pytest -m "critical and efms" -n auto --browser chrome --browser-headless true
# Retry is enabled by default (TEST_RERUNS=1); override with --reruns if needed
uv run pytest -m efms --reruns 2 --reruns-delay 3 --browser chrome --browser-headless true
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

### Example B — eTMS Auth (Login + Branch) ✅ CANONICAL

**Test data** — `tests/testdata/dataTest-etms.json`:
```json
{
    "test_smk_auth_001_login_success_etms": [
        {
            "test_case_id": "SMK_AUTH_001",
            "description": "Login eTMS successfully",
            "module": "Login",
            "priority": "critical",
            "preconditions": "User active"
        }
    ],
    "test_smk_auth_002_select_branch_etms": [
        {
            "test_case_id": "SMK_AUTH_002",
            "description": "Select Branch/Hub VNHCM successfully",
            "module": "Login",
            "priority": "critical",
            "preconditions": "Login success",
            "branch": "VNHCM",
            "expected_url_contains": "app/default/home"
        }
    ]
}
```

**Page objects:**
- `EtmsLoginPage` — login form + branch picker (`NgSelectComponent` for `ng-select`)
- `EtmsHomePage` — verify home URL + dashboard after branch select

**Test file** — `tests/etms/test_etms_auth.py`:
```python
import pytest

from automation.config import settings
from tests.data_provider import DataProvider


@pytest.mark.login
@pytest.mark.etms
class TestEtmsAuth:
    @pytest.mark.parametrize(
        "data", DataProvider.etms_cases("test_smk_auth_001_login_success_etms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_001")
    def test_smk_auth_001_login_success_etms(self, pages, data, etms_account_password):
        # Step 1: Open Login Page
        pages.etms_login_page.open()
        # Step 2–4: Enter credentials and login
        pages.etms_login_page.enter_username(settings.etms_username)
        pages.etms_login_page.enter_password(etms_account_password)
        pages.etms_login_page.click_login()
        # Expected: Branch/Hub selection screen
        assert pages.etms_login_page.is_branch_hub_selection_displayed()

    @pytest.mark.parametrize(
        "data", DataProvider.etms_cases("test_smk_auth_002_select_branch_etms"),
    )
    @pytest.mark.tc_id("SMK_AUTH_002")
    def test_smk_auth_002_select_branch_etms(self, pages, data, etms_account_password):
        pages.etms_login_page.open().login(
            settings.etms_username,
            etms_account_password,
        )
        assert pages.etms_login_page.is_branch_hub_selection_displayed()
        pages.etms_login_page.select_branch(data["branch"])
        assert pages.etms_login_page.is_branch_selected(data["branch"])
        pages.etms_login_page.click_select_branch()
        assert pages.etms_home_page.is_home_url(data["expected_url_contains"])
        assert pages.etms_home_page.is_dashboard_displayed()
```

**Run:**
```bash
uv run pytest tests/etms/test_etms_auth.py -v \
  --browser chrome --browser-headless false -m etms --reportportal
```

> **Branch verify:** UI hiển thị tên tiếng Việt (vd. "Hồ Chí Minh"), không phải mã `VNHCM`. Dùng `_branch_display_hints` + `text_utils.text_contains_any()` trong `EtmsLoginPage`.

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
        settings.efms_username,
        efms_account_password,
        data["company"],
    )

    error = pages.efms_login_page.get_login_error()
    assert data["expected_error"] in error
```

---

### Example E — eTMS Data-Driven Auth ✅ IMPLEMENTED (same as Example B)

Use `TestEtmsAuth` + JSON keys `test_smk_auth_001_login_success_etms` / `test_smk_auth_002_select_branch_etms`.  
**Removed:** `test_etms_login.py`, `ETMS-LOGIN-001`, login logic on `EtmsHomePage`.

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
        settings.efms_username,
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
| 5 | `dataTest-etms.json` wrong key / hardcoded password | DataProvider fails or security risk | **Fixed** — keys `test_smk_auth_*`; no credentials in JSON |
| 6 | `open_url()` settle wait + reload | Every navigation is slow | Tune via `settings.open_url_settle_ms` — do not hardcode ms |
| 7 | Jenkins `MARKER` dropdown missing `critical`/`navigation` | CI cannot select by priority from UI | **Fixed** — MARKER includes critical, high, navigation |
| 8 | `EfmsNavigationPage` removed | Old docs reference deleted class | Use module-specific pages under `commercial/`, `logistics/`, `services/` |
| 9 | Commercial scenarios without dashboard reset | Booking Receipt fails after Work Order | `goto #/home` between commercial scenarios (index > 0) |
| 10 | Services pages — datatable không phù hợp | Table-based verify fails | `ShipmentListComponent` + `shipment-item-wrapper` via `EfmsNavigateVerifyMixin` (Section 5.12) |
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

- [x] **Fix `dataTest-etms.json`** — SMK_AUTH_001/002 keys, no hardcoded password, `priority: critical`
- [x] **Migrate eTMS auth** — `TestEtmsAuth`, `EtmsLoginPage`, branch flow via `NgSelectComponent`
- [x] **COR_LP_001 Cost Of Route** — `TestEtmsCostOfRoute`, `EtmsCostOfRoutePage`, `login_etms` fixture
- [x] **Common Components layer** — `pages/common/` (ng-select, native select, SweetAlert)
- [x] **Utils layer** — `utils/text_utils.py` (`normalize_text`, `text_contains_any`)
- [x] **HTML Base URL metadata** — `metadata_support.py` picks eFMS vs eTMS URL per run
- [x] **Migrate login tests** to `DataProvider.*_cases()` + product password fixtures
- [x] **ReportPortal integration** — auto-enable, display names, per-app launches
- [x] **Update Jenkinsfile** — add `critical`, `navigation`, `high` to MARKER choices
- [ ] **Add API/DB layers** when first API or DB test is required (not scaffolded in repo)
- [x] **Restructure tests** — `tests/ui/{app}/` → `tests/{app}/` (app-first layout)
- [x] **Update README** to match current structure

### P2 — Medium (developer experience)

- [ ] **Playwright trace on failure** (optional — add `trace_dir` to settings when needed)
- [x] **Shared `conftest.py` per app** (`tests/efms/conftest.py`, `tests/etms/conftest.py`) for login precondition fixture
- [ ] **Extract `MENU_ACTIONS` dicts** to shared module if duplicated across new nav tests
- [ ] **AGENTS.md** reference to this `ruleAi.md`
- [ ] **Migrate Booking Receipt** — inline ng-select/swal → `NgSelectComponent` / `SwalModalComponent` when touching that page
- [ ] **Tighten fallback selectors** — remove overly broad `input[type='text']` where possible

### P3 — Low (nice to have)

- [ ] **Configure `pytest-xdist`** in Jenkins for parallel UI runs (careful: shared UAT env)
- [x] **Configure `pytest-rerunfailures`** — default 1 retry; ReportPortal final result only
- [x] **Secret redaction** — che password trong pytest/HTML/ReportPortal failure logs
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
2. Search Common Components→ src/automation/pages/common/  (ng-select, swal, native select)
3. Search Utils            → src/automation/utils/  (pure helpers — no Playwright)
4. Search BasePage         → src/automation/pages/base_page.py
5. Search PageManager      → src/automation/pages/page_manager.py
6. Search existing tests   → tests/{app}/  (see how similar flows are done)
7. Search fixtures         → tests/conftest.py
8. Search reporting/config → src/automation/{reporting,config}/  (metadata_support, secret_redaction, RP)
9. Search test data        → tests/testdata/dataTest-{app}.json
```

**Only after steps 1–9 return no match** → write a new method or file.

### 16.2 Where to look (reuse map)

| Need | Search here first | Reuse example |
|------|-------------------|---------------|
| Login (eFMS) | `EfmsLoginPage` | `open()`, `login()`, `NativeSelectComponent` for company |
| Login (eTMS) | `EtmsLoginPage` | `open()`, `login()`, `select_branch()`, `NgSelectComponent` |
| eTMS home | `EtmsHomePage` | `is_dashboard_displayed()`, `is_home_url()` |
| Cost Of Route (eTMS) | `EtmsCostOfRoutePage` | `open_via_menu_search()`, `choose_route()`, `fill_route_mapping_fields()`, `delete_cost_of_route()` |
| ng-select dropdown | `NgSelectComponent` | `select_option_by_text()`, `get_selected_text()` |
| HTML `<select>` | `NativeSelectComponent` | `select_by_label()` |
| SweetAlert2 popup | `SwalModalComponent` | `click_confirm()`, `is_message_visible()` |
| Text matching (branch labels) | `utils/text_utils.py` | `normalize_text()`, `text_contains_any()` |
| Logout / dashboard (eFMS) | `EfmsHomePage` | `is_dashboard_displayed()`, `wait_for_dashboard_ready()`, `click_logout()` |
| Commercial navigation | `EfmsAgentPage`, `EfmsCustomerPage`, … | `click_*_menu()`, `is_*_displayed()` — extend `EfmsCommercialMenuPage` |
| Commercial menu base | `commercial_menu_page.py` | `open_commercial_menu()`, `wait_for_sidebar_ready()` — extend, do not duplicate |
| Logistics navigation | `EfmsJobManagementPage`, `EfmsCustomClearancePage`, `EfmsTruckingInlandPage` | Same pattern — extend `EfmsLogisticsMenuPage` |
| Logistics menu base | `logistics_menu_page.py` | `open_logistics_menu()` — extend, do not duplicate |
| Services navigation | `EfmsServicesDocumentationPage` | All 8 doc pages — extend `EfmsServicesMenuPage` |
| Services menu base | `services_menu_page.py` | `open_services_menu()` — extend, do not duplicate |
| Wait for element | `BasePage` | `wait_for_visible()`, `wait_for_page_stable()`, `wait_for_dom_content_loaded()` |
| Open URL + reload | `BasePage` | `open_url()` — tune `open_url_settle_ms`, do not copy wait logic |
| Credentials | `conftest.py` + `settings` | `efms_account_password` / `etms_account_password`, `settings.efms_username` |
| Test data loading | `DataProvider` | `DataProvider.efms_cases("test_...")` / `etms_cases("test_...")` |
| Step logging | `step_logger.py` | `@log_method` decorator |
| Page access in test | `PageManager` | `pages.efms_login_page`, `pages.etms_login_page`, `pages.etms_home_page`, … |

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
| Similar widget on 2+ pages (ng-select, swal) | Extend or use existing class in `pages/common/` — do not copy-paste open/click/wait |
| Text normalize / hint matching | `utils/text_utils.py` — not inline in Page Object unless one-off |
| Same JSON company / metadata | Reuse existing JSON fields — do not duplicate rows with identical data |

### 16.4 Anti-patterns (DO NOT)

```python
# WRONG — duplicate ng-select open/option/close logic in every Page Object
def select_branch(self, code):
    self.page.locator("ng-select").click()
    self.page.locator(".ng-option").filter(has_text=code).click()

# CORRECT — compose NgSelectComponent (Section 7.1)
def select_branch(self, code):
    self._branch_select.select_option_by_text(code)
    return self
```

```python
# WRONG — put Playwright locators in utils/
# utils/dropdown_utils.py with page.locator(...)

# CORRECT — utils are pure Python only
from automation.utils.text_utils import text_contains_any
```

```python
# WRONG — register NgSelectComponent in PageManager
@property
def branch_select(self) -> NgSelectComponent: ...

# CORRECT — private @property on Page Object, compose internally
```

```python
# WRONG — duplicate login logic in test instead of reusing login()
def test_nav(pages, data, efms_account_password):
    pages.efms_login_page.open()
    pages.efms_login_page.enter_username(settings.efms_username)
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

> **Start with [Section 0](#0-ai-master-playbook--read-this-first)** — then verify every item below before finishing.

Before finishing any automation task, verify:

```
[ ] Read Section 0 — classified test type (A–F) and followed 8-step pipeline
[ ] Searched existing Page Objects / BasePage / fixtures — reused before creating (Section 16)
[ ] No hard-coded waits — all timing from settings or condition-based waits (Section 3.6)
[ ] Dashboard verify uses dashboard_ready_selectors (headless-safe), not h3 is_visible alone
[ ] Searched pages/common/ + utils/ before adding widget or text logic (Section 7.1, 16.1)
[ ] ng-select / native select / SweetAlert use Common Components — not duplicated inline
[ ] utils/ has no Playwright imports — pure helpers only
[ ] Login on EfmsLoginPage / EtmsLoginPage — dashboard on EfmsHomePage / EtmsHomePage
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
[ ] ReportPortal: run with `-m efms` or `-m etms` — not mixed full suite without app filter
[ ] Delivered: JSON + POM + test + run command (Section 0.6 response format)
[ ] Assertions only in tests with descriptive messages — not business assert in Page Objects (Section 3.7)
[ ] Unique create data generated at runtime — not hardcoded (Section 3.8)
[ ] New locators verified on live DOM — checklist Section 3.9
[ ] Headed debug first; headless only after stable (Section 3.10)
[ ] No debug prints / probe scripts left behind (Section 3.11)
[ ] Navigate list pages use EfmsNavigateVerifyMixin — grid rows or shipment items, not title-only (Section 5.12)
[ ] Flaky fix: classified root cause (Section 18) — verified 5+ headed + 1 headless run
[ ] BR/grid delete uses stable helper chain — not raw click_delete (Section 18.10)
```

---

## 18. Flaky Test Diagnosis & Fix

> **Purpose:** Adapted from NBR/ExtJS flaky-test-analyzer skill — mapped to **Angular/eFMS/eTMS** patterns in this repo. Full Cursor skill: `.cursor/skills/flaky-test-analyzer/SKILL.md`.

### 18.1 When to use

- Test passes and fails intermittently
- CI results inconsistent; local headed pass / headless fail (or reverse)
- Test fails only when another test runs first (ordering dependency)
- **Run FAIL, debug step-by-step PASS** — classic race condition

### 18.2 Analysis workflow

| Step | Action |
|------|--------|
| 1 Reproduce | Headed first: `--browser-headless false` (Section 3.10) |
| 2 Inspect | Stack trace, `test-results/screenshots/`, pytest-html |
| 3 Classify | Match category in 18.3 (Angular — not ExtJS `x-mask` / `set_combo`) |
| 4 Fix | Reuse existing Page Object helpers — do not invent parallel patterns |
| 5 Verify | **5+ consecutive** headed runs, then **≥1** headless run |

```bash
uv run pytest tests/efms/test_efms_navigate.py -m navigation -v --browser chrome --browser-headless false
```

CI safety net: `TEST_RERUNS=1` (default) via `pytest-rerunfailures` — fixes must not rely on reruns alone.

### 18.3 Root cause categories (eFMS/eTMS)

| # | Category | Symptom | Fix (this repo) |
|---|----------|---------|-----------------|
| 1 | Unstable locator | StrictMode / timeout xen kẽ | Section 3.4 priority; no `#mat-input-N`, no positional XPath |
| 2 | Hard waits | Pass local, fail CI | `settings.*_timeout` / `*_ms` — no `time.sleep()`, no literal ms |
| 3 | Grid not ready | Title OK, 0 data rows | `ListGridComponent.wait_until_ready()` + `wait_for_data_rows()` |
| 4 | ng-select misfire | Value visible, form unchanged | `NgSelectComponent.select_option_by_text()` |
| 5 | Block UI overlay | Click intercepted | Wait `.block-ui-active` gone; `_wait_for_grid_ready()` |
| 6 | SPA route race | Assert before hash changes | `wait_for_url` + `wait_for_page_stable()` |
| 7 | Headless title trap | h3 exists, `is_visible()` False | `dashboard_ready_selectors` + `inner_text()` (Issue #1) |
| 8 | Commercial menu state | BR fails after WO in same class | `goto_dashboard` between scenarios (Issue #9) |
| 9 | Services wrong widget | Table verify on card layout | `ShipmentListComponent` + `shipment-item-wrapper` |
| 10 | Grid delete race | Delete popup/API/grid stale | `delete_booking_receipt_from_grid()` — Section 5.13 |
| 11 | Test data conflict | Fail in suite, pass alone | Runtime `uuid` / `timestamp` (Section 3.8) |
| 12 | Stale element | Detached from DOM | Locators only — re-query after navigation |

**NBR/ExtJS patterns — do NOT port:**

| NBR (ExtJS) | eFMS/eTMS equivalent |
|-------------|----------------------|
| `x-mask`, `Ext.ComponentQuery` | `.m-blockui`, `.block-ui-active`, `wait_for_function` |
| `set_combo()` / `fill_visible()` | `NgSelectComponent`, `NativeSelectComponent` |
| Bounding-rect `.x-grid-cell-inner` | `ListGridComponent.wait_for_data_rows()` |
| `config/timeouts.py` tiers | `settings.browser_timeout`, `page_load_timeout`, `*_ms` keys |
| Allure `@allure.step` | `@log_method` + pytest-html + ReportPortal |
| Session autouse cleanup | Per-suite pattern — add when CRUD leaves UAT data |

### 18.4 Locator fix quick reference

| Element | Correct pattern |
|---------|-----------------|
| Button | `xpath=//button[contains(.,'Label')]` + `.first` if needed |
| Grid row by text | `xpath=//tr[contains(@class,'datatable')]//span[normalize-space()='{value}']` |
| Grid data ready | `ListGridComponent.wait_for_data_rows(min_rows=1)` |
| ng-select | `NgSelectComponent.select_option_by_text()` |
| Native `<select>` | `NativeSelectComponent.select_by_label()` |
| SweetAlert | `SwalModalComponent.click_confirm()` |
| Services card | `div[@class='shipment-item-wrapper']` via `ShipmentListComponent` |

### 18.5 Stability checklist (after fix)

```
[ ] Locator stable — Section 3.9 verified on live DOM
[ ] No time.sleep() / literal wait_for_timeout(ms)
[ ] Grid navigate: column headers + data rows (or shipment items)
[ ] Headless: 1920×1080 viewport + dashboard_ready_selectors
[ ] Commercial multi-scenario: dashboard reset between items
[ ] BR delete: delete_booking_receipt_from_grid() full chain
[ ] Unique runtime test data for creates
[ ] 5+ consecutive headed passes + 1+ headless pass
```

---

## 19. Framework Architect Quick Reference

> **Purpose:** Condensed scaffold guide — full skill: `.cursor/skills/framework-architect/SKILL.md`. **Source of truth remains `ruleAi.md`.**

### 19.1 Fixed stack

Python 3.12+ · `playwright.sync_api` · pytest · pytest-html · ReportPortal · Pydantic `settings` · JSON `DataProvider` · **no** Allure · **no** `infra/` unless requested.

### 19.2 Layer map

```text
Test (assertions) → pages fixture → PageManager → {App}Page → Common Components → BasePage → Playwright
Pure helpers: src/automation/utils/ (no Playwright imports)
```

### 19.3 New module checklist

1. `tests/{app}/test_{app}_{module}.py` + JSON key = function name
2. Page Object under `src/automation/pages/{app}/` — extend menu base when applicable
3. Register in `PageManager` if new page class
4. Markers: `@pytest.mark.efms` / `etms` + priority from JSON or `@pytest.mark.smoke`
5. Login precondition: `login_efms` fixture or explicit login in test
6. List navigate: extend menu page + `EfmsNavigateVerifyMixin`
7. Widgets: compose `NgSelectComponent`, `SwalModalComponent`, `ListGridComponent` — no inline duplicate
8. Run command documented in test docstring or PR

### 19.4 Anti-patterns (forbidden)

| Forbidden | Use instead |
|-----------|-------------|
| `page.locator()` in tests | `pages` → Page Object method |
| Assertions in Page Objects | `bool` return + `assert` in test |
| Title-only navigate verify | Grid rows / shipment items (Section 5.12) |
| Raw BR delete clicks | `delete_booking_receipt_from_grid()` |
| Hardcoded credentials / URLs | `settings` + `.env` |
| `time.sleep()` | Condition waits (Section 3.6) |

---

## Appendix B — Cursor Rules (`.cursor/rules/`)

Project AI rules are maintained in **`ruleAi.md`** (this file). For Cursor IDE, scoped rules mirror key sections:

| File | Scope | Content |
|------|-------|---------|
| `efms-playwright-waits.mdc` | `src/automation/pages/**/*.py`, `tests/**/*.py` | Wait strategy, no sleep, grid/delete race conditions |
| `efms-booking-receipt-xpath.mdc` | `**/efms_booking_receipt*.py` | XPath catalog Section 5.14, delete flow Section 5.13 |
| `locator-strategy.mdc` | `src/automation/pages/**/*.py` | Locator priority, forbidden patterns, verify checklist (Section 3.9) |
| `qa-general.mdc` | `tests/**/*.py`, `src/automation/**/*.py` | POM layers, assertions, test data, code quality (Sections 3.7–3.11) |
| `flaky-test-analyzer.mdc` | `tests/**/*.py`, `pages/**/*.py` | Flaky diagnosis quick reference (Section 18) |

**Cursor skills** (`.cursor/skills/`):

| Skill | Purpose |
|-------|---------|
| `flaky-test-analyzer/SKILL.md` | Full flaky workflow + Angular root causes |
| `framework-architect/SKILL.md` | Scaffold POM, fixtures, compliance checklist |

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
| `RP_VERIFY_SSL` | `false` | SSL verify for local Docker |
| `RP_LAUNCH_EFMS` | `efms-automation` | Launch when running eFMS only (`pytest -m efms`) |
| `RP_LAUNCH_ETMS` | `etms-automation` | Launch when running eTMS only (`pytest -m etms`) |
| `RP_LAUNCH_DESCRIPTION_EFMS` | eFMS UI automation | eFMS launch description |
| `RP_LAUNCH_DESCRIPTION_ETMS` | eTMS UI automation | eTMS launch description |

### Test retry

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_RERUNS` | `1` | Số lần chạy lại test failed (pytest-rerunfailures) |
| `TEST_RERUNS_DELAY` | `2` | Delay (giây) giữa các lần retry |

> **ReportPortal retry:** Lần fail trung gian (`outcome=rerun`) không gửi lên portal — chỉ kết quả lần chạy cuối. Pytest terminal/HTML vẫn ghi đủ 2 lần.

> **Secret redaction:** Traceback/ReportPortal hiển thị `efms_account_password = '***'`, không lộ giá trị từ `.env`.

> **Removed:** `RP_LAUNCH` / `RP_LAUNCH_DESCRIPTION` combined launch — always run eFMS and eTMS separately for correct ReportPortal dashboards.

**View launches:** `{RP_ENDPOINT}/ui/#{RP_PROJECT}/launches/all`

---

*Last updated: 2026-06-16 | POM: pages/common + utils | eTMS: TestEtmsAuth + COR_LP_001 | HTML Base URL: metadata_support.py | Retry + secret redaction*
