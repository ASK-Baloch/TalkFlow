"use client";

import React, { useState } from "react";
import { ChevronDown, Clock, RotateCw, X } from "lucide-react";

const INITIAL_TAGS = ["DNC", "DNQ", "CLBK", "SALE", "DAIR", "RAXFER", "XFER"];

export default function FilterToolbar({ onRefresh }) {
  const [selectedTags, setSelectedTags] = useState(INITIAL_TAGS);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const removeTag = (tagToRemove) => {
    setSelectedTags((prev) => prev.filter((tag) => tag !== tagToRemove));
  };

  const handleRefreshClick = () => {
    setIsRefreshing(true);
    if (onRefresh) onRefresh();
    setTimeout(() => setIsRefreshing(false), 600);
  };

  const buttonStyle =
    "flex items-center gap-1.5 rounded-md border border-neutral-300 bg-neutral-100 px-3 py-1.5 text-neutral-700 transition-colors hover:border-neutral-400 hover:bg-neutral-200 hover:text-neutral-900 dark:border-[#2a2a2a] dark:bg-[#141414] dark:text-neutral-300 dark:hover:border-neutral-600 dark:hover:bg-[#1a1a1a] dark:hover:text-white";

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-neutral-200 bg-neutral-50 px-6 py-2.5 text-xs transition-colors duration-200 dark:border-[#1a1a1a] dark:bg-[#0a0a0a]">
      {/* Dropdown Filters */}
      <button type="button" className={buttonStyle}>
        <span className="text-neutral-500 dark:text-neutral-400">Limit:</span>
        <span className="font-semibold text-neutral-900 dark:text-neutral-100">10,000</span>
        <ChevronDown className="h-3 w-3 text-neutral-400" />
      </button>

      <button type="button" className={buttonStyle}>
        <span className="text-neutral-500 dark:text-neutral-400">Disposition:</span>
        <span className="font-semibold text-neutral-900 dark:text-neutral-100">
          {selectedTags.length} selected
        </span>
        <ChevronDown className="h-3 w-3 text-neutral-400" />
      </button>

      <button type="button" className={buttonStyle}>
        <span className="text-neutral-500 dark:text-neutral-400">Type:</span>
        <span className="font-semibold text-neutral-900 dark:text-neutral-100">All</span>
        <ChevronDown className="h-3 w-3 text-neutral-400" />
      </button>

      <button type="button" className={buttonStyle}>
        <span className="text-neutral-500 dark:text-neutral-400">Dialer:</span>
        <span className="font-semibold text-neutral-900 dark:text-neutral-100">All</span>
        <ChevronDown className="h-3 w-3 text-neutral-400" />
      </button>

      <button type="button" className={buttonStyle}>
        <span className="text-neutral-500 dark:text-neutral-400">Server:</span>
        <span className="font-semibold text-neutral-900 dark:text-neutral-100">All</span>
        <ChevronDown className="h-3 w-3 text-neutral-400" />
      </button>

      {/* Date Range Selector */}
      <button
        type="button"
        className="flex items-center gap-2 rounded-md border border-neutral-300 bg-neutral-100 px-3 py-1 text-left text-neutral-700 transition-colors hover:border-neutral-400 hover:bg-neutral-200 hover:text-neutral-900 dark:border-[#2a2a2a] dark:bg-[#141414] dark:text-neutral-300 dark:hover:border-neutral-600 dark:hover:bg-[#1a1a1a] dark:hover:text-white"
      >
        <Clock className="h-3.5 w-3.5 text-neutral-500 dark:text-neutral-400" />
        <div className="flex flex-col">
          <span className="text-[11px] font-bold leading-tight text-neutral-900 dark:text-neutral-100">
            Last 24 hours
          </span>
          <span className="text-[9px] leading-tight text-neutral-500">
            Aug 24, 2026 00:03 — Aug 25, 2026 00:03
          </span>
        </div>
        <ChevronDown className="ml-1 h-3 w-3 text-neutral-400" />
      </button>

      {/* Refresh Action */}
      <button
        type="button"
        onClick={handleRefreshClick}
        title="Refresh Data"
        className="flex h-8 w-8 items-center justify-center rounded-md border border-neutral-300 bg-neutral-100 text-neutral-600 transition-colors hover:border-neutral-400 hover:bg-neutral-200 hover:text-neutral-900 dark:border-[#2a2a2a] dark:bg-[#141414] dark:text-neutral-400 dark:hover:border-neutral-600 dark:hover:bg-[#1a1a1a] dark:hover:text-white"
      >
        <RotateCw
          className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-cyan-500" : ""}`}
        />
      </button>

      {/* Active Disposition Tags */}
      <div className="flex flex-wrap items-center gap-1.5 pl-1">
        {selectedTags.map((tag) => (
          <span
            key={tag}
            className="flex items-center gap-1 rounded-full border border-neutral-300 bg-neutral-200 px-2.5 py-0.5 text-[11px] font-medium text-neutral-800 transition-colors dark:border-[#333333] dark:bg-[#1a1a1a] dark:text-neutral-200"
          >
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="text-neutral-500 hover:text-neutral-900 dark:hover:text-white"
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}