"use client";

import { Plus, Megaphone, TrendingUp, UserPlus, ScrollText, Activity } from "lucide-react";

const SUBTABS = [
  { id: "all", label: "All Campaigns", icon: Megaphone },
  { id: "performance", label: "Performance review", icon: TrendingUp },
  { id: "team", label: "Assign team", icon: UserPlus },
  { id: "scripts", label: "Active Scripts", icon: ScrollText },
  { id: "outcomes", label: "Live outcomes", icon: Activity },
];

export default function CampaignHeader({ totalCount, activeCount, pausedCount, currentMode, activeSubtab, onNavigate }) {
  return (
    <>
      {/* 1. Header Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-0.5">
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
            Campaign Management
          </h1>
          <div className="text-xs text-neutral-500 dark:text-neutral-400 font-medium">
            <span>{totalCount} total campaigns</span>
            <span className="mx-1">•</span>
            <span className="text-emerald-600 dark:text-emerald-400">{activeCount} active</span>
            <span className="mx-1">•</span>
            <span className="text-amber-600 dark:text-amber-400">{pausedCount} paused</span>
          </div>
        </div>

        <button
          type="button"
          onClick={() => onNavigate("new")}
          className="inline-flex items-center gap-1.5 rounded-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-3.5 py-1.5 text-xs font-semibold text-neutral-900 dark:text-white transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800 shadow-xs"
        >
          <Plus className="h-4 w-4" />
          <span>New Campaign</span>
        </button>
      </div>

      {/* 2. Top Segmented Subtabs Navigation Bar */}
      <div className="flex items-center gap-1 overflow-x-auto rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-1.5 shadow-xs">
        {SUBTABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentMode === "subtab" && activeSubtab === tab.id;

          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onNavigate(tab.id === "all" ? null : tab.id)}
              className={`flex items-center gap-2 rounded-lg px-3.5 py-2 text-xs font-semibold whitespace-nowrap transition-all duration-150 ${
                isActive
                  ? "bg-blue-600 text-white dark:bg-[#253246] dark:text-blue-300 shadow-xs"
                  : "text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 hover:text-neutral-900 dark:hover:bg-[#151518] dark:hover:text-white"
              }`}
            >
              <Icon className={`h-3.5 w-3.5 ${isActive ? "text-white dark:text-blue-300" : "opacity-70"}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </>
  );
}