/**
 * SecureSentinel Dialog Interceptor
 * Captures browser alerts, confirms, prompts, and notifications
 * Sends them to temporal analysis engine for real-time threat assessment
 */

console.log("%c[SecureSentinel] Dialog Interceptor Active", "color: #10b981; font-weight: bold");

// Store original functions
const originalAlert = window.alert;
const originalConfirm = window.confirm;
const originalPrompt = window.prompt;

// Track analyzed dialogs to avoid duplicates
const analyzedDialogs = new Set();

/**
 * Analyze text with temporal analysis engine
 */
async function analyzeDialogText(text, type) {
    try {
        const response = await chrome.runtime.sendMessage({
            type: "ANALYZE_DIALOG",
            text: text,
            dialogType: type,
            url: window.location.href
        });
        
        return response;
    } catch (error) {
        console.error("[SecureSentinel] Dialog analysis failed:", error);
        return null;
    }
}

/**
 * Show temporal analysis overlay
 */
function showTemporalOverlay(text, analysis, dialogType) {
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
    overlay.id = "sentinel-temporal-overlay";
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
                        SecureSentinel Temporal Analysis
                    </div>
                    <div style="color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                        ${dialogType} Intercepted
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
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
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
                    ${text}
                </div>
            </div>
            
            <!-- Actions -->
            <div style="display: flex; gap: 12px;">
                <button onclick="this.closest('#sentinel-temporal-overlay').remove(); window.sentinelDialogResult = false;" style="
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
                <button onclick="this.closest('#sentinel-temporal-overlay').remove(); window.sentinelDialogResult = true;" style="
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
                    Proceed Anyway
                </button>
            </div>
            
            <!-- Footer -->
            <div style="margin-top: 20px; text-align: center; color: #475569; font-size: 10px; font-weight: 500;">
                Real-time Temporal Analysis • Powered by ML Engine v4.2.1
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Wait for user decision
    return new Promise((resolve) => {
        const checkResult = setInterval(() => {
            if (window.sentinelDialogResult !== undefined) {
                clearInterval(checkResult);
                const result = window.sentinelDialogResult;
                delete window.sentinelDialogResult;
                resolve(result);
            }
        }, 100);
    });
}

/**
 * Intercept window.alert
 */
window.alert = async function(message) {
    const text = String(message);
    
    if (analyzedDialogs.has(text)) {
        return originalAlert.call(window, message);
    }
    
    analyzedDialogs.add(text);
    console.log("[SecureSentinel] Alert intercepted:", text);
    
    const analysis = await analyzeDialogText(text, "ALERT");
    
    if (analysis && analysis.riskScore > 0.3) {
        await showTemporalOverlay(text, analysis, "Alert Dialog");
    } else {
        originalAlert.call(window, message);
    }
};

/**
 * Intercept window.confirm
 */
window.confirm = async function(message) {
    const text = String(message);
    
    if (analyzedDialogs.has(text)) {
        return originalConfirm.call(window, message);
    }
    
    analyzedDialogs.add(text);
    console.log("[SecureSentinel] Confirm intercepted:", text);
    
    const analysis = await analyzeDialogText(text, "CONFIRM");
    
    if (analysis && analysis.riskScore > 0.3) {
        return await showTemporalOverlay(text, analysis, "Confirm Dialog");
    } else {
        return originalConfirm.call(window, message);
    }
};

/**
 * Intercept window.prompt
 */
window.prompt = async function(message, defaultValue) {
    const text = String(message);
    
    if (analyzedDialogs.has(text)) {
        return originalPrompt.call(window, message, defaultValue);
    }
    
    analyzedDialogs.add(text);
    console.log("[SecureSentinel] Prompt intercepted:", text);
    
    const analysis = await analyzeDialogText(text, "PROMPT");
    
    if (analysis && analysis.riskScore > 0.5) {
        const proceed = await showTemporalOverlay(text, analysis, "Prompt Dialog");
        if (proceed) {
            return originalPrompt.call(window, message, defaultValue);
        } else {
            return null;
        }
    } else {
        return originalPrompt.call(window, message, defaultValue);
    }
};

/**
 * Intercept Notification API
 */
if (window.Notification) {
    const OriginalNotification = window.Notification;
    
    window.Notification = function(title, options) {
        const text = `${title} ${options?.body || ''}`;
        
        console.log("[SecureSentinel] Notification intercepted:", text);
        
        // Analyze in background
        analyzeDialogText(text, "NOTIFICATION").then(analysis => {
            if (analysis && analysis.riskScore > 0.6) {
                console.warn("[SecureSentinel] High-risk notification blocked:", text);
                // Show our overlay instead
                showTemporalOverlay(text, analysis, "Notification");
            } else {
                // Allow notification
                return new OriginalNotification(title, options);
            }
        });
        
        // Return dummy notification to prevent errors
        return {
            close: () => {},
            addEventListener: () => {}
        };
    };
    
    // Copy static properties
    window.Notification.permission = OriginalNotification.permission;
    window.Notification.requestPermission = OriginalNotification.requestPermission.bind(OriginalNotification);
}

console.log("[SecureSentinel] Dialog interception ready");
