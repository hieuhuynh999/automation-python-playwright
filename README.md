# eFMS/eTMS Automation Framework

Automation framework for eFMS/eTMS using Python 3.12+, pytest, Playwright (sync API), pytest-html, httpx, psycopg, Pydantic Settings, Loguru, and Jenkins.

**AI / contributor guide:** see [`ruleAi.md`](ruleAi.md) for architecture rules, naming conventions, and copy-paste templates.

## Default environment

| Setting | Value |
|---------|-------|
| Environment | `UAT` |
| eFMS URL | `https://uat-efms.logtechub.com/en/#/home` |
| eTMS URL | `https://staging-itllog-etms.logtechub.com/en/#/app/default/home` |
| Browsers | `chrome`, `edge` |
| Default headless | `BROWSER_HEADLESS=false` (headed when display available) |

Copy `.env.example` to `.env` and set credentials per product. Never commit secrets.

| Product | `.env` keys |
|---------|-------------|
| eFMS | `EFMS_ACCOUNT_USERNAME`, `EFMS_ACCOUNT_PASSWORD` |
| eTMS | `ETMS_ACCOUNT_USERNAME`, `ETMS_ACCOUNT_PASSWORD` |

Legacy `ACCOUNT_USERNAME` / `ACCOUNT_PASSWORD` still work as **eFMS fallback** only.

## Project structure

```text
auotmation-techub/
├── src/automation/              # Framework package (import as `automation`)
│   ├── api/                     # BaseApiClient (httpx)
│   ├── config/settings.py       # Pydantic Settings + .env
│   ├── db/                      # PostgreSQL helpers
│   ├── logging/                 # Loguru + @log_method step logs
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── page_manager.py
│   │   ├── efms/
│   │   │   ├── efms_login_page.py
│   │   │   ├── efms_home_page.py
│   │   │   ├── commercial/      # Agent, Customer, Work Order, Booking Receipt
│   │   │   ├── logistics/       # Job Management, Customs Clearance, Trucking
│   │   │   └── services/        # 8 documentation pages
│   │   └── etms/etms_home_page.py
│   └── reporting/
├── tests/
│   ├── conftest.py              # Playwright fixtures + HTML report hooks
│   ├── data_provider.py         # JSON test data + auto priority markers
│   ├── testdata/
│   │   ├── dataTest-efms.json
│   │   └── dataTest-etms.json
│   ├── efms/                    # eFMS UI tests
│   │   ├── test_efms_auth.py    # TestEfmsAuth — SMK_AUTH_001/002
│   │   ├── test_efms_navigate.py# TestEfmsNavigate — SMK_NAV_001–006
│   │   └── test_efms_login.py   # EFMS-LOGIN-001
│   ├── etms/                    # eTMS UI tests
│   │   └── test_etms_login.py
│   ├── api/                     # API tests (create when needed)
│   └── db/                      # DB tests (create when needed)
├── reports/                     # HTML reports (gitignored)
├── test-results/                # Screenshots, attachments (gitignored)
├── logs/                        # automation.log (gitignored)
├── Jenkinsfile
├── pyproject.toml
├── ruleAi.md
└── .env.example
```

## Implemented tests

| TC_ID | File | Priority |
|-------|------|----------|
| SMK_AUTH_001, SMK_AUTH_002 | `tests/efms/test_efms_auth.py` | Critical |
| EFMS-LOGIN-001 | `tests/efms/test_efms_login.py` | High |
| SMK_NAV_001–006 | `tests/efms/test_efms_navigate.py` | High |
| ETMS-LOGIN-001 | `tests/etms/test_etms_login.py` | High |

## Local setup

**Requirements:** Python 3.12+, Google Chrome and/or Microsoft Edge (or let Playwright install them).

```bash
python3 -m pip install --user uv
uv sync --extra dev
uv run playwright install --with-deps chrome msedge
cp .env.example .env   # set EFMS_ACCOUNT_* and ETMS_ACCOUNT_*
```

Alternative with pip:

```bash
python3 -m venv .venv
. .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m playwright install --with-deps chrome msedge
```

## Run tests

```bash
# All tests — each product uses its own .env credentials
uv run pytest -v --browser chrome --browser-headless true

# By priority (from JSON via DataProvider.*_cases)
uv run pytest -m critical -v --browser chrome --browser-headless true
uv run pytest -m high -v --browser chrome --browser-headless true

# By suite
uv run pytest -m login -v --browser chrome --browser-headless true
uv run pytest -m navigation -v --browser chrome --browser-headless true
uv run pytest -m smoke -v --browser chrome --browser-headless true

# By application
uv run pytest -m 'login and efms' -v --browser chrome --browser-headless true
uv run pytest -m etms -v --browser edge --browser-headless true

# Single file
uv run pytest tests/efms/test_efms_auth.py -v --browser chrome --browser-headless false -s

# Headed mode (debug)
uv run pytest -m login --browser chrome --browser-headless false -s
```

If `EFMS_ACCOUNT_PASSWORD` or `ETMS_ACCOUNT_PASSWORD` is not set, login tests for that product are **skipped** safely.

## HTML report

```bash
uv run pytest -m login \
  --browser chrome \
  --browser-headless true \
  --html=reports/report.html \
  --self-contained-html
```

| Artifact | Path |
|----------|------|
| HTML report | `reports/report.html` |
| Failure screenshots | `test-results/screenshots/` |
| API response attachments | `test-results/attachments/` |
| File log | `logs/automation.log` |

## Configuration

All settings in `src/automation/config/settings.py`, overridable via `.env`:

```bash
BROWSER=chrome
BROWSER_HEADLESS=true
# eFMS
EFMS_ACCOUNT_USERNAME=your_efms_user
EFMS_ACCOUNT_PASSWORD=your_efms_password
# eTMS
ETMS_ACCOUNT_USERNAME=automation.test
ETMS_ACCOUNT_PASSWORD=your_etms_password
EFMS_BASE_URL=https://uat-efms.logtechub.com/en/#/home
ETMS_BASE_URL=https://staging-itllog-etms.logtechub.com/en/#/app/default/home
```

See `.env.example` for the full list.

## ReportPortal

Local ReportPortal UI: `http://localhost:8080/ui/#default_personal/dashboard`

1. Open **Profile → API Keys** in ReportPortal UI and copy your API key.
2. Add to `.env`:

```bash
RP_API_KEY=your-api-key-here
RP_ENDPOINT=http://localhost:8080
RP_PROJECT=default_personal
```

3. Run tests with `--reportportal`:

```bash
uv run pytest -m login --reportportal --browser chrome --browser-headless true
```

**Sent to ReportPortal automatically:**
- Test results (pass/fail/skip) + pytest markers (`efms`, `critical`, `tc_id`, …)
- Step logs from `@log_method`
- Failure screenshot (Playwright full page)
- Test Case IDs / Scenarios (multi-nav tests)

pytest-html report still works in parallel (`--html=reports/report.html`).

## Code quality

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Jenkins

`Jenkinsfile` runs: Checkout → Install (`uv sync`, Playwright browsers) → Quality (`ruff`, `pyright`) → Tests → Archive artifacts.

| Parameter | Options |
|-----------|---------|
| `MARKER` | `critical`, `high`, `login`, `navigation`, `smoke`, `regression` |
| `BROWSER` | `chrome`, `edge` |
| `HEADLESS` | `true`, `false` |
| `PYTEST_ARGS` | Extra pytest args (e.g. `tests/efms/test_efms_auth.py`) |

`EFMS_ACCOUNT_PASSWORD` and `ETMS_ACCOUNT_PASSWORD` are injected from Jenkins credentials (configure per product).

## Adding a new test

1. Add JSON data to `tests/testdata/dataTest-{app}.json` (key = test method name).
2. Create or extend Page Object under `src/automation/pages/{app}/`.
3. Register new page in `page_manager.py` if needed.
4. Add test to `tests/{app}/test_{app}_{module}.py`.
5. Follow [`ruleAi.md`](ruleAi.md) checklist before submitting.
