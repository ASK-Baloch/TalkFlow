"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

// 24-Hour Mock Telemetry Data Matching Screenshot Spike at 12:00 PM
const TIME_SERIES_DATA = [
  { time: "03:10 AM", CLBK: 0.0, DAIR: 0.2, DNC: 0.1, DNQ: 0.1, RAXFER: 0.0, SALE: 5.2, XFER: 0.1 },
  { time: "04:45 AM", CLBK: 0.0, DAIR: 0.1, DNC: 0.2, DNQ: 0.0, RAXFER: 0.0, SALE: 8.4, XFER: 0.1 },
  { time: "06:20 AM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 2.1, XFER: 0.0 },
  { time: "07:55 AM", CLBK: 0.0, DAIR: 0.0, DNC: 0.1, DNQ: 0.0, RAXFER: 0.0, SALE: 1.8, XFER: 0.0 },
  { time: "09:30 AM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 0.9, XFER: 0.0 },
  { time: "11:05 AM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 0.4, XFER: 0.0 },
  { time: "12:00 PM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 100.0, XFER: 0.0 },
  { time: "12:40 PM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 0.2, XFER: 0.0 },
  { time: "02:15 PM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 0.1, XFER: 0.0 },
  { time: "03:50 PM", CLBK: 0.0, DAIR: 0.0, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 0.8, XFER: 0.0 },
  { time: "05:25 PM", CLBK: 0.0, DAIR: 0.1, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 3.5, XFER: 0.1 },
  { time: "07:00 PM", CLBK: 0.0, DAIR: 0.2, DNC: 0.1, DNQ: 0.0, RAXFER: 0.0, SALE: 4.8, XFER: 0.2 },
  { time: "08:35 PM", CLBK: 0.0, DAIR: 0.1, DNC: 0.1, DNQ: 0.0, RAXFER: 0.0, SALE: 2.6, XFER: 0.1 },
  { time: "10:10 PM", CLBK: 0.0, DAIR: 0.2, DNC: 0.1, DNQ: 0.0, RAXFER: 0.0, SALE: 3.1, XFER: 0.1 },
  { time: "11:45 PM", CLBK: 0.0, DAIR: 0.1, DNC: 0.2, DNQ: 0.0, RAXFER: 0.0, SALE: 2.0, XFER: 0.1 },
  { time: "01:20 AM", CLBK: 0.0, DAIR: 0.3, DNC: 0.1, DNQ: 0.0, RAXFER: 0.0, SALE: 4.2, XFER: 0.1 },
  { time: "03:10 AM", CLBK: 0.0, DAIR: 0.1, DNC: 0.0, DNQ: 0.0, RAXFER: 0.0, SALE: 0.5, XFER: 0.0 },
];

const METRIC_CONFIG = [
  { key: "CLBK", label: "CLBK", color: "#06b6d4" },    // Cyan
  { key: "DAIR", label: "DAIR", color: "#f43f5e" },    // Red/Rose
  { key: "DNC", label: "DNC", color: "#22c55e" },      // Green
  { key: "DNQ", label: "DNQ", color: "#eab308" },      // Yellow
  { key: "RAXFER", label: "RAXFER", color: "#ec4899" },// Magenta
  { key: "SALE", label: "SALE", color: "#f97316" },    // Orange
  { key: "XFER", label: "XFER", color: "#38bdf8" },    // Light Blue
];

// Custom Floating Tooltip
const CustomChartTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border border-neutral-700/80 bg-[#121214]/95 p-3 text-xs shadow-2xl backdrop-blur-md">
        <p className="mb-2 font-semibold text-neutral-300">{label}</p>
        <div className="flex flex-col gap-1 font-mono text-[11px]">
          {payload.map((item) => (
            <div
              key={item.dataKey}
              className="flex items-center justify-between gap-4"
              style={{ color: item.color }}
            >
              <span className="font-semibold">{item.name} :</span>
              <span className="font-bold">{item.value.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

export default function DispositionComparison() {
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
        <span>DISPOSITION COMPARISON</span>
      </button>

      {/* Main Chart Container */}
      {isOpen && (
        <div className="w-full rounded-xl border border-neutral-200 bg-white p-5 shadow-sm transition-colors duration-200 dark:border-[#1e1e1e] dark:bg-[#0d0d0d]">
          <h3 className="mb-4 text-sm font-bold text-neutral-800 dark:text-neutral-200">
            Disposition Comparison
          </h3>

          {/* Responsive Scrollable Container for Narrow Mobile Screens */}
          <div className="w-full overflow-x-auto">
            <div className="h-72 min-w-[620px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={TIME_SERIES_DATA}
                  margin={{ top: 10, right: 20, left: -15, bottom: 0 }}
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
                  />
                  <YAxis
                    domain={[0, 100]}
                    ticks={[0, 25, 50, 75, 100]}
                    stroke="#737373"
                    tick={{ fontSize: 10, fill: "#737373" }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => `${val}%`}
                  />
                  <Tooltip content={<CustomChartTooltip />} />

                  {/* Render All Metric Lines */}
                  {METRIC_CONFIG.map((metric) => (
                    <Line
                      key={metric.key}
                      type="monotone"
                      dataKey={metric.key}
                      name={metric.label}
                      stroke={metric.color}
                      strokeWidth={metric.key === "SALE" ? 2 : 1.2}
                      dot={false}
                      activeDot={{ r: 4, strokeWidth: 1, stroke: "#fff" }}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bottom Interactive Legend */}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 border-t border-neutral-100 pt-3 text-[11px] dark:border-neutral-900">
            {METRIC_CONFIG.map((metric) => (
              <div
                key={metric.key}
                className="flex items-center gap-1.5 font-medium text-neutral-600 dark:text-neutral-400"
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: metric.color }}
                />
                <span>{metric.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}