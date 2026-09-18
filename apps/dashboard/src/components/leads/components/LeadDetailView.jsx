"use client";

import { ArrowLeft, Phone, Mail, MapPin, Award, Calendar, Play } from "lucide-react";

export default function LeadDetailView({ lead, onBack }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="p-1.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-neutral-900 dark:text-white">
                {lead.firstName} {lead.lastName}
              </h3>
              <span className="font-mono text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded border border-blue-200 dark:border-blue-800">
                {lead.id}
              </span>
            </div>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Lead Profile & Dialer Call Interaction History
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Metadata Card */}
        <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-neutral-100 dark:border-neutral-800 pb-3">
            <span className="text-xs font-bold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
              Lead Details
            </span>
            <span className="inline-flex items-center rounded-full bg-emerald-50 dark:bg-emerald-950/80 px-2.5 py-0.5 text-xs font-bold text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
              Score: {lead.score}/100
            </span>
          </div>

          <div className="flex flex-col gap-3 text-xs">
            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <Phone className="h-4 w-4 text-neutral-400 shrink-0" />
              <span className="font-mono font-semibold">{lead.phone}</span>
            </div>

            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <Mail className="h-4 w-4 text-neutral-400 shrink-0" />
              <span>{lead.email}</span>
            </div>

            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <MapPin className="h-4 w-4 text-neutral-400 shrink-0" />
              <span>{lead.address || "California, USA"}</span>
            </div>

            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <Award className="h-4 w-4 text-neutral-400 shrink-0" />
              <span>Campaign: <strong>{lead.campaign}</strong></span>
            </div>

            <div className="flex items-center gap-2.5 text-neutral-700 dark:text-neutral-300">
              <Calendar className="h-4 w-4 text-neutral-400 shrink-0" />
              <span>Created: {lead.createdAt}</span>
            </div>
          </div>

          <div className="mt-2 pt-3 border-t border-neutral-100 dark:border-neutral-800 flex flex-col gap-1.5">
            <span className="text-[11px] font-bold text-neutral-400 dark:text-neutral-500 uppercase">
              Lead Notes
            </span>
            <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed bg-neutral-50 dark:bg-[#151518] p-3 rounded-lg border border-neutral-200 dark:border-neutral-800">
              {lead.notes || "No additional notes recorded for this lead."}
            </p>
          </div>
        </div>

        {/* Call History Timeline */}
        <div className="lg:col-span-2 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-5 shadow-xs flex flex-col gap-4">
          <h4 className="text-sm font-bold text-neutral-900 dark:text-white border-b border-neutral-100 dark:border-neutral-800 pb-3">
            Call Interaction Timeline ({lead.callHistory?.length || 0} Calls)
          </h4>

          {(!lead.callHistory || lead.callHistory.length === 0) ? (
            <div className="py-12 text-center text-xs text-neutral-400 dark:text-neutral-500">
              No call recordings or dialer interactions logged for this lead yet.
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {lead.callHistory.map((call) => (
                <div
                  key={call.id}
                  className="flex flex-col gap-2 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-[#121215] p-4 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-neutral-900 dark:text-white">
                        {call.agent}
                      </span>
                      <span className="text-neutral-400">•</span>
                      <span className="text-neutral-500 dark:text-neutral-400">
                        {call.time}
                      </span>
                    </div>
                    <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 dark:bg-blue-950/80 px-2.5 py-0.5 text-xs font-bold text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                      {call.disposition}
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-neutral-600 dark:text-neutral-400 mt-1">
                    <span>Duration: <strong>{call.duration}</strong></span>
                    <button
                      type="button"
                      className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline font-bold"
                    >
                      <Play className="h-3 w-3" />
                      <span>Play Call Audio</span>
                    </button>
                  </div>

                  {call.notes && (
                    <p className="italic text-neutral-500 dark:text-neutral-400 mt-1 border-t border-neutral-200/60 dark:border-neutral-800/60 pt-2">
                      &quot;{call.notes}&quot;
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}