"use client";

export default function CallTranscriptTab({ call }) {
  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold">Call Transcript & Sentiment Analysis</h3>
        </div>
        <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-bold">
          Sentiment: {call.sentiment}
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {call.transcript.map((item, idx) => (
          <div
            key={idx}
            className={`flex flex-col gap-1 p-3.5 rounded-xl border text-xs ${
              item.speaker.startsWith("Bot")
                ? "bg-purple-50/80 dark:bg-purple-950/30 border-purple-200 dark:border-purple-800/60"
                : item.speaker.startsWith("Agent")
                ? "bg-blue-50/80 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800/60"
                : "bg-neutral-50 dark:bg-[#151518] border-neutral-200 dark:border-neutral-800"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-[11px] uppercase tracking-wider text-neutral-800 dark:text-neutral-200">
                {item.speaker}
              </span>
              <span className="font-mono text-[10px] text-neutral-400">{item.time}</span>
            </div>
            <p className="text-neutral-900 dark:text-neutral-100 leading-relaxed">{item.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}