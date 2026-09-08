"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

// Default seed dataset representing 5-minute telephony call buckets
const GENERATE_DEFAULT_BUCKETS = () => {
  const times = [
    { time: "09:40 PM", calls: 1950 },
    { time: "09:45 PM", calls: 3620 },
    { time: "09:50 PM", calls: 3580 },
    { time: "09:55 PM", calls: 3650 },
    { time: "10:00 PM", calls: 3590 },
    { time: "10:05 PM", calls: 3450 },
    { time: "10:10 PM", calls: 3710 },
    { time: "10:15 PM", calls: 3800 },
    { time: "10:20 PM", calls: 3420 },
    { time: "10:25 PM", calls: 3480 },
    { time: "10:30 PM", calls: 3010 },
    { time: "10:35 PM", calls: 3120 },
    { time: "10:40 PM", calls: 3200 },
    { time: "10:45 PM", calls: 3250 },
    { time: "10:50 PM", calls: 3410 },
    { time: "10:55 PM", calls: 3290 },
    { time: "11:00 PM", calls: 3100 },
    { time: "11:05 PM", calls: 2850 },
    { time: "11:10 PM", calls: 3320 },
    { time: "11:15 PM", calls: 3150 },
    { time: "11:20 PM", calls: 3200 },
    { time: "11:25 PM", calls: 3450 },
    { time: "11:30 PM", calls: 3250 },
    { time: "11:35 PM", calls: 2950 },
    { time: "11:40 PM", calls: 3180 },
    { time: "11:45 PM", calls: 3580 },
    { time: "11:50 PM", calls: 2432 }, // Hovered item from screenshot
    { time: "11:55 PM", calls: 3690 },
    { time: "12:00 AM", calls: 3080 },
    { time: "12:05 AM", calls: 3480 },
    { time: "12:10 AM", calls: 3420 },
    { time: "12:15 AM", calls: 3540 },
    { time: "12:20 AM", calls: 3600 },
    { time: "12:25 AM", calls: 3420 },
    { time: "12:30 AM", calls: 3500 },
    { time: "12:35 AM", calls: 3380 },
    { time: "12:40 AM", calls: 3520 },
    { time: "12:45 AM", calls: 3210 },
    { time: "12:50 AM", calls: 3240 },
    { time: "12:55 AM", calls: 3150 },
    { time: "01:00 AM", calls: 3480 },
    { time: "01:05 AM", calls: 3510 },
    { time: "01:10 AM", calls: 3580 },
    { time: "01:15 AM", calls: 3650 },
    { time: "01:20 AM", calls: 3420 },
    { time: "01:25 AM", calls: 3450 },
    { time: "01:30 AM", calls: 3490 },
    { time: "01:35 AM", calls: 3480 },
    { time: "01:40 AM", calls: 3180 },
    { time: "01:45 AM", calls: 3120 },
    { time: "01:50 AM", calls: 3190 },
    { time: "01:55 AM", calls: 3350 },
    { time: "02:00 AM", calls: 3520 },
    { time: "02:05 AM", calls: 3580 },
    { time: "02:10 AM", calls: 3020 },
    { time: "02:15 AM", calls: 3150 },
    { time: "02:20 AM", calls: 3140 },
    { time: "02:25 AM", calls: 3080 },
    { time: "02:30 AM", calls: 2790 },
    { time: "02:35 AM", calls: 3280 },
    { time: "02:40 AM", calls: 3250 },
    { time: "02:45 AM", calls: 3350 },
    { time: "02:50 AM", calls: 3180 },
    { time: "02:55 AM", calls: 3120 },
    { time: "03:00 AM", calls: 3240 },
    { time: "03:05 AM", calls: 3200 },
    { time: "03:10 AM", calls: 3150 },
    { time: "03:15 AM", calls: 2980 },
    { time: "03:20 AM", calls: 2450 },
    { time: "03:25 AM", calls: 3010 },
    { time: "03:30 AM", calls: 1450 },
    { time: "03:35 AM", calls: 980 },
    { time: "05:50 PM", calls: 1300 },
    { time: "05:55 PM", calls: 2350 },
    { time: "06:00 PM", calls: 3280 },
    { time: "06:05 PM", calls: 3300 },
    { time: "06:10 PM", calls: 3320 },
    { time: "06:15 PM", calls: 3100 },
    { time: "06:20 PM", calls: 2800 },
    { time: "06:25 PM", calls: 2950 },
    { time: "06:30 PM", calls: 3050 },
    { time: "06:35 PM", calls: 2750 },
    { time: "06:40 PM", calls: 2920 },
    { time: "06:45 PM", calls: 3100 },
    { time: "06:50 PM", calls: 3020 },
    { time: "06:55 PM", calls: 2950 },
    { time: "07:00 PM", calls: 2850 },
    { time: "07:05 PM", calls: 3280 },
    { time: "07:10 PM", calls: 3450 },
    { time: "07:15 PM", calls: 3320 },
    { time: "07:20 PM", calls: 3210 },
    { time: "07:25 PM", calls: 2600 },
    { time: "07:30 PM", calls: 2310 },
    { time: "07:35 PM", calls: 2050 },
    { time: "07:40 PM", calls: 2200 },
    { time: "07:45 PM", calls: 2320 },
    { time: "07:50 PM", calls: 2540 },
    { time: "07:55 PM", calls: 2620 },
    { time: "08:00 PM", calls: 2500 },
    { time: "08:05 PM", calls: 2420 },
    { time: "08:10 PM", calls: 2680 },
    { time: "08:15 PM", calls: 2850 },
    { time: "08:20 PM", calls: 3250 },
    { time: "08:25 PM", calls: 2050 },
    { time: "08:30 PM", calls: 3300 },
    { time: "08:35 PM", calls: 3480 },
    { time: "08:40 PM", calls: 3580 },
    { time: "08:45 PM", calls: 3720 },
    { time: "08:50 PM", calls: 1650 },
  ];
  return times;
};

// Custom Tooltip matching screenshot style
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="pointer-events-none z-50 rounded-lg border border-neutral-700/80 bg-[#161618] px-3.5 py-2 text-xs shadow-2xl backdrop-blur-md">
        <div className="font-semibold text-neutral-300">{label}</div>
        <div className="mt-0.5 font-medium text-cyan-400">
          Calls : {payload[0].value?.toLocaleString()}
        </div>
      </div>
    );
  }
  return null;
};

export default function CallsBucketChart({ data = GENERATE_DEFAULT_BUCKETS() }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex w-full flex-col gap-3">
      {/* Collapsible Header */}
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
        <span>CALLS PER 5-MINUTE BUCKET</span>
      </button>

      {/* Main Chart Container */}
      {isOpen && (
        <div className="w-full rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d]">
          <h3 className="mb-4 text-sm font-bold text-neutral-800 dark:text-neutral-200">
            Calls per 5-minute bucket
          </h3>

          {/* Responsive container with horizontal scroll protection for mobile */}
          <div className="w-full overflow-x-auto">
            <div className="h-72 min-w-[760px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={data}
                  margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                  barCategoryGap={1.5}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="#262626"
                    opacity={0.3}
                  />
                  <XAxis
                    dataKey="time"
                    stroke="#737373"
                    tick={{ fontSize: 10, fill: "#737373" }}
                    tickLine={false}
                    axisLine={{ stroke: "#262626" }}
                    interval={5} // Displays evenly spaced interval labels
                  />
                  <YAxis
                    domain={[0, 3800]}
                    ticks={[0, 950, 1900, 2850, 3800]}
                    stroke="#737373"
                    tick={{ fontSize: 10, fill: "#737373" }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => val.toLocaleString()}
                  />
                  <Tooltip
                    content={<CustomTooltip />}
                    cursor={{ fill: "rgba(255, 255, 255, 0.05)" }}
                  />
                  <Bar
                    dataKey="calls"
                    fill="#1d61f2"
                    radius={[1, 1, 0, 0]}
                    animationDuration={600}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}