"use client";

import React from "react";
import { BarChart3, Monitor, LogOut } from "lucide-react";

export default function TopNavbar() {
  return (
    <header className="flex h-12 w-full items-center justify-between border-b border-[#1f1f1f] bg-[#0a0a0a] px-6 text-white">
      {/* Brand Logo & Name */}
      <div className="flex items-center gap-2.5">
        <BarChart3 className="h-5 w-5 text-white" />
        <span className="text-base font-bold tracking-wide text-white">
          EsperBots Analytics
        </span>
      </div>

      {/* Action Icons */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          title="Toggle Display View"
          className="text-neutral-400 transition-colors hover:text-white"
        >
          <Monitor className="h-4 w-4" />
        </button>
        <button
          type="button"
          title="Logout"
          className="text-neutral-400 transition-colors hover:text-white"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}