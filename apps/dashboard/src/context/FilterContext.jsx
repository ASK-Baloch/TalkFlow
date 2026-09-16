"use client";

import React, { createContext, useContext, useState } from "react";
import {
  ALL_DISPOSITIONS,
  INITIAL_SELECTED_DISPOSITIONS,
  LIMIT_OPTIONS,
  TYPE_OPTIONS,
  DIALER_OPTIONS,
  SERVER_OPTIONS,
  DATE_PRESETS,
} from "@/data";

const FilterContext = createContext(null);

export function FilterProvider({ children }) {
  const [limit, setLimit] = useState("10,000");
  const [selectedDispositions, setSelectedDispositions] = useState(
    INITIAL_SELECTED_DISPOSITIONS
  );
  const [campaignType, setCampaignType] = useState("All");
  const [selectedDialer, setSelectedDialer] = useState("All");
  const [selectedServer, setSelectedServer] = useState("All");
  const [selectedDatePreset, setSelectedDatePreset] = useState(DATE_PRESETS[0]);

  const resetFilters = () => {
    setLimit("10,000");
    setSelectedDispositions(INITIAL_SELECTED_DISPOSITIONS);
    setCampaignType("All");
    setSelectedDialer("All");
    setSelectedServer("All");
    setSelectedDatePreset(DATE_PRESETS[0]);
  };

  const selectAllDispositions = () => {
    setSelectedDispositions([...ALL_DISPOSITIONS]);
  };

  const clearAllDispositions = () => {
    setSelectedDispositions([]);
  };

  const toggleDisposition = (disp) => {
    setSelectedDispositions((prev) =>
      prev.includes(disp)
        ? prev.filter((d) => d !== disp)
        : [...prev, disp]
    );
  };

  return (
    <FilterContext.Provider
      value={{
        limit,
        setLimit,
        selectedDispositions,
        setSelectedDispositions,
        campaignType,
        setCampaignType,
        selectedDialer,
        setSelectedDialer,
        selectedServer,
        setSelectedServer,
        selectedDatePreset,
        setSelectedDatePreset,
        resetFilters,
        selectAllDispositions,
        clearAllDispositions,
        toggleDisposition,
        LIMIT_OPTIONS,
        TYPE_OPTIONS,
        DIALER_OPTIONS,
        SERVER_OPTIONS,
        DATE_PRESETS,
        ALL_DISPOSITIONS,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilters() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error("useFilters must be used within a FilterProvider");
  }
  return context;
}
