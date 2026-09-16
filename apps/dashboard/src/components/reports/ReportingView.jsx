"use client";

import React, { useState } from "react";
import {
  BarChart3,
  Play,
  Pause,
  Download,
  FileText,
  CheckCircle2,
  XCircle,
  Star,
  Search,
  UserCheck,
  ShieldCheck,
  ChevronRight,
  X,
  Headphones,
  Radio,
  FileSpreadsheet,
  Check,
  Copy,
} from "lucide-react";
import { INITIAL_RECORDINGS, REPORT_CATALOG } from "@/data";

export default function ReportingView() {
  // Navigation / View State
  const [activeTab, setActiveTab] = useState("recordings"); // 'recordings', 'realtime', 'catalog', 'qa'
  const [categoryFilter, setCategoryFilter] = useState("all"); // 'all', 'realtime', 'performance', 'calls_audio', 'inbound'
  const [searchQuery, setSearchQuery] = useState("");

  // Recordings & Audio Player State (FR-10)
  const [recordings, setRecordings] = useState(INITIAL_RECORDINGS);
  const [activePlayingId, setActivePlayingId] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0); // 1.0, 1.25, 1.5, 2.0
  const [audioProgress, setAudioProgress] = useState(35); // 0 to 100%

  // Transcript Drawer State
  const [selectedTranscriptRec, setSelectedTranscriptRec] = useState(null);
  const [isTranscriptOpen, setIsTranscriptOpen] = useState(false);

  // QA Audit Modal State (FR-11)
  const [selectedQaRec, setSelectedQaRec] = useState(null);
  const [isQaModalOpen, setIsQaModalOpen] = useState(false);
  const [qaRating, setQaRating] = useState(5);
  const [qaConsentVerified, setQaConsentVerified] = useState(true);
  const [qaQualVerified, setQaQualVerified] = useState(true);
  const [qaTransferVerified, setQaTransferVerified] = useState(true);
  const [qaNotes, setQaNotes] = useState("");
  const [copiedId, setCopiedId] = useState(null);

  // Filtered Recordings List
  const filteredRecordings = recordings.filter((r) => {
    const matchesSearch =
      r.leadName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.phone.includes(searchQuery) ||
      r.callId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.disposition.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.verifier.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  // Filtered Report Catalog
  const filteredCatalog = REPORT_CATALOG.filter((rep) => {
    const matchesCategory = categoryFilter === "all" || rep.category === categoryFilter;
    const matchesSearch =
      rep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rep.desc.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Play / Pause Audio Control
  const togglePlayAudio = (recId) => {
    if (activePlayingId === recId) {
      setIsPlaying(!isPlaying);
    } else {
      setActivePlayingId(recId);
      setIsPlaying(true);
      setAudioProgress(10);
    }
  };

  // Open Transcript Drawer
  const openTranscript = (rec) => {
    setSelectedTranscriptRec(rec);
    setIsTranscriptOpen(true);
  };

  // Open QA Audit Modal
  const openQaAudit = (rec) => {
    setSelectedQaRec(rec);
    setQaRating(rec.qaScore || 5);
    setQaConsentVerified(rec.consentCaptured);
    setQaQualVerified(rec.qualStatus === "PASSED");
    setQaTransferVerified(rec.verifier !== "—");
    setQaNotes(`Call audited for ${rec.leadName} (${rec.callId}). Compliant Medicare bot qualification.`);
    setIsQaModalOpen(true);
  };

  // Save QA Score
  const saveQaAudit = (e) => {
    e.preventDefault();
    if (!selectedQaRec) return;

    setRecordings((prev) =>
      prev.map((item) =>
        item.id === selectedQaRec.id
          ? {
              ...item,
              qaScore: qaRating,
              qaStatus: "Audited",
              consentCaptured: qaConsentVerified,
            }
          : item
      )
    );
    setIsQaModalOpen(false);
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard?.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-100 font-sans min-h-screen bg-[#050505]">
      {/* 1. Header & Section Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Reporting & Call Recording Center
            </h1>
            <span className="rounded-full bg-emerald-600/20 border border-emerald-500/40 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
              PRD FR-10, FR-11 & FR-12
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-400">
            Searchable call recordings, inline waveform player, AI bot transcripts, QA scorecards, and Morpheus operations telemetry.
          </p>
        </div>

        {/* Global Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search leads, CDRs, phone, dispo..."
            className="w-full rounded-lg border border-neutral-800 bg-[#0d0d0d] pl-9 pr-4 py-2 text-xs text-white placeholder-neutral-500 outline-none focus:border-neutral-700"
          />
        </div>
      </div>

      {/* 2. Top Main View Mode Selector Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800/80 pb-3">
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab("recordings")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              activeTab === "recordings"
                ? "bg-blue-600 text-white font-bold shadow-sm"
                : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
            }`}
          >
            <Headphones className="h-4 w-4" />
            <span>Call Recordings & Player (FR-10)</span>
            <span className="rounded-full bg-blue-950 px-2 py-0.5 text-[10px] text-blue-300">
              {recordings.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("qa")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              activeTab === "qa"
                ? "bg-purple-600 text-white font-bold shadow-sm"
                : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
            }`}
          >
            <ShieldCheck className="h-4 w-4" />
            <span>QA & Compliance Review (FR-11)</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("realtime")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              activeTab === "realtime"
                ? "bg-emerald-600 text-white font-bold shadow-sm"
                : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
            }`}
          >
            <Radio className="h-4 w-4" />
            <span>Real-Time Operations</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("catalog")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              activeTab === "catalog"
                ? "bg-neutral-800 text-white font-bold shadow-sm"
                : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
            }`}
          >
            <BarChart3 className="h-4 w-4" />
            <span>Morpheus 27-Report Catalog</span>
          </button>
        </div>

        {/* Export Action */}
        <button
          type="button"
          onClick={() => alert("Exporting CDR & Recording Log to CSV...")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-800 bg-[#0d0d0d] px-3 py-1.5 text-xs font-semibold text-neutral-300 hover:bg-neutral-800 hover:text-white transition-colors"
        >
          <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-400" />
          <span>Export CDR CSV</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* VIEW 1: CALL RECORDINGS HUB & INLINE AUDIO PLAYER (PRD FR-10)             */}
      {/* ========================================================================= */}
      {activeTab === "recordings" && (
        <div className="flex flex-col gap-6">
          {/* Active Inline Audio Player Sticky Banner (If Playing) */}
          {activePlayingId && (
            <div className="rounded-xl border border-blue-900/60 bg-blue-950/30 p-4 shadow-xl backdrop-blur-xs flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => togglePlayAudio(activePlayingId)}
                  className="flex h-11 w-11 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-500 transition-transform active:scale-95"
                >
                  {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
                </button>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm">
                      {recordings.find((r) => r.id === activePlayingId)?.leadName}
                    </span>
                    <span className="font-mono text-xs text-blue-400">
                      {recordings.find((r) => r.id === activePlayingId)?.phone}
                    </span>
                    <span className="rounded-md bg-emerald-950 border border-emerald-800 px-2 py-0.5 text-[10px] font-bold text-emerald-400">
                      {recordings.find((r) => r.id === activePlayingId)?.disposition}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Verifier: <strong className="text-white">{recordings.find((r) => r.id === activePlayingId)?.verifier}</strong> • Consent: <span className="text-emerald-400 font-bold">FR-06 Captured</span>
                  </p>
                </div>
              </div>

              {/* Audio Waveform Progress Bar & Speed */}
              <div className="flex-1 max-w-xl w-full flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400">
                  <span>00:42</span>
                  <span className="text-neutral-500">
                    Waveform Preview • {recordings.find((r) => r.id === activePlayingId)?.duration}
                  </span>
                  <span>{recordings.find((r) => r.id === activePlayingId)?.duration}</span>
                </div>

                {/* Simulated Audio Waveform Visualizer */}
                <div
                  className="relative h-6 w-full cursor-pointer rounded bg-neutral-900 border border-neutral-800 flex items-center px-1 gap-0.5 overflow-hidden"
                  onClick={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const clickX = e.clientX - rect.left;
                    setAudioProgress(Math.round((clickX / rect.width) * 100));
                  }}
                >
                  {Array.from({ length: 48 }).map((_, idx) => {
                    const heightPct = Math.max(20, Math.sin(idx * 0.4) * 100);
                    const isPlayed = idx < (48 * audioProgress) / 100;
                    return (
                      <div
                        key={idx}
                        className={`flex-1 rounded-sm transition-all ${
                          isPlayed ? "bg-blue-500" : "bg-neutral-800"
                        }`}
                        style={{ height: `${heightPct}%` }}
                      />
                    );
                  })}
                </div>
              </div>

              {/* Speed & Transcript Action */}
              <div className="flex items-center gap-2">
                <select
                  value={playbackSpeed}
                  onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                  className="rounded-md border border-neutral-800 bg-[#121214] px-2.5 py-1.5 text-xs font-bold text-white outline-none"
                >
                  <option value={1.0}>1.0x</option>
                  <option value={1.25}>1.25x</option>
                  <option value={1.5}>1.5x</option>
                  <option value={2.0}>2.0x</option>
                </select>

                <button
                  type="button"
                  onClick={() => openTranscript(recordings.find((r) => r.id === activePlayingId))}
                  className="inline-flex items-center gap-1 rounded-md bg-purple-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-purple-700 transition-colors"
                >
                  <FileText className="h-3.5 w-3.5" />
                  <span>Transcript</span>
                </button>
              </div>
            </div>
          )}

          {/* Recordings Data Table (PRD FR-10) */}
          <div className="w-full rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Headphones className="h-4 w-4 text-blue-400" />
                  <span>Searchable CDR Audio Recordings (100% Medicare Call Capture)</span>
                </h2>
                <p className="text-xs text-neutral-400">
                  Play audio inline, inspect consent verification (FR-06), review qualification answers, and audit QA scorecards.
                </p>
              </div>

              <span className="text-xs text-neutral-500 font-mono">
                Showing {filteredRecordings.length} recordings
              </span>
            </div>

            <div className="w-full overflow-x-auto rounded-lg border border-neutral-800">
              <table className="w-full min-w-[1000px] border-collapse text-xs text-left">
                <thead>
                  <tr className="border-b border-neutral-800 bg-neutral-950 text-neutral-400 font-bold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Call ID / Lead</th>
                    <th className="px-4 py-3">Phone Number</th>
                    <th className="px-4 py-3">Campaign</th>
                    <th className="px-3 py-3 text-center">Dispo</th>
                    <th className="px-3 py-3 text-center">Duration</th>
                    <th className="px-4 py-3 text-center">Consent (FR-06)</th>
                    <th className="px-4 py-3">Verifier / QA</th>
                    <th className="px-4 py-3 text-right">Actions & Audio</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/70 bg-[#0d0d0d]">
                  {filteredRecordings.map((rec) => (
                    <tr
                      key={rec.id}
                      className={`transition-colors ${
                        activePlayingId === rec.id
                          ? "bg-blue-950/20"
                          : "hover:bg-neutral-900/50"
                      }`}
                    >
                      {/* Lead / Call ID */}
                      <td className="px-4 py-3.5">
                        <div className="flex flex-col">
                          <span className="font-bold text-white flex items-center gap-1.5">
                            {rec.leadName}
                            <button
                              onClick={() => copyToClipboard(rec.callId, rec.id)}
                              className="text-neutral-500 hover:text-neutral-300"
                              title="Copy Call ID"
                            >
                              {copiedId === rec.id ? (
                                <Check className="h-3 w-3 text-emerald-400" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </button>
                          </span>
                          <span className="text-[10px] font-mono text-neutral-500">
                            {rec.callId} • {rec.timestamp}
                          </span>
                        </div>
                      </td>

                      {/* Phone */}
                      <td className="px-4 py-3.5 font-mono text-neutral-300 font-medium">
                        {rec.phone}
                      </td>

                      {/* Campaign */}
                      <td className="px-4 py-3.5">
                        <span className="rounded-md bg-neutral-900 border border-neutral-800 px-2 py-0.5 text-[11px] font-semibold text-neutral-300">
                          {rec.campaign}
                        </span>
                      </td>

                      {/* Dispo Badge */}
                      <td className="px-3 py-3.5 text-center">
                        <span
                          className={`rounded-md px-2.5 py-0.5 text-[10px] font-extrabold uppercase ${
                            rec.disposition === "SALE"
                              ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                              : rec.disposition === "RAXFER"
                              ? "bg-blue-950 text-blue-400 border border-blue-800"
                              : rec.disposition === "DNC"
                              ? "bg-rose-950 text-rose-400 border border-rose-800"
                              : "bg-amber-950 text-amber-400 border border-amber-800"
                          }`}
                        >
                          {rec.disposition}
                        </span>
                      </td>

                      {/* Duration */}
                      <td className="px-3 py-3.5 text-center font-mono font-bold text-white">
                        {rec.duration}
                      </td>

                      {/* Consent Captured Badge */}
                      <td className="px-4 py-3.5 text-center">
                        {rec.consentCaptured ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-0.5 text-[10px] font-bold text-emerald-400">
                            <CheckCircle2 className="h-3 w-3" /> Captured
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 border border-rose-500/30 px-2.5 py-0.5 text-[10px] font-bold text-rose-400">
                            <XCircle className="h-3 w-3" /> Opt-Out
                          </span>
                        )}
                      </td>

                      {/* Verifier & QA Score */}
                      <td className="px-4 py-3.5">
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-white">
                            {rec.verifier}
                          </span>
                          <div className="flex items-center gap-1 text-[10px] text-amber-400 font-bold mt-0.5">
                            {rec.qaScore > 0 ? (
                              <>
                                <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                                <span>{rec.qaScore.toFixed(1)} / 5.0</span>
                              </>
                            ) : (
                              <span className="text-neutral-500">Unassigned</span>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Audio Controls */}
                      <td className="px-4 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            type="button"
                            onClick={() => togglePlayAudio(rec.id)}
                            className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-bold transition-colors ${
                              activePlayingId === rec.id && isPlaying
                                ? "bg-amber-600 text-white"
                                : "bg-blue-600 text-white hover:bg-blue-700"
                            }`}
                          >
                            {activePlayingId === rec.id && isPlaying ? (
                              <>
                                <Pause className="h-3 w-3" /> Pause
                              </>
                            ) : (
                              <>
                                <Play className="h-3 w-3" /> Play
                              </>
                            )}
                          </button>

                          <button
                            type="button"
                            onClick={() => openTranscript(rec)}
                            className="rounded-md border border-neutral-700 bg-neutral-900 p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-white"
                            title="View AI Bot Call Transcript"
                          >
                            <FileText className="h-3.5 w-3.5 text-purple-400" />
                          </button>

                          <button
                            type="button"
                            onClick={() => openQaAudit(rec)}
                            className="rounded-md border border-neutral-700 bg-neutral-900 p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-white"
                            title="Audit Call (QA Review)"
                          >
                            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                          </button>

                          <a
                            href={rec.audioUrl}
                            download
                            className="rounded-md border border-neutral-700 bg-neutral-900 p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-white"
                            title="Download Audio File (.mp3)"
                          >
                            <Download className="h-3.5 w-3.5 text-neutral-400" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* VIEW 2: QA & COMPLIANCE REVIEW SCORECARDS (PRD FR-11)                    */}
      {/* ========================================================================= */}
      {activeTab === "qa" && (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm">
              <div className="flex items-center justify-between text-xs font-semibold text-neutral-400">
                <span>Compliance Pass Rate</span>
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-emerald-400 mt-1">
                98.6%
              </div>
              <div className="text-[10px] text-neutral-500 mt-1">
                FR-06 mandatory consent statement verified
              </div>
            </div>

            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm">
              <div className="flex items-center justify-between text-xs font-semibold text-neutral-400">
                <span>Average QA Score</span>
                <Star className="h-4 w-4 text-amber-400" />
              </div>
              <div className="text-2xl font-extrabold text-amber-400 mt-1">
                4.85 / 5.0
              </div>
              <div className="text-[10px] text-neutral-500 mt-1">
                Based on 14 audited Medicare transfer calls
              </div>
            </div>

            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm">
              <div className="flex items-center justify-between text-xs font-semibold text-neutral-400">
                <span>Verifier Handoff Accuracy</span>
                <UserCheck className="h-4 w-4 text-blue-400" />
              </div>
              <div className="text-2xl font-extrabold text-blue-400 mt-1">
                99.1%
              </div>
              <div className="text-[10px] text-neutral-500 mt-1">
                FR-08 live agent transfer checklist
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm">
            <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-purple-400" />
              <span>QA Review Scorecards & Audit Logs (PRD FR-11)</span>
            </h2>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {recordings.map((rec) => (
                <div
                  key={rec.id}
                  className="rounded-xl border border-neutral-800 bg-[#121214] p-4 shadow-sm flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between border-b border-neutral-800 pb-2 mb-3">
                      <div>
                        <h3 className="font-bold text-white text-sm">{rec.leadName}</h3>
                        <p className="text-[10px] font-mono text-neutral-500">
                          {rec.callId} • {rec.phone}
                        </p>
                      </div>

                      <div className="flex items-center gap-1 text-amber-400 font-bold">
                        <Star className="h-4 w-4 fill-amber-400" />
                        <span>{rec.qaScore > 0 ? `${rec.qaScore.toFixed(1)} / 5.0` : "Pending"}</span>
                      </div>
                    </div>

                    {/* Qualification & Compliance Checks */}
                    <div className="flex flex-col gap-1.5 text-xs text-neutral-300">
                      <div className="flex items-center justify-between">
                        <span>Recording Consent Capture (FR-06):</span>
                        {rec.consentCaptured ? (
                          <span className="font-bold text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="h-3.5 w-3.5" /> Passed
                          </span>
                        ) : (
                          <span className="font-bold text-rose-400 flex items-center gap-1">
                            <XCircle className="h-3.5 w-3.5" /> Failed
                          </span>
                        )}
                      </div>

                      <div className="flex items-center justify-between">
                        <span>Medicare Qual Checks (FR-07):</span>
                        <span className="font-semibold text-neutral-200">
                          {rec.qualDetails}
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span>Live Verifier Handoff (FR-08):</span>
                        <span className="font-bold text-blue-400">{rec.verifier}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-neutral-800 flex items-center justify-between">
                    <span className="text-[10px] text-neutral-500">
                      Status: <strong className="text-white">{rec.qaStatus}</strong>
                    </span>
                    <button
                      type="button"
                      onClick={() => openQaAudit(rec)}
                      className="rounded-md bg-purple-600 px-3 py-1 text-xs font-bold text-white hover:bg-purple-700 transition-colors"
                    >
                      Audit Scorecard
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* VIEW 3: MORPHEUS 27-REPORT CATALOG GRID                                   */}
      {/* ========================================================================= */}
      {activeTab === "catalog" && (
        <div className="flex flex-col gap-6">
          {/* Category Filter Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto text-xs font-bold">
            <button
              onClick={() => setCategoryFilter("all")}
              className={`rounded-lg px-3 py-1.5 transition-colors ${
                categoryFilter === "all"
                  ? "bg-white text-black font-extrabold"
                  : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
              }`}
            >
              All Reports ({REPORT_CATALOG.length})
            </button>
            <button
              onClick={() => setCategoryFilter("realtime")}
              className={`rounded-lg px-3 py-1.5 transition-colors ${
                categoryFilter === "realtime"
                  ? "bg-white text-black font-extrabold"
                  : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
              }`}
            >
              Real-Time (5)
            </button>
            <button
              onClick={() => setCategoryFilter("performance")}
              className={`rounded-lg px-3 py-1.5 transition-colors ${
                categoryFilter === "performance"
                  ? "bg-white text-black font-extrabold"
                  : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
              }`}
            >
              Performance (12)
            </button>
            <button
              onClick={() => setCategoryFilter("calls_audio")}
              className={`rounded-lg px-3 py-1.5 transition-colors ${
                categoryFilter === "calls_audio"
                  ? "bg-white text-black font-extrabold"
                  : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
              }`}
            >
              Calls & Audio (5)
            </button>
            <button
              onClick={() => setCategoryFilter("inbound")}
              className={`rounded-lg px-3 py-1.5 transition-colors ${
                categoryFilter === "inbound"
                  ? "bg-white text-black font-extrabold"
                  : "bg-[#0d0d0d] text-neutral-400 hover:text-white border border-neutral-800"
              }`}
            >
              Inbound (3)
            </button>
          </div>

          {/* Catalog Cards Grid */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredCatalog.map((rep) => {
              const IconComp = rep.icon;
              return (
                <div
                  key={rep.id}
                  onClick={() => {
                    if (rep.category === "calls_audio") setActiveTab("recordings");
                    else if (rep.category === "realtime") setActiveTab("realtime");
                    else alert(`Opening report: ${rep.title}`);
                  }}
                  className="group cursor-pointer rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm transition-all hover:border-neutral-700 hover:bg-[#121215]"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-900 border border-neutral-800 text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                      <IconComp className="h-5 w-5" />
                    </div>
                    <span className="rounded-full bg-neutral-900 border border-neutral-800 px-2.5 py-0.5 text-[10px] font-bold text-neutral-400">
                      {rep.count}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors flex items-center justify-between">
                    <span>{rep.title}</span>
                    <ChevronRight className="h-4 w-4 text-neutral-600 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-transform" />
                  </h3>

                  <p className="text-xs text-neutral-400 mt-1.5 leading-relaxed">
                    {rep.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* VIEW 4: REAL-TIME OPERATIONS TELEMETRY (MORPHEUS REALTIME EMBEDDED)       */}
      {/* ========================================================================= */}
      {activeTab === "realtime" && (
        <div className="flex flex-col gap-6">
          {/* Quick Realtime Metric Bar */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-3 text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">Active Calls</span>
              <p className="text-xl font-extrabold text-cyan-400 font-mono mt-0.5">4</p>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-3 text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">Agents Online</span>
              <p className="text-xl font-extrabold text-emerald-400 font-mono mt-0.5">4 / 5</p>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-3 text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">Total Channels</span>
              <p className="text-xl font-extrabold text-indigo-400 font-mono mt-0.5">1,634</p>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-3 text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">Calls Today</span>
              <p className="text-xl font-extrabold text-blue-400 font-mono mt-0.5">142</p>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-3 text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">Sales / Qual</span>
              <p className="text-xl font-extrabold text-emerald-400 font-mono mt-0.5">18</p>
            </div>
            <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-3 text-center">
              <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500">Drop Rate</span>
              <p className="text-xl font-extrabold text-amber-400 font-mono mt-0.5">1.4%</p>
            </div>
          </div>

          {/* Realtime Call Sessions Table */}
          <div className="rounded-xl border border-neutral-800 bg-[#0d0d0d] p-5 shadow-sm">
            <h2 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <Radio className="h-4 w-4 text-emerald-400" />
              <span>Live Active Call Channels & Handoffs</span>
            </h2>

            <div className="w-full overflow-x-auto rounded-lg border border-neutral-800">
              <table className="w-full min-w-[850px] border-collapse text-xs text-left">
                <thead>
                  <tr className="border-b border-neutral-800 bg-neutral-950 text-neutral-400 font-bold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Caller ID</th>
                    <th className="px-4 py-3">Destination</th>
                    <th className="px-3 py-3 text-center">Talk Time</th>
                    <th className="px-4 py-3 text-center">State</th>
                    <th className="px-4 py-3">Assigned Verifier</th>
                    <th className="px-4 py-3">SIP Trunk Node</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/70 bg-[#0d0d0d]">
                  <tr className="hover:bg-neutral-900/50">
                    <td className="px-4 py-3.5 font-mono font-bold text-white">(850) 388-4586</td>
                    <td className="px-4 py-3.5 font-mono text-neutral-300">235812#7702568940</td>
                    <td className="px-3 py-3.5 text-center font-mono font-bold text-emerald-400">00:14</td>
                    <td className="px-4 py-3.5 text-center">
                      <span className="rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-bold text-emerald-400">In Call</span>
                    </td>
                    <td className="px-4 py-3.5 font-bold text-white">Adriana</td>
                    <td className="px-4 py-3.5 text-neutral-400 font-mono">node-us-east-1a</td>
                  </tr>
                  <tr className="hover:bg-neutral-900/50">
                    <td className="px-4 py-3.5 font-mono font-bold text-white">(321) 325-8709</td>
                    <td className="px-4 py-3.5 font-mono text-neutral-300">235812#3369055393</td>
                    <td className="px-3 py-3.5 text-center font-mono font-bold text-emerald-400">00:45</td>
                    <td className="px-4 py-3.5 text-center">
                      <span className="rounded-full bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-bold text-emerald-400">In Call</span>
                    </td>
                    <td className="px-4 py-3.5 font-bold text-white">Harper</td>
                    <td className="px-4 py-3.5 text-neutral-400 font-mono">node-us-east-1b</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 1: AI BOT CALL TRANSCRIPT DRAWER                                    */}
      {/* ========================================================================= */}
      {isTranscriptOpen && selectedTranscriptRec && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-xs">
          <div className="w-full max-w-2xl rounded-xl border border-neutral-800 bg-[#121214] p-6 shadow-2xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-purple-400" />
                <div>
                  <h3 className="text-base font-bold text-white">
                    AI Voice Bot Call Transcript
                  </h3>
                  <p className="text-xs text-neutral-400 font-mono">
                    {selectedTranscriptRec.callId} • {selectedTranscriptRec.leadName} ({selectedTranscriptRec.phone})
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsTranscriptOpen(false)}
                className="text-neutral-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Transcript Messages Stream */}
            <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-3 text-xs">
              {selectedTranscriptRec.transcript.map((line, idx) => (
                <div
                  key={idx}
                  className={`rounded-lg p-3 border ${
                    line.speaker === "Bot"
                      ? "bg-blue-950/30 border-blue-900/50 text-blue-100"
                      : line.speaker === "Lead"
                      ? "bg-neutral-900 border-neutral-800 text-neutral-200"
                      : "bg-purple-950/30 border-purple-900/50 text-purple-100"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1 font-bold text-[11px]">
                    <span
                      className={
                        line.speaker === "Bot"
                          ? "text-blue-400"
                          : line.speaker === "Lead"
                          ? "text-emerald-400"
                          : "text-purple-400"
                      }
                    >
                      {line.speaker === "Bot" ? "🤖 TalkFlow AI Bot" : line.speaker === "Lead" ? `👤 Lead (${selectedTranscriptRec.leadName})` : `🎙️ Verifier (${selectedTranscriptRec.verifier})`}
                    </span>
                    <span className="font-mono text-[10px] text-neutral-500">
                      {line.time}
                    </span>
                  </div>
                  <p className="leading-relaxed">{line.text}</p>
                </div>
              ))}
            </div>

            <div className="border-t border-neutral-800 pt-4 mt-4 flex items-center justify-between text-xs">
              <span className="text-neutral-400">
                Consent captured: <strong className="text-emerald-400">YES (FR-06)</strong>
              </span>
              <button
                type="button"
                onClick={() => setIsTranscriptOpen(false)}
                className="rounded-md bg-neutral-800 px-4 py-1.5 font-bold text-white hover:bg-neutral-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: QA AUDIT & SCORECARD MODAL (PRD FR-11)                          */}
      {/* ========================================================================= */}
      {isQaModalOpen && selectedQaRec && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-xl border border-neutral-800 bg-[#121214] p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-emerald-400" />
                <h3 className="text-base font-bold text-white">
                  QA Call Audit Scorecard (PRD FR-11)
                </h3>
              </div>
              <button
                onClick={() => setIsQaModalOpen(false)}
                className="text-neutral-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={saveQaAudit} className="flex flex-col gap-4 text-xs">
              <div className="rounded-lg bg-neutral-900 p-3 border border-neutral-800">
                <p className="font-bold text-white">
                  {selectedQaRec.leadName} ({selectedQaRec.phone})
                </p>
                <p className="text-[10px] text-neutral-400 font-mono mt-0.5">
                  Call ID: {selectedQaRec.callId} • Campaign: {selectedQaRec.campaign} • Verifier: {selectedQaRec.verifier}
                </p>
              </div>

              {/* Star Rating Selector */}
              <div>
                <label className="block font-bold text-neutral-300 mb-1">
                  Overall Call QA Rating (1 - 5 Stars)
                </label>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setQaRating(star)}
                      className={`p-1.5 rounded-lg border transition-all ${
                        qaRating >= star
                          ? "bg-amber-950/60 border-amber-500/80 text-amber-400"
                          : "bg-neutral-900 border-neutral-800 text-neutral-600"
                      }`}
                    >
                      <Star className={`h-5 w-5 ${qaRating >= star ? "fill-amber-400" : ""}`} />
                    </button>
                  ))}
                  <span className="font-bold text-amber-400 ml-2 font-mono text-sm">
                    {qaRating}.0 / 5.0
                  </span>
                </div>
              </div>

              {/* Mandatory Checklist Items */}
              <div className="flex flex-col gap-2 rounded-lg border border-neutral-800 bg-[#18181b] p-3">
                <span className="font-bold text-white text-[11px]">
                  Compliance Checklist Audits:
                </span>

                <label className="flex items-center justify-between cursor-pointer">
                  <span>Mandatory Recording Consent Capture (FR-06)</span>
                  <input
                    type="checkbox"
                    checked={qaConsentVerified}
                    onChange={(e) => setQaConsentVerified(e.target.checked)}
                    className="h-4 w-4 rounded accent-emerald-500"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <span>Medicare Part A & B Qualification (FR-07)</span>
                  <input
                    type="checkbox"
                    checked={qaQualVerified}
                    onChange={(e) => setQaQualVerified(e.target.checked)}
                    className="h-4 w-4 rounded accent-emerald-500"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <span>Live Verifier Warm Handoff (FR-08)</span>
                  <input
                    type="checkbox"
                    checked={qaTransferVerified}
                    onChange={(e) => setQaTransferVerified(e.target.checked)}
                    className="h-4 w-4 rounded accent-emerald-500"
                  />
                </label>
              </div>

              {/* Auditor Notes */}
              <div>
                <label className="block font-bold text-neutral-300 mb-1">
                  Auditor Comments & Compliance Notes
                </label>
                <textarea
                  rows={3}
                  value={qaNotes}
                  onChange={(e) => setQaNotes(e.target.value)}
                  placeholder="Enter auditor evaluation details..."
                  className="w-full rounded-md border border-neutral-800 bg-[#18181b] p-2.5 text-white outline-none focus:border-neutral-600"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-neutral-800 mt-2">
                <button
                  type="button"
                  onClick={() => setIsQaModalOpen(false)}
                  className="rounded-md px-3 py-1.5 text-neutral-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-md bg-purple-600 px-4 py-1.5 font-bold text-white hover:bg-purple-700 transition-colors"
                >
                  Save QA Scorecard
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
