"use client";

import {
  ArrowLeft,
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
} from "lucide-react";

export default function LeadImportWizard({
  onBack,
  importStep,
  onSetImportStep,
  uploadedFileName,
  onFileUpload,
  onStartImport,
  importProgress,
  onViewList,
}) {
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
            <h3 className="text-base font-bold text-neutral-900 dark:text-white">
              Bulk Lead Import Wizard
            </h3>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">
              Upload CSV or Excel list with automatic DNC scrubbing and campaign auto-assignment
            </p>
          </div>
        </div>
      </div>

      <div className="w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-[#0d0d0d] p-6 shadow-xs flex flex-col gap-6">
        {/* Step Indicators */}
        <div className="grid grid-cols-3 gap-4 border-b border-neutral-200 dark:border-neutral-800 pb-5">
          <div className={`flex items-center gap-3 ${importStep >= 1 ? "text-blue-600 dark:text-blue-400" : "text-neutral-400"}`}>
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${importStep >= 1 ? "bg-blue-600 text-white" : "bg-neutral-200 dark:bg-neutral-800"}`}>
              1
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold">Upload File</span>
              <span className="text-[11px] opacity-70">CSV / XLSX format</span>
            </div>
          </div>

          <div className={`flex items-center gap-3 ${importStep >= 2 ? "text-blue-600 dark:text-blue-400" : "text-neutral-400"}`}>
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${importStep >= 2 ? "bg-blue-600 text-white" : "bg-neutral-200 dark:bg-neutral-800"}`}>
              2
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold">Column Mapping</span>
              <span className="text-[11px] opacity-70">Verify Lead Fields</span>
            </div>
          </div>

          <div className={`flex items-center gap-3 ${importStep >= 3 ? "text-blue-600 dark:text-blue-400" : "text-neutral-400"}`}>
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${importStep >= 3 ? "bg-blue-600 text-white" : "bg-neutral-200 dark:bg-neutral-800"}`}>
              3
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold">Process & Scrub</span>
              <span className="text-[11px] opacity-70">Execute DNC Check</span>
            </div>
          </div>
        </div>

        {/* Step 1: Dropzone File Upload */}
        {importStep === 1 && (
          <div className="flex flex-col items-center justify-center border-2 border-dashed border-neutral-300 dark:border-neutral-800 rounded-xl p-10 bg-neutral-50/50 dark:bg-[#121215] text-center gap-3">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800/60">
              <UploadCloud className="h-7 w-7" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-neutral-900 dark:text-white">
                Select a CSV or Excel lead list to import
              </h4>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                Drag and drop your lead sheet here, or browse from your computer
              </p>
            </div>

            <label className="cursor-pointer inline-flex items-center gap-2 rounded-md bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-xs font-bold shadow-xs transition-colors mt-2">
              <FileSpreadsheet className="h-4 w-4" />
              <span>Choose Lead File</span>
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={onFileUpload}
                className="hidden"
              />
            </label>
          </div>
        )}

        {/* Step 2: Mapping Preview */}
        {importStep === 2 && (
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-between bg-blue-50 dark:bg-blue-950/40 p-3 rounded-lg border border-blue-200 dark:border-blue-800/60 text-xs">
              <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300 font-semibold">
                <FileSpreadsheet className="h-4 w-4" />
                <span>Loaded File: {uploadedFileName || "leads_batch_september.csv"}</span>
              </div>
              <span className="font-bold text-blue-600 dark:text-blue-400">1,250 Leads Detected</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="border-b border-neutral-200 dark:border-neutral-800 text-neutral-600 dark:text-neutral-400 font-semibold uppercase text-[11px]">
                    <th className="py-2.5 px-3">CSV Column Header</th>
                    <th className="py-2.5 px-3">Mapped TalkFlow Field</th>
                    <th className="py-2.5 px-3">Sample Value</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-200 dark:divide-neutral-800/60">
                  <tr>
                    <td className="py-3 px-3 font-mono">first_name</td>
                    <td className="py-3 px-3 font-bold text-blue-600 dark:text-blue-400">First Name</td>
                    <td className="py-3 px-3 text-neutral-600 dark:text-neutral-400">Carlos</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-3 font-mono">last_name</td>
                    <td className="py-3 px-3 font-bold text-blue-600 dark:text-blue-400">Last Name</td>
                    <td className="py-3 px-3 text-neutral-600 dark:text-neutral-400">Mendoza</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-3 font-mono">phone_number</td>
                    <td className="py-3 px-3 font-bold text-blue-600 dark:text-blue-400">Phone Number</td>
                    <td className="py-3 px-3 text-neutral-600 dark:text-neutral-400">+1 (555) 321-9988</td>
                  </tr>
                  <tr>
                    <td className="py-3 px-3 font-mono">email_address</td>
                    <td className="py-3 px-3 font-bold text-blue-600 dark:text-blue-400">Email Address</td>
                    <td className="py-3 px-3 text-neutral-600 dark:text-neutral-400">c.mendoza@import.com</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="flex justify-end gap-2 pt-4 border-t border-neutral-200 dark:border-neutral-800">
              <button
                type="button"
                onClick={() => onSetImportStep(1)}
                className="px-3 py-1.5 text-xs text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white"
              >
                Back
              </button>
              <button
                type="button"
                onClick={onStartImport}
                className="px-4 py-1.5 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-xs"
              >
                Start Import & Scrub DNC
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Import Progress */}
        {importStep === 3 && (
          <div className="flex flex-col items-center justify-center py-8 gap-4 text-center">
            {importProgress < 100 ? (
              <>
                <div className="h-2 w-full max-w-md bg-neutral-200 dark:bg-neutral-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all duration-300"
                    style={{ width: `${importProgress}%` }}
                  />
                </div>
                <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300">
                  Scrubbing & Importing Leads ({importProgress}%)...
                </span>
              </>
            ) : (
              <>
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800">
                  <CheckCircle2 className="h-6 w-6" />
                </div>
                <h4 className="text-sm font-bold text-neutral-900 dark:text-white">
                  Import Complete! 1,248 leads successfully added.
                </h4>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  2 phone numbers scrubbed & suppressed via DNC match.
                </p>

                <button
                  type="button"
                  onClick={onViewList}
                  className="mt-2 px-4 py-1.5 text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-xs"
                >
                  View Lead List
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}