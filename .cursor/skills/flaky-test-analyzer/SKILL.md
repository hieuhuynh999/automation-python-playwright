---
name: flaky-test-analyzer
description: Phân tích và sửa test automation không ổn định trong suite eFMS/eTMS — Python playwright.sync_api, Angular/PrimeNG UI. Xác định root cause và áp dụng fix đúng chuẩn project.
---

# Flaky Test Analyzer — eFMS/eTMS Automation

**Mục đích:** Xác định và khắc phục test không ổn định trong suite Playwright/Python cho eFMS và eTMS.

**Source of truth:** `ruleAi.md` (Section 3.6, 14, 18) · `.cursor/rules/efms-playwright-waits.mdc` · `.cursor/rules/locator-strategy.mdc`

---

## Khi nào dùng

- Test pass/fail xen kẽ giữa các lần chạy
- CI không nhất quán; local pass nhưng Jenkins fail
- Test fail chỉ khi chạy sau test khác (thứ tự phụ thuộc)
- Debug từng bước PASS nhưng chạy full suite FAIL (race condition)

---

## Quy trình phân tích

1. **Reproduce** — Chạy headed trước: `--browser-headless false` (Section 3.10)
2. **Inspect** — Đọc stack trace, screenshot `test-results/screenshots/`, pytest-html report
3. **Classify** — Chọn category bên dưới (Angular/eFMS, không dùng pattern ExtJS)
4. **Fix** — Áp dụng pattern đúng từ `ruleAi.md` / Page Object hiện có
5. **Verify** — Chạy lại test **5+ lần liên tiếp** headed, rồi ít nhất **1 lần** headless

```bash
# Reproduce single test
uv run pytest tests/efms/test_efms_booking_receipt.py::TestEfmsBookingReceipt::test_fms_br_005 -v --browser chrome --browser-headless false

# Stability check (5 runs)
for /L %i in (1,1,5) do uv run pytest <path>::<test> -v --browser chrome --browser-headless false
```

---

## Root Cause Categories & Fixes (Angular / eFMS)

### 1. Unstable Locator

**Triệu chứng:** `StrictModeViolation`, `TimeoutError` xen kẽ, locator "đúng" khi inspect thủ công.

| Pattern xấu | Vì sao hỏng |
|---|---|
| `#mat-input-3`, `_ngcontent-xxx` | Dynamic Angular attribute |
| `//div[3]/button[2]` | Positional XPath |
| `.p-datatable-tbody tr:nth-child(5)` | Index — layout đổi là vỡ |
| `input[type='text']` quá rộng | Match input ẩn / clone |

**Fix:** Ưu tiên locator theo `ruleAi.md` Section 3.4:

```python
# Xấu
page.locator("#mat-input-0")
page.locator("//div[3]/button")

# Tốt — data-testid / name / text / xpath ổn định
page.locator("xpath=//button[normalize-space(.)='Delete']").first
page.locator("xpath=//span[normalize-space()='{booking_no}']")
```

Grid row: dùng `ListGridComponent.wait_for_data_rows()` — không click cell trước khi grid ready.

---

### 2. Hard Waits (Timing)

**Triệu chứng:** Pass local, fail CI; fail tại `.click()` / `.fill()` "đáng lẽ đã sẵn sàng".

**Cấm trong project:**

```python
time.sleep(3)
page.wait_for_timeout(5000)   # literal ms — forbidden
```

**Fix:** Dùng `settings` + condition waits:

```python
from automation.config import settings

self.wait_for_visible(selectors, "Save button", timeout=settings.browser_timeout)
self.click_when_ready(selectors, "Save button")
self.wait_for_page_stable()
self.page.wait_for_url(lambda u: "#/home" in u, timeout=settings.page_load_timeout)
```

`page.wait_for_timeout(settings.navigation_settle_ms)` **chỉ** qua key settings — không literal.

---

### 3. Angular Grid / Datatable chưa render

**Triệu chứng:** `rows: 15` nhưng `cells with text: 0`; verify title pass nhưng không có data.

**Fix:** `ListGridComponent` + `EfmsNavigateVerifyMixin`:

```python
self.list_grid.wait_until_ready()
self.list_grid.verify_column_headers(["Booking No", "Customer"])
self.list_grid.wait_for_data_rows(min_rows=1)
```

Không verify navigate chỉ bằng title/URL — phải có row hoặc shipment item (Section 5.12).

---

### 4. ng-select / Dropdown — Click không chọn đúng

**Triệu chứng:** UI hiện text nhưng form không submit đúng; field phụ thuộc không xuất hiện.

**Fix:** `NgSelectComponent` / `NativeSelectComponent` — không raw `.click()` trên option:

```python
self.ng_select.select_option_by_text("Customer", customer_name)
self.native_select.select_by_label("Company", company_name)
```

---

### 5. Block UI / Loading Overlay

**Triệu chứng:** `ElementClickInterceptedError`; click trúng overlay.

**Selectors:** `.m-blockui`, `.block-ui-wrapper.block-ui-active`, `ng-progress-bar`

**Fix:** Chờ overlay biến mất trước khi tương tác:

```python
self.page.wait_for_function(
    "() => !document.querySelector('.block-ui-active')",
    timeout=settings.page_load_timeout,
)
# Hoặc reuse _wait_for_grid_ready() trên page có grid
```

---

### 6. SPA Navigation Race (Hash Route)

**Triệu chứng:** Assert chạy trước khi route đổi; sidebar click không phản hồi.

**Fix:**

```python
self.page.wait_for_url(lambda u: "#/commercial/booking-receipt" in u, timeout=settings.page_load_timeout)
self.wait_for_page_stable()
self.wait_for_visible(self.page_title_selectors, "Page title")
```

Headless: viewport `1920×1080` trong `tests/conftest.py`; sidebar dùng `scroll_into_view_if_needed()` + `click(force=True)`.

---

### 7. Dashboard / Title Verify Headless-Unsafe

**Triệu chứng:** `h3` "eFMS" tồn tại nhưng `is_visible()` = False (0×0).

**Fix:** `dashboard_ready_selectors` + `inner_text()` — Section 14 issue #1.

---

### 8. Commercial Menu State (Thứ tự scenario)

**Triệu chứng:** Booking Receipt fail sau Work Order trong cùng class.

**Fix:** Reset dashboard giữa scenarios (`goto_dashboard` / `#/home`) — Section 14 issue #9.

---

### 9. Services — Table vs Shipment Cards

**Triệu chứng:** Navigate Services pass title nhưng không verify content.

**Fix:** `ShipmentListComponent` + `shipment-item-wrapper` — không dùng datatable cho Services doc pages.

---

### 10. Grid Delete Race (Booking Receipt)

**Triệu chứng:** Run FAIL, debug PASS; popup không mở; record còn sau delete.

**Fix:** **Luôn** dùng `delete_booking_receipt_from_grid()` — Section 5.13:

- Toolbar delete only (không row trash)
- `_wait_toolbar_delete_ready()` — poll Delete enabled
- `expect_response` + toast + `wait_until_booking_absent`
- Exact `normalize-space()='{booking_no}'` — không `contains()`

---

### 11. Test Data Conflicts

**Triệu chứng:** Fail khi chạy suite; pass khi chạy đơn lẻ.

**Fix:** Unique data runtime (Section 3.8):

```python
from datetime import datetime
import uuid

booking_ref = f"AUTO_BR_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
email = f"auto_{uuid.uuid4().hex[:8]}@test.com"
```

CRUD ordered class: share `booking_no` qua class variable — không hardcode số booking cũ.

---

### 12. Stale Element After Navigation

**Triệu chứng:** `Element is not attached to the DOM`.

**Fix:** Dùng Locator (lazy), không cache `ElementHandle` qua navigation. Re-query sau `goto` / reload.

---

## Stability Checklist

Sau khi fix flaky test:

- [ ] Locator ổn định — không dynamic ID, không positional XPath (Section 3.9)
- [ ] Timing từ `settings.*` — không `time.sleep()` / literal ms
- [ ] Grid: `ListGridComponent.wait_until_ready()` + `wait_for_data_rows()`
- [ ] ng-select: `NgSelectComponent` — không raw click option
- [ ] Block UI cleared trước click
- [ ] Headless: viewport + `dashboard_ready_selectors`
- [ ] Commercial nav: dashboard reset giữa scenarios
- [ ] Services: shipment items — không chỉ title
- [ ] BR delete: `delete_booking_receipt_from_grid()` full chain
- [ ] Test data unique per run
- [ ] **5+ consecutive passes** headed + **1+** headless

---

## Tham chiếu

| File | Nội dung |
|------|----------|
| `ruleAi.md` §3.6 | Wait strategy, grid delete chain |
| `ruleAi.md` §14 | Known issues — không tái tạo |
| `ruleAi.md` §18 | Bản đầy đủ flaky categories |
| `.cursor/rules/efms-playwright-waits.mdc` | Race conditions, delete flow |
| `.cursor/rules/locator-strategy.mdc` | Locator priority |
