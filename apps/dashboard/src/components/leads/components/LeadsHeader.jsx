"use client";

import { UploadCloud, Plus } from "lucide-react";

export default function LeadsHeader({
  totalCount,
  qualifiedCount,
  convertedCount,
  contactedCount,
  onImportClick,
  onAddClick,
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex flex-col gap-0.5">
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
          Leads Management
        </h1>
        <div className="text-xs text-neutral-500 dark:text-neutral-400 font-medium">
          <span>{totalCount} total leads</span>
          <span className="mx-1">•</span>
          <span className="text-emerald-600 dark:text-emerald-400">{qualifiedCount} qualified</span>
          <span className="mx-1">•</span>
          <span className="text-blue-600 dark:text-blue-400">{convertedCount} converted</span>
          <span className="mx-1">•</span>
          <span className="text-amber-600 dark:text-amber-400">{contactedCount} contacted</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onImportClick}
          className="inline-flex items-center gap-1.5 rounded-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 px-3 py-1.5 text-xs font-semibold text-neutral-800 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 shadow-xs transition-colors"
        >
          <UploadCloud className="h-4 w-4" />
          <span>Import Leads</span>
        </button>
        <button
          type="button"
          onClick={onAddClick}
          className="inline-flex items-center gap-1.5 rounded-md border border-blue-600 bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-1.5 text-xs font-semibold shadow-xs transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>Add Lead</span>
        </button>
      </div>
    </div>
  );
}