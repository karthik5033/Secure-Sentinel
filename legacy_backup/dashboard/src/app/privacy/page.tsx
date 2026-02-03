"use client";

import { Lock, EyeOff, Hash, FileJson } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Privacy Center</h1>
        <p className="text-muted-foreground">Transparency report on how your data is handled.</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
          <div className="p-4 rounded-lg border border-border bg-card">
              <EyeOff className="w-6 h-6 text-emerald-500 mb-2" />
              <h3 className="font-medium">No PII Collected</h3>
              <p className="text-xs text-muted-foreground mt-1">We do not store emails, usernames, or passwords. All analysis is local or anonymized.</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-card">
              <Hash className="w-6 h-6 text-emerald-500 mb-2" />
              <h3 className="font-medium">Hashed Domains</h3>
              <p className="text-xs text-muted-foreground mt-1">URLs are converted to cryptographic hashes (SHA-256) before leaving your device.</p>
          </div>
      </div>

      <div className="p-6 rounded-xl border border-border bg-card space-y-4">
         <h3 className="text-base font-medium">What We Store</h3>
         <div className="space-y-3">
             <div className="flex items-center justify-between p-3 bg-secondary/30 rounded border border-border/50">
                 <div className="flex items-center gap-3">
                    <FileJson size={16} className="text-muted-foreground" />
                    <span className="text-sm font-mono">risk_events.json</span>
                 </div>
                 <div className="text-xs text-muted-foreground">142 KB</div>
             </div>
             <p className="text-xs text-muted-foreground">
                 This file contains the aggregated log of threats blocked. It links a risk score to a timestamp. 
                 It does <span className="text-foreground font-medium">not</span> contain page content.
             </p>
         </div>
         
         <div className="pt-4 border-t border-border/50">
             <button className="text-sm text-primary hover:underline">Download my data archive</button>
         </div>
      </div>
    </div>
  );
}
