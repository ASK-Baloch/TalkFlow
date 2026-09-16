"use client";

import React from "react";
import { useCallsState } from "./hooks/useCallsState";
import CallHistoryView from "./components/CallHistoryView";
import LiveMonitorPanel from "./components/LiveMonitorPanel";
import CallDetailView from "./components/CallDetailView";

export default function CallsView({ initialAction, onActionChange }) {
  const state = useCallsState(initialAction, onActionChange);

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* ROUTE 1: /calls (Call History CDR) */}
      {state.routeInfo.mode === "history" && (
        <CallHistoryView
          totalCallsCount={state.totalCallsCount}
          passedCount={state.passedCount}
          liveCount={state.liveCount}
          searchQuery={state.searchQuery}
          onSearchChange={state.setSearchQuery}
          dispositionFilter={state.dispositionFilter}
          onDispositionFilterChange={state.setDispositionFilter}
          filteredCalls={state.filteredCalls}
          onOpenLive={() => state.navigateToAction("live")}
          onOpenCall={state.navigateToAction}
        />
      )}

      {/* ROUTE 2: /calls/live (Live Call Monitoring) */}
      {state.routeInfo.mode === "live" && (
        <LiveMonitorPanel
          liveCalls={state.liveCalls}
          onBack={() => state.navigateToAction(null)}
          activeMonitorChannel={state.activeMonitorChannel}
          monitorMode={state.monitorMode}
          onOpenMonitor={state.openMonitor}
          onCloseMonitor={state.closeMonitor}
        />
      )}

      {/* ROUTE 3: /calls/[callId] (Call Detail View with Segmented Tabs) */}
      {state.routeInfo.mode === "detail" && state.activeCall && (
        <CallDetailView
          call={state.activeCall}
          onBack={() => state.navigateToAction(null)}
          detailTab={state.detailTab}
          onDetailTabChange={state.setDetailTab}
          isPlaying={state.isPlaying}
          onTogglePlay={() => state.setIsPlaying(!state.isPlaying)}
          playbackSpeed={state.playbackSpeed}
          onSpeedChange={state.setPlaybackSpeed}
        />
      )}
    </div>
  );
}