"use client";

import { useState, useMemo } from "react";
import {
  INITIAL_CAMPAIGNS,
  CAMPAIGN_TEAM_ASSIGNMENTS,
  CAMPAIGN_ACTIVE_SCRIPTS,
  CAMPAIGN_LIVE_OUTCOMES,
} from "@/data";

// Central campaign state + route parsing for CampaignsView.
// initialAction can be:
// - null / 'all' -> Main Campaign List View (/campaigns)
// - 'performance' -> Performance review subtab (/campaigns/performance)
// - 'team' -> Assign team subtab (/campaigns/team)
// - 'scripts' -> Active Scripts subtab (/campaigns/scripts)
// - 'outcomes' -> Live outcomes subtab (/campaigns/outcomes)
// - 'new' -> Create Campaign Page (/campaigns/new)
// - '[campaignId]' e.g. 'camp-2' -> Campaign Overview Page (/campaigns/camp-2)
// - '[campaignId]/dialing' e.g. 'camp-2/dialing' -> Dialing Settings (/campaigns/camp-2/dialing)
// - '[campaignId]/routing' e.g. 'camp-2/routing' -> Inbound & DID Routing (/campaigns/camp-2/routing)
// - '[campaignId]/script' e.g. 'camp-2/script' -> Active Script Binding (/campaigns/camp-2/script)
// - '[campaignId]/transfer' e.g. 'camp-2/transfer' -> Verifier Pool & Transfer Rules (/campaigns/camp-2/transfer)
// - '[campaignId]/performance' e.g. 'camp-2/performance' -> Campaign Analytics (/campaigns/camp-2/performance)
export function useCampaignState(initialAction, onActionChange) {
  const [campaigns, setCampaigns] = useState(INITIAL_CAMPAIGNS);
  const [teamAssignments, setTeamAssignments] = useState(CAMPAIGN_TEAM_ASSIGNMENTS);
  const [activeScripts, setActiveScripts] = useState(CAMPAIGN_ACTIVE_SCRIPTS);
  const [liveOutcomes, setLiveOutcomes] = useState(CAMPAIGN_LIVE_OUTCOMES);

  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortField, setSortField] = useState(null);
  const [sortAsc, setSortAsc] = useState(true);

  // Modals state
  const [isModalOpen, setIsModalOpen] = useState(initialAction === "new");
  const [selectedTeamCampaign, setSelectedTeamCampaign] = useState(null);
  const [newAgentName, setNewAgentName] = useState("");

  // Parse route segments
  const { currentMode, activeSubtab, activeCampId, subRoute } = useMemo(() => {
    if (!initialAction || initialAction === "all" || initialAction === "list") {
      return { currentMode: "subtab", activeSubtab: "all", activeCampId: null, subRoute: null };
    }
    if (initialAction === "performance" || initialAction === "team" || initialAction === "scripts" || initialAction === "outcomes") {
      return { currentMode: "subtab", activeSubtab: initialAction, activeCampId: null, subRoute: null };
    }
    if (initialAction === "new") {
      return { currentMode: "new", activeSubtab: "all", activeCampId: null, subRoute: null };
    }

    const parts = initialAction.split("/");
    const campId = parts[0];
    const sub = parts[1] || "overview";

    return { currentMode: "detail", activeSubtab: "all", activeCampId: campId, subRoute: sub };
  }, [initialAction]);

  const navigateToAction = (actionStr) => {
    if (onActionChange) {
      onActionChange(actionStr);
    }
  };

  // Find selected campaign for detail view
  const selectedCampaign = useMemo(() => {
    if (!activeCampId) return campaigns[0];
    return (
      campaigns.find(
        (c) =>
          c.id.toLowerCase() === activeCampId.toLowerCase() ||
          c.name.toLowerCase() === activeCampId.toLowerCase()
      ) || campaigns[0]
    );
  }, [campaigns, activeCampId]);

  // Form state for /campaigns/new
  const [newCampName, setNewCampName] = useState("");
  const [newDialMode, setNewDialMode] = useState("ratio");
  const [newDialLevel, setNewDialLevel] = useState("2.5");
  const [newAmd, setNewAmd] = useState("Enabled");
  const [newAmdSub, setNewAmdSub] = useState("Hangup");
  const [newManualTrunk, setNewManualTrunk] = useState("trunk_vici_01");
  const [newAutoTrunk, setNewAutoTrunk] = useState("trunk_vici_01");
  const [newThreeWayTrunk, setNewThreeWayTrunk] = useState("trunk_vici_01");
  const [newUserGroups, setNewUserGroups] = useState("Sales_Agents");

  // Summary metrics for list view
  const totalCount = campaigns.length;
  const activeCount = campaigns.filter((c) => c.status === "active").length;
  const pausedCount = campaigns.filter((c) => c.status === "paused").length;

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const filteredCampaigns = useMemo(() => {
    return campaigns
      .filter((camp) => {
        if (statusFilter === "active" && camp.status !== "active") return false;
        if (
          statusFilter === "inactive" &&
          camp.status !== "draft" &&
          camp.status !== "paused"
        )
          return false;

        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchName = camp.name.toLowerCase().includes(q);
          const matchMode = camp.dialMode.toLowerCase().includes(q);
          const matchStatus = camp.status.toLowerCase().includes(q);
          const matchTrunk =
            camp.trunks.manual.toLowerCase().includes(q) ||
            camp.trunks.auto.toLowerCase().includes(q);
          return matchName || matchMode || matchStatus || matchTrunk;
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
  }, [campaigns, searchQuery, statusFilter, sortField, sortAsc]);

  const handleCreateCampaignSubmit = (e) => {
    e.preventDefault();
    if (!newCampName.trim()) return;

    const newId = `camp-${Date.now().toString().slice(-4)}`;
    const newCampObj = {
      id: newId,
      name: newCampName.trim(),
      dialMode: newDialMode,
      status: "active",
      dialLevel: newDialLevel,
      amd: newAmd,
      amdSub: newAmd === "Enabled" ? newAmdSub : null,
      trunks: {
        manual: newManualTrunk,
        auto: newAutoTrunk,
        threeWay: newThreeWayTrunk,
      },
      recording: "On bridge",
      userGroups: newUserGroups,
      dialing: {
        hours: "09:00 - 18:00 EST",
        maxRetries: 4,
        callerIds: ["+1 (800) 555-0100"],
        pacing: `Mode ${newDialMode} (${newDialLevel}x)`,
        dropTimeout: "3.0s",
      },
      routing: {
        didMappings: [{ did: "+1 (800) 555-0100", queue: `${newCampName.trim()}_Q`, fallback: "IVR_Main" }],
        inboundQueue: `${newCampName.trim()}_Q`,
        fallbackIvr: "Default_Welcome_IVR",
      },
      script: {
        activeScript: "Default Sales Pitch v1",
        version: "v1.0.0",
        history: [{ version: "v1.0.0", date: new Date().toISOString().slice(0, 10), author: "Admin User", status: "Active" }],
      },
      transfer: {
        verifierPool: "Licensed QA Pool",
        transferRules: "Warm Consultative Transfer",
        maxWaitSec: 30,
      },
      performance: {
        callsDialed: "0",
        answered: "0",
        contactRate: "0.0%",
        conversions: "0",
        conversionRate: "0.0%",
        avgDuration: "0m 00s",
        dropRate: "0.0%",
      },
    };

    setCampaigns((prev) => [newCampObj, ...prev]);
    setNewCampName("");
    setIsModalOpen(false);
    navigateToAction(newId);
  };

  const handleAddAgentToTeam = (e) => {
    e.preventDefault();
    if (!selectedTeamCampaign || !newAgentName.trim()) return;

    setTeamAssignments((prev) =>
      prev.map((item) => {
        if (item.id === selectedTeamCampaign.id) {
          return {
            ...item,
            agentsCount: item.agentsCount + 1,
            agentsList: [
              ...item.agentsList,
              { name: newAgentName.trim(), role: "Licensed Agent", status: "Available" },
            ],
          };
        }
        return item;
      })
    );
    setNewAgentName("");
    setSelectedTeamCampaign(null);
  };

  return {
    campaigns,
    teamAssignments,
    activeScripts,
    liveOutcomes,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    isModalOpen,
    setIsModalOpen,
    selectedTeamCampaign,
    setSelectedTeamCampaign,
    newAgentName,
    setNewAgentName,
    currentMode,
    activeSubtab,
    subRoute,
    selectedCampaign,
    totalCount,
    activeCount,
    pausedCount,
    filteredCampaigns,
    newCampName,
    setNewCampName,
    newDialMode,
    setNewDialMode,
    newDialLevel,
    setNewDialLevel,
    newAmd,
    setNewAmd,
    newAmdSub,
    setNewAmdSub,
    newManualTrunk,
    setNewManualTrunk,
    newAutoTrunk,
    setNewAutoTrunk,
    newThreeWayTrunk,
    setNewThreeWayTrunk,
    handleCreateCampaignSubmit,
    handleAddAgentToTeam,
    navigateToAction,
  };
}