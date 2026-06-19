# eFMS/eTMS Automation Framework

Automation framework for eFMS/eTMS using Python 3.12+, pytest, Playwright (sync API), pytest-html, pytest-reportportal, Pydantic Settings, and Loguru.

**AI / contributor guide:** see [`ruleAi.md`](ruleAi.md) for architecture rules, naming conventions, and copy-paste templates.

## Default environment

| Setting | Value |
|---------|-------|
| Environment | `UAT` |
| eFMS URL | `https://uat-efms.logtechub.com/` |
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
├── conftest.py                  # Early hooks: .env + auto ReportPortal (not collect-only)
├── src/automation/
│   ├── config/                  # settings.py, secret_redaction.py
│   ├── logging/                 # Loguru + @log_method step logs
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── page_manager.py
│   │   ├── common/              # NgSelect, NativeSelect, SwalModal components
│   │   ├── efms/
│   │   │   ├── efms_login_page.py, efms_home_page.py
│   │   │   ├── commercial/      # Agent, Customer, Work Order, Booking Receipt
│   │   │   ├── logistics/       # Job Management, Customs, Trucking
│   │   │   └── services/        # 8 documentation pages
│   │   └── etms/
│   │       ├── etms_login_page.py
│   │       └── etms_home_page.py
│   ├── reporting/               # ReportPortal, rerun, HTML metadata
│   └── utils/                   # Pure helpers (text_utils)
├── tests/
│   ├── conftest.py              # Playwright fixtures + HTML report hooks
│   ├── conftest_reportportal.py # ReportPortal session config
│   ├── data_provider.py
│   ├── testdata/
│   │   ├── dataTest-efms.json
│   │   └── dataTest-etms.json
│   ├── efms/
│   │   ├── conftest.py          # login_efms fixture
│   │   ├── test_efms_auth.py    # TestEfmsAuth — SMK_AUTH_001/002
│   │   ├── test_efms_navigate.py# TestEfmsNavigate — SMK_NAV_001–006
│   │   └── test_efms_booking_receipt.py  # FMS_BR_001–005
│   ├── etms/
│   │   └── test_etms_auth.py    # TestEtmsAuth — SMK_AUTH_001/002
│   ├── test_reporting_support.py
│   └── test_text_utils.py
├── reports/                     # HTML reports (gitignored)
├── test-results/                # Screenshots (gitignored)
├── logs/                        # automation.log (gitignored)
├── Jenkinsfile
├── pyproject.toml
├── ruleAi.md
└── .env.example
```

> **Not implemented yet:** API tests (`httpx`), DB tests — add when explicitly needed (see `ruleAi.md` §9–10).

## Implemented tests

| TC_ID | File | Markers | Priority |
|-------|------|---------|----------|
| SMK_AUTH_001, SMK_AUTH_002 | `tests/efms/test_efms_auth.py` | smoke, login, efms | Critical |
| SMK_NAV_001–006 | `tests/efms/test_efms_navigate.py` | smoke, navigation, efms | High |
| FMS_BR_001–005 | `tests/efms/test_efms_booking_receipt.py` | regression, efms | High |
| SMK_AUTH_001, SMK_AUTH_002 | `tests/etms/test_etms_auth.py` | smoke, login, etms | Critical |

## Local setup

**Requirements:** Python 3.12+, Google Chrome and/or Microsoft Edge.

```bash
python3 -m pip install --user uv
uv sync --extra dev
uv run playwright install --with-deps chrome msedge
cp .env.example .env   # set EFMS_ACCOUNT_* and ETMS_ACCOUNT_*
```

## Run tests

```bash
# Smoke suite (auth + navigation)
uv run pytest -m smoke -v --browser chrome --browser-headless false

# By priority (from JSON via DataProvider.*_cases)
uv run pytest -m critical -v --browser chrome --browser-headless true
uv run pytest -m high -v --browser chrome --browser-headless true

# By suite
uv run pytest -m login -v --browser chrome --browser-headless true
uv run pytest -m navigation -v --browser chrome --browser-headless true
uv run pytest -m regression -v --browser chrome --browser-headless true

# By application (ReportPortal: separate launch per app)
uv run pytest -m efms -v --browser chrome --browser-headless false --reportportal
uv run pytest -m etms -v --browser chrome --browser-headless false --reportportal

# Local without ReportPortal
uv run pytest tests/efms/ -m efms -v --no-reportportal

# Single file (headed debug)
uv run pytest tests/efms/test_efms_auth.py -v --browser chrome --browser-headless false -s
```

If `EFMS_ACCOUNT_PASSWORD` or `ETMS_ACCOUNT_PASSWORD` is not set, login tests for that product are **skipped** safely.

## HTML report

```bash
uv run pytest tests/ -v \
  --browser chrome --browser-headless false \
  --html=reports/report.html --self-contained-html
```

| Artifact | Path |
|----------|------|
| HTML report | `reports/report.html` |
| Failure screenshots | `test-results/screenshots/` |
| File log | `logs/automation.log` |

## Configuration

All settings in `src/automation/config/settings.py`, overridable via `.env`. See `.env.example` for the full list.

Key variables: `BROWSER`, `BROWSER_HEADLESS`, `EFMS_BASE_URL`, `ETMS_BASE_URL`, `TEST_RERUNS`, `RP_*`.

## ReportPortal

1. Copy API key from ReportPortal UI → Profile → API Keys.
2. Add to `.env`:

```bash
RP_API_KEY=your-api-key-here
RP_ENDPOINT=http://10.50.1.26:8080
RP_PROJECT=default_personal
```

3. Run **per app** (mixed suite disables RP):

```bash
uv run pytest -m efms --reportportal --browser chrome --browser-headless true
uv run pytest -m etms --reportportal --browser chrome --browser-headless true
```

Skip ReportPortal locally: `--no-reportportal`

**Auto behavior:** RP enables on real test runs when `RP_API_KEY` is set; skipped on `--collect-only` (IDE discovery).

pytest-html works in parallel (`--html=reports/report.html`).

## Code quality

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
uv run pytest tests/test_reporting_support.py tests/test_text_utils.py -v
```

## Jenkins & GitHub Actions

### GitHub Actions

File: `.github/workflows/ci.yml` + `scripts/ci-run-tests.sh`

| Event | Jobs |
|-------|------|
| Pull Request | Lint + typecheck only |
| Push `main` / Manual | Lint + UI tests (Playwright) |

### Jenkins

| Parameter | Options |
|-----------|---------|
| `APP` | `efms`, `etms`, `all` |
| `MARKER` | `critical`, `high`, `login`, `navigation`, `smoke`, `regression`, `efms`, `etms` |
| `BROWSER` | `chrome`, `edge` |
| `HEADLESS` | `true`, `false` |

Full setup: [`ruleAi.md` Section 12.1](ruleAi.md#121-cicd-pipeline-github-actions--jenkins).

## Adding a new test

1. Add JSON data to `tests/testdata/dataTest-{app}.json` (key = test method name).
2. Create or extend Page Object under `src/automation/pages/{app}/`.
3. Reuse `pages/common/` components when widget repeats (ng-select, swal).
4. Register new page in `page_manager.py` if needed.
5. Add test to `tests/{app}/test_{app}_{module}.py`.
6. Follow [`ruleAi.md`](ruleAi.md) checklist before submitting.
