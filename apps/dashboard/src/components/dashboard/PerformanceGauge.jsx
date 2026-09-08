"use client";

import React, { useState } from "react";

export default function PerformanceGauge({
  label,
  fullName,
  value = 0,
  maxScale = 10.0,
  totalCalls,
  xferCount,
}) {
  const [isHovered, setIsHovered] = useState(false);

  // Gauge geometry
  const radius = 34;
  const strokeWidth = 5.5;
  const startAngle = 145; // Bottom-left
  const endAngle = 395;   // Bottom-right across top (250° sweep)
  const totalAngle = endAngle - startAngle;

  // Stable coordinate calculation with float rounding for SSR consistency
  const polarToCartesian = (cx, cy, r, angleInDegrees) => {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180.0;
    return {
      x: +(cx + r * Math.cos(angleInRadians)).toFixed(3),
      y: +(cy + r * Math.sin(angleInRadians)).toFixed(3),
    };
  };

  const describeArc = (x, y, r, startAng, endAng) => {
    const start = polarToCartesian(x, y, r, endAng);
    const end = polarToCartesian(x, y, r, startAng);
    const largeArcFlag = endAng - startAng <= 180 ? "0" : "1";
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
  };

  // Safe percentage clamp
  const clampedValue = Math.min(Math.max(value, 0), maxScale);
  const fillPercentage = clampedValue / maxScale;
  const currentAngle = +(startAngle + totalAngle * fillPercentage).toFixed(3);

  const backgroundArc = describeArc(50, 48, radius, startAngle, endAngle);
  const foregroundArc =
    value > 0 ? describeArc(50, 48, radius, startAngle, currentAngle) : null;

  const isZero = value === 0;

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative flex flex-col items-center justify-between rounded-xl p-2.5 transition-all duration-200 hover:bg-neutral-100 dark:hover:bg-neutral-900/60"
    >
      {/* Floating Tooltip */}
      {isHovered && (
        <div className="pointer-events-none absolute -top-14 z-50 whitespace-nowrap rounded-lg border border-neutral-700/80 bg-[#161618] px-3 py-1.5 text-xs shadow-2xl backdrop-blur-md">
          <div className="font-semibold text-neutral-200">
            {fullName || label}
          </div>
          <div className="flex items-center gap-2 font-mono text-[11px] text-emerald-400">
            <span>XFER Rate: {value.toFixed(2)}%</span>
            {totalCalls && (
              <span className="text-neutral-400">
                ({xferCount || 0} / {totalCalls} Calls)
              </span>
            )}
          </div>
        </div>
      )}

      {/* SVG Arc Gauge */}
      <div className="relative flex h-20 w-24 items-center justify-center">
        <svg viewBox="0 0 100 85" className="h-full w-full overflow-visible">
          {/* Base Inactive Track */}
          <path
            d={backgroundArc}
            fill="none"
            stroke={isZero ? "#3b171c" : "#4a1924"}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Active Filled Progress Arc */}
          {foregroundArc && (
            <path
              d={foregroundArc}
              fill="none"
              stroke="#10b981"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              className="transition-all duration-700 ease-out"
            />
          )}

          {/* Zero Indicator Bullet */}
          {isZero && (
            <circle
              cx="23.484"
              cy="69.281"
              r="3.5"
              fill="#ef4444"
              className="animate-pulse"
            />
          )}
        </svg>

        {/* Center Percentage Display */}
        <div className="absolute inset-0 flex items-center justify-center pt-1">
          <span
            className={`font-mono text-base font-bold tracking-tight ${
              isZero
                ? "text-rose-500"
                : "text-emerald-500 dark:text-[#22c55e]"
            }`}
          >
            {value.toFixed(2)}
          </span>
        </div>
      </div>

      {/* Title */}
      <span
        title={fullName || label}
        className="mt-1 w-full truncate text-center text-[11px] font-medium text-neutral-600 transition-colors group-hover:text-neutral-900 dark:text-neutral-400 dark:group-hover:text-neutral-200"
      >
        {label}
      </span>
    </div>
  );
}