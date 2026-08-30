"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";
import PerformanceGauge from "./PerformanceGauge";

const DEFAULT_AGENTS = [
  { id: "ag-1", name: "Adriana", value: 3.45, totalCalls: 1240, xferCount: 43 },
  { id: "ag-2", name: "Harper", value: 3.73, totalCalls: 1580, xferCount: 59 },
  { id: "ag-3", name: "Jennifer", value: 3.16, totalCalls: 1420, xferCount: 45 },
  { id: "ag-4", name: "Samantha", value: 3.34, totalCalls: 1610, xferCount: 54 },
  { id: "ag-5", name: "Scarlett", value: 3.65, totalCalls: 1390, xferCount: 51 },
];

const DEFAULT_SCRIPTS = [
  {
    id: "sc-1",
    label: "1038 Medicare T Smar...",
    fullName: "1038 Medicare T Smart Brains V1",
    value: 0.0,
    totalCalls: 120,
    xferCount: 0,
  },
  {
    id: "sc-2",
    label: "1033 Medicare T Smar...",
    fullName: "1033 Medicare T Smart Brains Direct",
    value: 3.09,
    totalCalls: 4500,
    xferCount: 139,
  },
  {
    id: "sc-3",
    label: "1019 Medicare T Smar...",
    fullName: "1019 Medicare T Smart Brains Inbound",
    value: 3.05,
    totalCalls: 3800,
    xferCount: 116,
  },
  {
    id: "sc-4",
    label: "1038 Medicare T Smar...",
    fullName: "1038 Medicare T Smart Brains Enhanced",
    value: 9.09,
    totalCalls: 2200,
    xferCount: 200,
  },
  {
    id: "sc-5",
    label: "001 Smart Brains HR V...",
    fullName: "001 Smart Brains HR Verification V2",
    value: 4.06,
    totalCalls: 1800,
    xferCount: 73,
  },
  {
    id: "sc-6",
    label: "1016 Medicare T Smar...",
    fullName: "1016 Medicare T Smart Brains FL",
    value: 3.69,
    totalCalls: 3100,
    xferCount: 114,
  },
  {
    id: "sc-7",
    label: "1017 Medicare T Smar...",
    fullName: "1017 Medicare T Smart Brains TX",
    value: 2.63,
    totalCalls: 2900,
    xferCount: 76,
  },
  {
    id: "sc-8",
    label: "1032 Medicare T Smar...",
    fullName: "1032 Medicare T Smart Brains CA",
    value: 2.69,
    totalCalls: 2400,
    xferCount: 65,
  },
  {
    id: "sc-9",
    label: "1039 Medicare T Smar...",
    fullName: "1039 Medicare T Smart Brains East",
    value: 3.22,
    totalCalls: 1950,
    xferCount: 63,
  },
  {
    id: "sc-10",
    label: "1083 Medicare T Smar...",
    fullName: "1083 Medicare T Smart Brains West",
    value: 2.99,
    totalCalls: 2100,
    xferCount: 63,
  },
  {
    id: "sc-11",
    label: "1082 Medicare T Smar...",
    fullName: "1082 Medicare T Smart Brains Central",
    value: 4.17,
    totalCalls: 3300,
    xferCount: 138,
  },
];

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