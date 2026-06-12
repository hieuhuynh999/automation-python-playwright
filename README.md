# EFMS/eTMS Automation Framework - Python

Automation framework for eFMS/eTMS using Python 3.12, pytest, Playwright Python, pytest-html, httpx, psycopg, logging, Git and Jenkins.

## Default environment

- Environment: `UAT`
- eFMS URL: `https://uat-efms.logtechub.com/en/#/home`
- eTMS URL: `https://staging-itllog-etms.logtechub.com/en/#/app/default/home`
- Shared login username: `henry.hieu`
- Supported browsers: `chrome`, `edge`
- Default browser mode: `BROWSER_HEADLESS=false` so Chrome/Edge opens in headed mode when a display is available

## Project structure

```text
src/automation
|-- api
|-- config
|-- db
|-- logging
|-- pages
|   |-- base_page.py
|   |-- page_manager.py
|   |-- efms/efms_home_page.py
|   `-- etms/etms_home_page.py
`-- reporting

tests
|-- conftest.py
|-- ui
|   |-- efms
|   `-- etms
|-- api
`-- db

src/test/resources/report-html
|-- html
`-- images
```

## Local setup

Required tools:

- Python 3.12+
- Google Chrome and Microsoft Edge installed, or allow Playwright to install them

Install dependencies with uv:

```bash
python3 -m pip install --user uv
uv sync --extra dev
uv run playwright install --with-deps chrome msedge
```

Alternative with pip:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
python -m playwright install --with-deps chrome msedge
```

## Run tests

Run smoke suite for eFMS/eTMS:

```bash
uv run pytest -m smoke --browser chrome --browser-headless true
```

Run only eFMS:

```bash
uv run pytest -m 'smoke and efms' --browser chrome --browser-headless true
```

Run only eTMS:

```bash
uv run pytest -m 'smoke and etms' --browser edge --browser-headless true
```

Run headed mode:

```bash
uv run pytest -m smoke --browser chrome --browser-headless false -s
```

Run login suite for both eFMS and eTMS. Pass the password at runtime:

```bash
ACCOUNT_PASSWORD='<password>' uv run pytest -m login --browser chrome --browser-headless true
```

If `ACCOUNT_PASSWORD` is not provided, login tests are skipped safely.

## HTML report

Generate a self-contained pytest-html report:

```bash
uv run pytest -m smoke \
  --browser chrome \
  --browser-headless true \
  --html=reports/report.html \
  --self-contained-html
```

HTML entry point:

```text
reports/report.html
```

Failure artifacts:

```text
test-results/screenshots/
test-results/attachments/
logs/
```

## Configuration

Configuration is defined in `src/automation/config/settings.py` and can be overridden by environment variables or `.env`.

Example:

```bash
export BROWSER=edge
export BROWSER_HEADLESS=true
export ACCOUNT_PASSWORD='<password>'
export DB_URL='postgresql://host:5432/db'
```

Never commit real passwords or tokens to Git.

## Code quality

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Jenkins

`Jenkinsfile` provides a parameterized Python pipeline using uv, pytest, Playwright and pytest-html artifacts.

## Design documents

```text
reports/automation-test-framework-design.md
reports/python-automation-framework-migration-plan.md
```
