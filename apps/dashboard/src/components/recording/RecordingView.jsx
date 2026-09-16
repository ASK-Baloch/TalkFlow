"use client";

import React, { useState } from "react";
import {
  Headphones,
  Play,
  Pause,
  Download,
  FileText,
  CheckCircle2,
  XCircle,
  Star,
  Search,
  Clock,
  ShieldCheck,
  X,
  FileSpreadsheet,
  Check,
  Copy,
  UserCheck,
} from "lucide-react";
import { INITIAL_RECORDINGS } from "@/data";

export default function RecordingView() {
  const [activeTab, setActiveTab] = useState("recordings"); // 'recordings', 'qa'
  const [searchQuery, setSearchQuery] = useState("");

  // Recordings & Audio Player State
  const [recordings, setRecordings] = useState(INITIAL_RECORDINGS);
  const [activePlayingId, setActivePlayingId] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [audioProgress, setAudioProgress] = useState(35);

  // Transcript Drawer State
  const [selectedTranscriptRec, setSelectedTranscriptRec] = useState(null);
  const [isTranscriptOpen, setIsTranscriptOpen] = useState(false);

  // QA Audit Modal State
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

  const togglePlayAudio = (recId) => {
    if (activePlayingId === recId) {
      setIsPlaying(!isPlaying);
    } else {
      setActivePlayingId(recId);
      setIsPlaying(true);
      setAudioProgress(10);
    }
  };

  const openTranscript = (rec) => {
    setSelectedTranscriptRec(rec);
    setIsTranscriptOpen(true);
  };

  const openQaAudit = (rec) => {
    setSelectedQaRec(rec);
    setQaRating(rec.qaScore || 5);
    setQaConsentVerified(rec.consentCaptured);
    setQaQualVerified(rec.qualStatus === "PASSED");
    setQaTransferVerified(rec.verifier !== "—");
    setQaNotes(`Call audited for ${rec.leadName} (${rec.callId}). Compliant bot qualification.`);
    setIsQaModalOpen(true);
  };

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
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* 1. PRD Header & Section Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
              CDR Recordings & QA Compliance
            </h1>
            <span className="rounded-full bg-blue-100 dark:bg-blue-600/20 border border-blue-300 dark:border-blue-500/40 px-2.5 py-0.5 text-[10px] font-bold text-blue-700 dark:text-blue-400">
              PRD Sec 10 & 11 Compliant
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
            Search audio recordings, verify Medicare consent, review AI qualification transcripts, and audit QA compliance scorecards.
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-neutral-400 dark:text-neutral-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search leads, CDRs, phone, dispo..."
            className="w-full rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] pl-9 pr-4 py-2 text-xs text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-neutral-500 outline-none focus:border-blue-500 dark:focus:border-neutral-700"
          />
        </div>
      </div>

      {/* 2. Mode Selector Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-200 dark:border-neutral-800/80 pb-3">
        <div className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab("recordings")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              activeTab === "recordings"
                ? "bg-blue-600 text-white font-bold shadow-xs"
                : "bg-white dark:bg-[#0d0d0d] text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white border border-neutral-200 dark:border-neutral-800"
            }`}
          >
            <Headphones className="h-4 w-4" />
            <span>Call Recordings & Waveform Player</span>
            <span className="rounded-full bg-blue-100 dark:bg-blue-950 px-2 py-0.5 text-[10px] text-blue-700 dark:text-blue-300 font-bold">
              {recordings.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("qa")}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 transition-all ${
              activeTab === "qa"
                ? "bg-purple-600 text-white font-bold shadow-xs"
                : "bg-white dark:bg-[#0d0d0d] text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white border border-neutral-200 dark:border-neutral-800"
            }`}
          >
            <ShieldCheck className="h-4 w-4" />
            <span>QA & Compliance Review</span>
          </button>
        </div>

        {/* Export Action */}
        <button
          type="button"
          onClick={() => alert("Exporting CDR & Recording Log to CSV...")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] px-3 py-1.5 text-xs font-semibold text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-white transition-colors"
        >
          <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>Export CDR CSV</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* VIEW 1: CALL RECORDINGS HUB & INLINE AUDIO PLAYER                          */}
      {/* ========================================================================= */}
      {activeTab === "recordings" && (
        <div className="flex flex-col gap-6">
          {/* Active Inline Audio Player Sticky Banner (If Playing) */}
          {activePlayingId && (
            <div className="rounded-xl border border-blue-200 dark:border-blue-900/60 bg-blue-50/90 dark:bg-blue-950/30 p-4 shadow-xl backdrop-blur-xs flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => togglePlayAudio(activePlayingId)}
                  className="flex h-11 w-11 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-500 transition-transform active:scale-95 shrink-0"
                >
                  {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
                </button>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-neutral-900 dark:text-white text-sm">
                      {recordings.find((r) => r.id === activePlayingId)?.leadName}
                    </span>
                    <span className="font-mono text-xs text-blue-600 dark:text-blue-400">
                      {recordings.find((r) => r.id === activePlayingId)?.phone}
                    </span>
                    <span className="rounded-md bg-emerald-100 dark:bg-emerald-950 border border-emerald-300 dark:border-emerald-800 px-2 py-0.5 text-[10px] font-bold text-emerald-800 dark:text-emerald-400">
                      {recordings.find((r) => r.id === activePlayingId)?.disposition}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-0.5">
                    Verifier: <strong className="text-neutral-900 dark:text-white">{recordings.find((r) => r.id === activePlayingId)?.verifier}</strong> • Consent: <span className="text-emerald-600 dark:text-emerald-400 font-bold">Captured</span>
                  </p>
                </div>
              </div>

              {/* Audio Waveform Progress Bar & Speed */}
              <div className="flex-1 max-w-xl w-full flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-[11px] font-mono text-neutral-500 dark:text-neutral-400">
                  <span>00:42</span>
                  <span className="text-neutral-500">
                    Waveform Preview • {recordings.find((r) => r.id === activePlayingId)?.duration}
                  </span>
                  <span>{recordings.find((r) => r.id === activePlayingId)?.duration}</span>
                </div>

                {/* Simulated Audio Waveform Visualizer */}
                <div
                  className="relative h-6 w-full cursor-pointer rounded bg-neutral-200 dark:bg-neutral-900 border border-neutral-300 dark:border-neutral-800 flex items-center px-1 gap-0.5 overflow-hidden"
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
                          isPlayed ? "bg-blue-600 dark:bg-blue-500" : "bg-neutral-300 dark:bg-neutral-800"
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
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-white dark:bg-[#121214] px-2.5 py-1.5 text-xs font-bold text-neutral-900 dark:text-white outline-none"
                >
                  <option value={1.0}>1.0x</option>
                  <option value={1.25}>1.25x</option>
                  <option value={1.5}>1.5x</option>
                  <option value={2.0}>2.0x</option>
                </select>

                <button
                  type="button"
                  onClick={() => openTranscript(recordings.find((r) => r.id === activePlayingId))}
                  className="inline-flex items-center gap-1 rounded-md bg-purple-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-purple-700 transition-colors shrink-0"
                >
                  <FileText className="h-3.5 w-3.5" />
                  <span>Transcript</span>
                </button>
              </div>
            </div>
          )}

          {/* Recordings Data Table */}
          <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                  <Headphones className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  <span>Searchable CDR Audio Recordings</span>
                </h2>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Play audio inline, inspect consent verification, review qualification answers, and audit QA scorecards.
                </p>
              </div>

              <span className="text-xs text-neutral-500 font-mono">
                Showing {filteredRecordings.length} recordings
              </span>
            </div>

            <div className="w-full overflow-x-auto rounded-lg border border-neutral-200 dark:border-neutral-800">
              <table className="w-full min-w-[1000px] border-collapse text-xs text-left">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-neutral-950 text-neutral-600 dark:text-neutral-400 font-bold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Call ID / Lead</th>
                    <th className="px-4 py-3">Phone Number</th>
                    <th className="px-4 py-3">Campaign</th>
                    <th className="px-3 py-3 text-center">Dispo</th>
                    <th className="px-3 py-3 text-center">Duration</th>
                    <th className="px-4 py-3 text-center">Consent Status</th>
                    <th className="px-4 py-3">Verifier / QA</th>
                    <th className="px-4 py-3 text-right">Actions & Audio</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/70 bg-white dark:bg-[#0d0d0d]">
                  {filteredRecordings.map((rec) => (
                    <tr
                      key={rec.id}
                      className={`transition-colors ${
                        activePlayingId === rec.id
                          ? "bg-blue-50 dark:bg-blue-950/20"
                          : "hover:bg-neutral-50 dark:hover:bg-neutral-900/50"
                      }`}
                    >
                      {/* Lead / Call ID */}
                      <td className="px-4 py-3.5">
                        <div className="flex flex-col">
                          <span className="font-bold text-neutral-900 dark:text-white flex items-center gap-1.5">
                            {rec.leadName}
                            <button
                              onClick={() => copyToClipboard(rec.callId, rec.id)}
                              className="text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-300"
                              title="Copy Call ID"
                            >
                              {copiedId === rec.id ? (
                                <Check className="h-3 w-3 text-emerald-500" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </button>
                          </span>
                          <span className="text-[10px] font-mono text-neutral-500 mt-0.5">
                            {rec.callId} • {rec.timestamp}
                          </span>
                        </div>
                      </td>

                      {/* Phone */}
                      <td className="px-4 py-3.5 font-mono text-neutral-700 dark:text-neutral-300 font-semibold">
                        {rec.phone}
                      </td>

                      {/* Campaign */}
                      <td className="px-4 py-3.5">
                        <span className="rounded-full bg-blue-100 dark:bg-blue-950/60 border border-blue-300 dark:border-blue-800/50 px-2.5 py-0.5 text-[10px] font-bold text-blue-700 dark:text-blue-300">
                          {rec.campaign}
                        </span>
                      </td>

                      {/* Dispo Badge */}
                      <td className="px-3 py-3.5 text-center">
                        <span
                          className={`inline-block rounded-md px-2 py-0.5 text-[10px] font-bold ${
                            rec.disposition === "SALE"
                              ? "bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800"
                              : rec.disposition === "RAXFER"
                              ? "bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-800"
                              : rec.disposition === "DNC"
                              ? "bg-rose-100 dark:bg-rose-950 text-rose-700 dark:text-rose-400 border border-rose-300 dark:border-rose-800"
                              : "bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800"
                          }`}
                        >
                          {rec.disposition}
                        </span>
                      </td>

                      {/* Duration */}
                      <td className="px-3 py-3.5 text-center font-mono text-neutral-700 dark:text-neutral-300 font-bold">
                        {rec.duration}
                      </td>

                      {/* Consent Captured Badge */}
                      <td className="px-4 py-3.5 text-center">
                        {rec.consentCaptured ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/30 px-2.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
                            <CheckCircle2 className="h-3 w-3" /> Captured
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-rose-100 dark:bg-rose-500/10 border border-rose-300 dark:border-rose-500/30 px-2.5 py-0.5 text-[10px] font-bold text-rose-700 dark:text-rose-400">
                            <XCircle className="h-3 w-3" /> Opt-Out
                          </span>
                        )}
                      </td>

                      {/* Verifier & QA Score */}
                      <td className="px-4 py-3.5">
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-neutral-900 dark:text-white">
                            {rec.verifier}
                          </span>
                          <div className="flex items-center gap-1 text-[10px] text-amber-600 dark:text-amber-400 font-bold mt-0.5">
                            {rec.qaScore > 0 ? (
                              <>
                                <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                                <span>{rec.qaScore.toFixed(1)} / 5.0</span>
                              </>
                            ) : (
                              <span className="text-neutral-400 dark:text-neutral-500">Unassigned</span>
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
                            className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-bold transition-all ${
                              activePlayingId === rec.id && isPlaying
                                ? "bg-amber-600 text-white shadow-xs"
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
                            className="rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-900 p-1.5 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-white"
                            title="View AI Bot Call Transcript"
                          >
                            <FileText className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400" />
                          </button>

                          <button
                            type="button"
                            onClick={() => openQaAudit(rec)}
                            className="rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-900 p-1.5 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-white"
                            title="Audit Call (QA Review)"
                          >
                            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                          </button>

                          <a
                            href={rec.audioUrl}
                            download
                            className="rounded-md border border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-900 p-1.5 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-white"
                            title="Download Audio File (.mp3)"
                          >
                            <Download className="h-3.5 w-3.5 text-neutral-500 dark:text-neutral-400" />
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
      {/* VIEW 2: QA & COMPLIANCE REVIEW SCORECARDS                                 */}
      {/* ========================================================================= */}
      {activeTab === "qa" && (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
              <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
                <span>Compliance Pass Rate</span>
                <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                98.6%
              </div>
              <div className="text-[10px] text-neutral-500 mt-1">
                Mandatory consent statement verified
              </div>
            </div>

            <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
              <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
                <span>Average QA Score</span>
                <Star className="h-4 w-4 text-amber-600 dark:text-amber-400" />
              </div>
              <div className="text-2xl font-extrabold text-amber-600 dark:text-amber-400 mt-1">
                4.85 / 5.0
              </div>
              <div className="text-[10px] text-neutral-500 mt-1">
                Based on 14 audited transfer calls
              </div>
            </div>

            <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
              <div className="flex items-center justify-between text-xs font-semibold text-neutral-500 dark:text-neutral-400">
                <span>Verifier Handoff Accuracy</span>
                <UserCheck className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div className="text-2xl font-extrabold text-blue-600 dark:text-blue-400 mt-1">
                99.1%
              </div>
              <div className="text-[10px] text-neutral-500 mt-1">
                Live agent transfer checklist
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white mb-4 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              <span>QA Review Scorecards & Audit Logs</span>
            </h2>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {recordings.map((rec) => (
                <div
                  key={rec.id}
                  className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#121214] p-4 shadow-xs flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-2 mb-3">
                      <div>
                        <h3 className="font-bold text-neutral-900 dark:text-white text-sm">{rec.leadName}</h3>
                        <p className="text-[10px] font-mono text-neutral-500">
                          {rec.callId} • {rec.phone}
                        </p>
                      </div>

                      <div className="flex items-center gap-1 text-amber-600 dark:text-amber-400 font-bold">
                        <Star className="h-4 w-4 fill-amber-400" />
                        <span>{rec.qaScore > 0 ? `${rec.qaScore.toFixed(1)} / 5.0` : "Pending"}</span>
                      </div>
                    </div>

                    {/* Qualification & Compliance Checks */}
                    <div className="flex flex-col gap-1.5 text-xs text-neutral-700 dark:text-neutral-300">
                      <div className="flex items-center justify-between">
                        <span>Recording Consent Capture:</span>
                        {rec.consentCaptured ? (
                          <span className="font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 className="h-3.5 w-3.5" /> Passed
                          </span>
                        ) : (
                          <span className="font-bold text-rose-600 dark:text-rose-400 flex items-center gap-1">
                            <XCircle className="h-3.5 w-3.5" /> Failed
                          </span>
                        )}
                      </div>

                      <div className="flex items-center justify-between">
                        <span>Qualification Checks:</span>
                        <span className="font-semibold text-neutral-800 dark:text-neutral-200">
                          {rec.qualDetails}
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span>Live Verifier Handoff:</span>
                        <span className="font-bold text-blue-600 dark:text-blue-400">{rec.verifier}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
                    <span className="text-[10px] text-neutral-500">
                      Status: <strong className="text-neutral-800 dark:text-white">{rec.qaStatus}</strong>
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
      {/* MODAL 1: AI BOT CALL TRANSCRIPT DRAWER                                    */}
      {/* ========================================================================= */}
      {isTranscriptOpen && selectedTranscriptRec && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-2xl rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                <div>
                  <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                    AI Voice Bot Call Transcript
                  </h3>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 font-mono">
                    {selectedTranscriptRec.callId} • {selectedTranscriptRec.leadName} ({selectedTranscriptRec.phone})
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsTranscriptOpen(false)}
                className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white"
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
                      ? "bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-900/50 text-blue-900 dark:text-blue-100"
                      : line.speaker === "Lead"
                      ? "bg-neutral-100 dark:bg-neutral-900 border-neutral-200 dark:border-neutral-800 text-neutral-800 dark:text-neutral-200"
                      : "bg-purple-50 dark:bg-purple-950/30 border-purple-200 dark:border-purple-900/50 text-purple-900 dark:text-purple-100"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1 font-bold text-[11px]">
                    <span
                      className={
                        line.speaker === "Bot"
                          ? "text-blue-600 dark:text-blue-400"
                          : line.speaker === "Lead"
                          ? "text-emerald-600 dark:text-emerald-400"
                          : "text-purple-600 dark:text-purple-400"
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

            <div className="border-t border-neutral-200 dark:border-neutral-800 pt-4 mt-4 flex items-center justify-between text-xs">
              <span className="text-neutral-500 dark:text-neutral-400">
                Consent captured: <strong className="text-emerald-600 dark:text-emerald-400">YES</strong>
              </span>
              <button
                type="button"
                onClick={() => setIsTranscriptOpen(false)}
                className="rounded-md bg-neutral-200 dark:bg-neutral-800 px-4 py-1.5 font-bold text-neutral-800 dark:text-white hover:bg-neutral-300 dark:hover:bg-neutral-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: QA AUDIT & SCORECARD MODAL                                      */}
      {/* ========================================================================= */}
      {isQaModalOpen && selectedQaRec && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#121214] p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-neutral-200 dark:border-neutral-800 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                <h3 className="text-base font-bold text-neutral-900 dark:text-white">
                  QA Call Audit Scorecard
                </h3>
              </div>
              <button
                onClick={() => setIsQaModalOpen(false)}
                className="text-neutral-400 hover:text-neutral-700 dark:hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={saveQaAudit} className="flex flex-col gap-4 text-xs">
              <div className="rounded-lg bg-neutral-100 dark:bg-neutral-900 p-3 border border-neutral-200 dark:border-neutral-800">
                <p className="font-bold text-neutral-900 dark:text-white">
                  {selectedQaRec.leadName} ({selectedQaRec.phone})
                </p>
                <p className="text-[10px] text-neutral-500 dark:text-neutral-400 font-mono mt-0.5">
                  Call ID: {selectedQaRec.callId} • Campaign: {selectedQaRec.campaign} • Verifier: {selectedQaRec.verifier}
                </p>
              </div>

              {/* Star Rating Selector */}
              <div>
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
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
                          ? "bg-amber-100 dark:bg-amber-950/60 border-amber-400 dark:border-amber-500/80 text-amber-600 dark:text-amber-400"
                          : "bg-neutral-100 dark:bg-neutral-900 border-neutral-300 dark:border-neutral-800 text-neutral-400 dark:text-neutral-600"
                      }`}
                    >
                      <Star className={`h-5 w-5 ${qaRating >= star ? "fill-amber-400" : ""}`} />
                    </button>
                  ))}
                  <span className="font-bold text-amber-600 dark:text-amber-400 ml-2 font-mono text-sm">
                    {qaRating}.0 / 5.0
                  </span>
                </div>
              </div>

              {/* Mandatory Checklist Items */}
              <div className="flex flex-col gap-2 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] p-3">
                <span className="font-bold text-neutral-900 dark:text-white text-[11px]">
                  Compliance Checklist Audits:
                </span>

                <label className="flex items-center justify-between cursor-pointer text-neutral-800 dark:text-neutral-200">
                  <span>Mandatory Recording Consent Capture</span>
                  <input
                    type="checkbox"
                    checked={qaConsentVerified}
                    onChange={(e) => setQaConsentVerified(e.target.checked)}
                    className="h-4 w-4 rounded accent-emerald-500"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer text-neutral-800 dark:text-neutral-200">
                  <span>Medicare Qualification Checks</span>
                  <input
                    type="checkbox"
                    checked={qaQualVerified}
                    onChange={(e) => setQaQualVerified(e.target.checked)}
                    className="h-4 w-4 rounded accent-emerald-500"
                  />
                </label>

                <label className="flex items-center justify-between cursor-pointer text-neutral-800 dark:text-neutral-200">
                  <span>Live Verifier Warm Handoff</span>
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
                <label className="block font-bold text-neutral-700 dark:text-neutral-300 mb-1">
                  Auditor Comments & Compliance Notes
                </label>
                <textarea
                  rows={3}
                  value={qaNotes}
                  onChange={(e) => setQaNotes(e.target.value)}
                  placeholder="Enter auditor evaluation details..."
                  className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#18181b] p-2.5 text-neutral-900 dark:text-white outline-none focus:border-blue-500 dark:focus:border-neutral-600"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-800 mt-2">
                <button
                  type="button"
                  onClick={() => setIsQaModalOpen(false)}
                  className="rounded-md px-3 py-1.5 text-neutral-500 hover:text-neutral-800 dark:text-neutral-400 dark:hover:text-white"
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
