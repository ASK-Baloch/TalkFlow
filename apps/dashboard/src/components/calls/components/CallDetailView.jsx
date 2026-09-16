"use client";

import { ArrowLeft, FileText, Volume2, MessageSquare, ShieldCheck } from "lucide-react";
import CallOverviewTab from "./CallOverviewTab";
import AudioPlayerControls from "./AudioPlayerControls";
import CallTranscriptTab from "./CallTranscriptTab";
import CallQaTab from "./CallQaTab";

const DETAIL_TABS = [
  { id: "overview", label: "1. Overview & Metadata", icon: FileText },
  { id: "audio", label: "2. Audio Player & Recording", icon: Volume2 },
  { id: "transcript", label: "3. AI Transcript & Sentiment", icon: MessageSquare },
  { id: "qa", label: "4. Quality Audit & Notes", icon: ShieldCheck },
];

export default function CallDetailView({
  call,
  onBack,
  detailTab,
  onDetailTabChange,
  isPlaying,
  onTogglePlay,
  playbackSpeed,
  onSpeedChange,
}) {
  return (
    <div className="flex flex-col gap-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800/80 pb-4">
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
                Call Detail: {call.callId}
              </h2>
              <span className="font-mono text-xs font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">
                {call.disposition}
              </span>
            </div>
            <span className="text-xs text-neutral-500">
              Lead: {call.leadName} ({call.phone})
            </span>
          </div>
        </div>
      </div>

      {/* Segmented Detail Subtabs */}
      <div className="flex items-center gap-1 overflow-x-auto rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-1.5 shadow-xs text-xs font-semibold">
        {DETAIL_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = detailTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onDetailTabChange(tab.id)}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 whitespace-nowrap transition-all ${
                isActive
                  ? "bg-blue-600 text-white font-bold shadow-xs"
                  : "text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-[#151518]"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB 1: OVERVIEW & METADATA */}
      {detailTab === "overview" && <CallOverviewTab call={call} />}

      {/* TAB 2: AUDIO PLAYER */}
      {detailTab === "audio" && (
        <AudioPlayerControls
          call={call}
          isPlaying={isPlaying}
          onTogglePlay={onTogglePlay}
          playbackSpeed={playbackSpeed}
          onSpeedChange={onSpeedChange}
        />
      )}

      {/* TAB 3: TRANSCRIPT & SENTIMENT */}
      {detailTab === "transcript" && <CallTranscriptTab call={call} />}

      {/* TAB 4: QA AUDIT */}
      {detailTab === "qa" && <CallQaTab call={call} />}
    </div>
  );
}