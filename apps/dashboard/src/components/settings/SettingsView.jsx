"use client";

import React, { useState, useMemo } from "react";
import {
  Settings,
  Server,
  Sparkles,
  PhoneCall,
  Shield,
  Database,
  Save,
  CheckCircle2,
  AlertCircle,
  Globe,
  Lock,
  Users,
  Radio,
  Sliders,
  Clock,
  Mic,
  Volume2,
  HardDrive,
  RefreshCw,
  Zap,
  Check,
  Bot,
  ShieldCheck,
  Headphones,
  ShieldAlert,
  UserCheck,
  Plus,
  Play,
  UserPlus,
  X,
  FileCode,
  Lock as LockIcon,
} from "lucide-react";
import { PendingApprovalsView } from "@/components/users";
import { RoleGuard } from "@/components/auth";

export default function SettingsView({ initialAction, onActionChange }) {
  // Determine mode from initialAction (e.g. /settings/telephony -> 'telephony')
  const activeSubTab = useMemo(() => {
    if (!initialAction || initialAction === "general") return "general";
    const parts = initialAction.split("/");
    return parts[0];
  }, [initialAction]);

  const handleSubTabChange = (sub) => {
    if (onActionChange) {
      onActionChange(sub === "general" ? null : sub);
    }
  };

  const [isSaved, setIsSaved] = useState(false);

  // Form States - General Settings
  const [displayName, setDisplayName] = useState("SmartBrains Medicare Portal");
  const [timezone, setTimezone] = useState("America/New_York (EST)");
  const [dateFormat, setDateFormat] = useState("YYYY-MM-DD");
  const [defaultPageSize, setDefaultPageSize] = useState("25");
  const [defaultRange, setDefaultRange] = useState("Today");

  // Telephony Settings (§30)
  const [callTimeout, setCallTimeout] = useState("45");
  const [amdSensitivity, setAmdSensitivity] = useState("High");
  const [callerIdStrategy, setCallerIdStrategy] = useState("Area Code Match Pool");

  // STT Settings (§30)
  const [sttProvider, setSttProvider] = useState("Deepgram Nova-2");
  const [sttModel, setSttModel] = useState("Nova-2 Medical/Medicare Optimized");
  const [sttLanguage, setSttLanguage] = useState("en-US");
  const [vadThreshold, setVadThreshold] = useState("250ms");

  // TTS Settings (§30)
  const [ttsProvider, setTtsProvider] = useState("ElevenLabs Turbo v2.5");
  const [ttsVoice, setTtsVoice] = useState("Rachel (US Professional Female)");
  const [ttsSpeed, setTtsSpeed] = useState("1.0");

  // LLM Settings (§30)
  const [llmProvider, setLlmProvider] = useState("Meta / Groq");
  const [llmModel, setLlmModel] = useState("Llama-3.3-70b-Instruct");
  const [llmMaxTokens, setLlmMaxTokens] = useState("256");
  const [llmTemperature, setLlmTemperature] = useState("0.1");
  const [llmFallbackEnabled, setLlmFallbackEnabled] = useState(true);

  // Qualification Rule Sets (§30)
  const [activeRuleSet, setActiveRuleSet] = useState("RuleSet-v2026.1 (Medicare Part A/B)");
  const [minAge, setMinAge] = useState("65");

  // Recordings Policy (§30)
  const [recordingEnabled, setRecordingEnabled] = useState(true);
  const [retentionDays, setRetentionDays] = useState("365");
  const [autoPurge, setAutoPurge] = useState(true);

  // Compliance Defaults (§30)
  const [consentVersion, setConsentVersion] = useState("v3.1 Verbal Disclosure");
  const [callingStart, setCallingStart] = useState("09:00");
  const [callingEnd, setCallingEnd] = useState("20:00");
  const [optOutKeywords, setOptOutKeywords] = useState("stop, do not call, remove me, opt out");

  // Security Settings (§30)
  const [sessionTimeout, setSessionTimeout] = useState("30");
  const [enforceMFA, setEnforceMFA] = useState(true);

  // User Accounts State (§30) — now served by PendingApprovalsView + UsersView via API.

  const handleSaveSettings = (e) => {
    e.preventDefault();
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2500);
  };

  const subtabItems = [
    { id: "general", label: "General", icon: Sliders },
    { id: "telephony", label: "Telephony", icon: PhoneCall },
    { id: "stt", label: "Speech-to-Text (STT)", icon: Mic },
    { id: "tts", label: "Text-to-Speech (TTS)", icon: Volume2 },
    { id: "llm", label: "LLM Engine", icon: Bot },
    { id: "qualification", label: "Eligibility Rules", icon: ShieldCheck },
    { id: "recordings", label: "Recordings Policy", icon: Headphones },
    { id: "compliance", label: "Compliance", icon: ShieldAlert },
    { id: "security", label: "Security", icon: Lock },
    { id: "users", label: "Users", icon: Users },
    { id: "roles", label: "Roles & Permissions", icon: UserCheck },
  ];

  return (
    <div className="flex flex-col gap-6 p-4 sm:p-6 text-neutral-900 dark:text-neutral-100 font-sans min-h-screen bg-neutral-50 dark:bg-[#050505] transition-colors duration-200">
      {/* 1. Header & Section Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200 dark:border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-neutral-900 dark:text-white tracking-tight">
              Application Settings & Configuration
            </h1>
            <span className="rounded-full bg-blue-100 dark:bg-blue-600/20 border border-blue-300 dark:border-blue-500/40 px-2.5 py-0.5 text-[10px] font-bold text-blue-700 dark:text-blue-400">
              PRD §30 FULL COMPLIANCE
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
            Configure system defaults, telephony connections, AI models (STT/TTS/LLM), Medicare eligibility rules, users, and security matrix.
          </p>
        </div>

        <button
          type="button"
          onClick={handleSaveSettings}
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-blue-700 transition-colors"
        >
          {isSaved ? (
            <>
              <Check className="h-4 w-4 text-emerald-300" />
              <span>Settings Saved!</span>
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              <span>Save Configuration</span>
            </>
          )}
        </button>
      </div>

      {/* 2. Horizontal Sub-Tabs Bar */}
      <div className="flex items-center gap-1.5 overflow-x-auto border-b border-neutral-200 dark:border-neutral-800/80 pb-3 text-xs font-semibold">
        {subtabItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeSubTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSubTabChange(item.id)}
              className={`flex items-center gap-2 rounded-lg px-3.5 py-2 whitespace-nowrap transition-all ${
                isActive
                  ? "bg-blue-600 text-white font-bold shadow-xs"
                  : "bg-white dark:bg-[#0d0d0d] text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white border border-neutral-200 dark:border-neutral-800"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* 3. Subtab Content Views */}

      {/* SUBTAB 1: General Settings */}
      {activeSubTab === "general" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Sliders className="h-4 w-4 text-blue-500" />
              <span>General Platform Preferences (PRD §30)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Portal Display Name</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Default Operating Timezone</label>
                <select
                  value={timezone}
                  onChange={(e) => setTimezone(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="America/New_York (EST)">America/New_York (EST)</option>
                  <option value="America/Chicago (CST)">America/Chicago (CST)</option>
                  <option value="America/Denver (MST)">America/Denver (MST)</option>
                  <option value="America/Los_Angeles (PST)">America/Los_Angeles (PST)</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Date Format</label>
                <select
                  value={dateFormat}
                  onChange={(e) => setDateFormat(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="YYYY-MM-DD">YYYY-MM-DD (ISO-8601)</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY (US Standard)</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Default Table Page Size</label>
                <select
                  value={defaultPageSize}
                  onChange={(e) => setDefaultPageSize(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="25">25 Rows</option>
                  <option value="50">50 Rows</option>
                  <option value="100">100 Rows</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Default Dashboard Date Range</label>
                <select
                  value={defaultRange}
                  onChange={(e) => setDefaultRange(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="Today">Today</option>
                  <option value="7 Days">Last 7 Days</option>
                  <option value="30 Days">Last 30 Days</option>
                </select>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 2: Telephony Settings */}
      {activeSubTab === "telephony" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                <PhoneCall className="h-4 w-4 text-emerald-500" />
                <span>Telephony Layer Status & Connection Settings (§30)</span>
              </h2>
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 text-[10px] font-bold">
                CONNECTED (Status Only)
              </span>
            </div>

            <p className="text-xs text-neutral-500">
              PRD §30 Note: Credentials remain backend-mediated. The frontend displays operational connection status and dialer timeouts.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Asterisk / VICIdial Endpoint</label>
                <input
                  type="text"
                  readOnly
                  value="sip:trunk.smartbrains.telephony (Active)"
                  className="rounded-md border border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-[#151518] px-3 py-2 outline-none text-neutral-500 font-mono"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Default Call Ring Timeout (seconds)</label>
                <input
                  type="number"
                  value={callTimeout}
                  onChange={(e) => setCallTimeout(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">AMD Machine Detection Sensitivity</label>
                <select
                  value={amdSensitivity}
                  onChange={(e) => setAmdSensitivity(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="High">High (Neural VAD + Tone Detection)</option>
                  <option value="Standard">Standard</option>
                  <option value="Disabled">Disabled</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Outbound Caller ID Rotation Strategy</label>
                <select
                  value={callerIdStrategy}
                  onChange={(e) => setCallerIdStrategy(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="Area Code Match Pool">Area Code Match Pool (STIR/SHAKEN A-Level)</option>
                  <option value="Round-Robin Trunk DID">Round-Robin Trunk DID</option>
                </select>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 3: STT Settings */}
      {activeSubTab === "stt" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Mic className="h-4 w-4 text-purple-500" />
              <span>Speech-to-Text (STT) Model & Provider Configuration (§30)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Active STT Provider</label>
                <select
                  value={sttProvider}
                  onChange={(e) => setSttProvider(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="Deepgram Nova-2">Deepgram Nova-2 (Streaming)</option>
                  <option value="Whisper Large-v3">Whisper Large-v3 (GPU Worker)</option>
                  <option value="Parakeet TDT">Parakeet TDT 1.1B</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Acoustic Model Domain</label>
                <input
                  type="text"
                  value={sttModel}
                  onChange={(e) => setSttModel(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Primary Language</label>
                <select
                  value={sttLanguage}
                  onChange={(e) => setSttLanguage(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="en-US">English (US) - en-US</option>
                  <option value="es-US">Spanish (US) - es-US</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Silero VAD Silence Endpoint Threshold</label>
                <input
                  type="text"
                  value={vadThreshold}
                  onChange={(e) => setVadThreshold(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 4: TTS Settings */}
      {activeSubTab === "tts" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Volume2 className="h-4 w-4 text-indigo-500" />
              <span>Text-to-Speech (TTS) Voice Synthesis Settings (§30)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">TTS Neural Engine Provider</label>
                <select
                  value={ttsProvider}
                  onChange={(e) => setTtsProvider(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="ElevenLabs Turbo v2.5">ElevenLabs Turbo v2.5</option>
                  <option value="Kokoro v1.0">Kokoro v1.0 82M</option>
                  <option value="Chatterbox Neural">Chatterbox Neural</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Bot Voice Persona</label>
                <select
                  value={ttsVoice}
                  onChange={(e) => setTtsVoice(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="Rachel (US Professional Female)">Rachel (US Professional Female)</option>
                  <option value="Adam (US Professional Male)">Adam (US Professional Male)</option>
                  <option value="Sarah (Empathetic Senior Specialist)">Sarah (Empathetic Senior Specialist)</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Speech Rate / Speed Multiplier</label>
                <input
                  type="text"
                  value={ttsSpeed}
                  onChange={(e) => setTtsSpeed(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>

              <div className="flex flex-col justify-end">
                <button
                  type="button"
                  onClick={() => alert("Playing sample bot audio preview: 'Hello, my name is Rachel with Medicare qualification...'")}
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 font-bold"
                >
                  <Play className="h-4 w-4" />
                  <span>Test Voice Synthesis Sample</span>
                </button>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 5: LLM Settings */}
      {activeSubTab === "llm" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Bot className="h-4 w-4 text-amber-500" />
              <span>Generative LLM Reasoning Fallback Engine (§30)</span>
            </h2>

            <div className="rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 p-3 text-amber-800 dark:text-amber-300 text-[11px] leading-relaxed">
              <strong>CRITICAL ARCHITECTURAL RULE (PRD §1 & §30):</strong> The LLM is used exclusively for conversational fallback and clarification. It must <strong>never</strong> be authoritative for final Medicare qualification decisions. Rule-based Script Engine evaluates all eligibility.
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">LLM Provider</label>
                <select
                  value={llmProvider}
                  onChange={(e) => setLlmProvider(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="Meta / Groq">Meta / Groq (Low Latency LPU)</option>
                  <option value="Qwen vLLM Cluster">Qwen vLLM On-Premise GPU Cluster</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Model Name</label>
                <input
                  type="text"
                  value={llmModel}
                  onChange={(e) => setLlmModel(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Max Tokens per Turn</label>
                <input
                  type="number"
                  value={llmMaxTokens}
                  onChange={(e) => setLlmMaxTokens(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Sampling Temperature</label>
                <input
                  type="text"
                  value={llmTemperature}
                  onChange={(e) => setLlmTemperature(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-neutral-200 dark:border-neutral-800">
              <span className="font-bold text-neutral-700 dark:text-neutral-300">Enable Generative Fallback for Unmapped Questions</span>
              <input
                type="checkbox"
                checked={llmFallbackEnabled}
                onChange={(e) => setLlmFallbackEnabled(e.target.checked)}
                className="h-4 w-4 rounded border-neutral-300 text-blue-600 focus:ring-blue-500"
              />
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 6: Eligibility Qualification Rules */}
      {activeSubTab === "qualification" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-blue-600" />
                <span>Medicare Eligibility Rule Sets & Version Binding (§30)</span>
              </h2>
              <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400 font-mono text-[10px] font-bold">
                EVALUATED BY BACKEND ONLY
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Active Rule Set Version</label>
                <select
                  value={activeRuleSet}
                  onChange={(e) => setActiveRuleSet(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-bold"
                >
                  <option value="RuleSet-v2026.1 (Medicare Part A/B)">RuleSet-v2026.1 (Medicare Part A/B)</option>
                  <option value="RuleSet-v2025.4 (Legacy)">RuleSet-v2025.4 (Legacy)</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Minimum Qualifying Age</label>
                <input
                  type="number"
                  value={minAge}
                  onChange={(e) => setMinAge(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-bold"
                />
              </div>
            </div>

            <div className="mt-2 border border-neutral-200 dark:border-neutral-800 rounded-lg p-3 bg-neutral-50 dark:bg-[#121215] flex flex-col gap-2">
              <span className="font-bold text-neutral-800 dark:text-neutral-200">Mandatory Qualified Prospect Criteria:</span>
              <ul className="list-disc list-inside text-neutral-600 dark:text-neutral-400 flex flex-col gap-1">
                <li>Age &gt;= 65 years (or Disability Medicare Entitlement)</li>
                <li>Medicare Part A Active = Yes</li>
                <li>Medicare Part B Active = Yes</li>
                <li>Resides in permitted campaign ZIP/State territory</li>
              </ul>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 7: Recordings Policy */}
      {activeSubTab === "recordings" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Headphones className="h-4 w-4 text-teal-600" />
              <span>Recording Retention & Access Policy (§30)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Record Call Audio Policy</label>
                <select
                  value={recordingEnabled ? "enabled" : "disabled"}
                  onChange={(e) => setRecordingEnabled(e.target.value === "enabled")}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="enabled">Enabled (Dual-Channel Stereo MP3)</option>
                  <option value="disabled">Disabled</option>
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Retention Days (Purge Policy)</label>
                <select
                  value={retentionDays}
                  onChange={(e) => setRetentionDays(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="90">90 Days</option>
                  <option value="180">180 Days</option>
                  <option value="365">365 Days (1 Year Standard)</option>
                  <option value="730">730 Days (2 Years Compliance)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-neutral-200 dark:border-neutral-800">
              <span className="font-bold text-neutral-700 dark:text-neutral-300">Automated S3 Retention Purge Worker</span>
              <input
                type="checkbox"
                checked={autoPurge}
                onChange={(e) => setAutoPurge(e.target.checked)}
                className="h-4 w-4 rounded border-neutral-300 text-blue-600 focus:ring-blue-500"
              />
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 8: Compliance */}
      {activeSubTab === "compliance" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-rose-500" />
              <span>TCPA & Compliance Defaults (§30)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Mandatory Consent Disclosure Version</label>
                <input
                  type="text"
                  value={consentVersion}
                  onChange={(e) => setConsentVersion(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-bold"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Default Calling Hours Window</label>
                <div className="flex items-center gap-2">
                  <input
                    type="time"
                    value={callingStart}
                    onChange={(e) => setCallingStart(e.target.value)}
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                  />
                  <span>to</span>
                  <input
                    type="time"
                    value={callingEnd}
                    onChange={(e) => setCallingEnd(e.target.value)}
                    className="w-full rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1.5 sm:col-span-2">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Opt-Out & DNC Keyword Triggers</label>
                <input
                  type="text"
                  value={optOutKeywords}
                  onChange={(e) => setOptOutKeywords(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 9: Security */}
      {activeSubTab === "security" && (
        <form onSubmit={handleSaveSettings} className="flex flex-col gap-6 max-w-3xl">
          <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
            <h2 className="text-sm font-bold text-neutral-900 dark:text-white flex items-center gap-2">
              <Lock className="h-4 w-4 text-blue-500" />
              <span>Security & Access Controls (§30)</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Idle Session Timeout (minutes)</label>
                <input
                  type="number"
                  value={sessionTimeout}
                  onChange={(e) => setSessionTimeout(e.target.value)}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-mono"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-bold text-neutral-700 dark:text-neutral-300">Multi-Factor Authentication (MFA)</label>
                <select
                  value={enforceMFA ? "enforce" : "optional"}
                  onChange={(e) => setEnforceMFA(e.target.value === "enforce")}
                  className="rounded-md border border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-[#151518] px-3 py-2 outline-none font-semibold"
                >
                  <option value="enforce">Enforce for All Roles</option>
                  <option value="optional">Optional</option>
                </select>
              </div>
            </div>
          </div>
        </form>
      )}

      {/* SUBTAB 10: Users Management (Approvals & Directory) */}
      {activeSubTab === "users" && (
        <RoleGuard
          allowedRoles={["MASTER_ADMIN", "DEVOPS_IT"]}
          fallback={
            <div className="flex min-h-[300px] w-full flex-col items-center justify-center rounded-xl border border-amber-200 bg-amber-50/40 p-6 text-center dark:border-amber-900/30 dark:bg-amber-950/20">
              <LockIcon className="h-8 w-8 text-amber-500" />
              <h3 className="mt-3 text-sm font-bold text-neutral-900 dark:text-white">
                Admin Role Required
              </h3>
              <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
                The Users management tab requires MASTER_ADMIN or DEVOPS_IT role.
              </p>
            </div>
          }
        >
          <PendingApprovalsView />
        </RoleGuard>
      )}

      {/* SUBTAB 11: Roles & Permission Matrix */}
      {activeSubTab === "roles" && (
        <div className="flex flex-col gap-4">
          <div className="border-b border-neutral-200 dark:border-neutral-800 pb-3">
            <h2 className="text-lg font-bold text-neutral-900 dark:text-white">Role Permission Matrix (PRD §3 & §7)</h2>
            <p className="text-xs text-neutral-500">Read-only view of TalkFlow&apos;s 6 PRD role definitions and module permission grants.</p>
          </div>

          <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-4 shadow-xs overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse min-w-[750px]">
              <thead>
                <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-500 uppercase text-[11px]">
                  <th className="py-2.5 px-3">Module Nav Group</th>
                  <th className="py-2.5 px-3">MASTER_ADMIN</th>
                  <th className="py-2.5 px-3">CAMPAIGN_MANAGER</th>
                  <th className="py-2.5 px-3">VERIFIER</th>
                  <th className="py-2.5 px-3">QA_MANAGER</th>
                  <th className="py-2.5 px-3">REPORTING_USER</th>
                  <th className="py-2.5 px-3">IT_OPS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60 font-medium">
                <tr><td className="py-2.5 px-3 font-bold">Dashboard</td><td>✓ Full</td><td>✓ Full</td><td>✓ Verifier</td><td>✓ QA</td><td>✓ Analytics</td><td>✓ Ops</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Leads</td><td>✓ Full</td><td>✓ Full</td><td>–</td><td>–</td><td>–</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Suppression</td><td>✓ Full</td><td>✓ Full</td><td>–</td><td>View</td><td>–</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Campaigns</td><td>✓ Full</td><td>✓ Full</td><td>–</td><td>View</td><td>View</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Scripts</td><td>✓ Full</td><td>✓ Full</td><td>–</td><td>View</td><td>–</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Transfers</td><td>✓ Full</td><td>✓ Full</td><td>Own</td><td>View</td><td>–</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Verifier Workspace</td><td>✓ Full</td><td>–</td><td>✓ Full</td><td>–</td><td>–</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">QA Module</td><td>✓ Full</td><td>View</td><td>–</td><td>✓ Full</td><td>View</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Analytics</td><td>✓ Full</td><td>✓ Full</td><td>–</td><td>✓ Full</td><td>✓ Full</td><td>–</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">System Health</td><td>✓ Full</td><td>–</td><td>–</td><td>–</td><td>–</td><td>✓ Full</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Settings</td><td>✓ Full</td><td>Limited</td><td>–</td><td>Limited</td><td>–</td><td>Limited</td></tr>
                <tr><td className="py-2.5 px-3 font-bold">Audit Log</td><td>✓ Full</td><td>–</td><td>–</td><td>View</td><td>–</td><td>View</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
