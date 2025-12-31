/**
 * Auto-dismiss common cookie banners and popups.
 *
 * This script attempts to click on common "Accept", "Agree", "Close" buttons
 * found in cookie consent banners and other modal popups.
 *
 * Usage: Inject this script after page navigation to clear UI clutter
 * before taking screenshots or performing tests.
 */

(function dismissBanners() {
    'use strict';

    // Common selectors for cookie/consent banners
    const COOKIE_SELECTORS = [
        // ID-based selectors
        '#onetrust-accept-btn-handler',
        '#accept-cookies',
        '#cookie-accept',
        '#cookieAccept',
        '#accept-all-cookies',
        '#acceptAllCookies',
        '#gdpr-accept',
        '#consent-accept',

        // Class-based selectors
        '.cookie-accept',
        '.accept-cookies',
        '.js-cookie-accept',
        '.cookie-consent-accept',
        '.gdpr-accept',
        '.consent-accept',
        '.cc-accept',
        '.cc-btn-accept',

        // Attribute-based selectors
        '[data-cookie-accept]',
        '[data-consent="accept"]',
        '[data-action="accept-cookies"]',

        // Generic button selectors with common text patterns
        'button[id*="cookie"][id*="accept"]',
        'button[class*="cookie"][class*="accept"]',
        'button[id*="consent"][id*="accept"]',
        'button[class*="consent"][class*="accept"]',

        // Common banner containers with buttons
        '[class*="cookie-banner"] button:first-of-type',
        '[class*="cookie-notice"] button:first-of-type',
        '[class*="gdpr-banner"] button:first-of-type',
        '[id*="cookie-banner"] button:first-of-type'
    ];

    // Common selectors for generic modal close buttons
    const MODAL_CLOSE_SELECTORS = [
        '.modal-close',
        '.close-modal',
        '.popup-close',
        '.close-popup',
        '[data-dismiss="modal"]',
        '[aria-label="Close"]',
        '[aria-label="close"]',
        '.overlay-close'
    ];

    // Text patterns to look for in buttons (case-insensitive)
    const ACCEPT_TEXT_PATTERNS = [
        'accept',
        'agree',
        'allow',
        'consent',
        'got it',
        'ok',
        'okay',
        'continue',
        'understood',
        'i understand'
    ];

    const DISMISS_TEXT_PATTERNS = [
        'close',
        'dismiss',
        'no thanks',
        'not now',
        'maybe later',
        'skip'
    ];

    let dismissedCount = 0;

    /**
     * Try to click an element safely
     */
    function safeClick(element) {
        try {
            if (element && element.offsetParent !== null) {
                element.click();
                dismissedCount++;
                console.log('[E2E] Dismissed element:', element.tagName, element.className || element.id);
                return true;
            }
        } catch (e) {
            console.log('[E2E] Failed to click element:', e.message);
        }
        return false;
    }

    /**
     * Find and click elements matching selectors
     */
    function dismissBySelectors(selectors) {
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => safeClick(el));
            } catch (e) {
                // Selector might be invalid, skip it
            }
        });
    }

    /**
     * Find buttons by text content
     */
    function dismissByTextContent(patterns, tagName = 'button') {
        const elements = document.querySelectorAll(tagName);
        elements.forEach(el => {
            const text = (el.textContent || el.innerText || '').toLowerCase().trim();
            for (const pattern of patterns) {
                if (text.includes(pattern.toLowerCase())) {
                    // Avoid clicking navigation or important buttons
                    const isLikelyNavigation = el.closest('nav') ||
                                               el.closest('header:not([class*="cookie"])') ||
                                               el.closest('[role="navigation"]');
                    if (!isLikelyNavigation) {
                        safeClick(el);
                        break;
                    }
                }
            }
        });
    }

    /**
     * Remove overlay elements that might block interaction
     */
    function removeOverlays() {
        const overlaySelectors = [
            '[class*="overlay"][class*="cookie"]',
            '[class*="overlay"][class*="consent"]',
            '[class*="modal-backdrop"]',
            '[class*="cookie-overlay"]',
            '[id*="cookie-overlay"]'
        ];

        overlaySelectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    el.style.display = 'none';
                    console.log('[E2E] Hidden overlay:', selector);
                });
            } catch (e) {}
        });
    }

    // Execute dismissal
    console.log('[E2E] Starting banner dismissal...');

    // First try specific cookie selectors
    dismissBySelectors(COOKIE_SELECTORS);

    // Then try modal close buttons
    dismissBySelectors(MODAL_CLOSE_SELECTORS);

    // Try finding buttons by text
    dismissByTextContent(ACCEPT_TEXT_PATTERNS, 'button');
    dismissByTextContent(ACCEPT_TEXT_PATTERNS, 'a');
    dismissByTextContent(DISMISS_TEXT_PATTERNS, 'button');

    // Remove blocking overlays
    removeOverlays();

    console.log(`[E2E] Banner dismissal complete. Dismissed ${dismissedCount} elements.`);

    // Return count for verification
    return dismissedCount;
})();
