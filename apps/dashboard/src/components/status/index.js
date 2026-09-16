"use client";

import React from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  PhoneCall,
  ShieldCheck,
  ShieldAlert,
  Radio,
  Activity,
} from "lucide-react";

// Generic Status Badge: Icon + Label + Colour per TalkFlow.md §9.2
export function StatusBadge({ icon: Icon, label, variant = "neutral", className = "" }) {
  const variantStyles = {
    success: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-900/40",
    danger: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-900/40",
    warning: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-900/40",
    info: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-900/40",
    neutral: "bg-neutral-100 text-neutral-700 border-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:border-neutral-700",
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${variantStyles[variant] || variantStyles.neutral} ${className}`}>
      {Icon && <Icon className="h-3 w-3 shrink-0" />}
      <span>{label}</span>
    </span>
  );
}

// Qualification Badge: Qualified | Pending | Ineligible
export function QualificationBadge({ status }) {
  const norm = String(status || "").toLowerCase();
  if (norm.includes("qualif")) {
    return <StatusBadge icon={CheckCircle2} label="Qualified" variant="success" />;
  }
  if (norm.includes("inelig") || norm.includes("disqual")) {
    return <StatusBadge icon={XCircle} label="Ineligible" variant="danger" />;
  }
  return <StatusBadge icon={Clock} label="Pending Review" variant="warning" />;
}

// System Health Badge: Healthy | Degraded | Offline
export function HealthBadge({ status }) {
  const norm = String(status || "").toLowerCase();
  if (norm.includes("health") || norm.includes("online")) {
    return <StatusBadge icon={CheckCircle2} label="Healthy" variant="success" />;
  }
  if (norm.includes("degrad") || norm.includes("warn")) {
    return <StatusBadge icon={AlertTriangle} label="Degraded" variant="warning" />;
  }
  return <StatusBadge icon={XCircle} label="Offline" variant="danger" />;
}

// Script Status Badge: Approved | Active | Draft | In Review
export function ScriptStatusBadge({ status }) {
  const norm = String(status || "").toLowerCase();
  if (norm.includes("active")) {
    return <StatusBadge icon={Radio} label="Active" variant="info" />;
  }
  if (norm.includes("approv")) {
    return <StatusBadge icon={CheckCircle2} label="Approved" variant="success" />;
  }
  if (norm.includes("draft")) {
    return <StatusBadge icon={Clock} label="Draft" variant="neutral" />;
  }
  return <StatusBadge icon={AlertTriangle} label="In Review" variant="warning" />;
}

// Global Connection Indicator per TalkFlow.md §8
export function ConnectionIndicator({ status = "connected" }) {
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[11px] font-semibold ${
        status === "connected"
          ? "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/40 dark:bg-emerald-950/40 dark:text-emerald-300"
          : status === "reconnecting"
          ? "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-300"
          : "border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-900/40 dark:bg-rose-950/40 dark:text-rose-300"
      }`}
    >
      <span className="relative flex h-2 w-2">
        {status === "connected" && (
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
        )}
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            status === "connected" ? "bg-emerald-500" : status === "reconnecting" ? "bg-amber-500" : "bg-rose-500"
          }`}
        />
      </span>
      <span>Live: {status === "connected" ? "Connected" : status === "reconnecting" ? "Reconnecting" : "Disconnected"}</span>
    </div>
  );
}
