"use client";

import { useState, useMemo } from "react";
import { INITIAL_LEADS, SUPPRESSION_LIST_DATA } from "@/data";

// Central state + route parsing for LeadsView.
// initialAction mapping:
// - null / 'all' / 'list' -> Lead List View
// - 'import' -> Import Wizard View
// - 'suppression' -> DNC Suppression List View
// - otherwise (e.g. 'LEAD-1001') -> Lead Detail View
export function useLeadsState(initialAction, onActionChange) {
  const viewMode = useMemo(() => {
    if (!initialAction || initialAction === "all" || initialAction === "list") return "list";
    if (initialAction === "import") return "import";
    if (initialAction === "suppression") return "suppression";
    return "detail";
  }, [initialAction]);

  const activeLeadId = viewMode === "detail" ? initialAction : null;

  const navigateToAction = (actionStr) => {
    if (onActionChange) {
      onActionChange(actionStr);
    }
  };

  // State datasets
  const [leads, setLeads] = useState(INITIAL_LEADS);
  const [suppressionList, setSuppressionList] = useState(SUPPRESSION_LIST_DATA);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortField, setSortField] = useState("createdAt");
  const [sortAsc, setSortAsc] = useState(false);

  // Add Lead Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newFirstName, setNewFirstName] = useState("");
  const [newLastName, setNewLastName] = useState("");
  const [newPhone, setNewPhone] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newCampaign, setNewCampaign] = useState("Med Fronter");
  const [newStatus, setNewStatus] = useState("New");
  const [newState, setNewState] = useState("CA");

  // Add DNC Modal State
  const [isDncModalOpen, setIsDncModalOpen] = useState(false);
  const [newDncPhone, setNewDncPhone] = useState("");
  const [newDncReason, setNewDncReason] = useState("Customer Request");

  // Import Wizard State
  const [importStep, setImportStep] = useState(1); // 1: upload, 2: mapping, 3: progress
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [importProgress, setImportProgress] = useState(0);

  // Summary Metrics
  const totalCount = leads.length;
  const qualifiedCount = leads.filter((l) => l.status === "Qualified").length;
  const convertedCount = leads.filter((l) => l.status === "Converted").length;
  const contactedCount = leads.filter((l) => l.status === "Contacted").length;

  // Selected lead for detail view
  const selectedLead = useMemo(() => {
    if (!activeLeadId) return leads[0] || null;
    return leads.find((l) => l.id.toLowerCase() === activeLeadId.toLowerCase()) || leads[0];
  }, [leads, activeLeadId]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const filteredLeads = useMemo(() => {
    return leads
      .filter((lead) => {
        if (statusFilter !== "all" && lead.status.toLowerCase() !== statusFilter.toLowerCase()) {
          return false;
        }

        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const fullName = `${lead.firstName} ${lead.lastName}`.toLowerCase();
          const matchName = fullName.includes(q);
          const matchPhone = lead.phone.toLowerCase().includes(q);
          const matchEmail = lead.email.toLowerCase().includes(q);
          const matchCamp = lead.campaign.toLowerCase().includes(q);
          const matchId = lead.id.toLowerCase().includes(q);

          return matchName || matchPhone || matchEmail || matchCamp || matchId;
        }

        return true;
      })
      .sort((a, b) => {
        if (!sortField) return 0;
        let valA = a[sortField] || "";
        let valB = b[sortField] || "";
        if (typeof valA === "string") valA = valA.toLowerCase();
        if (typeof valB === "string") valB = valB.toLowerCase();

        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
      });
  }, [leads, searchQuery, statusFilter, sortField, sortAsc]);

  const handleAddLead = (e) => {
    e.preventDefault();
    if (!newFirstName.trim() || !newPhone.trim()) return;

    const newLeadObj = {
      id: `LEAD-${Date.now().toString().slice(-4)}`,
      firstName: newFirstName.trim(),
      lastName: newLastName.trim(),
      phone: newPhone.trim(),
      email: newEmail.trim() || "—",
      campaign: newCampaign,
      status: newStatus,
      state: newState,
      score: 75,
      createdAt: new Date().toISOString().replace("T", " ").slice(0, 16),
      lastContacted: "Just now",
      address: `${newState}, USA`,
      notes: "Newly added lead via dashboard interface.",
      callHistory: [],
    };

    setLeads((prev) => [newLeadObj, ...prev]);
    setNewFirstName("");
    setNewLastName("");
    setNewPhone("");
    setNewEmail("");
    setIsAddModalOpen(false);
  };

  const handleAddDnc = (e) => {
    e.preventDefault();
    if (!newDncPhone.trim()) return;

    const newDncObj = {
      id: `dnc-${Date.now().toString().slice(-3)}`,
      phone: newDncPhone.trim(),
      reason: newDncReason,
      addedBy: "Admin User",
      source: "Manual Entry",
      dateAdded: new Date().toISOString().slice(0, 10),
      status: "Active Suppression",
    };

    setSuppressionList((prev) => [newDncObj, ...prev]);
    setNewDncPhone("");
    setIsDncModalOpen(false);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFileName(file.name);
      setImportStep(2);
    }
  };

  const handleStartImport = () => {
    setImportStep(3);
    setImportProgress(25);
    setTimeout(() => setImportProgress(65), 500);
    setTimeout(() => {
      setImportProgress(100);
      // Append sample imported lead
      const importedLead = {
        id: `LEAD-${Date.now().toString().slice(-4)}`,
        firstName: "Carlos",
        lastName: "Mendoza",
        phone: "+1 (555) 321-9988",
        email: "c.mendoza@import.com",
        campaign: "Solar Outreach East",
        status: "New",
        state: "FL",
        score: 80,
        createdAt: new Date().toISOString().replace("T", " ").slice(0, 16),
        lastContacted: "—",
        address: "700 Biscayne Blvd, Miami, FL 33132",
        notes: "Imported via CSV Batch Upload.",
        callHistory: [],
      };
      setLeads((prev) => [importedLead, ...prev]);
    }, 1200);
  };

  return {
    viewMode,
    leads,
    setLeads,
    suppressionList,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    sortField,
    sortAsc,
    isAddModalOpen,
    setIsAddModalOpen,
    newFirstName,
    setNewFirstName,
    newLastName,
    setNewLastName,
    newPhone,
    setNewPhone,
    newEmail,
    setNewEmail,
    newCampaign,
    setNewCampaign,
    newStatus,
    setNewStatus,
    newState,
    setNewState,
    isDncModalOpen,
    setIsDncModalOpen,
    newDncPhone,
    setNewDncPhone,
    newDncReason,
    setNewDncReason,
    importStep,
    setImportStep,
    uploadedFileName,
    importProgress,
    totalCount,
    qualifiedCount,
    convertedCount,
    contactedCount,
    selectedLead,
    filteredLeads,
    navigateToAction,
    handleSort,
    handleAddLead,
    handleAddDnc,
    handleFileUpload,
    handleStartImport,
  };
}