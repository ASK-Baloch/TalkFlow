"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Monitor, Sun, LogOut } from "lucide-react";
import logo from "../../../public/logo2.png";

export default function TopNavbar() {
  const [isLightMode, setIsLightMode] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (isLightMode) {
      root.classList.remove("dark");
    } else {
      root.classList.add("dark");
    }
  }, [isLightMode]);

  const toggleTheme = () => {
    setIsLightMode((prev) => !prev);
  };

  return (
    <header className="flex h-14 w-full items-center justify-between border-b border-neutral-200 bg-white px-6 text-neutral-900 transition-colors duration-200 dark:border-[#1f1f1f] dark:bg-[#0a0a0a] dark:text-white">
      {/* Brand Logo */}
      <div className="flex items-center gap-3">
        <div className="flex items-center">
          <Image
            src={logo}
            alt="SmartBrains Logo"
            className="h-8 w-auto object-contain"
            priority
          />
        </div>
      </div>

      {/* Action Icons */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={toggleTheme}
          title={isLightMode ? "Switch to Dark Display" : "Switch to Light Display"}
          className="rounded p-1 text-neutral-500 transition-colors hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white"
        >
          {isLightMode ? (
            <Sun className="h-4 w-4 text-amber-500 transition-transform duration-200 hover:rotate-45" />
          ) : (
            <Monitor className="h-4 w-4 transition-transform duration-200 hover:scale-110" />
          )}
        </button>
        <button
          type="button"
          title="Logout"
          className="rounded p-1 text-neutral-500 transition-colors hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}