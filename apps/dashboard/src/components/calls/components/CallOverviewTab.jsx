"use client";

export default function CallOverviewTab({ call }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
        <h3 className="text-sm font-bold border-b border-neutral-100 dark:border-neutral-800 pb-3">
          CDR Call Metadata Overview
        </h3>

        <div className="flex flex-col gap-3">
          <div className="flex justify-between">
            <span className="text-neutral-500">Call Reference ID:</span>
            <span className="font-mono font-bold text-blue-600">{call.callId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">SIP Call ID:</span>
            <span className="font-mono">{call.sipCallId}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">Call Direction:</span>
            <span className="font-bold">{call.direction}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">Customer Name:</span>
            <span className="font-bold">{call.leadName}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">Phone Number:</span>
            <span className="font-mono font-bold">{call.phone}</span>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4 text-xs">
        <h3 className="text-sm font-bold border-b border-neutral-100 dark:border-neutral-800 pb-3">
          Campaign & Agent Execution
        </h3>

        <div className="flex flex-col gap-3">
          <div className="flex justify-between">
            <span className="text-neutral-500">Campaign Name:</span>
            <span className="font-bold text-neutral-800 dark:text-neutral-200">{call.campaign}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">Assigned Agent / Bot:</span>
            <span className="font-bold text-blue-600">{call.agent}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">AMD Machine Detection:</span>
            <span className="font-bold text-emerald-600">{call.amdResult}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-500">Duration:</span>
            <span className="font-mono font-bold">{call.duration} ({call.durationSec}s)</span>
          </div>
        </div>
      </div>
    </div>
  );
}