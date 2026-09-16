"use client";

import { useState, useMemo } from "react";
import { INITIAL_CALLS, LIVE_CALLS_DATA } from "@/data";

// Central state + route parsing for CallsView.
// initialAction can be 'live' (monitor), '[callId]' (detail), or null/'all'/'history' (CDR list).
export function useCallsState(initialAction, onActionChange) {
  const [callsList, setCallsList] = useState(INITIAL_CALLS);
  const [liveCalls, setLiveCalls] = useState(LIVE_CALLS_DATA);
  const [searchQuery, setSearchQuery] = useState("");
  const [dispositionFilter, setDispositionFilter] = useState("all");

  // Route parsing
  const routeInfo = useMemo(() => {
    if (!initialAction || initialAction === "all" || initialAction === "history") {
      return { mode: "history", callId: null };
    }
    if (initialAction === "live") {
      return { mode: "live", callId: null };
    }
    return { mode: "detail", callId: initialAction };
  }, [initialAction]);

  const navigateToAction = (actionStr) => {
    if (onActionChange) {
      onActionChange(actionStr);
    }
  };

  // Find active call for detail view
  const activeCall = useMemo(() => {
    if (!routeInfo.callId) return callsList[0];
    return (
      callsList.find(
        (c) =>
          c.id.toLowerCase() === routeInfo.callId.toLowerCase() ||
          c.callId.toLowerCase() === routeInfo.callId.toLowerCase()
      ) || callsList[0]
    );
  }, [callsList, routeInfo.callId]);

  // Tabbed detail state for /calls/[callId]
  const [detailTab, setDetailTab] = useState("overview"); // 'overview' | 'audio' | 'transcript' | 'qa'

  // Audio player state
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [audioProgress, setAudioProgress] = useState(35); // %

  // Live monitor action modal / state
  const [activeMonitorChannel, setActiveMonitorChannel] = useState(null);
  const [monitorMode, setMonitorMode] = useState(null); // 'listen' | 'whisper' | 'barge'

  // Filtered CDR Call History
  const filteredCalls = useMemo(() => {
    return callsList.filter((c) => {
      if (dispositionFilter !== "all") {
        if (dispositionFilter === "sale" && !c.disposition.includes("SALE")) return false;
        if (dispositionFilter === "raxfer" && !c.disposition.includes("RAXFER")) return false;
        if (dispositionFilter === "dnc" && !c.disposition.includes("DNC")) return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          c.callId.toLowerCase().includes(q) ||
          c.leadName.toLowerCase().includes(q) ||
          c.phone.toLowerCase().includes(q) ||
          c.campaign.toLowerCase().includes(q) ||
          c.agent.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [callsList, searchQuery, dispositionFilter]);

  // Summary Metrics
  const totalCallsCount = callsList.length;
  const passedCount = callsList.filter((c) => c.disposition.includes("SALE")).length;
  const liveCount = liveCalls.length;

  const openMonitor = (channel, mode) => {
    setActiveMonitorChannel(channel);
    setMonitorMode(mode);
  };

  const closeMonitor = () => {
    setActiveMonitorChannel(null);
  };

  return {
    callsList,
    liveCalls,
    searchQuery,
    setSearchQuery,
    dispositionFilter,
    setDispositionFilter,
    routeInfo,
    activeCall,
    detailTab,
    setDetailTab,
    isPlaying,
    setIsPlaying,
    playbackSpeed,
    setPlaybackSpeed,
    setAudioProgress,
    activeMonitorChannel,
    monitorMode,
    filteredCalls,
    totalCallsCount,
    passedCount,
    liveCount,
    navigateToAction,
    openMonitor,
    closeMonitor,
  };
}