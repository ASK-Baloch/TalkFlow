"use client";

import React, { useState } from "react";
import { PhoneIncoming, PhoneCall, ArrowRight, X } from "lucide-react";
import { useAuth } from "@/context";
import { getRoleKey } from "@/config/navigation";

export default function IncomingTransferBanner({ onNavigate }) {
  const { role, user } = useAuth();
  const rawRole = user?.role || user?.type || role || "MASTER_ADMIN";
  const roleKey = getRoleKey(rawRole);

  const [dismissed, setDismissed] = useState(false);

  // Per TalkFlow.md §8: Banner is specifically for VERIFIER role & MASTER_ADMIN
  const isAuthorizedRole = roleKey === "VERIFIER" || roleKey === "MASTER_ADMIN";

  const liveIncoming = {
    callId: "CALL-2026-98124",
    prospectName: "Robert D. Miller",
    phone: "+1 (555) 392-8104",
    state: "FL (Miami)",
    age: 67,
    campaign: "Medicare Advantage Dual-Eligible Q3",
    status: "QUALIFIED_WAITING_VERIFIER",
  };

  if (!isAuthorizedRole || dismissed) return null;

  return (
    <div className="w-full bg-emerald-800 text-white border-b border-emerald-900 px-4 py-2 text-xs transition-colors z-40">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-emerald-900 text-emerald-200 shrink-0 border border-emerald-700">
            <PhoneIncoming className="h-3.5 w-3.5" />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="rounded bg-emerald-900 px-1.5 py-0.5 text-[10px] font-bold tracking-wider uppercase text-emerald-200 border border-emerald-700">
                LIVE VERIFIER INCOMING TRANSFER
              </span>
              <span className="font-mono text-[11px] text-emerald-200">{liveIncoming.callId}</span>
            </div>
            <p className="font-semibold text-white mt-0.5">
              Incoming Lead: {liveIncoming.prospectName} ({liveIncoming.phone}) • Age {liveIncoming.age} • {liveIncoming.state}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => {
              if (onNavigate) onNavigate("verifier", null);
            }}
            className="flex items-center gap-1.5 rounded-md bg-white px-3 py-1 text-xs font-bold text-emerald-900 hover:bg-emerald-50 border border-emerald-200 transition-colors"
          >
            <PhoneCall className="h-3.5 w-3.5 text-emerald-700" />
            <span>Open Verifier Workspace</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            onClick={() => setDismissed(true)}
            title="Dismiss Banner"
            className="rounded-md p-1 text-emerald-200 hover:bg-emerald-900 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
