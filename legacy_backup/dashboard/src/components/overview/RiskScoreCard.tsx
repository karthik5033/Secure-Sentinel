"use client";

import { motion } from "framer-motion";
import { ShieldCheck, ShieldAlert, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

export function RiskScoreCard({ score }: { score: number }) {
  // score is 0-1 (risk). Safety Score = (1 - risk) * 100
  const safetyScore = Math.round((1 - score) * 100);
  
  let riskLevel = "Safe";
  let color = "text-emerald-500";
  let bgColor = "bg-emerald-500/10";
  let Icon = ShieldCheck;

  if (score > 0.7) {
    riskLevel = "Critical";
    color = "text-rose-500";
    bgColor = "bg-rose-500/10";
    Icon = ShieldAlert;
  } else if (score > 0.4) {
    riskLevel = "Moderate";
    color = "text-amber-500";
    bgColor = "bg-amber-500/10";
    Icon = Shield;
  }

  return (
    <div className="p-6 rounded-xl border border-border bg-card shadow-sm relative overflow-hidden">
      <div className="absolute top-0 right-0 p-32 bg-primary/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
      
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Safety Health</h3>
          <p className="text-xs text-muted-foreground mt-1">Based on last 30 days activity</p>
        </div>
        <div className={cn("p-2 rounded-lg", bgColor)}>
          <Icon className={cn("w-6 h-6", color)} />
        </div>
      </div>

      <div className="flex items-baseline gap-2 mt-2">
        <span className={cn("text-4xl font-bold tracking-tight", color)}>
          {safetyScore}
        </span>
        <span className="text-sm text-muted-foreground">/ 100</span>
      </div>

      <div className="mt-4">
        <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${safetyScore}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={cn("h-full rounded-full", color.replace("text-", "bg-"))}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs">
          <span className="font-medium text-foreground">{riskLevel} Status</span>
          <span className="text-muted-foreground">Top 10% of users</span>
        </div>
      </div>
    </div>
  );
}
