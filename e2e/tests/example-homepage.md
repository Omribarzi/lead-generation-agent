# Homepage Load Test

## Test Case: [TC-HOME-001] Homepage Loads Correctly
**Priority:** High
**Category:** E2E
**Last Updated:** 2024-12-31

### Description
Verify that the application homepage loads correctly with all critical elements visible.

### Preconditions
- [ ] Application is running
- [ ] No authentication required for homepage

### Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Navigate to homepage | Page loads within 3 seconds |
| 2 | Dismiss cookie banners | Banners are dismissed |
| 3 | Verify page title | Title matches expected |
| 4 | Verify navigation present | Nav menu is visible |
| 5 | Check console for errors | No critical errors |
| 6 | Capture screenshot | Screenshot saved |

### Detailed Steps

#### Step 1: Navigate to homepage
```
Navigate to: [APP_URL]
Wait for: Document ready state
Timeout: 10 seconds
```

#### Step 2: Dismiss popups
```
Run: e2e/scripts/auto_dismiss_banners.js
Expected: Cookie banners dismissed
```

#### Step 3: Verify page title
```
Assert: document.title is not empty
Assert: document.title contains expected app name
```

#### Step 4: Verify navigation
```
Assert: nav element exists
Assert: nav contains expected links
```

#### Step 5: Check console
```
Read: browser console logs
Assert: No errors with level "SEVERE"
```

#### Step 6: Capture screenshot
```
Screenshot: e2e/screenshots/TC-HOME-001-homepage.png
Type: full-page
```

### Expected Results
- [ ] Page loads successfully (HTTP 200)
- [ ] Page title is correct
- [ ] Navigation menu is visible
- [ ] No JavaScript errors in console
- [ ] Screenshot captured successfully

### Automation Script

```python
from e2e.scripts.browser_utils import BrowserHelper

def test_homepage_loads():
    with BrowserHelper() as browser:
        # Step 1: Navigate
        browser.navigate("http://localhost:3000")

        # Step 2: Dismiss popups
        browser.dismiss_banners()

        # Step 3: Verify title
        info = browser.get_page_info()
        assert info["title"], "Page title should not be empty"

        # Step 4: Verify navigation
        nav = browser.wait_for_element("nav", timeout=5)
        assert nav is not None, "Navigation should be present"

        # Step 5: Check console
        logs = browser.get_console_logs()
        errors = [log for log in logs if log.get("level") == "SEVERE"]
        assert len(errors) == 0, f"Found console errors: {errors}"

        # Step 6: Screenshot
        browser.full_page_screenshot("e2e/screenshots/TC-HOME-001-homepage.png")

        print("TC-HOME-001: PASSED")
```
