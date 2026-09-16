"use client";

import { ArrowLeft, Radio, XCircle } from "lucide-react";

export default function LiveMonitorPanel({
  liveCalls,
  onBack,
  activeMonitorChannel,
  monitorMode,
  onOpenMonitor,
  onCloseMonitor,
}) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="p-1.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-600 hover:text-neutral-900"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-neutral-900 dark:text-white">
                Live Call Monitoring
              </h2>
              <span className="flex items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-300">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                LIVE 1s REFRESH
              </span>
            </div>
            <p className="text-xs text-neutral-500">
              Real-time active Asterisk/VICIDIAL channels, agent whisper, and live barge-in.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {liveCalls.map((lc) => (
          <div
            key={lc.id}
            className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col justify-between gap-4"
          >
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between border-b border-neutral-100 dark:border-neutral-800 pb-3">
                <div className="flex items-center gap-2">
                  <Radio className="h-4 w-4 text-emerald-500 animate-pulse" />
                  <span className="font-mono text-xs font-bold text-blue-600">{lc.channel}</span>
                </div>
                <span className="font-mono text-xs font-extrabold text-emerald-600">
                  {lc.duration}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-neutral-500">Customer Phone:</span>
                  <p className="font-mono font-bold text-neutral-900 dark:text-white">{lc.customerPhone}</p>
                </div>
                <div>
                  <span className="text-neutral-500">Assigned Agent:</span>
                  <p className="font-bold text-neutral-900 dark:text-white">{lc.agentName}</p>
                </div>
                <div>
                  <span className="text-neutral-500">Campaign:</span>
                  <p className="font-semibold text-neutral-700 dark:text-neutral-300">{lc.campaign}</p>
                </div>
                <div>
                  <span className="text-neutral-500">AMD Result:</span>
                  <p className="font-semibold text-emerald-600">{lc.amdResult}</p>
                </div>
              </div>

              <div className="flex flex-col gap-1 mt-1 bg-neutral-50 dark:bg-[#151518] p-3 rounded-lg border border-neutral-200 dark:border-neutral-800">
                <span className="text-[10px] text-neutral-400 font-bold uppercase">Live Audio Stream Waveform</span>
                <div className="flex items-center gap-1 h-6">
                  {[40, 70, 90, 60, 30, 80, 100, 50, 40, 85, 95, 40, 60].map((h, i) => (
                    <div
                      key={i}
                      className="w-1.5 bg-emerald-500 rounded-full transition-all duration-300"
                      style={{ height: `${(h * lc.audioLevel) / 100}%` }}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-neutral-100 dark:border-neutral-800">
              <button
                type="button"
                onClick={() => onOpenMonitor(lc, "listen")}
                className="px-3 py-1.5 bg-blue-50 text-blue-600 font-bold text-xs rounded-md border border-blue-200 hover:bg-blue-100"
              >
                Listen (Silent)
              </button>
              <button
                type="button"
                onClick={() => onOpenMonitor(lc, "whisper")}
                className="px-3 py-1.5 bg-purple-50 text-purple-700 font-bold text-xs rounded-md border border-purple-200 hover:bg-purple-100"
              >
                Whisper Agent
              </button>
              <button
                type="button"
                onClick={() => onOpenMonitor(lc, "barge")}
                className="px-3 py-1.5 bg-rose-600 text-white font-bold text-xs rounded-md hover:bg-rose-700"
              >
                Barge In
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Monitor Modal */}
      {activeMonitorChannel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl flex flex-col gap-4">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3">
              <h3 className="text-base font-bold uppercase tracking-wider">
                {monitorMode} Mode Activated
              </h3>
              <button onClick={onCloseMonitor} className="text-neutral-400 hover:text-white">
                <XCircle className="h-5 w-5" />
              </button>
            </div>
            <div className="text-xs flex flex-col gap-2">
              <p>Channel: <span className="font-mono font-bold text-blue-600">{activeMonitorChannel.channel}</span></p>
              <p>Agent: <span className="font-bold">{activeMonitorChannel.agentName}</span></p>
              <p>Customer Phone: <span className="font-mono font-bold">{activeMonitorChannel.customerPhone}</span></p>
            </div>
            <div className="p-3 bg-emerald-50 text-emerald-800 text-xs font-bold rounded-lg text-center border border-emerald-200">
              Audio socket connected. Live stream active.
            </div>
            <div className="flex justify-end pt-2 border-t border-neutral-200 dark:border-neutral-800">
              <button
                type="button"
                onClick={onCloseMonitor}
                className="px-4 py-1.5 text-xs font-bold bg-neutral-800 text-white rounded-md"
              >
                Disconnect Session
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}