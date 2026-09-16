"use client";

import React from "react";
import {
  TrendingUp,
  PhoneCall,
  ShieldCheck,
  ShieldAlert,
  Play,
  Pause,
  Clock,
  User,
  FileText,
  Radio,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

// StatCard Primitive per §10 Domain Components
export function StatCard({ title, value, change, trend = "up", icon: Icon }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-4 dark:border-[#1a1a1a] dark:bg-[#09090b] shadow-xs">
      <div className="flex items-center justify-between">
        <span className="text-xs text-neutral-500 dark:text-neutral-400 font-medium">{title}</span>
        {Icon && <Icon className="h-4 w-4 text-neutral-400" />}
      </div>
      <div className="mt-2 flex items-baseline justify-between">
        <span className="text-xl font-bold text-neutral-900 dark:text-white font-mono">{value}</span>
        {change && (
          <span
            className={`flex items-center text-xs font-semibold ${
              trend === "up" ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"
            }`}
          >
            {change}
          </span>
        )}
      </div>
    </div>
  );
}

// Consent Evidence Card
export function ConsentEvidenceCard({ consentCaptured = true, timestamp = "14:22:05" }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-neutral-50/60 p-3 dark:border-neutral-800 dark:bg-[#121215] text-xs space-y-1">
      <div className="flex items-center justify-between">
        <span className="font-bold text-neutral-900 dark:text-white flex items-center gap-1.5">
          <ShieldCheck className="h-4 w-4 text-emerald-600" /> Verbal TCPA Consent Captured
        </span>
        <span className="font-mono text-[10px] text-neutral-400">{timestamp}</span>
      </div>
      <p className="text-[11px] text-neutral-600 dark:text-neutral-400">
        Caller affirmatively agreed to Medicare qualification and licensed agent call transfer.
      </p>
    </div>
  );
}

// Alert Banner Primitive
export function AlertBanner({ title, description, severity = "warning" }) {
  const styles = {
    critical: "bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-950/40 dark:border-rose-900/40 dark:text-rose-300",
    warning: "bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-900/40 dark:text-amber-300",
    info: "bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-950/40 dark:border-blue-900/40 dark:text-blue-300",
  };

  return (
    <div className={`rounded-lg border p-3 text-xs ${styles[severity] || styles.warning}`}>
      <div className="font-bold flex items-center gap-1.5">
        <AlertTriangle className="h-4 w-4 shrink-0" />
        <span>{title}</span>
      </div>
      {description && <p className="mt-1 text-[11px] opacity-90">{description}</p>}
    </div>
  );
}
