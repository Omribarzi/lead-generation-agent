# Test Case Template

Copy this file and rename it for your specific test case.

---

## Test Case: [TC-XXX-001] Test Name Here
**Priority:** High | Medium | Low
**Category:** UI | API | Integration | E2E
**Last Updated:** YYYY-MM-DD

### Description
Brief description of what this test validates.

### Preconditions
- [ ] Application is running on `localhost:3000` (or specify URL)
- [ ] User is logged in (if required)
- [ ] Test data has been seeded (if required)

### Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to [URL] | Page loads successfully |
| 2 | Click [element] | [Expected behavior] |
| 3 | Enter [data] in [field] | [Expected behavior] |
| 4 | Verify [condition] | [Expected state] |

### Detailed Steps

#### Step 1: Navigate to page
```
Navigate to: https://example.com/page
Wait for: Page load complete
```

#### Step 2: Dismiss any popups
```
Run: e2e/scripts/auto_dismiss_banners.js
```

#### Step 3: Perform action
```
Click: button#submit
Wait for: Success message appears
```

#### Step 4: Verify result
```
Assert: .success-message contains "Operation successful"
Screenshot: e2e/screenshots/TC-XXX-001-result.png
```

### Expected Results
- [ ] Success message is displayed
- [ ] Data is saved correctly
- [ ] No console errors

### Test Data
| Field | Value |
|-------|-------|
| Username | test@example.com |
| Password | testpass123 |

### Notes
Any additional notes, edge cases, or known issues.

---

## Automation Script (Optional)

```python
from e2e.scripts.browser_utils import BrowserHelper

def test_tc_xxx_001():
    with BrowserHelper() as browser:
        # Step 1: Navigate
        browser.navigate("https://example.com/page")

        # Step 2: Dismiss popups
        browser.dismiss_banners()

        # Step 3: Perform action
        browser.click_element("button#submit")

        # Step 4: Verify
        text = browser.get_text(".success-message")
        assert "Operation successful" in text

        # Screenshot
        browser.full_page_screenshot("e2e/screenshots/TC-XXX-001-result.png")
```
