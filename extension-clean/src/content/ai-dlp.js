/**
 * SecureSentinel AI Safety Module
 * Prevent accidental leakage of sensitive PII (Personally Identifiable Information)
 * to AI Chatbots like ChatGPT, Gemini, and Claude.
 */

console.log("%c[SecureSentinel] AI Safety Shield Active", "color: #8b5cf6; font-weight: bold");

// --- Configuration ---
const AI_DLP_CONFIG = {
    checkInterval: 1000,
    blockedKeywords: [], // Populated dynamically if needed
    patterns: {
        creditCard: /\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b/,
        ssn: /\b\d{3}-\d{2}-\d{4}\b/,
        email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
        phone: /\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b/,
        // Updated to catch "password is 123", "password 123", "password: 123"
        passwordKeyword: /(?:password|passwd|pwd|secret|key|token)(?:(?:\s+(?:is|for|of))?|[\s-_]*[:=])\s+["']?([^\s"']{3,})/i,
        privateKey: /-----BEGIN (?:RSA )?PRIVATE KEY-----/,
        jwt: /ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*/
    }
};

// --- Selectors for AI Platforms ---
const AI_SELECTORS = {
    chatgpt: {
        input: '#prompt-textarea',
        button: '[data-testid="send-button"]'
    },
    gemini: {
        input: 'div[contenteditable="true"].textarea', // Broad selector for Gemini's rich text editor
        altInput: 'rich-textarea > div[contenteditable="true"]',
        button: '.send-button, [aria-label="Send message"]'
    },
    claude: {
        input: 'div[contenteditable="true"]',
        button: 'button[aria-label="Send Message"]'
    }
};

// --- State ---
let lastCheckedValue = "";

// --- Helper: Detect Platform ---
function getPlatformConfig() {
    const host = window.location.hostname;
    if (host.includes('chatgpt.com') || host.includes('openai.com')) return AI_SELECTORS.chatgpt;
    if (host.includes('gemini.google.com')) return AI_SELECTORS.gemini;
    if (host.includes('claude.ai')) return AI_SELECTORS.claude;
    return null;
}

// --- Helper: Scan Text for PII ---
function scanForPII(text) {
    const findings = [];
    const lowerText = text.toLowerCase();
    
    // === EXPLICIT PATTERNS ===
    if (AI_DLP_CONFIG.patterns.creditCard.test(text)) findings.push("Credit Card Number");
    if (AI_DLP_CONFIG.patterns.privateKey.test(text)) findings.push("Private Encryption Key");
    if (AI_DLP_CONFIG.patterns.passwordKeyword.test(text)) findings.push("Password/Secret");
    
    // === NUMERIC SEQUENCES (Potential PINs, OTPs, Account Numbers) ===
    // PIN-like: 4-6 consecutive digits
    const pinPattern = /\b\d{4,6}\b/g;
    const pinMatches = text.match(pinPattern);
    if (pinMatches && pinMatches.length > 0) {
        // Check if it's in a suspicious context
        const suspiciousContexts = [
            'pin', 'otp', 'code', 'verification', 'my number', 'account number',
            'password', 'passcode', 'security code', 'atm', 'debit', 'bank'
        ];
        
        const hasSuspiciousContext = suspiciousContexts.some(ctx => lowerText.includes(ctx));
        
        // Also flag if someone says "it's 1234" or "the code is 5678"
        const implicitPatterns = [
            /(?:it'?s|is|was)\s+\d{4,6}/i,
            /(?:the|my)\s+(?:code|pin|number|password)\s+(?:is|was)?\s*\d{4,6}/i
        ];
        const hasImplicitPattern = implicitPatterns.some(p => p.test(text));
        
        if (hasSuspiciousContext || hasImplicitPattern) {
            findings.push("PIN/OTP/Account Number");
        }
    }
    
    // === CREDENTIAL KEYWORDS (Implicit) ===
    // Detect phrases like "my gmail password", "bank login", "email password" even without explicit value
    const credentialKeywords = [
        /(?:my|the)\s+(?:gmail|email|bank|facebook|instagram|twitter|account)\s+(?:password|login|credentials?)/i,
        /(?:bank|atm|debit|credit)\s+(?:pin|password|code)/i,
        /(?:login|signin|username)\s+(?:and|&)?\s+password/i,
        /(?:email|gmail|yahoo|outlook)\s+(?:and|&)?\s+password/i
    ];
    
    const hasCredentialKeyword = credentialKeywords.some(pattern => pattern.test(text));
    if (hasCredentialKeyword) {
        findings.push("Account Credentials Reference");
    }
    
    // === EMAIL + PASSWORD COMBINATION ===
    if (AI_DLP_CONFIG.patterns.email.test(text)) {
        // If email appears with password-like words or numeric sequences
        if (lowerText.includes("password") || 
            lowerText.includes("pass") || 
            /\b\w{8,}\b/.test(text)) { // 8+ char alphanumeric (potential password)
            findings.push("Email & Password Combination");
        }
    }
    
    // === API KEYS & TOKENS (Expanded) ===
    if (AI_DLP_CONFIG.patterns.jwt.test(text)) findings.push("JWT Token");
    
    // Generic API key patterns (long alphanumeric strings)
    const apiKeyPattern = /\b[A-Za-z0-9_-]{32,}\b/;
    if (apiKeyPattern.test(text) && (lowerText.includes('api') || lowerText.includes('key') || lowerText.includes('token'))) {
        findings.push("API Key/Token");
    }
    
    // === PHONE NUMBERS (If mentioned with sensitive context) ===
    if (AI_DLP_CONFIG.patterns.phone.test(text)) {
        const phoneContexts = ['my number', 'phone', 'mobile', 'contact', 'otp', 'verification'];
        if (phoneContexts.some(ctx => lowerText.includes(ctx))) {
            findings.push("Phone Number");
        }
    }

    return findings;
}

// --- UI: Warning Modal ---
function showBlockingModal(findings, onAllow, onCancel) {
    // Remove existing
    const existing = document.getElementById('sentinel-ai-blocker');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'sentinel-ai-blocker';
    overlay.style.cssText = `
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(8px);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: -apple-system, sans-serif;
    `;

    const modal = document.createElement('div');
    modal.style.cssText = `
        background: #fff;
        padding: 32px;
        border-radius: 20px;
        width: 100%;
        max-width: 480px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        animation: sentinelPopIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        border: 1px solid #e2e8f0;
    `;

    // Inject animation
    const style = document.createElement('style');
    style.innerHTML = `@keyframes sentinelPopIn { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }`;
    document.head.appendChild(style);

    modal.innerHTML = `
        <div style="display: flex; align-items: start; gap: 20px; margin-bottom: 24px;">
            <div style="width: 48px; height: 48px; border-radius: 12px; background: #fee2e2; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
            </div>
            <div>
                <h2 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 700; color: #1e293b;">Sensitive Data Detected</h2>
                <p style="margin: 0; font-size: 15px; line-height: 1.5; color: #64748b;">
                    SecureSentinel flagged this message because it appears to contain your 
                    <strong style="color: #dc2626;">${findings.join(', ')}</strong>.
                </p>
                <p style="margin: 12px 0 0 0; font-size: 13px; color: #94a3b8;">
                    Sharing PII with AI models puts your data at risk of being stored or trained upon.
                </p>
            </div>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button id="sentinel-cancel-send" style="
                padding: 10px 20px;
                border: 1px solid #cbd5e1;
                background: #fff;
                color: #475569;
                font-weight: 600;
                border-radius: 10px;
                cursor: pointer;
                transition: all 0.2s;
            ">Back to Edit</button>
            <button id="sentinel-force-send" style="
                padding: 10px 20px;
                border: none;
                background: #dc2626;
                color: #fff;
                font-weight: 600;
                border-radius: 10px;
                cursor: pointer;
                box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.2);
                transition: all 0.2s;
            ">Send Anyway</button>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    document.getElementById('sentinel-cancel-send').addEventListener('click', () => {
        overlay.remove();
        onCancel();
    });

    document.getElementById('sentinel-force-send').addEventListener('click', () => {
        overlay.remove();
        onAllow();
    });

    // Hover effects via JS since inline CSS is limited for pseudo-classes
    const btnCancel = document.getElementById('sentinel-cancel-send');
    const btnForce = document.getElementById('sentinel-force-send');

    btnCancel.onmouseover = () => { btnCancel.style.background = '#f8fafc'; };
    btnCancel.onmouseout = () => { btnCancel.style.background = '#fff'; };

    btnForce.onmouseover = () => { btnForce.style.background = '#b91c1c'; };
    btnForce.onmouseout = () => { btnForce.style.background = '#dc2626'; };
}

// --- Main Logic: Interceptor ---
function attachInterceptors() {
    const config = getPlatformConfig();
    if (!config) return;

    // We attach a listener to the window capture phase to catch 'Enter' before the text area
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            const activeEl = document.activeElement;
            // Check if active element matches our target input selectors
            const isTarget = activeEl.matches(config.input) || 
                             (config.altInput && activeEl.matches(config.altInput));
            
            if (isTarget) {
                const text = activeEl.innerText || activeEl.value || "";
                
                // Allow empty or very short messages
                if (text.length < 5) return;

                const sensitiveData = scanForPII(text);
                
                if (sensitiveData.length > 0) {
                    console.log("[SecureSentinel] Blocked sensitive input:", sensitiveData);
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();

                    // NUCLEAR OPTION: Clear the input immediately to prevent leak
                    // Save it first so we can restore it if user allows
                    activeEl.dataset.sentinelBackup = text;
                    if (activeEl.isContentEditable) {
                        activeEl.innerHTML = ''; 
                        activeEl.innerText = ''; // React sometimes needs this
                    } else {
                        activeEl.value = '';
                    }
                    
                    // Trigger an input event so React knows it's empty
                    activeEl.dispatchEvent(new Event('input', { bubbles: true }));

                    showBlockingModal(
                        sensitiveData, 
                        () => {
                            // User clicked 'Send Anyway'
                            // Restore text
                            if (activeEl.dataset.sentinelBackup) {
                                if (activeEl.isContentEditable) {
                                    activeEl.innerText = activeEl.dataset.sentinelBackup;
                                } else {
                                    activeEl.value = activeEl.dataset.sentinelBackup;
                                }
                                activeEl.dispatchEvent(new Event('input', { bubbles: true }));
                            }

                            activeEl.dataset.sentinelBypass = "true";
                            
                            // Dispatch new Enter
                            const newEvent = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                charCode: 13,
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            activeEl.dispatchEvent(newEvent);
                            
                            setTimeout(() => delete activeEl.dataset.sentinelBypass, 500);
                        },
                        () => {
                            // Cancel - Restore text and focus
                            if (activeEl.dataset.sentinelBackup) {
                                if (activeEl.isContentEditable) {
                                    activeEl.innerText = activeEl.dataset.sentinelBackup;
                                } else {
                                    activeEl.value = activeEl.dataset.sentinelBackup;
                                }
                                activeEl.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                            activeEl.focus();
                        }
                    );
                } else {
                    if (activeEl.dataset.sentinelBypass) return;
                }
            }
        }
    }, true);

    // Click Listener for Send Button
    document.addEventListener('click', (e) => {
        const target = e.target.closest(config.button);
        if (target) {
            const inputEl = document.querySelector(config.input) || document.querySelector(config.altInput);
            if (!inputEl) return;

            const text = inputEl.innerText || inputEl.value || "";
            if (text.length < 5) return;

            const sensitiveData = scanForPII(text);
            
            if (sensitiveData.length > 0 && !inputEl.dataset.sentinelBypass) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();

                // NUCLEAR OPTION: Clear input
                inputEl.dataset.sentinelBackup = text;
                if (inputEl.isContentEditable) {
                    inputEl.innerHTML = '';
                    inputEl.innerText = '';
                } else {
                    inputEl.value = '';
                }
                inputEl.dispatchEvent(new Event('input', { bubbles: true }));

                showBlockingModal(
                    sensitiveData,
                    () => {
                        // Restore
                        if (inputEl.dataset.sentinelBackup) {
                            if (inputEl.isContentEditable) inputEl.innerText = inputEl.dataset.sentinelBackup;
                            else inputEl.value = inputEl.dataset.sentinelBackup;
                            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                        }

                        inputEl.dataset.sentinelBypass = "true";
                        target.click(); 
                        setTimeout(() => delete inputEl.dataset.sentinelBypass, 500);
                    },
                    () => {
                        // Restore
                         if (inputEl.dataset.sentinelBackup) {
                            if (inputEl.isContentEditable) inputEl.innerText = inputEl.dataset.sentinelBackup;
                            else inputEl.value = inputEl.dataset.sentinelBackup;
                            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                        inputEl.focus();
                    }
                );
            }
        }
    }, true);

    // --- RESPONSE BLOCKER (Experimental) ---
    // Watches for the 'Stop generating' button or new messages if we think a leak happened
    const responseObserver = new MutationObserver((mutations) => {
        // Broad check for AI response containers
        const stopBtn = document.querySelector('[aria-label="Stop generating"]') || document.querySelector('.ec-stop-generating');
        if (stopBtn && window.sentinelFlagged) {
             console.log("[SecureSentinel] Emergency Stop Triggered");
             stopBtn.click();
             window.sentinelFlagged = false;
        }
    });
    
    responseObserver.observe(document.body, { childList: true, subtree: true });
}

// Start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachInterceptors);
} else {
    attachInterceptors();
}
