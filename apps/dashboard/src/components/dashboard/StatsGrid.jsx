"use client";

import React, { useState, useMemo } from "react";
import { ChevronDown } from "lucide-react";
import { STATS_DATA } from "@/data";
import { useFilters } from "@/context";

export default function StatsGrid() {
  const [isOpen, setIsOpen] = useState(true);
  const { selectedDispositions } = useFilters();

  const filteredStats = useMemo(() => {
    // If specific disposition titles match selected dispositions, highlight or filter
    if (!selectedDispositions || selectedDispositions.length === 0) {
      return STATS_DATA;
    }
    return STATS_DATA;
  }, [selectedDispositions]);

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