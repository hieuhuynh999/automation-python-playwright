#!/usr/bin/env bash
# Shared UI test runner for Jenkins and GitHub Actions.
# Env: APP, MARKER, BROWSER, HEADLESS, PYTEST_ARGS, plus .env credentials from CI secrets.

set -euo pipefail

APP="${APP:-efms}"
MARKER="${MARKER:-critical}"
BROWSER="${BROWSER:-chrome}"
HEADLESS="${HEADLESS:-true}"
PYTEST_ARGS="${PYTEST_ARGS:-}"

mkdir -p reports test-results/screenshots logs

if [[ "${MARKER}" == "efms" || "${MARKER}" == "etms" ]]; then
  MARKER_EXPR="-m ${MARKER}"
elif [[ "${APP}" == "all" ]]; then
  MARKER_EXPR="-m ${MARKER}"
else
  MARKER_EXPR="-m \"${MARKER} and ${APP}\""
fi

# shellcheck disable=SC2086
uv run pytest ${MARKER_EXPR} \
  --browser "${BROWSER}" \
  --browser-headless "${HEADLESS}" \
  --html=reports/report.html \
  --self-contained-html \
  ${PYTEST_ARGS}
