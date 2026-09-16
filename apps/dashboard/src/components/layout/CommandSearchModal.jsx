"use client";

import React, { useState, useEffect } from "react";
import { Search, X, Megaphone, PhoneCall, Contact, FileText, ArrowRight, CornerDownLeft } from "lucide-react";

export default function CommandSearchModal({ isOpen, onClose, onNavigate }) {
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Trigger open via parent
        }
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sampleResults = [
    {
      type: "call",
      id: "CALL-2026-98124",
      title: "Robert D. Miller — (555) 392-8104",
      subtitle: "Qualified • Medicare Advantage Q3 • 4m 12s",
      tab: "calls",
      action: "CALL-2026-98124",
      icon: PhoneCall,
    },
    {
      type: "lead",
      id: "LD-88412",
      title: "Eleanor Vance — (555) 234-9011",
      subtitle: "Imported Lead • Miami, FL • Status: Qualified",
      tab: "leads",
      action: "LD-88412",
      icon: Contact,
    },
    {
      type: "campaign",
      id: "CMP-001",
      title: "Medicare Advantage Dual-Eligible Q3",
      subtitle: "Active Outbound • 1,420 calls placed • 98.4% transfer rate",
      tab: "campaigns",
      action: "CMP-001",
      icon: Megaphone,
    },
    {
      type: "script",
      id: "SCR-204",
      title: "Medicare Dual-Eligible Script v2.4",
      subtitle: "Approved & Active • 8 state loops • 65ms TTS latency",
      tab: "scripts",
      action: "SCR-204",
      icon: FileText,
    },
  ];

  const filteredResults = searchQuery.trim()
    ? sampleResults.filter(
        (item) =>
          item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.subtitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.id.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : sampleResults;

  const handleSelect = (tab, action) => {
    if (onNavigate) {
      onNavigate(tab, action);
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/60 backdrop-blur-xs transition-all animate-in fade-in duration-150">
      <div
        className="w-full max-w-2xl overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-2xl dark:border-neutral-800 dark:bg-[#0d0d0f]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Header */}
        <div className="flex items-center gap-3 border-b border-neutral-200 px-4 py-3.5 dark:border-neutral-800">
          <Search className="h-5 w-5 text-neutral-400 shrink-0" />
          <input
            type="text"
            autoFocus
            placeholder="Search calls, leads, campaigns, and scripts... (Phase 1 reserved slot)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 bg-transparent text-sm font-medium text-neutral-900 placeholder-neutral-400 focus:outline-none dark:text-white"
          />
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2">
          <div className="px-3 py-1.5 text-[11px] font-bold text-neutral-400 uppercase tracking-wider">
            Phase 1 Global Search Catalogue
          </div>

          {filteredResults.length === 0 ? (
            <div className="p-8 text-center text-xs text-neutral-500">
              No matching records found for "{searchQuery}".
            </div>
          ) : (
            <div className="space-y-1">
              {filteredResults.map((res) => {
                const ResIcon = res.icon;
                return (
                  <button
                    key={res.id}
                    type="button"
                    onClick={() => handleSelect(res.tab, res.action)}
                    className="flex w-full items-center justify-between rounded-lg p-3 text-left transition-colors hover:bg-neutral-100 dark:hover:bg-[#161619]"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400">
                        <ResIcon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-neutral-900 dark:text-white">
                          {res.title}
                        </p>
                        <p className="text-[11px] text-neutral-500 dark:text-neutral-400">
                          {res.subtitle}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 text-[11px] font-semibold text-blue-600 dark:text-blue-400 opacity-0 group-hover:opacity-100">
                      <span>Jump</span>
                      <CornerDownLeft className="h-3 w-3" />
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer Shortcut Bar */}
        <div className="flex items-center justify-between border-t border-neutral-100 bg-neutral-50/80 px-4 py-2 text-[11px] text-neutral-500 dark:border-neutral-800 dark:bg-[#111114]">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="rounded border border-neutral-300 bg-white px-1.5 py-0.5 text-[10px] dark:border-neutral-700 dark:bg-neutral-800">
                ↑↓
              </kbd>
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="rounded border border-neutral-300 bg-white px-1.5 py-0.5 text-[10px] dark:border-neutral-700 dark:bg-neutral-800">
                ↵
              </kbd>
              Select
            </span>
          </div>

          <span className="font-mono">Backend Endpoint: GET /api/v1/search</span>
        </div>
      </div>
    </div>
  );
}
