"use client";

import React from "react";
import TopNavbar from "@/components/dashboard/TopNavbar";
import FilterToolbar from "@/components/dashboard/FilterToolbox";
import SubHeader from "@/components/dashboard/SubHeader";

export default function DashboardPage() {
  const handleRefresh = () => {
    console.log("Refreshing dashboard telemetry data...");
  };

  const handleExportCalls = () => {
    console.log("Exporting call logs...");
  };

  const handleExportSales = () => {
    console.log("Exporting sales & transfer reports...");
  };

  return (
    <div className="min-h-screen bg-[#050505] text-neutral-100">
      {/* Top Brand Bar */}
      <TopNavbar />

      {/* Multi-Select Filters & Tags */}
      <FilterToolbar onRefresh={handleRefresh} />

      {/* Section Header & Export Buttons */}
      <SubHeader
        onExportCalls={handleExportCalls}
        onExportSales={handleExportSales}
      />

      {/* Dashboard Body Content */}
      <main className="p-6">
        {/* Metric Cards, Graphs & Data Tables will be placed here */}
      </main>
    </div>
  );
}