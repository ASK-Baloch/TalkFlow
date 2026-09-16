"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";
import PerformanceGauge from "./PerformanceGauge";
import { DEFAULT_AGENTS, DEFAULT_SCRIPTS } from "@/data";

export default function PerformanceSection({
  agents = DEFAULT_AGENTS,
  scripts = DEFAULT_SCRIPTS,
}) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex w-full flex-col gap-3">
      {/* Collapsible Section Header */}
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
        <span>PERFORMANCE</span>
      </button>

      {/* Main Container */}
      {isOpen && (
        <div className="flex flex-col gap-4">
          {/* Panel 1: Agent Performance - XFER% */}
          <div className="w-full rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d]">
            <h3 className="mb-4 text-sm font-bold text-neutral-800 dark:text-neutral-200">
              Agent Performance - XFER%
            </h3>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5">
              {agents.map((agent) => (
                <PerformanceGauge
                  key={agent.id}
                  label={agent.name}
                  fullName={agent.name}
                  value={agent.value}
                  totalCalls={agent.totalCalls}
                  xferCount={agent.xferCount}
                />
              ))}
            </div>
          </div>

          {/* Panel 2: Script Performance - XFER% */}
          <div className="w-full rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d]">
            <h3 className="mb-4 text-sm font-bold text-neutral-800 dark:text-neutral-200">
              Script Performance - XFER%
            </h3>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8">
              {scripts.map((script) => (
                <PerformanceGauge
                  key={script.id}
                  label={script.label}
                  fullName={script.fullName}
                  value={script.value}
                  totalCalls={script.totalCalls}
                  xferCount={script.xferCount}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}