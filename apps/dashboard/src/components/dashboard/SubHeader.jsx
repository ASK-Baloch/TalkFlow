"use client";

import React from "react";
import { Download } from "lucide-react";

export default function SubHeader({ onExportCalls, onExportSales }) {
  return (
    <div className="flex items-center justify-between bg-[#0a0a0a] px-6 py-4">
      {/* Title */}
      <h1 className="text-xl font-bold tracking-tight text-white">
        Smart Brains Dashboard
      </h1>

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onExportCalls}
          className="flex items-center gap-2 rounded-lg border border-[#2f2f2f] bg-[#121212] px-4 py-2 text-xs font-semibold text-neutral-200 shadow-sm transition-all hover:border-neutral-500 hover:bg-[#1c1c1c] hover:text-white active:scale-95"
        >
          <Download className="h-3.5 w-3.5 text-neutral-400" />
          Export Calls
        </button>

        <button
          type="button"
          onClick={onExportSales}
          className="flex items-center gap-2 rounded-lg border border-[#2f2f2f] bg-[#121212] px-4 py-2 text-xs font-semibold text-neutral-200 shadow-sm transition-all hover:border-neutral-500 hover:bg-[#1c1c1c] hover:text-white active:scale-95"
        >
          <Download className="h-3.5 w-3.5 text-neutral-400" />
          Export XFERs/Sales
        </button>
      </div>
    </div>
  );
}