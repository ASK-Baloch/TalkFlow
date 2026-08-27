"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

const STATS_DATA = [
  { id: "1", title: "TOTAL CALLS", value: "399.6K", color: "emerald", count: "399,600 Total Dialed" },
  { id: "2", title: "AVG. CALL DURATION", value: "17.3", unit: "s", color: "neutral", count: "17.3 Seconds / Call" },
  { id: "3", title: "SALE", value: "24.9K", color: "emerald", count: "24,900 Total Qualified Leads" },
  { id: "4", title: "SALE %", value: "6.24", unit: "%", color: "emerald", count: "6.24% of Answered Calls" },
  { id: "5", title: "AVG. CONVERSION DU...", value: "54.4", unit: "s", color: "neutral", count: "54.4 Seconds to Qualify" },
  { id: "6", title: "NO. OF CALLS PER AGE...", value: "53.05", color: "neutral", count: "53.05 Calls / Agent" },
  { id: "7", title: "DAIR %", value: "1", unit: "%", color: "emerald", count: "1% Dead Air Rate" },
  { id: "8", title: "A", value: "15.0K", color: "emerald", count: "15,000 Answering Machine Passed" },
  { id: "9", title: "DC", value: "19.1K", color: "rose", count: "19,100 Disconnected Lines" },
  { id: "10", title: "DNC", value: "8,301", color: "rose", count: "8,301 Do Not Call Requests" },
  { id: "11", title: "DNQ", value: "10.0K", color: "rose", count: "10,000 Does Not Qualify" },
];

export default function StatsGrid() {
  const [isOpen, setIsOpen] = useState(true);

  const getColorClasses = (color) => {
    switch (color) {
      case "emerald":
        return "text-[#10b981] dark:text-[#22c55e]";
      case "rose":
        return "text-[#ef4444] dark:text-[#f87171]";
      default:
        return "text-neutral-900 dark:text-neutral-100";
    }
  };

  return (
    <div className="flex w-full flex-col gap-3">
      {/* Collapsible Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-fit select-none items-center gap-1.5 text-xs font-bold tracking-wider text-neutral-500 transition-colors hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white"
      >
        <ChevronDown
          className={`h-4 w-4 transition-transform duration-200 ${
            isOpen ? "rotate-0" : "-rotate-90"
          }`}
        />
        <span>STATS</span>
      </button>

      {/* Responsive 4-Column Grid inside 55% Viewport */}
      {isOpen && (
        <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {STATS_DATA.map((item) => (
            <div
              key={item.id}
              title={item.count}
              className="group relative flex flex-col justify-between rounded-xl border border-neutral-200 bg-white p-3.5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-neutral-400 hover:shadow-md dark:border-[#1e1e1e] dark:bg-[#0d0d0d] dark:hover:border-neutral-700"
            >
              <span className="truncate text-[10px] font-semibold uppercase tracking-wider text-neutral-500 transition-colors group-hover:text-neutral-800 dark:text-neutral-400 dark:group-hover:text-neutral-200">
                {item.title}
              </span>
              <div className="mt-2 flex items-baseline gap-1">
                <span className={`text-xl font-bold tracking-tight sm:text-2xl ${getColorClasses(item.color)}`}>
                  {item.value}
                </span>
                {item.unit && (
                  <span className={`text-xs font-medium ${getColorClasses(item.color)}`}>
                    {item.unit}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}