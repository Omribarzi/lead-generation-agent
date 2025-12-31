# Claude Code Instructions

## Project Overview
This is the Ksharim Lead Generation Agent for Migdalor (מגדלור) - Israeli Naval Academy Alumni Association.

## E2E Testing Workflow

### Browser Interaction Rules
- **Token Efficiency:** Avoid loading entire HTML `main` or `body` tags. Use specific selectors to locate elements.
- **Visual Analysis:** Use a single full-page screenshot for UI layout reviews instead of scrolling.
- **Auto-Dismiss:** After navigating to a new URL, run the banner dismissal script to clear cookie popups.

### Available Scripts

#### Full-Page Screenshot
```bash
python e2e/scripts/full_page_screenshot.py <url> <output_path>
# Example:
python e2e/scripts/full_page_screenshot.py https://example.com e2e/screenshots/example.png
```

#### Viewport Screenshot (above-fold only)
```bash
python e2e/scripts/full_page_screenshot.py <url> <output_path> --viewport
```

#### Browser Utilities (Python)
```python
from e2e.scripts.browser_utils import BrowserHelper

with BrowserHelper(headless=True) as browser:
    browser.navigate("https://example.com")
    browser.dismiss_banners()
    browser.full_page_screenshot("screenshot.png")
```

### Testing Workflow

1. **Pre-test Check:** Before starting a test, check context usage. If >70%, summarize and compact.

2. **Execution:** Follow steps in the test file strictly.

3. **Reporting:** After every test run, update `e2e/TEST_RESULTS.md` with:
   - Test ID and Status (PASS/FAIL/SKIP)
   - Screenshots of any found issues
   - Console logs if errors were detected

### Test Case Structure
Test cases are stored in `e2e/tests/` as Markdown files. Each test should have:
- Test ID and Priority
- Preconditions
- Step-by-step instructions
- Expected results

## Development Workflow

### For Every Task:
1. Write code
2. Run locally and verify
3. Run tests: `pytest tests/ -v`
4. Git commit & push
5. Verify with Claude Chrome extension
6. Move to next task

### Git Commit Format
```
feat: description of feature
fix: description of bug fix
test: description of test changes
docs: documentation changes
```

### API Keys
- Never commit real API keys
- Use `.env` for local development (gitignored)
- Use `.env.example` as template (committed)

## Project Structure
```
Lead Generation Agent/
├── src/                    # Main application code
├── tests/                  # Unit tests (pytest)
├── e2e/                    # E2E testing infrastructure
│   ├── scripts/            # Utility scripts
│   │   ├── full_page_screenshot.py
│   │   ├── auto_dismiss_banners.js
│   │   └── browser_utils.py
│   ├── tests/              # E2E test cases (markdown)
│   ├── screenshots/        # Test screenshots (gitignored)
│   └── TEST_RESULTS.md     # Test results log
├── scripts/                # Application scripts
├── .env                    # Environment variables (gitignored)
├── .env.example            # Environment template
└── CLAUDE.md               # This file
```
