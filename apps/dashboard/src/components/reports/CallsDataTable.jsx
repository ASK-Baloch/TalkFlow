"use client";

import React, { useState, useMemo } from "react";
import {
  ChevronDown,
  Filter,
  Copy,
  Check,
  Play,
  Pause,
} from "lucide-react";
import { DEFAULT_CALLS_DATA } from "@/data";
import { useFilters } from "@/context";

export default function CallsDataTable({ calls = DEFAULT_CALLS_DATA }) {
  const [isOpen, setIsOpen] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const [playingId, setPlayingId] = useState(null);
  const { selectedDispositions } = useFilters();

  const filteredCalls = useMemo(() => {
    if (!selectedDispositions || selectedDispositions.length === 0) return calls;
    return calls.filter((c) => selectedDispositions.includes(c.disposition));
  }, [calls, selectedDispositions]);

  const handleCopy = (id, e) => {
    e.stopPropagation();
    navigator.clipboard?.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const togglePlay = (id) => {
    if (playingId === id) {
      setPlayingId(null);
    } else {
      setPlayingId(id);
    }
  };

  return (
    <div className="flex w-full flex-col gap-3">
      {/* Collapsible Section Header Trigger */}
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
        <span>CALLS DATA</span>
      </button>

      {/* Main Table Card Container */}
      {isOpen && (
        <div className="w-full rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d]">
          <div className="w-full overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
            <table className="w-full min-w-[950px] border-collapse text-xs text-left">
              <thead>
                <tr className="border-b border-neutral-200 bg-neutral-100/90 text-neutral-700 dark:border-neutral-800 dark:bg-[#121214] dark:text-neutral-300">
                  {/* # Column */}
                  <th className="px-3 py-3 font-semibold text-neutral-500 dark:text-neutral-400 w-12 text-center">
                    #
                  </th>

                  {/* Call ID Filter Column */}
                  <th className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-1.5 cursor-pointer hover:text-neutral-900 dark:hover:text-white">
                      <span>Call ID</span>
                      <Filter className="h-3.5 w-3.5 text-neutral-400 opacity-70" />
                    </div>
                  </th>

                  {/* Name Filter Column */}
                  <th className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-1.5 cursor-pointer hover:text-neutral-900 dark:hover:text-white">
                      <span>Name</span>
                      <Filter className="h-3.5 w-3.5 text-neutral-400 opacity-70" />
                    </div>
                  </th>

                  {/* VICI Lead ID Filter Column */}
                  <th className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-1.5 cursor-pointer hover:text-neutral-900 dark:hover:text-white">
                      <span>VICI Lead ID</span>
                      <Filter className="h-3.5 w-3.5 text-neutral-400 opacity-70" />
                    </div>
                  </th>

                  {/* Disposition Filter Column */}
                  <th className="px-4 py-3 font-medium text-center">
                    <div className="flex items-center justify-center gap-1.5 cursor-pointer hover:text-neutral-900 dark:hover:text-white">
                      <span>Disposition</span>
                      <Filter className="h-3.5 w-3.5 text-neutral-400 opacity-70" />
                    </div>
                  </th>

                  {/* Duration Column */}
                  <th className="px-4 py-3 font-medium text-center">Duration</th>

                  {/* Date Entered Filter Column */}
                  <th className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-1.5 cursor-pointer hover:text-neutral-900 dark:hover:text-white">
                      <span>Date Entered</span>
                      <Filter className="h-3.5 w-3.5 text-neutral-400 opacity-70" />
                    </div>
                  </th>

                  {/* Audio Column */}
                  <th className="px-4 py-3 font-medium text-center">Audio</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-neutral-200/70 dark:divide-neutral-800/70">
                {filteredCalls.map((call) => (
                  <tr
                    key={call.index}
                    className="transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900/40"
                  >
                    {/* Index # */}
                    <td className="px-3 py-3 text-center text-neutral-500 font-mono dark:text-neutral-400">
                      {call.index}
                    </td>

                    {/* Call ID with Copy Button */}
                    <td className="px-4 py-3 font-mono font-bold text-neutral-900 dark:text-neutral-100">
                      <div className="flex items-center gap-2">
                        <span>{call.shortCallId}</span>
                        <button
                          type="button"
                          onClick={(e) => handleCopy(call.fullCallId, e)}
                          title="Copy Full Call ID"
                          className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white transition-colors"
                        >
                          {copiedId === call.fullCallId ? (
                            <Check className="h-3.5 w-3.5 text-emerald-500" />
                          ) : (
                            <Copy className="h-3.5 w-3.5" />
                          )}
                        </button>
                      </div>
                    </td>

                    {/* Name / Phone */}
                    <td className="px-4 py-3 font-mono font-bold text-neutral-900 dark:text-neutral-100">
                      {call.name}
                    </td>

                    {/* VICI Lead ID */}
                    <td className="px-4 py-3 font-mono text-neutral-500 dark:text-neutral-400">
                      {call.shortViciLeadId}
                    </td>

                    {/* Disposition Badge */}
                    <td className="px-4 py-3 text-center">
                      {call.disposition === "SALE" ? (
                        <span className="inline-flex items-center justify-center rounded-full bg-white px-3 py-0.5 text-xs font-extrabold text-black shadow-xs dark:bg-white dark:text-black">
                          SALE
                        </span>
                      ) : (
                        <span className="inline-flex items-center justify-center rounded-full border border-neutral-300 bg-neutral-100 px-2.5 py-0.5 text-[11px] font-bold text-neutral-800 dark:border-neutral-700 dark:bg-[#1a1a1c] dark:text-neutral-200">
                          {call.disposition}
                        </span>
                      )}
                    </td>

                    {/* Duration */}
                    <td className="px-4 py-3 text-center font-medium text-neutral-700 dark:text-neutral-300">
                      {call.duration}
                    </td>

                    {/* Date Entered */}
                    <td className="px-4 py-3 text-neutral-600 dark:text-neutral-400 whitespace-nowrap">
                      {call.dateEntered}
                    </td>

                    {/* Audio Play Button */}
                    <td className="px-4 py-3 text-center">
                      <button
                        type="button"
                        onClick={() => togglePlay(call.index)}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-neutral-800 transition-colors hover:text-black dark:text-neutral-200 dark:hover:text-white"
                      >
                        {playingId === call.index ? (
                          <>
                            <Pause className="h-3.5 w-3.5 text-rose-500 fill-rose-500" />
                            <span>Pause</span>
                          </>
                        ) : (
                          <>
                            <Play className="h-3.5 w-3.5 fill-current" />
                            <span>Play</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
