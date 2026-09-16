"use client";

import React, { useState, useEffect } from "react";
import {
  Zap,
  PhoneOutgoing,
  PhoneCall,
  Server,
  Activity,
  Clock,
  PhoneIncoming,
  Users,
  UserCheck,
  UserX,
  PauseCircle,
  Filter,
  RefreshCw,
  Settings,
  ChevronDown,
  Play,
  Pause,
  SlidersHorizontal,
} from "lucide-react";
import { REALTIME_CAMPAIGNS, LIVE_CALL_SESSIONS } from "@/data";

export default function RealtimeReportView() {
  const [liveUpdate, setLiveUpdate] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState("all");
  const [refreshInterval, setRefreshInterval] = useState("5");
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Collapsible section toggles
  const [isOverviewOpen, setIsOverviewOpen] = useState(true);
  const [isCampaignsOpen, setIsCampaignsOpen] = useState(true);
  const [isLiveCallsOpen, setIsLiveCallsOpen] = useState(true);

  const handleManualRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 600);
  };

  // Filtered campaigns list
  const filteredCampaigns =
    selectedCampaign === "all"
      ? REALTIME_CAMPAIGNS
      : REALTIME_CAMPAIGNS.filter((c) => c.id === selectedCampaign);

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-100 font-sans min-h-screen bg-stone-950">
      {/* 1. Realtime Report Control Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-stone-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Realtime Report
          </h1>
          <p className="mt-0.5 text-xs text-stone-400">
            Live operations dashboard ·{" "}
            <span className="text-emerald-400 font-bold">4 agents online</span>
          </p>
        </div>

        {/* Toolbar Controls */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Live Update Toggle */}
          <button
            type="button"
            onClick={() => setLiveUpdate(!liveUpdate)}
            className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 font-semibold transition-colors ${
              liveUpdate
                ? "border-emerald-800/80 bg-emerald-950/60 text-emerald-400 hover:bg-emerald-900/60"
                : "border-stone-700 bg-stone-900 text-stone-400 hover:bg-stone-800"
            }`}
          >
            <span className="relative flex h-2 w-2">
              {liveUpdate && (
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              )}
              <span
                className={`relative inline-flex h-2 w-2 rounded-full ${
                  liveUpdate ? "bg-emerald-400" : "bg-stone-500"
                }`}
              />
            </span>
            <span>Live update: {liveUpdate ? "On" : "Off"}</span>
          </button>

          {/* Campaign Filter Select */}
          <div className="flex items-center gap-1.5 text-stone-400">
            <span className="hidden sm:inline text-xs font-medium">Campaign:</span>
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="rounded-lg border border-stone-700 bg-stone-900 px-2.5 py-1.5 text-xs font-semibold text-white outline-none focus:border-stone-500"
            >
              <option value="all">All campaigns</option>
              {REALTIME_CAMPAIGNS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Refresh Interval Select */}
          <div className="flex items-center gap-1.5 text-stone-400">
            <span className="hidden sm:inline text-xs font-medium">Refresh:</span>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(e.target.value)}
              className="rounded-lg border border-stone-700 bg-stone-900 px-2.5 py-1.5 text-xs font-semibold text-white outline-none focus:border-stone-500"
            >
              <option value="5">5s</option>
              <option value="10">10s</option>
              <option value="20">20s</option>
              <option value="40">40s</option>
              <option value="60">60s</option>
            </select>
          </div>

          {/* Manual Refresh Button */}
          <button
            type="button"
            onClick={handleManualRefresh}
            title="Refresh Operations Telemetry"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-stone-700 bg-stone-900 text-stone-300 transition-colors hover:border-stone-500 hover:bg-stone-800"
          >
            <RefreshCw
              className={`h-3.5 w-3.5 ${
                isRefreshing ? "animate-spin text-emerald-400" : ""
              }`}
            />
          </button>
        </div>
      </div>

      {/* 2. System Overview 12-KPI Grid */}
      <div className="rounded-xl border border-stone-800 bg-stone-900 shadow-sm">
        <button
          type="button"
          onClick={() => setIsOverviewOpen(!isOverviewOpen)}
          className="flex w-full items-center justify-between px-5 py-3 text-left transition-colors hover:bg-stone-800/50 rounded-t-xl"
        >
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-emerald-400" />
            <span className="text-sm font-bold text-white">System Overview</span>
            <span className="text-[11px] text-stone-500 font-mono">
              142 calls today
            </span>
          </div>
          <ChevronDown
            className={`h-4 w-4 text-stone-400 transition-transform duration-200 ${
              isOverviewOpen ? "rotate-0" : "-rotate-90"
            }`}
          />
        </button>

        {isOverviewOpen && (
          <div className="border-t border-stone-800 p-4">
            <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-6 xl:grid-cols-12 text-center">
              {/* Card 1: Calls Dialing */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <PhoneOutgoing className="mx-auto mb-1 h-4 w-4 text-blue-400" />
                <p className="text-base font-extrabold text-blue-400 font-mono">2</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Calls Dialing
                </p>
              </div>

              {/* Card 2: Active Calls */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <PhoneCall className="mx-auto mb-1 h-4 w-4 text-cyan-400" />
                <p className="text-base font-extrabold text-cyan-400 font-mono">4</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Active Calls
                </p>
              </div>

              {/* Card 3: Total Channels */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <Server className="mx-auto mb-1 h-4 w-4 text-indigo-400" />
                <p className="text-base font-extrabold text-indigo-400 font-mono">1,634</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Total Channels
                </p>
              </div>

              {/* Card 4: Difference */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <Activity className="mx-auto mb-1 h-4 w-4 text-violet-400" />
                <p className="text-base font-extrabold text-violet-400 font-mono">1,634</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Int. Legs
                </p>
              </div>

              {/* Card 5: Calls Waiting */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <Clock className="mx-auto mb-1 h-4 w-4 text-purple-400" />
                <p className="text-base font-extrabold text-purple-400 font-mono">1</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Calls Waiting
                </p>
              </div>

              {/* Card 6: Inbound Calls */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <PhoneIncoming className="mx-auto mb-1 h-4 w-4 text-teal-400" />
                <p className="text-base font-extrabold text-teal-400 font-mono">0</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Inbound Calls
                </p>
              </div>

              {/* Card 7: Agents Logged-In */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <Users className="mx-auto mb-1 h-4 w-4 text-emerald-400" />
                <p className="text-base font-extrabold text-emerald-400 font-mono">4</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Agents Logged-In
                </p>
              </div>

              {/* Card 8: Agents In Calls */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <UserCheck className="mx-auto mb-1 h-4 w-4 text-emerald-500" />
                <p className="text-base font-extrabold text-emerald-500 font-mono">3</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Agents In Calls
                </p>
              </div>

              {/* Card 9: Agents Waiting */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <Clock className="mx-auto mb-1 h-4 w-4 text-sky-400" />
                <p className="text-base font-extrabold text-sky-400 font-mono">1</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Agents Waiting
                </p>
              </div>

              {/* Card 10: Agents Paused */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <PauseCircle className="mx-auto mb-1 h-4 w-4 text-amber-400" />
                <p className="text-base font-extrabold text-amber-400 font-mono">0</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Agents Paused
                </p>
              </div>

              {/* Card 11: Agents In Dead */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <UserX className="mx-auto mb-1 h-4 w-4 text-rose-400" />
                <p className="text-base font-extrabold text-rose-400 font-mono">0</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Agents In Dead
                </p>
              </div>

              {/* Card 12: Agents Dispo */}
              <div className="rounded-lg border border-stone-800/80 bg-stone-950/60 p-2.5 transition-all hover:border-stone-700">
                <SlidersHorizontal className="mx-auto mb-1 h-4 w-4 text-orange-400" />
                <p className="text-base font-extrabold text-orange-400 font-mono">0</p>
                <p className="truncate text-[9px] font-bold uppercase tracking-wider text-stone-500">
                  Agents Dispo
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 3. Campaign Realtime Summary Table */}
      <div className="rounded-xl border border-stone-800 bg-stone-900 shadow-sm">
        <button
          type="button"
          onClick={() => setIsCampaignsOpen(!isCampaignsOpen)}
          className="flex w-full items-center justify-between px-5 py-3 text-left transition-colors hover:bg-stone-800/50 rounded-t-xl"
        >
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-emerald-400" />
            <span className="text-sm font-bold text-white">
              Campaign Realtime Performance
            </span>
          </div>
          <ChevronDown
            className={`h-4 w-4 text-stone-400 transition-transform duration-200 ${
              isCampaignsOpen ? "rotate-0" : "-rotate-90"
            }`}
          />
        </button>

        {isCampaignsOpen && (
          <div className="border-t border-stone-800 p-4">
            <div className="w-full overflow-x-auto rounded-lg border border-stone-800">
              <table className="w-full min-w-[950px] border-collapse text-xs text-left">
                <thead>
                  <tr className="border-b border-stone-800 bg-stone-950 text-stone-400 font-bold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Campaign</th>
                    <th className="px-3 py-3 text-center">Dial Lvl</th>
                    <th className="px-3 py-3 text-center">Mult</th>
                    <th className="px-3 py-3 text-center">Ratio DTO</th>
                    <th className="px-3 py-3 text-center">Agents</th>
                    <th className="px-3 py-3 text-right">Calls</th>
                    <th className="px-3 py-3 text-right">Sales</th>
                    <th className="px-3 py-3 text-right">Drops</th>
                    <th className="px-3 py-3 text-right">Drop%</th>
                    <th className="px-4 py-3 text-center">AMD (H/N/M)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-800/70 bg-stone-900/50">
                  {filteredCampaigns.map((camp) => (
                    <tr
                      key={camp.id}
                      className="transition-colors hover:bg-stone-800/40"
                    >
                      <td className="px-4 py-3.5 font-bold text-white">
                        {camp.name}
                      </td>
                      <td className="px-3 py-3.5 text-center font-mono text-stone-300">
                        {camp.dialLvl}
                      </td>
                      <td className="px-3 py-3.5 text-center font-mono text-stone-300">
                        {camp.mult}
                      </td>
                      <td className="px-3 py-3.5 text-center font-mono text-stone-300">
                        {camp.ratioDto}
                      </td>
                      <td className="px-3 py-3.5 text-center font-mono font-bold text-emerald-400">
                        {camp.agents}
                      </td>
                      <td className="px-3 py-3.5 text-right font-mono font-bold text-white">
                        {camp.calls.toLocaleString()}
                      </td>
                      <td className="px-3 py-3.5 text-right font-mono font-bold text-emerald-400">
                        {camp.sales}
                      </td>
                      <td className="px-3 py-3.5 text-right font-mono text-rose-400">
                        {camp.drops}
                      </td>
                      <td className="px-3 py-3.5 text-right font-mono text-amber-400">
                        {camp.dropPct}
                      </td>
                      <td className="px-4 py-3.5 text-center font-mono text-stone-400">
                        {camp.amdHnm}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* 4. Live Calls & Active Sessions Table */}
      <div className="rounded-xl border border-stone-800 bg-stone-900 shadow-sm">
        <button
          type="button"
          onClick={() => setIsLiveCallsOpen(!isLiveCallsOpen)}
          className="flex w-full items-center justify-between px-5 py-3 text-left transition-colors hover:bg-stone-800/50 rounded-t-xl"
        >
          <div className="flex items-center gap-2">
            <PhoneCall className="h-4 w-4 text-cyan-400" />
            <span className="text-sm font-bold text-white">
              Live Active Call Sessions
            </span>
          </div>
          <ChevronDown
            className={`h-4 w-4 text-stone-400 transition-transform duration-200 ${
              isLiveCallsOpen ? "rotate-0" : "-rotate-90"
            }`}
          />
        </button>

        {isLiveCallsOpen && (
          <div className="border-t border-stone-800 p-4">
            <div className="w-full overflow-x-auto rounded-lg border border-stone-800">
              <table className="w-full min-w-[900px] border-collapse text-xs text-left">
                <thead>
                  <tr className="border-b border-stone-800 bg-stone-950 text-stone-400 font-bold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Phone Number</th>
                    <th className="px-4 py-3">Direction</th>
                    <th className="px-4 py-3">Destination</th>
                    <th className="px-3 py-3 text-center">Talk Time</th>
                    <th className="px-3 py-3 text-center">Wait Time</th>
                    <th className="px-4 py-3 text-center">State</th>
                    <th className="px-4 py-3">Agent</th>
                    <th className="px-4 py-3">Voice Node</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-800/70 bg-stone-900/50">
                  {LIVE_CALL_SESSIONS.map((sess) => (
                    <tr
                      key={sess.id}
                      className="transition-colors hover:bg-stone-800/40"
                    >
                      <td className="px-4 py-3.5 font-mono font-bold text-white">
                        {sess.phoneNumber}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="inline-flex items-center gap-1 text-xs text-blue-400 font-semibold">
                          <PhoneOutgoing className="h-3 w-3" /> {sess.direction}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-mono text-stone-300">
                        {sess.destination}
                      </td>
                      <td className="px-3 py-3.5 text-center font-mono font-bold text-emerald-400">
                        {sess.talkTime}
                      </td>
                      <td className="px-3 py-3.5 text-center font-mono text-amber-400">
                        {sess.waitTime}
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span className="inline-flex items-center rounded-full bg-cyan-950/80 px-2.5 py-0.5 text-xs font-bold text-cyan-400 border border-cyan-800/60">
                          {sess.state}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-bold text-white">
                        {sess.agent}
                      </td>
                      <td className="px-4 py-3.5 text-stone-400 font-mono">
                        {sess.node}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
