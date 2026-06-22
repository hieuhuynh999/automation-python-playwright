---
name: framework-architect
description: Thiết kế và scaffold framework automation eFMS/eTMS — Python 3.12+, playwright.sync_api, pytest, pytest-html, ReportPortal, Angular UI. Scaffold test package, Page Object, review compliance với ruleAi.md.
---

# Framework Architect — eFMS/eTMS Automation

## Mô tả

Skill scaffold và duy trì framework automation eFMS/eTMS: Python/Playwright/pytest cho Angular web UI (PrimeNG, ng-select, SweetAlert2).

Agent có thể:
- Scaffold test package mới (`conftest.py`, test files)
- Tạo Page Object theo pattern menu base + feature page
- Review compliance với `ruleAi.md`
- Thiết kế module theo POM và pattern đã có

**Source of truth:** `ruleAi.md` — skill này bị override khi conflict.

---

## Khi nào dùng

- Scaffold test package / module mới
- Thêm Page Object class
- Review framework compliance
- Giải thích kiến trúc project

---

## Stack cố định — Không đổi

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Browser | `playwright.sync_api` — **không** `pytest-playwright` async |
| Test runner | `pytest` |
| HTML report | `pytest-html` |
| Portal | `pytest-reportportal` |
| Config | Pydantic `settings.py` + `.env` |
| Test data | JSON + `DataProvider` + `Faker` / `uuid` / `datetime` |
| Retry | `pytest-rerunfailures` (`TEST_RERUNS` default 1) |
| Lint | theo repo (nếu có) |

**Chưa implement:** Allure, `infra/` API clients, DB layer — không scaffold trừ khi user yêu cầu.

---

## Cấu trúc project (canonical)

```text
project-root/
├── ruleAi.md                         ← source of truth
├── .cursor/
│   ├── rules/*.mdc                   ← scoped AI rules
│   └── skills/                       ← flaky-test-analyzer, framework-architect
├── src/automation/
│   ├── config/settings.py            ← credentials via .env (Pydantic)
│   ├── pages/
│   │   ├── base_page.py              ← wait_for_visible, click_when_ready, open_url
│   │   ├── page_manager.py           ← pages fixture entry
│   │   ├── common/                   ← NgSelect, NativeSelect, Swal, ListGrid, ShipmentList
│   │   ├── efms/
│   │   │   ├── commercial/           ← menu base + feature pages
│   │   │   ├── logistics/
│   │   │   ├── services/
│   │   │   └── efms_navigate_verify_mixin.py
│   │   └── etms/
│   ├── utils/                        ← pure helpers — NO Playwright imports
│   └── reporting/                    ← secret redaction, metadata
├── tests/
│   ├── conftest.py                   ← browser, viewport headless, screenshot on fail
│   ├── data_provider.py
│   ├── testdata/dataTest-{app}.json
│   ├── efms/conftest.py              ← login_efms fixture
│   └── efms/test_*.py
├── pyproject.toml
└── .env.example
```

---

## Trách nhiệm từng layer

### `src/automation/pages/`
- Locators (`*_selectors`), UI actions, navigation
- **Không:** assertions business, test data generation, infra API

### `tests/`
- Assertions, orchestration, `# Step N` comments
- **Không:** `page.locator()` trực tiếp, locators

### `src/automation/utils/`
- Pure helpers (text normalize, date, file)
- **Không:** import Playwright

### `tests/conftest.py` + `tests/{app}/conftest.py`
- Browser factory, credentials fixtures, app login preconditions

---

## PageManager & Fixture Pattern

```python
# Test — luôn dùng pages fixture
def test_smk_nav_001(pages, login_efms):
    assert pages.efms_agent_page.click_agent_menu()
    assert pages.efms_agent_page.is_agent_list_displayed()
```

```python
# tests/efms/conftest.py
@pytest.fixture
def login_efms(pages, efms_account_password):
    pages.efms_login_page.open().login(...)
    assert pages.efms_home_page.is_dashboard_displayed()
```

Fixture scope:
| Scope | Dùng khi |
|---|---|
| `function` | Mặc định — fresh state mỗi test |
| `class` | CRUD ordered suite chia sẻ `booking_no` (TestEfmsBookingReceipt) |
| `module` | Ít dùng — cân nhắc state leak |

---

## BasePage Contract

Tất cả Page Object kế thừa `BasePage`:

| Method | Mục đích |
|--------|----------|
| `wait_for_visible(selectors, name, timeout=settings.browser_timeout)` | Chờ element xuất hiện |
| `click_when_ready(selectors, name)` | Visible + enabled → click |
| `wait_for_page_stable()` | readyState + `navigation_settle_ms` |
| `open_url(path)` | goto + `open_url_settle_ms` |

Widget-specific → **Common Components** (compose, không duplicate):
- `NgSelectComponent`, `NativeSelectComponent`, `SwalModalComponent`
- `ListGridComponent`, `ShipmentListComponent`

---

## Angular Patterns (critical)

### 1. ng-select
```python
self.ng_select.select_option_by_text("Field label", value)
# Never: raw click on .ng-option
```

### 2. Grid / Datatable
```python
self.list_grid.wait_until_ready()
self.list_grid.wait_for_data_rows(min_rows=1)
```

### 3. Navigate verify
```python
# Commercial / Logistics — extend EfmsNavigateVerifyMixin
self._verify_list_page_displayed(column_headers=[...])

# Services — shipment cards
self._verify_shipment_page_displayed()
```

### 4. SweetAlert
```python
self.swal.click_confirm()
self.swal.is_message_visible("Success")
```

### 5. Block UI
Chờ `.block-ui-active` gone trước interaction — hoặc `_wait_for_grid_ready()`.

---

## Locator Strategy (priority)

1. `data-testid` → `id` → `name` → `aria-label`
2. XPath text: `normalize-space(.)`, `contains(@class, ...)`
3. `contains()` class — chỉ khi stable
4. **Forbidden:** positional XPath, dynamic `_ngcontent-*`, `nth-child` không document

Chi tiết: `ruleAi.md` Section 3.4, `.cursor/rules/locator-strategy.mdc`

---

## Wait Strategy

| Tình huống | Pattern |
|---|---|
| Element visible | `wait_for_visible()` |
| URL / hash route | `page.wait_for_url(..., timeout=settings.page_load_timeout)` |
| DOM condition | `page.wait_for_function()` |
| Post navigation | `wait_for_page_stable()` |
| Grid ready | `ListGridComponent.wait_until_ready()` |
| Delete API | `expect_response` + toast + `wait_until_booking_absent` |

**Forbidden:** `time.sleep()`, literal `wait_for_timeout(5000)`

---

## Test Data Rules

- JSON key = test function name chính xác
- Credentials chỉ trong `.env` — fixture `efms_account_password`
- Unique fields: `datetime` / `uuid` tại runtime

---

## Naming Conventions

| Element | Rule | Example |
|---|---|---|
| Page class | `Efms` + feature + `Page` | `EfmsBookingReceiptPage` |
| Menu base | `EfmsCommercialMenuPage` | extend cho Agent, Customer, … |
| Test file | `test_{app}_{module}.py` | `test_efms_navigate.py` |
| Test method | `test_{tc_id_lower}_...` | `test_fms_br_002_create_booking_receipt` |
| Page method | snake_case, verb-first | `click_add_new`, `is_list_displayed` |

---

## New Package Checklist

1. `tests/{app}/test_{app}_{module}.py` + JSON entry trong `dataTest-{app}.json`
2. Page Object trong `src/automation/pages/{app}/` — extend menu base nếu có
3. Register trong `PageManager` nếu page mới
4. Markers: `@pytest.mark.{efms|etms}`, `@pytest.mark.{smoke|navigation|critical}`
5. `login_efms` / credentials fixture cho precondition login
6. Navigate list: `EfmsNavigateVerifyMixin` — grid rows hoặc shipment items
7. Chạy: `uv run pytest tests/{app}/... -v --browser chrome`

---

## Anti-Patterns (FORBIDDEN)

| Forbidden | Correct |
|---|---|
| `playwright.async_api` | `sync_api` |
| `page.locator()` in tests | `pages` fixture → Page Object |
| `time.sleep()` | `wait_for_visible` / `settings` |
| Assertions in Page Objects | `assert` in tests với message |
| Hardcoded credentials | `settings` + `.env` |
| Title-only navigate verify | Grid rows / shipment items |
| Raw BR delete clicks | `delete_booking_receipt_from_grid()` |
| Duplicate ng-select/swal logic | Common Components |

---

## Tham chiếu

| File | Scope |
|---|---|
| `ruleAi.md` | Full architecture — 18 sections |
| `.cursor/rules/qa-general.mdc` | POM, assertions, test data |
| `.cursor/rules/efms-playwright-waits.mdc` | Wait + race conditions |
| `.cursor/skills/flaky-test-analyzer/SKILL.md` | Debug flaky tests |
