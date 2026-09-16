"use client";

import { Server, Zap, Radio, Cpu, RefreshCw, Activity, CheckCircle2 } from "lucide-react";

export default function SystemHealthView({ services, onRunDiagnostics }) {
  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
              System Service Health & Telemetry
            </h1>
            <span className="rounded-full bg-emerald-100 dark:bg-emerald-600/20 border border-emerald-300 dark:border-emerald-500/40 px-2.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
              ALL 14 SUBSYSTEMS OPERATIONAL
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
            TalkFlow Core Control Plane: Asterisk, VICIdial, AudioSocket Gateway, STT, TTS, LLM, Script & Rule Engines, Redis, and Database Clusters.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onRunDiagnostics}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-neutral-800 dark:text-white bg-white dark:bg-neutral-900 border border-neutral-300 dark:border-neutral-700 rounded-lg shadow-xs hover:bg-neutral-100 dark:hover:bg-neutral-800"
          >
            <RefreshCw className="h-4 w-4 text-blue-500" />
            <span>Run Subsystem Diagnostics</span>
          </button>
        </div>
      </div>

      {/* Quick Telemetry Overview Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <div className="flex items-center justify-between text-neutral-500">
            <span>Active Subsystems</span>
            <Server className="h-4 w-4 text-blue-500" />
          </div>
          <span className="text-xl font-extrabold text-neutral-900 dark:text-white">14 / 14 Online</span>
          <span className="text-[11px] text-emerald-600 font-bold">100% Operational Uptime</span>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <div className="flex items-center justify-between text-neutral-500">
            <span>Avg Control Latency</span>
            <Zap className="h-4 w-4 text-purple-500" />
          </div>
          <span className="text-xl font-extrabold text-purple-600">27ms</span>
          <span className="text-[11px] text-neutral-500 font-semibold">Real-time Stream Sync</span>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <div className="flex items-center justify-between text-neutral-500">
            <span>SIP Channels Active</span>
            <Radio className="h-4 w-4 text-emerald-500" />
          </div>
          <span className="text-xl font-extrabold text-emerald-600">1,634 Legs</span>
          <span className="text-[11px] text-neutral-500 font-semibold">Carrier Trunk Capacity 81.7%</span>
        </div>

        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs flex flex-col gap-1">
          <div className="flex items-center justify-between text-neutral-500">
            <span>GPU Worker Allocation</span>
            <Cpu className="h-4 w-4 text-amber-500" />
          </div>
          <span className="text-xl font-extrabold text-amber-600">100 Workers</span>
          <span className="text-[11px] text-neutral-500 font-semibold">68 STT / 32 LLM Inference</span>
        </div>
      </div>

      {/* Subsystem Health Cards Grid */}
      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
        <h2 className="text-sm font-bold text-neutral-900 dark:text-white mb-4 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-blue-500" />
            <span>Core Infrastructure Subsystems Telemetry Cards (PRD §29.1)</span>
          </span>
          <span className="text-xs text-neutral-400 font-normal">Real-time WebSocket & REST Poll Synced</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          {services.map((srv) => (
            <div
              key={srv.key}
              className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#121215] p-4 flex flex-col justify-between gap-3 shadow-xs hover:border-neutral-300 dark:hover:border-neutral-700 transition-colors"
            >
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-400">
                    {srv.category}
                  </span>
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800 px-2 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
                    <CheckCircle2 className="h-3 w-3" /> {srv.status.toUpperCase()}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center justify-between">
                  <span>{srv.name}</span>
                  <span className="text-[11px] font-mono text-neutral-400">{srv.version}</span>
                </h3>
                <p className="text-xs text-neutral-500 leading-relaxed">{srv.description}</p>
                {srv.message && (
                  <div className="text-[11px] font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 px-2 py-1 rounded border border-emerald-200 dark:border-emerald-900/50">
                    {srv.message}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-neutral-200 dark:border-neutral-800 flex flex-col gap-1.5 text-[11px]">
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Active Load / Capacity:</span>
                  <span className="font-mono font-bold text-neutral-900 dark:text-white">{srv.concurrency}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Roundtrip Latency:</span>
                  <span className="font-mono font-bold text-blue-600 dark:text-blue-400">{srv.latency}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Uptime / Last Checked:</span>
                  <span className="font-mono text-neutral-400">
                    <strong className="text-emerald-600 dark:text-emerald-400">{srv.uptime}</strong> · {srv.lastCheck}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}