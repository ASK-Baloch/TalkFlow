"use client";

import React, { useState } from "react";
import { Search, Filter, Download, Columns, ChevronLeft, ChevronRight, ArrowUpDown } from "lucide-react";

// Debounced Search Input Primitive
export function SearchInput({ value, onChange, placeholder = "Search records...", className = "" }) {
  return (
    <div className={`relative flex items-center ${className}`}>
      <Search className="absolute left-3 h-3.5 w-3.5 text-neutral-400" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-md border border-neutral-300 bg-white pl-9 pr-3 py-1.5 text-xs text-neutral-900 placeholder-neutral-400 focus:border-blue-500 focus:outline-none dark:border-neutral-800 dark:bg-[#121215] dark:text-white"
      />
    </div>
  );
}

// Server-Driven / Interactive DataTable Primitive per TalkFlow.md §10
export function DataTable({ columns, data, loading, emptyState, onRowClick }) {
  if (loading) {
    return (
      <div className="p-8 text-center text-xs text-neutral-500 animate-pulse">
        Loading data records...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="p-8 text-center text-xs text-neutral-500">
        {emptyState || "No records found matching criteria."}
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
      <table className="w-full text-left text-xs">
        <thead className="border-b border-neutral-200 bg-neutral-50 text-neutral-600 dark:border-neutral-800 dark:bg-[#121215] dark:text-neutral-400">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="p-3 font-semibold">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
          {data.map((row, idx) => (
            <tr
              key={row.id || idx}
              onClick={() => onRowClick && onRowClick(row)}
              className={`transition-colors ${
                onRowClick ? "cursor-pointer hover:bg-neutral-50/80 dark:hover:bg-[#141417]" : ""
              }`}
            >
              {columns.map((col) => (
                <td key={col.key} className="p-3 text-neutral-800 dark:text-neutral-200">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Pagination Controls
export function Pagination({ currentPage = 1, totalPages = 5, onPageChange }) {
  return (
    <div className="flex items-center justify-between border-t border-neutral-200 pt-3 text-xs text-neutral-500 dark:border-neutral-800">
      <span>Page {currentPage} of {totalPages}</span>
      <div className="flex items-center gap-1">
        <button
          type="button"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="rounded-md border border-neutral-300 p-1 hover:bg-neutral-100 disabled:opacity-40 dark:border-neutral-800 dark:hover:bg-neutral-800"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <button
          type="button"
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange(currentPage + 1)}
          className="rounded-md border border-neutral-300 p-1 hover:bg-neutral-100 disabled:opacity-40 dark:border-neutral-800 dark:hover:bg-neutral-800"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

// Export Button Primitive
export function ExportButton({ onExport, label = "Export CSV" }) {
  return (
    <button
      type="button"
      onClick={onExport}
      className="flex items-center gap-1.5 rounded-md border border-neutral-300 bg-white px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-neutral-50 dark:border-neutral-800 dark:bg-[#121215] dark:text-neutral-300 dark:hover:bg-neutral-800 transition-colors"
    >
      <Download className="h-3.5 w-3.5 text-neutral-500" />
      <span>{label}</span>
    </button>
  );
}