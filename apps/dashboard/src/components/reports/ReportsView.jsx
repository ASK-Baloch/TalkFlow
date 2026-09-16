"use client";

import React, { useState } from "react";
import {
  Search,
  ChevronRight,
} from "lucide-react";
import { MORPHEUS_REPORTS, REPORT_CATEGORIES } from "@/data";

export default function ReportsView() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredReports = MORPHEUS_REPORTS.filter((rep) => {
    const matchesCategory =
      selectedCategory === "all" || rep.category === selectedCategory;
    const matchesSearch =
      rep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rep.desc.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const categories = REPORT_CATEGORIES;

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* 1. Header & Search Bar (Matching Morpheus Admin Reports Layout) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">Reports</h1>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
            27 reports • 5 categories · Telemetry, agent performance, CDRs, and billing analytics.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-400 dark:text-neutral-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search reports..."
            className="w-full rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] pl-9 pr-4 py-2 text-xs text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 outline-none focus:border-blue-500 dark:focus:border-neutral-700"
          />
        </div>
      </div>

      {/* 2. Top Segmented Category Filter Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto border-b border-neutral-200 dark:border-neutral-800/80 pb-3 text-xs font-semibold">
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            onClick={() => setSelectedCategory(cat.id)}
            className={`flex items-center gap-1.5 rounded-lg px-3.5 py-1.5 transition-all ${
              selectedCategory === cat.id
                ? "bg-blue-600 text-white font-extrabold shadow-sm dark:bg-white dark:text-black"
                : "bg-white text-neutral-600 hover:text-neutral-900 border border-neutral-300 dark:bg-[#0d0d0d] dark:text-neutral-400 dark:hover:text-white dark:border-neutral-800"
            }`}
          >
            <span>{cat.label}</span>
            <span
              className={`rounded-full px-1.5 py-0.2 text-[10px] ${
                selectedCategory === cat.id
                  ? "bg-white/20 text-white dark:bg-neutral-200 dark:text-black font-bold"
                  : "bg-neutral-100 text-neutral-600 dark:bg-neutral-900 dark:text-neutral-500"
              }`}
            >
              {cat.count}
            </span>
          </button>
        ))}
      </div>

      {/* 3. Static Reports Cards Grid (Morpheus Pulse Admin Style) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filteredReports.map((rep) => {
          const IconComp = rep.icon;
          return (
            <div
              key={rep.id}
              onClick={() => alert(`Launching Morpheus report: ${rep.title}`)}
              className="group cursor-pointer rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs transition-all hover:border-blue-400 dark:hover:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-[#121215] flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-blue-600 dark:text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <IconComp className="h-4 w-4" />
                  </div>
                  <span className="rounded-full bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800/80 px-2.5 py-0.5 text-[10px] font-bold text-neutral-600 dark:text-neutral-400">
                    {rep.badge}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-neutral-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex items-center justify-between">
                  <span>{rep.title}</span>
                  <ChevronRight className="h-4 w-4 text-neutral-400 dark:text-neutral-600 group-hover:text-blue-600 dark:group-hover:text-blue-400 group-hover:translate-x-0.5 transition-transform" />
                </h3>

                <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1.5 leading-relaxed">
                  {rep.desc}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-neutral-200 dark:border-neutral-800/60 flex items-center justify-between text-[11px] text-neutral-500">
                <span className="uppercase font-bold text-[10px] tracking-wider text-neutral-400 dark:text-neutral-500">
                  {rep.category.replace("_", " & ")}
                </span>
                <span className="text-blue-600 dark:text-blue-400 font-semibold group-hover:underline">
                  View Report →
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
