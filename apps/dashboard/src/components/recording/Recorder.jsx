"use client";

import React, { useState, useRef, useEffect } from "react";
import { Mic, Square, Pause, Play, Download, Trash2, Volume2, RefreshCw } from "lucide-react";

export default function Recorder({ onRecordingComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [recordingFilename, setRecordingFilename] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const audioPlayerRef = useRef(null);

  // Timer logic
  useEffect(() => {
    if (isRecording && !isPaused) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }

    return () => clearInterval(timerRef.current);
  }, [isRecording, isPaused]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        setAudioBlob(blob);
        setAudioUrl(url);
        setRecordingFilename(`talkflow-recording-${Date.now()}.webm`);

        if (onRecordingComplete) {
          onRecordingComplete({ blob, url, duration: recordingTime });
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setIsPaused(false);
      setRecordingTime(0);
      setAudioUrl(null);
      setRecordingFilename(null);
    } catch (err) {
      console.error("Microphone access denied or error starting recording:", err);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      // Stop all audio tracks
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
      setIsPaused(false);
    }
  };

  const togglePlayback = () => {
    if (audioPlayerRef.current) {
      if (isPlaying) {
        audioPlayerRef.current.pause();
        setIsPlaying(false);
      } else {
        audioPlayerRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const discardRecording = () => {
    setAudioUrl(null);
    setAudioBlob(null);
    setRecordingFilename(null);
    setRecordingTime(0);
    setIsPlaying(false);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 text-white max-w-lg shadow-xl">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <div className={`p-2 rounded-lg ${isRecording ? "bg-red-500/20 text-red-400 animate-pulse" : "bg-emerald-500/20 text-emerald-400"}`}>
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm">TalkFlow Audio Recorder</h3>
            <p className="text-xs text-slate-400">Capture caller voice & verifier handoff audio</p>
          </div>
        </div>
        <span className="font-mono text-sm px-3 py-1 bg-slate-800 rounded-full border border-slate-700 text-cyan-400 font-semibold">
          {formatTime(recordingTime)}
        </span>
      </div>

      {/* Waveform / Visual Indicator */}
      <div className="bg-slate-950 rounded-lg p-4 mb-4 flex items-center justify-center min-h-[70px] border border-slate-800/80">
        {isRecording ? (
          <div className="flex items-center space-x-1.5 h-8">
            {[40, 70, 30, 90, 50, 80, 100, 60, 40, 85, 30, 75, 45, 95, 60].map((h, i) => (
              <div
                key={i}
                className="w-1 bg-gradient-to-t from-cyan-500 to-emerald-400 rounded-full animate-pulse"
                style={{
                  height: isPaused ? "10%" : `${h}%`,
                  animationDelay: `${i * 0.08}s`,
                  transition: "height 0.2s ease",
                }}
              />
            ))}
          </div>
        ) : audioUrl ? (
          <div className="w-full flex items-center justify-between px-2">
            <audio
              ref={audioPlayerRef}
              src={audioUrl}
              onEnded={() => setIsPlaying(false)}
              className="hidden"
            />
            <button
              onClick={togglePlayback}
              className="p-2.5 bg-emerald-500 hover:bg-emerald-600 rounded-full text-slate-950 font-bold transition flex items-center justify-center"
            >
              {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
            </button>
            <div className="flex-1 mx-4">
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className={`h-full bg-emerald-400 ${isPlaying ? "animate-pulse w-full" : "w-1/3"}`} />
              </div>
            </div>
            <Volume2 className="w-5 h-5 text-slate-400" />
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic">Click Start Recording to begin voice capture</p>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between">
        {!isRecording && !audioUrl && (
          <button
            onClick={startRecording}
            className="w-full py-2.5 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg flex items-center justify-center space-x-2 transition shadow-lg shadow-red-950/50"
          >
            <Mic className="w-4 h-4" />
            <span>Start Recording</span>
          </button>
        )}

        {isRecording && (
          <div className="flex items-center space-x-3 w-full">
            <button
              onClick={pauseRecording}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded-lg flex items-center justify-center space-x-1.5 transition border border-slate-700"
            >
              {isPaused ? <Play className="w-4 h-4 text-emerald-400" /> : <Pause className="w-4 h-4 text-amber-400" />}
              <span>{isPaused ? "Resume" : "Pause"}</span>
            </button>
            <button
              onClick={stopRecording}
              className="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-lg flex items-center justify-center space-x-1.5 transition shadow-md shadow-red-950/30"
            >
              <Square className="w-4 h-4 fill-current" />
              <span>Stop & Save</span>
            </button>
          </div>
        )}

        {audioUrl && !isRecording && (
          <div className="flex items-center space-x-2 w-full">
            <button
              onClick={discardRecording}
              className="py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg flex items-center space-x-1 border border-slate-700 transition"
            >
              <Trash2 className="w-3.5 h-3.5 text-red-400" />
              <span>Discard</span>
            </button>
            <button
              onClick={startRecording}
              className="py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg flex items-center space-x-1 border border-slate-700 transition"
            >
              <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
              <span>Re-record</span>
            </button>
            <a
              href={audioUrl}
              download={recordingFilename}
              className="flex-1 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium rounded-lg flex items-center justify-center space-x-1 transition shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download MP3/WebM</span>
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
