# Ksharim Lead Generation Agent - Claude Instructions

## CRITICAL WORKFLOW INSTRUCTIONS

### Development Process - MUST FOLLOW FOR EVERY TASK:

1. **Write code** for the task
2. **Run locally** and verify it works
3. **Run tests** (pytest) and make sure they pass
4. **Git commit & push** with descriptive message
5. **E2E Verification** - Use E2E infrastructure to verify the task
6. **STOP and verify with Claude** (Chrome extension) that the task was completed correctly
7. **Only then** move to the next task

### Git Workflow
```bash
# After each completed task:
git add .
git commit -m "feat: [description of what was built]"
git push origin main
```

### Verification Checkpoints
After pushing each major component:
- Run E2E verification using the scripts in `e2e/scripts/`
- Say: "I've completed [X]. Please verify the code in the repo before I continue."
- Wait for confirmation before proceeding

---

## Project Overview

Build an automated LinkedIn outreach system for "Migdalor" (מגדלור), the Israeli Naval Academy Alumni Association. The "Ksharim" (קשרים) program provides mentoring for Israeli veterans.

**Goal**: Reach CSR/HR managers at large Israeli companies (500+ employees) to recruit corporate partners.

## Key Links
- Monday.com Board: https://hovlim-squad.monday.com/boards/5088565278
- Calendar Link: https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ07bZr11Q5sapPKamtzMMuz9sgXtyBC7HYjn6XscNqMieAMNCYrnTkFbfaSYuZvGbdUroS6Zako
- PhantomBuster: https://phantombuster.com/

## Tech Stack
- Python 3.11+
- PhantomBuster API (LinkedIn automation + lead scraping)
- Monday.com API (CRM)
- OpenAI API (AI message generation)
- Redis (job queue for human approval)
- Google Calendar API (meeting scheduling)

---

## E2E Testing Infrastructure

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

### E2E Testing Workflow

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

---

## Project Structure

```
Lead Generation Agent/
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── conversation_agent.py    # AI message generation (OpenAI)
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── phantombuster.py         # LinkedIn automation
│   │   ├── monday_client.py         # CRM integration
│   │   └── google_calendar.py       # Calendar booking
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── approval_queue.py        # Human review queue (Redis)
│   │   └── rate_limiter.py          # Safety limits
│   └── config/
│       ├── __init__.py
│       └── settings.py              # Environment config
├── scripts/
│   ├── daily_outreach.py            # Main cron job
│   ├── process_replies.py           # Handle incoming messages
│   └── setup_monday_board.py        # Initialize CRM board
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Shared fixtures
│   ├── test_config.py
│   ├── test_monday.py
│   ├── test_phantombuster.py
│   ├── test_conversation_agent.py
│   ├── test_approval_queue.py
│   └── test_daily_outreach.py
├── e2e/
│   ├── scripts/
│   │   ├── full_page_screenshot.py
│   │   ├── auto_dismiss_banners.js
│   │   └── browser_utils.py
│   ├── tests/                       # E2E test cases (markdown)
│   ├── screenshots/                 # Test screenshots (gitignored)
│   └── TEST_RESULTS.md              # Test results log
├── .env.example
├── .env                             # Your actual keys (gitignored)
├── .gitignore
├── requirements.txt
├── CLAUDE.md                        # This file
└── README.md
```

---

## Environment Variables (.env)

```bash
# PhantomBuster
PHANTOMBUSTER_API_KEY=your_key_here

# Monday.com
MONDAY_API_KEY=your_key_here
MONDAY_BOARD_ID=5088565278

# OpenAI
OPENAI_API_KEY=your_key_here

# Redis (for approval queue)
REDIS_URL=redis://localhost:6379/0

# Settings
DAILY_MESSAGE_LIMIT=10
REQUIRE_HUMAN_APPROVAL=true
TIMEZONE=Asia/Jerusalem
```

---

## Safety Limits (Critical!)

LinkedIn will block aggressive automation. Enforce these limits:

- Max 10 messages per day
- Max 20 profile views per day
- Random delays: 60-180 seconds between actions
- Working hours only: 09:00-18:00 Israel time
- No weekend activity
- Never send same message twice

---

## AI Message Generation (Hebrew)

### System Prompt for OpenAI
```
You are גיא from מגדלור - ארגון בוגרי קורס חובלים.

Rules:
- Hebrew only (עברית)
- Max 30 words per message
- No dashes (use comma or period)
- Never start with a verb
- Oral, pragmatic tone
- Max 2 questions per conversation
- Never ask for meeting in first message

First message rules:
- Greet by name
- Reference ONE specific detail from their profile
- No flattery words (impressed, admire, love)
- End with ONE bold question about CSR/social impact

Offering:
תוכנית "קשרים" של מגדלור מחברת בין חן מהצבא לבוגרים שלנו בתעשייה של פיננסים,
היטק ועסקים של פיננס ושירותים פיננסיים, ומסייעת למשוחררים לרקוע בקריירה.
```

---

## Monday.com Board Columns

Create these columns on the board:
- Name (text)
- Company (text)
- Position (text)
- LinkedIn URL (link)
- Status: New | Contacted | In Conversation | Meeting Scheduled | Not Interested | Won
- Last Message Date (date)
- Conversation Log (long text)
- Lead Score (number)

---

## Git Commit Format

```
feat: description of feature
fix: description of bug fix
test: description of test changes
docs: documentation changes
```

## API Keys
- Never commit real API keys
- Use `.env` for local development (gitignored)
- Use `.env.example` as template (committed)

---

## TASK COMPLETION CHECKLIST

For every task completed:

- [ ] Code written and working locally
- [ ] Unit tests written and passing: `pytest tests/test_xxx.py -v`
- [ ] E2E verification completed (if applicable)
- [ ] Git commit with descriptive message
- [ ] Git push to origin main
- [ ] Verification requested from user

---

## FINAL PROJECT CHECKLIST

Before marking the project complete:

- [ ] All 7 tasks completed
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Code coverage > 80%: `pytest tests/ --cov=src`
- [ ] .env file has real API keys
- [ ] Monday.com board has correct columns
- [ ] PhantomBuster account connected
- [ ] One successful E2E test run
