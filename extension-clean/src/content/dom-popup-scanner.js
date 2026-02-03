/**
 * SecureSentinel DOM Popup Scanner
 * Automatically detects and analyzes popups, modals, banners, and notifications
 * that appear on websites (not just native browser dialogs)
 */

console.log("%c[SecureSentinel] DOM Popup Scanner Active", "color: #10b981; font-weight: bold");

// Track analyzed elements to avoid duplicates
const analyzedElements = new WeakSet();
const analyzedTexts = new Set();

// Configuration
const CONFIG = {
    minTextLength: 20,           // Minimum text length to analyze
    maxTextLength: 1000,         // Maximum text length to analyze
    scanInterval: 500,           // Check for new popups every 500ms
    riskThreshold: 0.4,          // Show overlay if risk > 40%
    debounceTime: 1000           // Debounce rapid changes
};

// Selectors for common popup/modal patterns
const POPUP_SELECTORS = [
    // Generic modals
    '[role="dialog"]',
    '[role="alertdialog"]',
    '[aria-modal="true"]',
    '.modal',
    '.popup',
    '.dialog',
    '.overlay',
    '.lightbox',
    
    // Notifications & Alerts
    '[role="alert"]',
    '[role="status"]',
    '.notification',
    '.alert',
    '.toast',
    '.snackbar',
    '.banner',
    
    // Cookie/GDPR banners
    '.cookie-banner',
    '.cookie-consent',
    '.cookie-notice',
    '.gdpr-banner',
    '.gdpr-notice',
    '#cookie-notice',
    '#cookie-consent',
    '#cookieConsent',
    '[class*="cookie"]',
    '[id*="cookie"]',
    '[class*="consent"]',
    
    // Chat widgets / Live chat
    '[class*="chat-widget"]',
    '[class*="chatwidget"]',
    '[class*="livechat"]',
    '[id*="chat-widget"]',
    '.tawk-widget',
    '.intercom-launcher',
    '#hubspot-messages-iframe-container',
    
    // Promo bars / Announcement bars
    '[class*="announcement"]',
    '[class*="promo-bar"]',
    '[class*="top-bar"]',
    '[class*="notice-bar"]',
    '[class*="info-bar"]',
    '.announcement-bar',
    '.promo-banner',
    '.site-notice',
    
    // Floating elements
    '[class*="floating"]',
    '[class*="sticky-banner"]',
    '[class*="fixed-banner"]',
    'div[style*="position: fixed"]',
    'div[style*="position:fixed"]',
    
    // Hero sections / CTA blocks (capture main page content)
    '[class*="hero"]',
    '[class*="cta"]',
    '[class*="call-to-action"]',
    '[class*="banner"]',
    '[class*="jumbotron"]',
    '[class*="masthead"]',
    'section[class*="intro"]',
    'section[class*="main"]',
    'header[class*="main"]',
    
    // Common frameworks
    '.MuiDialog-root',           // Material-UI
    '.MuiSnackbar-root',
    '.ant-modal',                // Ant Design
    '.ant-notification',
    '.v-dialog',                 // Vuetify
    '.modal-dialog',             // Bootstrap
    '.modal-content',
    '.chakra-modal',             // Chakra UI
    '.p-dialog',                 // PrimeReact
    '.swal2-popup',              // SweetAlert2
    '.fancybox-content',         // Fancybox
    
    // Custom patterns
    'div[class*="modal"]',
    'div[class*="popup"]',
    'div[class*="dialog"]',
    'div[class*="notification"]',
    'div[class*="alert"]',
    'div[id*="modal"]',
    'div[id*="popup"]',
    'div[id*="notification"]',
    
    // Ad Containers & Iframes (NEW)
    'div[class*="ad-"]',
    'div[class*="ads-"]',
    'div[id*="ad-"]',
    'div[id*="google_ads"]',
    'div[id*="gpt"]',
    'iframe[src*="google"]',
    'iframe[src*="doubleclick"]',
    'iframe[src*="ads"]',
    'ins.adsbygoogle',
    'aside[class*="ad"]',
    '[class*="sticky-footer"]',
    '[class*="bottom-banner"]'
];

/**
 * Extract meaningful text from an element
 */
function extractText(element) {
    if (!element) return '';
    
    // IFRAME HANDLING: If it's an iframe or contains one, capture the source
    const iframe = element.tagName === 'IFRAME' ? element : element.querySelector('iframe');
    if (iframe) {
        try {
            // Prefer text if available (same origin), otherwise use SRC as proxy for content
            const internalText = iframe.contentDocument?.body?.innerText;
            if (internalText && internalText.length > 10) return internalText;
            
            // If cross-origin or empty, use metadata signature
            return `[IFRAME_AD] Source: ${iframe.src} | Title: ${iframe.title || 'Ad Frame'}`;
        } catch(e) {
            return `[IFRAME_AD] Source: ${iframe.src}`;
        }
    }
    
    // Clone element to avoid modifying the DOM
    const clone = element.cloneNode(true);
    
    // Remove script and style tags
    const scripts = clone.querySelectorAll('script, style, noscript');
    scripts.forEach(s => s.remove());
    
    // Get text content
    let text = clone.textContent || clone.innerText || '';
    
    // Clean up whitespace
    text = text.replace(/\s+/g, ' ').trim();
    
    return text;
}

/**
 * Check if element is visible
 */
function isVisible(element) {
    if (!element) return false;
    
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    
    return (
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        style.opacity !== '0' &&
        rect.width > 0 &&
        rect.height > 0
    );
}

/**
 * Analyze text with backend
 */
async function analyzeText(text, elementInfo) {
    try {
        // QUICK CHECK FOR AD SIGNATURES LOCALLY to save API calls
        if (text.includes("[IFRAME_AD]") || 
            text.includes("doubleclick.net") || 
            text.includes("googlesyndication") ||
            text.includes("adnxs") ||
            (elementInfo.className && typeof elementInfo.className === 'string' && elementInfo.className.includes("ad-")) || 
            (elementInfo.id && elementInfo.id.includes("google_ads"))) {
            
            return {
                riskScore: 0.85, // High risk for ads
                triggers: [{ word: "Ad Network", score: 0.9, category: "ADVERTISEMENT" }]
            };
        }

        const response = await chrome.runtime.sendMessage({
            type: "ANALYZE_DIALOG",
            text: text,
            dialogType: "DOM_POPUP",
            url: window.location.href,
            elementInfo: elementInfo
        });
        
        return response;
    } catch (error) {
        console.error("[SecureSentinel] Analysis failed:", error);
        return null;
    }
}

/**
 * Show temporal analysis overlay
 */
function showAnalysisOverlay(text, analysis, element) {
    const score = analysis?.riskScore || 0;
    const percentage = Math.round(score * 100);
    
    let riskLevel, riskColor, riskBg;
    if (score > 0.7) {
        riskLevel = "HIGH RISK";
        riskColor = "#ef4444";
        riskBg = "#7f1d1d";
    } else if (score > 0.4) {
        riskLevel = "MODERATE";
        riskColor = "#f59e0b";
        riskBg = "#78350f";
    } else {
        riskLevel = "SAFE";
        riskColor = "#10b981";
        riskBg = "#064e3b";
    }
    
    // Create overlay
    const overlay = document.createElement("div");
    overlay.id = "sentinel-popup-analysis-overlay";
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.95);
        z-index: 2147483647;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        animation: fadeIn 0.3s ease-out;
    `;
    
    overlay.innerHTML = `
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>
        
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 2px solid ${riskColor};
            border-radius: 24px;
            padding: 32px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px ${riskColor}40;
            animation: slideUp 0.4s ease-out;
        ">
            <!-- Header -->
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
                <div style="
                    width: 48px;
                    height: 48px;
                    background: ${riskBg};
                    border: 2px solid ${riskColor};
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 20px ${riskColor}40;
                ">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${riskColor}" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <div>
                    <div style="color: white; font-size: 20px; font-weight: 700; letter-spacing: -0.5px;">
                        SecureSentinel Auto-Scan
                    </div>
                    <div style="color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                        Popup Detected & Analyzed
                    </div>
                </div>
            </div>
            
            <!-- Risk Assessment -->
            <div style="
                background: linear-gradient(135deg, ${riskColor}20, ${riskColor}10);
                border-left: 4px solid ${riskColor};
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 24px;
            ">
                <div style="color: ${riskColor}; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">
                    Temporal Pressure Analysis
                </div>
                <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;">
                    <span style="color: white; font-size: 48px; font-weight: 700; line-height: 1; font-variant-numeric: tabular-nums;">
                        ${percentage}%
                    </span>
                    <span style="color: ${riskColor}; font-size: 16px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                        ${riskLevel}
                    </span>
                </div>
                <div style="background: #0f172a; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="
                        background: ${riskColor};
                        height: 100%;
                        width: ${percentage}%;
                        border-radius: 4px;
                        box-shadow: 0 0 12px ${riskColor};
                        transition: width 1s ease-out;
                    "></div>
                </div>
            </div>
            
            <!-- Trigger Timeline -->
            ${analysis?.triggers && analysis.triggers.length > 0 ? `
                <div style="margin-bottom: 24px;">
                    <div style="color: #94a3b8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        Detected Triggers
                    </div>
                    <div style="display: grid; gap: 8px; max-height: 200px; overflow-y: auto;">
                        ${analysis.triggers.slice(0, 5).map((trigger, i) => `
                            <div style="
                                background: #0f172a;
                                border: 1px solid #1e293b;
                                border-radius: 8px;
                                padding: 12px;
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                animation: slideUp ${0.3 + (i * 0.1)}s ease-out;
                            ">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="
                                        width: 6px;
                                        height: 6px;
                                        background: ${trigger.score > 0.7 ? '#ef4444' : trigger.score > 0.4 ? '#f59e0b' : '#10b981'};
                                        border-radius: 50%;
                                        box-shadow: 0 0 8px ${trigger.score > 0.7 ? '#ef4444' : trigger.score > 0.4 ? '#f59e0b' : '#10b981'};
                                        animation: pulse 2s infinite;
                                    "></div>
                                    <span style="color: white; font-size: 14px; font-weight: 600;">
                                        "${trigger.word}"
                                    </span>
                                    <span style="
                                        background: ${trigger.category === 'URGENCY' ? '#78350f' : trigger.category === 'FEAR' ? '#7f1d1d' : '#1e3a8a'};
                                        color: ${trigger.category === 'URGENCY' ? '#fbbf24' : trigger.category === 'FEAR' ? '#f87171' : '#60a5fa'};
                                        font-size: 9px;
                                        font-weight: 700;
                                        padding: 4px 8px;
                                        border-radius: 4px;
                                        text-transform: uppercase;
                                        letter-spacing: 0.5px;
                                    ">
                                        ${trigger.category}
                                    </span>
                                </div>
                                <span style="color: #64748b; font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums;">
                                    ${Math.round(trigger.score * 100)}%
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <!-- Message Content -->
            <div style="
                background: #0f172a;
                border: 1px solid #1e293b;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 24px;
            ">
                <div style="color: #64748b; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                    Intercepted Message
                </div>
                <div style="color: #cbd5e1; font-size: 13px; line-height: 1.6; max-height: 150px; overflow-y: auto;">
                    ${text.substring(0, 500)}${text.length > 500 ? '...' : ''}
                </div>
            </div>
            
            <!-- Actions -->
            <div style="display: flex; gap: 12px;">
                <button id="sentinel-block-popup" style="
                    flex: 1;
                    background: #1e293b;
                    border: 1px solid #334155;
                    color: white;
                    padding: 14px 24px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                ">
                    Block & Close
                </button>
                <button id="sentinel-allow-popup" style="
                    flex: 1;
                    background: linear-gradient(135deg, ${riskColor}, ${riskColor}dd);
                    border: none;
                    color: white;
                    padding: 14px 24px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s;
                    box-shadow: 0 4px 12px ${riskColor}40;
                ">
                    Allow & Continue
                </button>
            </div>
            
            <!-- Footer -->
            <div style="margin-top: 20px; text-align: center; color: #475569; font-size: 10px; font-weight: 500;">
                Auto-Scan • Powered by ML Engine v4.2.1
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Handle user actions
    document.getElementById('sentinel-block-popup').addEventListener('click', () => {
        // Hide the original popup
        if (element && element.parentNode) {
            element.style.display = 'none';
        }
        overlay.remove();
    });
    
    document.getElementById('sentinel-allow-popup').addEventListener('click', () => {
        overlay.remove();
    });
}

/**
 * Scan for new popups
 */
let lastScanTime = 0;
async function scanForPopups() {
    const now = Date.now();
    
    // Debounce
    if (now - lastScanTime < CONFIG.debounceTime) {
        return;
    }
    lastScanTime = now;

    // EXCEPTION: Do not run generic popup/ad scanner on AI platforms
    // These have their own dedicated scanner (ai-dlp.js) and complex UIs that break easily
    const hostname = window.location.hostname;
    if (hostname.includes('chatgpt.com') || 
        hostname.includes('openai.com') || 
        hostname.includes('claude.ai') || 
        hostname.includes('gemini.google.com')) {
        return;
    }
    
    // Find all potential popup elements
    const selector = POPUP_SELECTORS.join(', ');
    const elements = document.querySelectorAll(selector);
    
    for (const element of elements) {
        // Skip if already analyzed
        if (analyzedElements.has(element)) continue;
        
        // Skip if not visible
        if (!isVisible(element)) continue;

        // SAFEGUARD: Never block critical layout elements unless they are explicitly modals
        const riskyTags = ['MAIN', 'HEADER', 'FOOTER', 'NAV', 'ARTICLE', 'SECTION', 'BODY', 'HTML'];
        const isVitalTag = riskyTags.includes(element.tagName);
        const hasModalClass = element.className && typeof element.className === 'string' && (element.className.includes('modal') || element.className.includes('popup') || element.className.includes('overlay'));
        
        // If it's a vital tag and NOT explicitly a modal class, skip blocking (only analyze)
        const isCriticalLayout = isVitalTag && !hasModalClass;
        
        // Also check for full-page root containers
        const isRootContainer = element.id === 'root' || element.id === 'app' || element.id === '__next';
        
        if (isCriticalLayout || isRootContainer) {
             // Just logging, don't process as popup
             // console.log("[SecureSentinel] Skipping critical element:", element.tagName, element.id);
             continue;
        }
        
        // Extract text
        const text = extractText(element);
        
        // CHECK IF IT IS AN AD CONTAINER (Even if empty/short)
        // If the ID or Class strongly suggests an ad, we want to analyze it regardless of text length
        const isAdContainer = (
            element.id.includes('google_ads') || 
            element.id.includes('gpt') || 
            element.className.includes('ad-') ||
            element.className.includes('ads-') ||
            (text && text.startsWith("[IFRAME_AD]"))
        );

        // Skip if text is too short, UNLESS it's an identified Ad Frame/Container
        if (!isAdContainer && (text.length < CONFIG.minTextLength || text.length > CONFIG.maxTextLength)) {
            // Only mark as analyzed if it actually has content (so we don't skip empty loading containers)
            if (text.length > 5) { 
                analyzedElements.add(element);
            }
            continue;
        }
        
        // Skip if we've already analyzed this exact text recently
        if (analyzedTexts.has(text)) {
            analyzedElements.add(element);
            continue;
        }
        
        // Mark as analyzed
        analyzedElements.add(element);
        analyzedTexts.add(text);
        
        // Clean up old texts (keep only last 50)
        if (analyzedTexts.size > 50) {
            const firstText = analyzedTexts.values().next().value;
            analyzedTexts.delete(firstText);
        }
        
        console.log(`[SecureSentinel] 🔍 Auto-scanning popup: "${text.substring(0, 50)}..."`);
        
        // Analyze with backend (silently - data goes to dashboard, no browser popup)
        const analysis = await analyzeText(text, {
            tagName: element.tagName,
            className: element.className,
            id: element.id
        });
        
        // Log result and BLOCK if risky
        if (analysis && analysis.riskScore > CONFIG.riskThreshold) {
            console.group(`[SecureSentinel] 🛡️ BLOCKING ELEMENT`);
            console.log(`%cRisk Score: ${Math.round(analysis.riskScore * 100)}%`, "color: #ef4444; font-weight: bold");
            console.log(`Element: <${element.tagName.toLowerCase()}>`, element);
            console.log(`Classes: .${Array.from(element.classList).join('.')}`);
            console.log(`ID: #${element.id}`);
            console.log(`Content Preview: "${text.substring(0, 100)}..."`);
            console.groupEnd();
            
            // --- COGNITIVE SHIELD ACTIVATED ---
            try {
                // Create clean placeholder
                const shield = document.createElement('div');
                shield.setAttribute('data-sentinel-shield', 'true');
                shield.style.cssText = `
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: #f8fafc !important;
                    border: 1px dashed #cbd5e1 !important;
                    border-radius: 8px !important;
                    padding: 12px !important;
                    color: #94a3b8 !important;
                    font-family: system-ui, -apple-system, sans-serif !important;
                    font-size: 11px !important;
                    font-weight: 600 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.5px !important;
                    box-shadow: none !important;
                    z-index: ${window.getComputedStyle(element).zIndex} !important;
                    min-height: 60px;
                    width: ${element.offsetWidth > 0 ? element.offsetWidth + 'px' : '100%'};
                    height: ${element.offsetHeight > 0 ? element.offsetHeight + 'px' : 'auto'};
                    margin: ${window.getComputedStyle(element).margin};
                `;
                
                shield.innerHTML = `
                    <div style="display:flex; align-items:center; gap:8px; pointer-events:none;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        </svg>
                        Cognitive Shield Active
                    </div>
                `;
                
                // Inject shield and hide original
                if(element.parentNode) {
                    element.parentNode.insertBefore(shield, element);
                    element.style.display = 'none';
                    element.setAttribute('data-sentinel-blocked', 'true');
                }
            } catch (err) {
                console.error("[SecureSentinel] Failed to inject shield:", err);
                // Fallback: just hide it
                element.style.display = 'none';
            }
        } else {
            console.log(`[SecureSentinel] ✅ Safe popup. Score: ${Math.round((analysis?.riskScore || 0) * 100)}%`);
        }
    }
}

// Initialize observer when DOM is ready
function initializeScanner() {
    if (!document.body) {
        // Wait for body to be available
        setTimeout(initializeScanner, 100);
        return;
    }
    
    // Start periodic scanning
    setInterval(scanForPopups, CONFIG.scanInterval);
    
    // Also scan on DOM mutations (for dynamic content)
    const mutationObserver = new MutationObserver((mutations) => {
        // Check if any new elements were added
        const hasNewElements = mutations.some(mutation => 
            mutation.addedNodes.length > 0
        );
        
        if (hasNewElements) {
            // Debounced scan
            setTimeout(scanForPopups, 200);
        }
    });
    
    // Start observing
    mutationObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Initial scan
    setTimeout(scanForPopups, 1000);
    
    // Fallback: If no popups found after 3 seconds, scan main page content
    setTimeout(async () => {
        if (analyzedTexts.size === 0) {
            console.log("[SecureSentinel] 📄 No popups found, scanning main page content...");
            
            // Try to find the main content area
            // EXCEPTION: Skip on AI platforms
            const hostname = window.location.hostname;
            if (hostname.includes('chatgpt.com') || 
                hostname.includes('openai.com') || 
                hostname.includes('claude.ai') || 
                hostname.includes('gemini.google.com')) {
                return;
            }

            const mainSelectors = ['main', 'article', '[role="main"]', '.content', '#content', '.main-content'];
            let mainContent = null;
            
            for (const sel of mainSelectors) {
                mainContent = document.querySelector(sel);
                if (mainContent) break;
            }
            
            // Fallback to body if no main content found
            if (!mainContent) {
                mainContent = document.body;
            }
            
            const text = extractText(mainContent);
            if (text && text.length >= CONFIG.minTextLength && text.length <= 2000) {
                analyzedTexts.add(text.substring(0, 500)); // Only store first 500 chars
                
                console.log(`[SecureSentinel] 🔍 Scanning page content: "${text.substring(0, 50)}..."`);
                
                const analysis = await analyzeText(text.substring(0, 1000), {
                    tagName: 'PAGE_CONTENT',
                    className: 'main',
                    id: window.location.hostname
                });
                
                if (analysis) {
                    console.log(`[SecureSentinel] 📊 Page analysis: Score ${Math.round(analysis.riskScore * 100)}% → Sent to Dashboard`);
                }
            }
        }
    }, 3000);
    
    console.log("[SecureSentinel] DOM Popup Scanner ready - Auto-scanning enabled");
}

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeScanner);
} else {
    initializeScanner();
}

