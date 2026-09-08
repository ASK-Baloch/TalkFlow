"use client";

import React from "react";
import { Download } from "lucide-react";

export default function SubHeader({ onExportCalls, onExportSales }) {
  return (
    <div className="flex items-center justify-between border-b border-neutral-200 bg-white px-6 py-4 transition-colors duration-200 dark:border-[#1a1a1a] dark:bg-[#0a0a0a]">
      {/* Title */}
      <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-white">
        Smart Brains Dashboard
      </h1>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onExportCalls}
          className="flex items-center gap-2 rounded-lg border border-neutral-300 bg-neutral-100 px-4 py-2 text-xs font-semibold text-neutral-800 shadow-sm transition-all hover:border-neutral-400 hover:bg-neutral-200 hover:text-neutral-950 active:scale-95 dark:border-[#2f2f2f] dark:bg-[#121212] dark:text-neutral-200 dark:hover:border-neutral-500 dark:hover:bg-[#1c1c1c] dark:hover:text-white"
        >
          <Download className="h-3.5 w-3.5 text-neutral-500 dark:text-neutral-400" />
          Export Calls
        </button>

        <button
          type="button"
          onClick={onExportSales}
          className="flex items-center gap-2 rounded-lg border border-neutral-300 bg-neutral-100 px-4 py-2 text-xs font-semibold text-neutral-800 shadow-sm transition-all hover:border-neutral-400 hover:bg-neutral-200 hover:text-neutral-950 active:scale-95 dark:border-[#2f2f2f] dark:bg-[#121212] dark:text-neutral-200 dark:hover:border-neutral-500 dark:hover:bg-[#1c1c1c] dark:hover:text-white"
        >
          <Download className="h-3.5 w-3.5 text-neutral-500 dark:text-neutral-400" />
          Export XFERs/Sales
        </button>
      </div>
    </div>
  );
}