"use client";

import React from "react";
import FilterToolbox from "./FilterToolbox";
import SubHeader from "./SubHeader";
import StatsGrid from "./StatsGrid";
import PerformanceSection from "./PerformanceSection";
import {
  DispositionChart,
  DispositionComparison,
  CallsBucketChart,
  CallsPerDayChart,
  ViciListBreakdown,
} from "@/components/charts";
import { CallsDataTable } from "@/components/reports";

export default function DashboardView() {
  const handleRefresh = () => {
    console.log("Refreshing dashboard telemetry...");
  };

  const handleExportCalls = () => {
    console.log("Exporting call logs...");
  };

  const handleExportSales = () => {
    console.log("Exporting sales & transfer reports...");
  };

  return (
    <div className="flex min-h-screen w-full flex-col bg-neutral-100 text-neutral-900 transition-colors duration-200 dark:bg-[#050505] dark:text-neutral-100">
      {/* 1. Filter Toolbar */}
      <FilterToolbox onRefresh={handleRefresh} />

      {/* 3. SubHeader with Action Buttons */}
      <SubHeader
        onExportCalls={handleExportCalls}
        onExportSales={handleExportSales}
      />

      {/* 4. Main Analytics Dashboard Layout */}
      <main className="flex flex-col gap-6 px-4 py-4 sm:px-6">
        {/* Row 1: KPI Stats Grid (55%) + Disposition % Breakdown (45%) */}
        <div className="grid grid-cols-1 items-start gap-5 lg:grid-cols-[55fr_45fr]">
          <div className="w-full">
            <StatsGrid />
          </div>
          <div className="w-full">
            <DispositionChart />
          </div>
        </div>

        {/* Row 2: Full-Width Disposition Comparison */}
        <div className="w-full">
          <DispositionComparison />
        </div>

        {/* Row 3: Full-Width Calls Per 5-Minute Bucket */}
        <div className="w-full">
          <CallsBucketChart />
        </div>

        {/* Row 4: Full-Width Calls Per Day (Last 7 Days) */}
        <div className="w-full">
          <CallsPerDayChart />
        </div>

        {/* Row 5: Agent & Script Performance (XFER% Gauges) */}
        <div className="w-full">
          <PerformanceSection />
        </div>

        {/* Row 6: Disposition Breakdown by Vici List */}
        <div className="w-full">
          <ViciListBreakdown />
        </div>

        {/* Row 7: Calls Data Table */}
        <div className="w-full">
          <CallsDataTable />
        </div>
      </main>
    </div>
  );
}