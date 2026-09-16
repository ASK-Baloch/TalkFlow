"use client";

import React, { useState } from "react";
import { DISPOSITION_DATA } from "@/data";
import { useFilters } from "@/context";

export default function DispositionChart() {
  const [hoveredItem, setHoveredItem] = useState(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const { selectedDispositions } = useFilters();

  const handleMouseMove = (e, item) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
    setHoveredItem(item);
  };

  return (
    <div className="relative flex h-full w-full flex-col rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d]">
      <h3 className="text-sm font-bold text-neutral-800 dark:text-neutral-200">
        Disposition %
      </h3>

      <div
        className="relative mt-4 flex flex-col gap-2.5"
        onMouseLeave={() => setHoveredItem(null)}
      >
        {/* Background Vertical Grid Dotted Lines */}
        <div className="pointer-events-none absolute inset-0 flex justify-between pl-16 pr-12 opacity-15">
          <div className="h-full border-r border-dashed border-neutral-400 dark:border-neutral-600" />
          <div className="h-full border-r border-dashed border-neutral-400 dark:border-neutral-600" />
          <div className="h-full border-r border-dashed border-neutral-400 dark:border-neutral-600" />
          <div className="h-full border-r border-dashed border-neutral-400 dark:border-neutral-600" />
        </div>

        {/* Floating Tooltip */}
        {hoveredItem && (
          <div
            className="pointer-events-none absolute z-50 rounded-lg border border-neutral-700/80 bg-[#161618] px-3.5 py-2 text-xs shadow-2xl backdrop-blur-md transition-all duration-75"
            style={{
              top: `${mousePos.y + 12}px`,
              left: `${Math.min(Math.max(mousePos.x - 30, 20), 280)}px`,
            }}
          >
            <div className="font-semibold text-neutral-200">
              {hoveredItem.code}
            </div>
            <div className="mt-0.5 font-medium text-cyan-400">
              Count : {hoveredItem.count.toLocaleString()} ({hoveredItem.percentage.toFixed(1)}%)
            </div>
          </div>
        )}

        {/* Horizontal Bars */}
        {DISPOSITION_DATA.map((item) => {
          const isHovered = hoveredItem?.code === item.code;
          const isSelected =
            !selectedDispositions ||
            selectedDispositions.length === 0 ||
            selectedDispositions.includes(item.code);

          return (
            <div
              key={item.code}
              onMouseEnter={(e) => handleMouseMove(e, item)}
              onMouseMove={(e) => handleMouseMove(e, item)}
              className={`group relative flex cursor-pointer items-center text-xs transition-opacity duration-150 ${
                isSelected ? "opacity-100" : "opacity-35"
              }`}
            >
              {/* Left Code Label */}
              <span className="w-16 shrink-0 pr-3 text-right text-[11px] font-medium text-neutral-600 transition-colors group-hover:text-neutral-950 dark:text-neutral-400 dark:group-hover:text-white">
                {item.code}
              </span>

              {/* Bar Track with Full-Width Hover Highlight */}
              <div className="relative flex flex-1 items-center">
                <div
                  className={`h-6 w-full rounded-sm transition-colors duration-150 ${
                    isHovered
                      ? "bg-slate-300 dark:bg-[#d1d5db]"
                      : "bg-neutral-100 dark:bg-transparent"
                  }`}
                >
                  <div
                    className="h-full rounded-sm transition-all duration-300"
                    style={{
                      width: `${Math.max(item.percentage, 0.6)}%`,
                      backgroundColor: item.color,
                    }}
                  />
                </div>

                {/* Percentage Text on the Right */}
                <span className="ml-2.5 w-11 shrink-0 text-[11px] font-semibold text-neutral-700 dark:text-neutral-300">
                  {item.percentage.toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}