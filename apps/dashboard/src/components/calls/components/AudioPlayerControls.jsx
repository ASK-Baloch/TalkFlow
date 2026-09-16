"use client";

import { Play, Pause, Download } from "lucide-react";

export default function AudioPlayerControls({
  call,
  isPlaying,
  onTogglePlay,
  playbackSpeed,
  onSpeedChange,
}) {
  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6 max-w-3xl">
      <div>
        <h3 className="text-base font-bold">Audio Recording Player</h3>
        <p className="text-xs text-neutral-500">Playback dual-channel stereo call audio</p>
      </div>

      <div className="bg-neutral-50 dark:bg-[#151518] p-5 rounded-xl border border-neutral-200 dark:border-neutral-800 flex flex-col gap-4">
        <div className="flex items-center justify-between text-xs">
          <span className="font-mono font-bold">{call.callId}.mp3</span>
          <span className="text-neutral-500 font-mono">00:58 / {call.duration}</span>
        </div>

        {/* Simulated Waveform */}
        <div className="flex items-center gap-1 h-12 bg-white dark:bg-[#09090b] p-3 rounded-lg border border-neutral-200 dark:border-neutral-800">
          {call.audioWaveform.map((val, idx) => (
            <div
              key={idx}
              className={`flex-1 rounded-full transition-colors ${
                idx < 7 ? "bg-blue-600" : "bg-neutral-300 dark:bg-neutral-700"
              }`}
              style={{ height: `${val}%` }}
            />
          ))}
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onTogglePlay}
              className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 shadow-md"
            >
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
            </button>
            <div className="flex items-center gap-1 text-xs">
              <span className="text-neutral-500 font-semibold">Speed:</span>
              {[1.0, 1.25, 1.5].map((spd) => (
                <button
                  key={spd}
                  onClick={() => onSpeedChange(spd)}
                  className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                    playbackSpeed === spd
                      ? "bg-blue-100 text-blue-700"
                      : "text-neutral-500"
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>
          </div>

          <a
            href={call.recordingUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-md border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-xs font-bold hover:bg-neutral-100"
          >
            <Download className="h-4 w-4" />
            <span>Download Recording MP3</span>
          </a>
        </div>
      </div>
    </div>
  );
}